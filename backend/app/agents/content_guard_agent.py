import json
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "content_guard.txt"


class ContentGuardAgent(BaseAgent):
    name = "ContentGuardAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Check content safety."

    def _execute(self, resource: dict | None = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"待检查的资源:\n{json.dumps(resource or {}, ensure_ascii=False)}\n\n"
                "请检查内容安全性。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="content_guard")
