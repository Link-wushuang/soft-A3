from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class SafetyAuditLog(Base):
    __tablename__ = "safety_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey("generated_resource.id"), nullable=True, index=True)
    check_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    details = Column(Text, default="")
    blocked_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

