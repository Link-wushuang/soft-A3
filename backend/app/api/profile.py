from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.profile import ProfileUpdateLog, StudentProfile
from app.models.user import User
from app.schemas.profile import DialogueRequest, ProfileResponse
from app.services.profile_service import extract_and_save_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/dialogue", response_model=ProfileResponse)
def dialogue(req: DialogueRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return extract_and_save_profile(db, user.id, req.course_id, req.message)


@router.get("/logs")
def get_profile_logs_by_query(
    course_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _profile_logs(db, user.id, course_id)


@router.get("/{course_id}", response_model=ProfileResponse)
def get_profile(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()
    if not profile:
        return ProfileResponse(
            base_level="medium",
            learning_goal="",
            knowledge_state="",
            weak_points=[],
            mastered_points=[],
            learning_preference=[],
            cognitive_style="visual",
            time_budget="",
            confidence="low",
        )
    return profile


@router.get("/{course_id}/logs")
def get_profile_logs(course_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _profile_logs(db, user.id, course_id)


def _profile_logs(db: Session, user_id: int, course_id: int) -> list[dict]:
    logs = (
        db.query(ProfileUpdateLog)
        .filter_by(user_id=user_id, course_id=course_id)
        .order_by(ProfileUpdateLog.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "old_profile_json": log.old_profile_json,
            "new_profile_json": log.new_profile_json,
            "evidence": log.evidence,
            "change_reason": log.change_reason,
            "updated_by": log.updated_by,
            "created_at": str(log.created_at),
        }
        for log in logs
    ]

