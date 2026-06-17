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
        return {
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
