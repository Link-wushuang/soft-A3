from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_point.id"), nullable=False, index=True)
    question_type = Column(String(32), nullable=False, default="choice")
    difficulty = Column(String(16), default="medium")
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    tags = Column(JSON, default=list)
    source = Column(String(16), default="seed")
    created_at = Column(DateTime, server_default=func.now())


class AnswerRecord(Base):
    __tablename__ = "answer_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    feedback = Column(Text, default="")
    mistake_tags = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())

