from pydantic import BaseModel


class GeneratePathRequest(BaseModel):
    course_id: int


class PathNodeResponse(BaseModel):
    id: int
    knowledge_point_id: int
    knowledge_point_title: str
    sort_order: int
    status: str
    reason: str

    model_config = {"from_attributes": True}


class LearningPathResponse(BaseModel):
    id: int
    course_id: int
    status: str
    nodes: list[PathNodeResponse]

    model_config = {"from_attributes": True}


class UpdateNodeStatusRequest(BaseModel):
    status: str
