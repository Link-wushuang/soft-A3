import json
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "evaluation.txt"


class EvaluationAgent(BaseAgent):
    name = "EvaluationAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Evaluate student answer."

    def _execute(self, question: str = "", correct_answer: str = "",
                 user_answer: str = "", question_type: str = "choice", **kwargs) -> Any:
        if question_type == "choice":
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
            if is_correct:
                return {
                    "score": 1.0,
                    "is_correct": True,
                    "feedback": "回答正确！",
                    "mistake_tags": [],
                }

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"题目: {question}\n"
                f"标准答案: {correct_answer}\n"
                f"学生答案: {user_answer}\n"
                f"题型: {question_type}\n"
                "请评分。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="evaluation")
