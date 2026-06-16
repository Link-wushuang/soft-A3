from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class GeneratedResource(Base):
    __tablename__ = "generated_resource"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("agent_task.id"), nullable=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_point.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    resource_type = Column(String(32), nullable=False)
    title = Column(String(256), default="")
    content = Column(Text, nullable=False)
    content_format = Column(String(16), default="markdown")
    confidence = Column(String(16), default="medium")
    warnings = Column(JSON, default=list)
    safety_status = Column(String(16), default="pending")
    created_at = Column(DateTime, server_default=func.now())

