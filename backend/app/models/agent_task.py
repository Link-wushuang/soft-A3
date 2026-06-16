from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class AgentTask(Base):
    __tablename__ = "agent_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    task_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    progress = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AgentTrace(Base):
    __tablename__ = "agent_trace"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("agent_task.id"), nullable=False, index=True)
    agent_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    input_summary = Column(Text, default="")
    output_summary = Column(Text, default="")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    warnings = Column(JSON, default=list)
    confidence = Column(String(16), nullable=True)

