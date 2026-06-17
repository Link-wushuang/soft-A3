from sqlalchemy.orm import Session

from app.agents.evaluation_agent import EvaluationAgent
from app.agents.reflection_agent import ReflectionAgent
from app.models.course import KnowledgePoint
from app.models.exercise import AnswerRecord, Exercise
from app.models.profile import ProfileUpdateLog, StudentProfile
from app.services.llm_client import get_llm_client


def submit_and_evaluate(db: Session, user_id: int, exercise_id: int,
                        user_answer: str) -> dict:
    llm = get_llm_client()

    exercise = db.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        raise ValueError(f"Exercise {exercise_id} not found")

    eval_agent = EvaluationAgent(llm=llm)
    eval_result = eval_agent.run(
        question=exercise.question,
        correct_answer=exercise.answer,
        user_answer=user_answer,
        question_type=exercise.question_type,
    )

    eval_data = eval_result.data if eval_result.success else {
        "score": 0, "is_correct": False,
        "feedback": "评估失败", "mistake_tags": [],
    }

    record = AnswerRecord(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=user_answer,
        is_correct=1 if eval_data.get("is_correct") else 0,
        score=eval_data.get("score", 0),
        feedback=eval_data.get("feedback", ""),
        mistake_tags=eval_data.get("mistake_tags", []),
    )
    db.add(record)

    kp = db.query(KnowledgePoint).filter_by(id=exercise.knowledge_point_id).first()
    profile = db.query(StudentProfile).filter_by(user_id=user_id).first()

    reflection_data: dict = {}
    if profile and not eval_data.get("is_correct"):
        reflection_agent = ReflectionAgent(llm=llm)
        ref_result = reflection_agent.run(
            evaluation_result=eval_data,
            current_profile={
                "weak_points": profile.weak_points or [],
                "mastered_points": profile.mastered_points or [],
            },
        )
        if ref_result.success:
            reflection_data = ref_result.data
            changes = reflection_data.get("profile_changes", {})
            weak_changes = changes.get("weak_points", {})
            new_weak = list(set(
                (profile.weak_points or []) +
                weak_changes.get("added", [])
            ) - set(weak_changes.get("removed", [])))
            old_json = {
                "weak_points": profile.weak_points,
                "mastered_points": profile.mastered_points,
            }
            profile.weak_points = new_weak
            db.add(ProfileUpdateLog(
                user_id=user_id,
                course_id=profile.course_id,
                old_profile_json=old_json,
                new_profile_json={
                    "weak_points": new_weak,
                    "mastered_points": profile.mastered_points,
                },
                evidence=f"答题结果: {exercise.question[:50]}",
                change_reason=reflection_data.get("change_reason", "练习反馈更新"),
                updated_by="ReflectionAgent",
            ))

    db.commit()
    return {
        "evaluation": eval_data,
        "reflection": reflection_data,
        "answer_record_id": record.id,
    }
