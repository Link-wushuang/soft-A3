from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.exercise import AnswerRecord, Exercise
from app.models.user import User
from app.schemas.exercise import AnswerRecordResponse, ExerciseResponse, SubmitAnswerRequest
from app.services.evaluation_service import submit_and_evaluate

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseResponse])
def list_exercises(knowledge_point_id: int, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    exercises = db.query(Exercise).filter_by(knowledge_point_id=knowledge_point_id).all()
    return exercises


@router.post("/{exercise_id}/submit")
def submit(exercise_id: int, req: SubmitAnswerRequest,
           user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = submit_and_evaluate(db, user.id, exercise_id, req.user_answer)
    return result


@router.get("/answer-records", response_model=list[AnswerRecordResponse])
def answer_records(user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    records = db.query(AnswerRecord).filter_by(user_id=user.id).order_by(
        AnswerRecord.created_at.desc()
    ).limit(50).all()
    return records
