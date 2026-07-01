from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.course import KnowledgePoint
from app.models.exercise import AnswerRecord, Exercise
from app.models.profile import StudentProfile
from app.models.resource import GeneratedResource
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _date_range(period: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return (start_datetime, end_datetime) for the given period."""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "today":
        return today, now
    elif period == "week":
        monday = today - timedelta(days=today.weekday())
        return monday, now
    elif period == "month":
        first = today.replace(day=1)
        return first, now
    elif period == "semester":
        # rough: last 5 months
        return today - timedelta(days=150), now
    elif period == "custom":
        if start_date and end_date:
            return (
                datetime.strptime(start_date, "%Y-%m-%d"),
                datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1),
            )
        return today - timedelta(days=30), now
    # default: all time
    return None, None


@router.get("/summary")
def student_summary(course_id: int = 1, period: str = Query("all"),
                    start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None),
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    start, end = _date_range(period, start_date, end_date)

    answers_q = db.query(AnswerRecord).filter_by(user_id=user.id)
    resources_q = db.query(GeneratedResource).filter_by(user_id=user.id)
    if start:
        answers_q = answers_q.filter(AnswerRecord.created_at >= start)
        resources_q = resources_q.filter(GeneratedResource.created_at >= start)
    if end:
        answers_q = answers_q.filter(AnswerRecord.created_at <= end)
        resources_q = resources_q.filter(GeneratedResource.created_at <= end)

    total_answers = answers_q.count()
    correct_answers = answers_q.filter_by(is_correct=1).count()
    total_resources = resources_q.count()
    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()

    correctness_rate = (correct_answers / total_answers * 100) if total_answers > 0 else 0

    mistake_tag_counts: dict[str, int] = {}
    records = answers_q.all()
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


@router.get("/study-time")
def study_time(course_id: int = Query(1),
               user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    """返回近 7 天每日学习时长（分钟）与今日已学时长。

    学习时长由答题记录与资源生成记录的活动时间估算：每次答题计 5 分钟，
    每次资源生成计 15 分钟。今日聚焦建议基于画像薄弱点生成。
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=6)

    answer_records = (
        db.query(AnswerRecord)
        .filter(AnswerRecord.user_id == user.id, AnswerRecord.created_at >= week_ago)
        .all()
    )
    resource_records = (
        db.query(GeneratedResource)
        .filter(GeneratedResource.user_id == user.id, GeneratedResource.created_at >= week_ago)
        .all()
    )

    weekday_map = ["一", "二", "三", "四", "五", "六", "日"]
    daily_minutes: dict = {}
    for offset in range(7):
        day = week_ago + timedelta(days=offset)
        daily_minutes[day.date()] = 0

    for r in answer_records:
        if r.created_at:
            d = r.created_at.date()
            if d in daily_minutes:
                daily_minutes[d] += 5
    for r in resource_records:
        if r.created_at:
            d = r.created_at.date()
            if d in daily_minutes:
                daily_minutes[d] += 15

    today_minutes = daily_minutes.get(today.date(), 0)
    week_data = []
    sorted_days = sorted(daily_minutes.keys())
    for d in sorted_days:
        idx = d.weekday()
        week_data.append({
            "date": weekday_map[idx],
            "minutes": daily_minutes[d],
            "isToday": d == today.date(),
        })

    # 基于画像薄弱点生成今日聚焦建议
    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()
    suggestion = ""
    if profile and profile.weak_points:
        focus_topic = profile.weak_points[0]
        remaining = max(0, 90 - today_minutes)
        suggestion = f"建议聚焦「{focus_topic}」主题，今日还可学 {remaining} 分钟"
    else:
        suggestion = "暂无薄弱点，建议预习新知识点"

    return {
        "today_minutes": today_minutes,
        "daily_budget_minutes": 90,
        "week_data": week_data,
        "suggestion": suggestion,
    }


@router.get("/recommendations")
def recommendations(course_id: int = Query(1), period: str = Query("all"),
                    start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None),
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    start, end = _date_range(period, start_date, end_date)

    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()
    if not profile:
        return {"recommended": [], "reason": "请先完成对话建档"}

    weak = profile.weak_points or []

    mistake_counts: dict[int, int] = {}
    records_q = db.query(AnswerRecord).filter_by(user_id=user.id, is_correct=0)
    if start:
        records_q = records_q.filter(AnswerRecord.created_at >= start)
    if end:
        records_q = records_q.filter(AnswerRecord.created_at <= end)
    records = records_q.all()
    for r in records:
        ex = db.query(Exercise).filter_by(id=r.exercise_id).first()
        if ex:
            mistake_counts[ex.knowledge_point_id] = mistake_counts.get(ex.knowledge_point_id, 0) + 1

    recommended = []
    all_kps = db.query(KnowledgePoint).filter_by(course_id=course_id).order_by(KnowledgePoint.sort_order).all()
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
            else:
                score += 1
                reasons.append("未掌握的基础知识点")
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
def teacher_summary(period: str = Query("all"),
                    start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None),
                    user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")

    start, end = _date_range(period, start_date, end_date)

    total_students = db.query(User).filter_by(role="student").count()

    answers_q = db.query(AnswerRecord)
    resources_q = db.query(GeneratedResource)
    if start:
        answers_q = answers_q.filter(AnswerRecord.created_at >= start)
        resources_q = resources_q.filter(GeneratedResource.created_at >= start)
    if end:
        answers_q = answers_q.filter(AnswerRecord.created_at <= end)
        resources_q = resources_q.filter(GeneratedResource.created_at <= end)

    total_answers = answers_q.count()
    correct_answers = answers_q.filter_by(is_correct=1).count()
    overall_correctness_rate = (
        round(correct_answers / total_answers * 100, 1) if total_answers > 0 else 0
    )

    total_resources = resources_q.count()

    type_rows = (
        resources_q.with_entities(GeneratedResource.resource_type, sa_func.count())
        .group_by(GeneratedResource.resource_type)
        .all()
    )
    resource_type_counts = {row[0]: row[1] for row in type_rows}

    mistake_tag_counts: dict[str, int] = {}
    records = answers_q.all()
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
