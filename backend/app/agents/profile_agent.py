from pathlib import Path
from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient, get_llm_client

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "profile.txt"


class ProfileAgent(BaseAgent):
    name = "ProfileAgent"

    def __init__(self, llm: LLMClient | None = None):
        super().__init__(llm or get_llm_client())
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Extract an 8-dimension student profile from the conversation."

    def _execute(self, user_message: str = "", context: dict | None = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        return self.llm.chat_json(messages, schema_hint="profile")

