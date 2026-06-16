from sqlalchemy.orm import Session

from app.agents.profile_agent import ProfileAgent
from app.models.profile import ProfileUpdateLog, StudentProfile


PROFILE_FIELDS = [
    "base_level",
    "learning_goal",
    "knowledge_state",
    "weak_points",
    "mastered_points",
    "learning_preference",
    "cognitive_style",
    "time_budget",
]


def extract_and_save_profile(db: Session, user_id: int, course_id: int, message: str) -> dict:
    agent = ProfileAgent()
    result = agent.run(user_message=message, context={})
    if not result.success:
        raise RuntimeError(f"ProfileAgent failed: {result.error}")

    profile_data = _normalize_profile(result.data)
    existing = db.query(StudentProfile).filter_by(user_id=user_id, course_id=course_id).first()
    old_json = {}

    if existing:
        old_json = {field: getattr(existing, field) for field in PROFILE_FIELDS}
        for field in PROFILE_FIELDS:
            setattr(existing, field, profile_data[field])
        existing.confidence = profile_data["confidence"]
    else:
        existing = StudentProfile(
            user_id=user_id,
            course_id=course_id,
            base_level=profile_data["base_level"],
            learning_goal=profile_data["learning_goal"],
            knowledge_state=profile_data["knowledge_state"],
            weak_points=profile_data["weak_points"],
            mastered_points=profile_data["mastered_points"],
            learning_preference=profile_data["learning_preference"],
            cognitive_style=profile_data["cognitive_style"],
            time_budget=profile_data["time_budget"],
            confidence=profile_data["confidence"],
        )
        db.add(existing)

    log = ProfileUpdateLog(
        user_id=user_id,
        course_id=course_id,
        old_profile_json=old_json,
        new_profile_json=profile_data,
        evidence=profile_data.get("evidence", ""),
        change_reason=profile_data.get("profile_change_reason", "Profile extracted from dialogue"),
        updated_by="ProfileAgent",
    )
    db.add(log)
    db.commit()
    db.refresh(existing)
    return {**profile_data, "confidence": existing.confidence}


def _normalize_profile(data: dict) -> dict:
    return {
        "base_level": data.get("base_level", "medium"),
        "learning_goal": data.get("learning_goal", ""),
        "knowledge_state": data.get("knowledge_state", ""),
        "weak_points": list(data.get("weak_points") or []),
        "mastered_points": list(data.get("mastered_points") or []),
        "learning_preference": list(data.get("learning_preference") or []),
        "cognitive_style": data.get("cognitive_style", "visual"),
        "time_budget": data.get("time_budget", ""),
        "confidence": data.get("confidence", "medium"),
        "evidence": data.get("evidence", ""),
        "profile_change_reason": data.get("profile_change_reason", "Profile extracted from dialogue"),
    }

