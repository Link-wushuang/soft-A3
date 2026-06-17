import json
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "extended_reading.txt"


class ExtendedReadingAgent(BaseAgent):
    name = "ExtendedReadingAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Generate reading list."

    def _execute(self, profile: dict | None = None, knowledge_context: dict | None = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            "请推荐拓展阅读材料。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        return self.llm.chat_json(messages, schema_hint="extended_reading")
