from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.exercise import AnswerRecord
from app.models.profile import StudentProfile
from app.models.resource import GeneratedResource
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def student_summary(course_id: int = 1, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    total_answers = db.query(AnswerRecord).filter_by(user_id=user.id).count()
    correct_answers = db.query(AnswerRecord).filter_by(user_id=user.id, is_correct=1).count()
    total_resources = db.query(GeneratedResource).filter_by(user_id=user.id).count()
    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()

    correctness_rate = (correct_answers / total_answers * 100) if total_answers > 0 else 0

    mistake_tag_counts: dict[str, int] = {}
    records = db.query(AnswerRecord).filter_by(user_id=user.id).all()
    for record in records:
        for tag in (record.mistake_tags or []):
            mistake_tag_counts[tag] = mistake_tag_counts.get(tag, 0) + 1

    return {
        "total_answers": total_answers,
        "correct_answers": correct_answers,
        "correctness_rate": round(correctness_rate, 1),
        "total_resources": total_resources,
        "weak_points": profile.weak_points if profile else [],
        "mastered_points": profile.mastered_points if profile else [],
        "mistake_tag_counts": mistake_tag_counts,
    }
