import json

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


class ChatMessage(BaseModel):
    role: str
    content: str


class AssistantChatRequest(BaseModel):
    messages: list[ChatMessage]
    knowledge_point_id: int | None = None


def _build_context(db: Session, user: User, kp_id: int | None):
    knowledge_context: dict = {}
    course_id = 1
    if kp_id:
        kp = db.query(KnowledgePoint).filter_by(id=kp_id).first()
        if kp:
            knowledge_context = {
                "title": kp.title, "chapter": kp.chapter,
                "summary": kp.summary, "key_content": kp.key_content,
                "common_mistakes": kp.common_mistakes, "tags": kp.tags,
            }
            course_id = kp.course_id
            from app.agents.knowledge_agent import KnowledgeAgent
            doc_ctx = KnowledgeAgent()._get_document_context(db, kp)
            if doc_ctx:
                knowledge_context["document_context"] = doc_ctx

    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()
    profile_dict: dict = {}
    if profile:
        profile_dict = {
            "base_level": profile.base_level,
            "weak_points": profile.weak_points,
            "learning_preference": profile.learning_preference,
            "cognitive_style": profile.cognitive_style,
        }
    return knowledge_context, profile_dict


@router.post("/ask")
def tutor_ask(
    req: TutorAskRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kp = db.query(KnowledgePoint).filter_by(id=req.knowledge_point_id).first()
    if not kp:
        raise HTTPException(404, "Knowledge point not found")

    knowledge_context, profile_dict = _build_context(db, user, req.knowledge_point_id)

    agent = TutorAgent()
    result = agent.run(
        question=req.question,
        profile=profile_dict,
        knowledge_context=knowledge_context,
    )
    if not result.success:
        raise HTTPException(500, f"Tutor failed: {result.error}")

    return {"answer": result.data.get("answer", ""), "knowledge_point": kp.title}


@router.post("/chat")
def assistant_chat(
    req: AssistantChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not req.messages:
        raise HTTPException(400, "messages cannot be empty")

    knowledge_context, profile_dict = _build_context(db, user, req.knowledge_point_id)

    from app.services.llm_client import get_llm_client
    llm = get_llm_client()

    system_content = (
        "你是 EduPath 智能学习助手，帮助学生解答操作系统课程相关问题。\n"
        "要求：1.根据学生水平调整解释深度 2.给出具体例子 3.使用Markdown格式 4.简洁准确\n"
    )
    if profile_dict:
        system_content += f"\n学生画像：{json.dumps(profile_dict, ensure_ascii=False)}"
    if knowledge_context:
        system_content += f"\n知识上下文：{json.dumps(knowledge_context, ensure_ascii=False)}"

    messages = [{"role": "system", "content": system_content}]
    for m in req.messages:
        messages.append({"role": m.role, "content": m.content})

    answer = llm.chat(messages)
    return {"answer": answer}
