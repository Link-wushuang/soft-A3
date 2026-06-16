from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())


class KnowledgePoint(Base):
    __tablename__ = "knowledge_point"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    chapter = Column(String(128), nullable=False)
    title = Column(String(256), nullable=False)
    summary = Column(Text, default="")
    key_content = Column(Text, default="")
    common_mistakes = Column(JSON, default=list)
    example_question = Column(Text, default="")
    example_answer = Column(Text, default="")
    difficulty = Column(String(16), default="medium")
    tags = Column(JSON, default=list)
    sources = Column(JSON, default=list)
    case_materials = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class KnowledgeSource(Base):
    __tablename__ = "knowledge_source"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    chapter = Column(String(128), nullable=False)
    source_name = Column(String(256), nullable=False)
    source_url = Column(String(512), default="")
    created_at = Column(DateTime, server_default=func.now())

