from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.agent_task import AgentTask, AgentTrace
from app.models.user import User
from app.schemas.agent_task import AgentTaskResponse, AgentTraceResponse

router = APIRouter(prefix="/agent-tasks", tags=["agent-tasks"])


@router.get("/{task_id}", response_model=AgentTaskResponse)
def get_task(task_id: int, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    task = db.query(AgentTask).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/trace", response_model=list[AgentTraceResponse])
def get_trace(task_id: int, user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    traces = db.query(AgentTrace).filter_by(task_id=task_id).all()
    return traces
