from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.course import KnowledgePoint
from app.models.exercise import AnswerRecord
from app.models.profile import StudentProfile
from app.models.resource import GeneratedResource
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


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


@router.get("/recommendations")
def recommendations(course_id: int = Query(1), user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()
    if not profile:
        return {"recommended": [], "reason": "请先完成对话建档"}

    weak = profile.weak_points or []

    mistake_counts: dict[int, int] = {}
    records = db.query(AnswerRecord).filter_by(user_id=user.id, is_correct=0).all()
    from app.models.exercise import Exercise
    for r in records:
        ex = db.query(Exercise).filter_by(id=r.exercise_id).first()
        if ex:
            mistake_counts[ex.knowledge_point_id] = mistake_counts.get(ex.knowledge_point_id, 0) + 1

    recommended = []
    all_kps = db.query(KnowledgePoint).filter_by(course_id=course_id).all()
    for kp in all_kps:
        score = 0
        reasons = []
        if kp.title in weak:
            score += 3
            reasons.append("画像薄弱点")
        if kp.id in mistake_counts:
            score += mistake_counts[kp.id]
            reasons.append(f"答错{mistake_counts[kp.id]}题")
        if kp.title not in (profile.mastered_points or []) and score == 0:
            if kp.difficulty in ("medium", "hard"):
                score += 1
                reasons.append("未掌握的中高难度知识点")
        if score > 0:
            recommended.append({
                "knowledge_point_id": kp.id,
                "title": kp.title,
                "chapter": kp.chapter,
                "difficulty": kp.difficulty,
                "score": score,
                "reasons": reasons,
            })

    recommended.sort(key=lambda x: x["score"], reverse=True)
    return {"recommended": recommended[:8]}


@router.get("/teacher-summary")
def teacher_summary(user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")

    total_students = db.query(User).filter_by(role="student").count()

    total_answers = db.query(AnswerRecord).count()
    correct_answers = db.query(AnswerRecord).filter_by(is_correct=1).count()
    overall_correctness_rate = (
        round(correct_answers / total_answers * 100, 1) if total_answers > 0 else 0
    )

    total_resources = db.query(GeneratedResource).count()

    type_rows = (
        db.query(GeneratedResource.resource_type, sa_func.count())
        .group_by(GeneratedResource.resource_type)
        .all()
    )
    resource_type_counts = {row[0]: row[1] for row in type_rows}

    mistake_tag_counts: dict[str, int] = {}
    records = db.query(AnswerRecord).all()
    for record in records:
        for tag in (record.mistake_tags or []):
            mistake_tag_counts[tag] = mistake_tag_counts.get(tag, 0) + 1

    top_mistake_tags = sorted(
        [{"tag": t, "count": c} for t, c in mistake_tag_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    trend_by_date: dict[str, dict[str, int]] = {}
    for record in records:
        day = record.created_at.date().isoformat() if record.created_at else "unknown"
        bucket = trend_by_date.setdefault(day, {"total": 0, "correct": 0})
        bucket["total"] += 1
        if record.is_correct:
            bucket["correct"] += 1

    correctness_rate_trend = [
        {
            "date": day,
            "correctness_rate": round(bucket["correct"] / bucket["total"] * 100, 1),
            "total_answers": bucket["total"],
        }
        for day, bucket in sorted(trend_by_date.items())
    ]

    weak_points: list[str] = []
    profiles = db.query(StudentProfile).all()
    for p in profiles:
        for wp in (p.weak_points or []):
            if wp not in weak_points:
                weak_points.append(wp)

    return {
        "total_students": total_students,
        "total_answers": total_answers,
        "overall_correctness_rate": overall_correctness_rate,
        "total_resources": total_resources,
        "resource_type_counts": resource_type_counts,
        "top_mistake_tags": top_mistake_tags,
        "correctness_rate_trend": correctness_rate_trend,
        "weak_points_summary": weak_points,
    }
