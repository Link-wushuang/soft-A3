from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class LearningPath(Base):
    __tablename__ = "learning_path"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    status = Column(String(16), default="active")
    created_at = Column(DateTime, server_default=func.now())


class LearningPathNode(Base):
    __tablename__ = "learning_path_node"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path_id = Column(Integer, ForeignKey("learning_path.id"), nullable=False, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_point.id"), nullable=False)
    sort_order = Column(Integer, default=0)
    status = Column(String(16), default="pending")
    reason = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())

