from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client


class KnowledgeAgent(BaseAgent):
    name = "KnowledgeAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())

    def _execute(self, knowledge_point_id: int = 0, db=None, **kwargs) -> Any:
        if db is None:
            return kwargs.get("knowledge_context", {})
        from app.models.course import KnowledgePoint
        kp = db.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
        if not kp:
            return {}
        result = {
            "title": kp.title,
            "chapter": kp.chapter,
            "summary": kp.summary,
            "key_content": kp.key_content,
            "common_mistakes": kp.common_mistakes,
            "example_question": kp.example_question,
            "example_answer": kp.example_answer,
            "tags": kp.tags,
            "sources": kp.sources,
        }

        doc_context = self._get_document_context(db, kp)
        if doc_context:
            result["document_context"] = doc_context
        return result

    def _get_document_context(self, db, kp) -> str:
        try:
            from app.models.document import DocumentChunk
        except ImportError:
            return ""
        # 1. Chunks directly linked to this knowledge point
        chunks = db.query(DocumentChunk).filter_by(knowledge_point_id=kp.id).limit(3).all()
        # 2. Full-text search by title
        if not chunks:
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.content.contains(kp.title)
            ).limit(3).all()
        # 3. Partial title match (first 6 chars, to handle OCR errors)
        if not chunks and len(kp.title) >= 6:
            short = kp.title[:6]
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.content.contains(short)
            ).limit(3).all()
        # 4. Match by chapter + any content
        if not chunks and kp.chapter:
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.content.contains(kp.chapter[:4])
            ).limit(3).all()
        if not chunks:
            return ""
        return "\n\n".join(c.content for c in chunks)
