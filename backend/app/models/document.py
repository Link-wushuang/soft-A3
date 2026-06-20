from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class CourseDocument(Base):
    __tablename__ = "course_document"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    content_text = Column(Text, default="")
    content_type = Column(String(32), default="txt")
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("course_document.id"), nullable=False, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_point.id"), nullable=True, index=True)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)

    document = relationship("CourseDocument", back_populates="chunks")
