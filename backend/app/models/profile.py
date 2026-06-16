from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    base_level = Column(String(16), default="medium")
    learning_goal = Column(Text, default="")
    knowledge_state = Column(Text, default="")
    weak_points = Column(JSON, default=list)
    mastered_points = Column(JSON, default=list)
    learning_preference = Column(JSON, default=list)
    cognitive_style = Column(String(32), default="visual")
    time_budget = Column(String(128), default="")
    confidence = Column(String(16), default="low")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())


class ProfileUpdateLog(Base):
    __tablename__ = "profile_update_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    old_profile_json = Column(JSON, default=dict)
    new_profile_json = Column(JSON, default=dict)
    evidence = Column(Text, default="")
    change_reason = Column(Text, default="")
    updated_by = Column(String(32), default="ProfileAgent")
    created_at = Column(DateTime, server_default=func.now())

