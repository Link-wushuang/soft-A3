from pydantic import BaseModel


class GenerateResourceRequest(BaseModel):
    knowledge_point_id: int


class ResourceResponse(BaseModel):
    id: int
    resource_type: str
    title: str
    content: str
    content_format: str
    confidence: str
    warnings: list[str]
    safety_status: str

    model_config = {"from_attributes": True}
