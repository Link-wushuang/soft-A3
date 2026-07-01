from sqlalchemy.orm import Session

from app.agents.evaluation_agent import EvaluationAgent
from app.agents.reflection_agent import ReflectionAgent
from app.models.course import KnowledgePoint
from app.models.exercise import AnswerRecord, Exercise
from app.models.learning_path import LearningPath
from app.models.profile import ProfileUpdateLog, StudentProfile
from app.services.llm_client import get_llm_client
from app.services.path_service import generate_learning_path

# 防抖：同一用户+课程下，距离上次自动重规划不足该秒数则跳过，避免每次答题都重建路径
REPLAN_DEBOUNCE_SECONDS = 600


def submit_and_evaluate(db: Session, user_id: int, exercise_id: int,
                        user_answer: str) -> dict:
    llm = get_llm_client()

    exercise = db.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        raise ValueError(f"Exercise {exercise_id} not found")

    eval_agent = EvaluationAgent(llm=llm)
    eval_result = eval_agent.run(
        question=exercise.question,
        correct_answer=exercise.answer,
        user_answer=user_answer,
        question_type=exercise.question_type,
    )

    eval_data = eval_result.data if eval_result.success else {
        "score": 0, "is_correct": False,
        "feedback": "评估失败", "mistake_tags": [],
    }

    record = AnswerRecord(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=user_answer,
        is_correct=1 if eval_data.get("is_correct") else 0,
        score=eval_data.get("score", 0),
        feedback=eval_data.get("feedback", ""),
        mistake_tags=eval_data.get("mistake_tags", []),
    )
    db.add(record)

    kp = db.query(KnowledgePoint).filter_by(id=exercise.knowledge_point_id).first()
    kp_title = kp.title if kp else ""
    profile = db.query(StudentProfile).filter_by(user_id=user_id).first()

    reflection_data: dict = {}
    if profile:
        old_json = {
            "weak_points": list(profile.weak_points or []),
            "mastered_points": list(profile.mastered_points or []),
        }

        if eval_data.get("is_correct"):
            correct_count = db.query(AnswerRecord).join(Exercise).filter(
                AnswerRecord.user_id == user_id,
                Exercise.knowledge_point_id == exercise.knowledge_point_id,
                AnswerRecord.is_correct == 1,
            ).count()
            if correct_count >= 2 and kp_title:
                new_weak = [w for w in (profile.weak_points or []) if w != kp_title]
                new_mastered = list(set((profile.mastered_points or []) + [kp_title]))
                if new_weak != (profile.weak_points or []) or new_mastered != (profile.mastered_points or []):
                    profile.weak_points = new_weak
                    profile.mastered_points = new_mastered
                    reflection_data = {
                        "change_reason": f"连续答对{correct_count}题，'{kp_title}'从薄弱点升级为已掌握",
                        "profile_changes": {
                            "weak_points": {"added": [], "removed": [kp_title]},
                            "mastered_points": {"added": [kp_title], "removed": []},
                        },
                    }
                    db.add(ProfileUpdateLog(
                        user_id=user_id,
                        course_id=profile.course_id,
                        old_profile_json=old_json,
                        new_profile_json={"weak_points": new_weak, "mastered_points": new_mastered},
                        evidence=f"连续答对{correct_count}题: {exercise.question[:50]}",
                        change_reason=reflection_data["change_reason"],
                        updated_by="ReflectionAgent",
                    ))
        else:
            reflection_agent = ReflectionAgent(llm=llm)
            ref_result = reflection_agent.run(
                evaluation_result={**eval_data, "knowledge_point": kp_title},
                current_profile=old_json,
            )
            if ref_result.success:
                reflection_data = ref_result.data
                changes = reflection_data.get("profile_changes", {})
                weak_changes = changes.get("weak_points", {})
                new_weak = list(set(
                    (profile.weak_points or []) +
                    weak_changes.get("added", []) +
                    ([kp_title] if kp_title else [])
                ) - set(weak_changes.get("removed", [])))
                mastered_changes = changes.get("mastered_points", {})
                new_mastered = list(set(
                    (profile.mastered_points or []) +
                    mastered_changes.get("added", [])
                ) - set(mastered_changes.get("removed", []) + ([kp_title] if kp_title else [])))
                profile.weak_points = new_weak
                profile.mastered_points = new_mastered
                db.add(ProfileUpdateLog(
                    user_id=user_id,
                    course_id=profile.course_id,
                    old_profile_json=old_json,
                    new_profile_json={"weak_points": new_weak, "mastered_points": new_mastered},
                    evidence=f"答题结果: {exercise.question[:50]}",
                    change_reason=reflection_data.get("change_reason", "练习反馈更新"),
                    updated_by="ReflectionAgent",
                ))

    db.commit()

    # 反思导致画像薄弱点变化时，触发 PathPlannerAgent 重新规划学习路径，
    # 形成 Reflection → PathPlanner 的多智能体协同闭环。
    # 仅在薄弱点确实发生变化且距离上次重规划超过防抖窗口时执行。
    path_replanned = False
    if profile and reflection_data:
        new_weak = set(profile.weak_points or [])
        old_weak = set(old_json.get("weak_points", []))
        if new_weak != old_weak:
            path_replanned = _maybe_replan_path(db, user_id, profile.course_id)

    return {
        "evaluation": eval_data,
        "reflection": reflection_data,
        "answer_record_id": record.id,
        "profile_updated": bool(reflection_data),
        "path_replanned": path_replanned,
    }


def _maybe_replan_path(db: Session, user_id: int, course_id: int) -> bool:
    """当画像薄弱点变化时触发路径重规划，带防抖避免频繁替换。"""
    from datetime import datetime, timedelta

    recent_cutoff = datetime.utcnow() - timedelta(seconds=REPLAN_DEBOUNCE_SECONDS)
    recent = (
        db.query(LearningPath)
        .filter(
            LearningPath.user_id == user_id,
            LearningPath.course_id == course_id,
            LearningPath.created_at >= recent_cutoff,
        )
        .order_by(LearningPath.created_at.desc())
        .first()
    )
    if recent:
        return False

    try:
        generate_learning_path(db, user_id, course_id)
        return True
    except Exception:
        # 路径重规划失败不应影响答题结果的返回
        return False
