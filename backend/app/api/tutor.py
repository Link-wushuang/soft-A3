from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.tutor_agent import TutorAgent
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.course import KnowledgePoint
from app.models.profile import StudentProfile
from app.models.user import User

router = APIRouter(prefix="/tutor", tags=["tutor"])


class TutorAskRequest(BaseModel):
    knowledge_point_id: int
    question: str


@router.post("/ask")
def tutor_ask(
    req: TutorAskRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kp = db.query(KnowledgePoint).filter_by(id=req.knowledge_point_id).first()
    if not kp:
        raise HTTPException(404, "Knowledge point not found")

    knowledge_context = {
        "title": kp.title,
        "chapter": kp.chapter,
        "summary": kp.summary,
        "key_content": kp.key_content,
        "common_mistakes": kp.common_mistakes,
        "tags": kp.tags,
    }

    # Fetch document chunks (textbook OCR) for additional context
    from app.agents.knowledge_agent import KnowledgeAgent
    k_agent = KnowledgeAgent()
    doc_context = k_agent._get_document_context(db, kp)
    if doc_context:
        knowledge_context["document_context"] = doc_context

    profile = db.query(StudentProfile).filter_by(
        user_id=user.id, course_id=kp.course_id
    ).first()
    profile_dict: dict = {}
    if profile:
        profile_dict = {
            "base_level": profile.base_level,
            "weak_points": profile.weak_points,
            "learning_preference": profile.learning_preference,
            "cognitive_style": profile.cognitive_style,
        }

    agent = TutorAgent()
    result = agent.run(
        question=req.question,
        profile=profile_dict,
        knowledge_context=knowledge_context,
    )
    if not result.success:
        raise HTTPException(500, f"Tutor failed: {result.error}")

    return {"answer": result.data.get("answer", ""), "knowledge_point": kp.title}
