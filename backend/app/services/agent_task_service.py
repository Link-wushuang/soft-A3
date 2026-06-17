from sqlalchemy.orm import Session

from app.models.agent_task import AgentTask, AgentTrace


def create_task(db: Session, user_id: int, task_type: str, total_steps: int) -> AgentTask:
    task = AgentTask(
        user_id=user_id,
        task_type=task_type,
        status="pending",
        total_steps=total_steps,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task_progress(db: Session, task_id: int, progress: int, status: str = "running") -> None:
    task = db.query(AgentTask).filter_by(id=task_id).first()
    if task:
        task.progress = progress
        task.status = status
        db.commit()


def save_single_trace(db: Session, task_id: int, item: dict) -> None:
    existing = db.query(AgentTrace).filter_by(
        task_id=task_id, agent_name=item["agent_name"]
    ).first()
    if existing:
        existing.status = item["status"]
        existing.finished_at = item.get("finished_at")
        existing.duration_ms = item.get("duration_ms", 0)
        existing.warnings = item.get("warnings", [])
        existing.confidence = item.get("confidence")
    else:
        trace = AgentTrace(
            task_id=task_id,
            agent_name=item["agent_name"],
            status=item["status"],
            input_summary=item.get("input_summary", ""),
            output_summary=item.get("output_summary", ""),
            started_at=item.get("started_at"),
            finished_at=item.get("finished_at"),
            duration_ms=item.get("duration_ms", 0),
            warnings=item.get("warnings", []),
            confidence=item.get("confidence"),
        )
        db.add(trace)
    db.commit()
