from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.services.llm_client import LLMClient


@dataclass
class AgentResult:
    success: bool
    data: Any = None
    error: str = ""
    warnings: list[str] = field(default_factory=list)
    confidence: str = "medium"
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None
    duration_ms: int = 0

    @property
    def status(self) -> str:
        return "success" if self.success else "failed"

    def finish(self):
        self.finished_at = datetime.now()
        self.duration_ms = int((self.finished_at - self.started_at).total_seconds() * 1000)


class BaseAgent:
    name: str = "BaseAgent"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, **kwargs) -> AgentResult:
        result = AgentResult(success=False, started_at=datetime.now())
        try:
            data = self._execute(**kwargs)
            result.success = True
            result.data = data
        except Exception as exc:
            result.error = str(exc)
        result.finish()
        return result

    def _execute(self, **kwargs) -> Any:
        raise NotImplementedError

