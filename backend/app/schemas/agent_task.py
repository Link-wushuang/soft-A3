from pydantic import BaseModel


class AgentTaskResponse(BaseModel):
    id: int
    task_type: str
    status: str
    progress: int
    total_steps: int
    error_message: str

    model_config = {"from_attributes": True}


class AgentTraceResponse(BaseModel):
    agent_name: str
    status: str
    duration_ms: int | None
    warnings: list[str]
    confidence: str | None

    model_config = {"from_attributes": True}
