import json
import threading

from sqlalchemy.orm import Session

from app.agents.orchestrator import Orchestrator
from app.models.agent_task import AgentTask
from app.models.course import KnowledgePoint
from app.models.profile import StudentProfile
from app.models.resource import GeneratedResource
from app.models.safety import SafetyAuditLog
from app.services.agent_task_service import create_task, save_single_trace, update_task_progress
from app.services.llm_client import get_llm_client

import app.db.session as db_module


def start_resource_generation(db: Session, user_id: int, knowledge_point_id: int) -> int:
    kp = db.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
    if not kp:
        raise ValueError(f"Knowledge point {knowledge_point_id} not found")

    task = create_task(db, user_id, "resource_generation", total_steps=9)

    thread = threading.Thread(
        target=_run_generation,
        args=(task.id, user_id, knowledge_point_id),
        daemon=True,
    )
    thread.start()
    return task.id


def _run_generation(task_id: int, user_id: int, knowledge_point_id: int) -> None:
    db = db_module.SessionLocal()
    try:
        llm = get_llm_client()
        orchestrator = Orchestrator(llm=llm)

        kp = db.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
        if not kp:
            raise ValueError(f"Knowledge point {knowledge_point_id} not found")

        knowledge_context = {
            "title": kp.title,
            "chapter": kp.chapter,
            "summary": kp.summary,
            "key_content": kp.key_content,
            "common_mistakes": kp.common_mistakes,
            "example_question": kp.example_question,
            "example_answer": kp.example_answer,
            "tags": kp.tags,
            "sources": kp.sources,
        }

        profile = db.query(StudentProfile).filter_by(
            user_id=user_id, course_id=kp.course_id
        ).first()
        profile_dict: dict = {}
        if profile:
            profile_dict = {
                "base_level": profile.base_level,
                "weak_points": profile.weak_points,
                "mastered_points": profile.mastered_points,
                "learning_preference": profile.learning_preference,
                "cognitive_style": profile.cognitive_style,
            }

        update_task_progress(db, task_id, 0, "running")

        completed_agents: set[str] = set()
        completed_lock = threading.Lock()

        def on_trace(trace_item: dict) -> None:
            # 并行执行时每个 trace 写入用独立 session，
            # 避免多线程共享同一 SQLAlchemy Session 导致 commit 冲突
            trace_db = db_module.SessionLocal()
            try:
                save_single_trace(trace_db, task_id, trace_item)
                if trace_item.get("status") == "success":
                    with completed_lock:
                        completed_agents.add(trace_item["agent_name"])
                        count = len(completed_agents)
                    update_task_progress(trace_db, task_id, count, "running")
            finally:
                trace_db.close()

        result = orchestrator.generate_resources(
            profile=profile_dict,
            knowledge_context=knowledge_context,
            on_trace=on_trace,
        )

        for res_data in result["resources"]:
            content = res_data["content"]
            if isinstance(content, (dict, list)):
                content_str = json.dumps(content, ensure_ascii=False)
                content_format = "json"
            else:
                content_str = str(content)
                content_format = "markdown"

            resource = GeneratedResource(
                task_id=task_id,
                knowledge_point_id=knowledge_point_id,
                user_id=user_id,
                resource_type=res_data["resource_type"],
                title=f"{kp.title} - {res_data['resource_type']}",
                content=content_str,
                content_format=content_format,
                confidence=res_data.get("confidence", "medium"),
                warnings=res_data.get("warnings", []),
                safety_status="passed" if not res_data.get("warnings") else "warning",
            )
            db.add(resource)
            db.flush()

            for warning in res_data.get("warnings", []):
                db.add(SafetyAuditLog(
                    resource_id=resource.id,
                    check_type=warning,
                    status="warning",
                    details=f"Warning during {res_data['resource_type']} generation",
                ))
            db.add(SafetyAuditLog(
                resource_id=resource.id,
                check_type="overall",
                status="passed" if not res_data.get("warnings") else "warning",
                details=f"{res_data['resource_type']} generation complete",
            ))

        update_task_progress(db, task_id, len(completed_agents), "completed")
        db.commit()

    except Exception as exc:
        try:
            update_task_progress(db, task_id, 0, "failed")
            task = db.query(AgentTask).filter_by(id=task_id).first()
            if task:
                task.error_message = str(exc)
            db.commit()
        except Exception:
            pass  # Database may have been torn down during tests
    finally:
        db.close()
