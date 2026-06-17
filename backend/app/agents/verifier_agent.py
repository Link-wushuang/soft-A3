import json
from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "verifier.txt"


class VerifierAgent(BaseAgent):
    name = "VerifierAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Verify factual consistency of generated content."

    def _execute(self, resource: dict | None = None, knowledge_context: dict | None = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
                f"生成的资源:\n{json.dumps(resource or {}, ensure_ascii=False)}\n\n"
                "请验证资源内容的事实一致性。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="verifier")
