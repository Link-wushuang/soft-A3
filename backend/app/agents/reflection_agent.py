import json
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "reflection.txt"


class ReflectionAgent(BaseAgent):
    name = "ReflectionAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Reflect on evaluation and update profile."

    def _execute(self, evaluation_result: dict | None = None,
                 current_profile: dict | None = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"评估结果:\n{json.dumps(evaluation_result or {}, ensure_ascii=False)}\n\n"
                f"当前画像:\n{json.dumps(current_profile or {}, ensure_ascii=False)}\n\n"
                "请反思并给出画像更新建议。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="reflection")
