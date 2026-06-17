import json
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "path_planner.txt"


class PathPlannerAgent(BaseAgent):
    name = "PathPlannerAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Generate a personalized learning path."

    def _execute(self, profile: dict | None = None, knowledge_points: list | None = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"可用知识点:\n{json.dumps(knowledge_points or [], ensure_ascii=False)}\n\n"
            "请生成学习路径。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        return self.llm.chat_json(messages, schema_hint="path")
