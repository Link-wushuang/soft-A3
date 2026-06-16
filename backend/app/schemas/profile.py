from pydantic import BaseModel


class DialogueRequest(BaseModel):
    course_id: int
    message: str


class ProfileResponse(BaseModel):
    base_level: str
    learning_goal: str
    knowledge_state: str
    weak_points: list[str]
    mastered_points: list[str]
    learning_preference: list[str]
    cognitive_style: str
    time_budget: str
    confidence: str

    model_config = {"from_attributes": True}


class ProfileUpdateLogResponse(BaseModel):
    old_profile_json: dict
    new_profile_json: dict
    evidence: str
    change_reason: str
    updated_by: str
    created_at: str

    model_config = {"from_attributes": True}

