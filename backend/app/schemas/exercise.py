from pydantic import BaseModel


class SubmitAnswerRequest(BaseModel):
    user_answer: str


class ExerciseResponse(BaseModel):
    id: int
    question_type: str
    difficulty: str
    question: str
    options: list[str] | None
    tags: list[str]

    model_config = {"from_attributes": True}


class AnswerRecordResponse(BaseModel):
    id: int
    exercise_id: int
    user_answer: str
    is_correct: int
    score: float
    feedback: str
    mistake_tags: list[str]

    model_config = {"from_attributes": True}
