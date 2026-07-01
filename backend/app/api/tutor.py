import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.tutor_agent import TutorAgent
from app.core.deps import get_current_user
from app.core.security import decode_token
from app.db.session import get_db
from app.models.course import KnowledgePoint
from app.models.profile import StudentProfile
from app.models.user import User
from app.services.llm_client import get_llm_client

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


@router.get("/chat/stream")
def assistant_chat_stream(
    question: str = Query(...),
    knowledge_point_id: int | None = Query(None),
    token: str = Query(...),
):
    """SSE 流式答疑接口。

    用 SparkLLM.stream() 真·逐 token 流式输出，满足赛题"流式输出"要求。
    EventSource 不支持自定义 header，通过 query 传 token 鉴权。
    事件：token（增量文本）/ done（结束）/ error（错误）。
    """
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        return StreamingResponse(
            iter([f"event: error\ndata: {json.dumps({'message': 'Invalid token'})}\n\n"]),
            media_type="text/event-stream",
        )
    user_id = int(payload["sub"])

    def event_stream():
        import app.db.session as db_module
        db = db_module.SessionLocal()
        try:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                yield f"event: error\ndata: {json.dumps({'message': 'User not found'})}\n\n"
                return

            knowledge_context, profile_dict = _build_context(db, user, knowledge_point_id)

            system_content = (
                "你是 EduPath 智能学习助手，帮助学生解答操作系统课程相关问题。\n"
                "要求：1.根据学生水平调整解释深度 2.给出具体例子 "
                "3.使用Markdown格式 4.简洁准确\n"
            )
            if profile_dict:
                system_content += f"\n学生画像：{json.dumps(profile_dict, ensure_ascii=False)}"
            if knowledge_context:
                system_content += f"\n知识上下文：{json.dumps(knowledge_context, ensure_ascii=False)}"

            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": question},
            ]

            llm = get_llm_client()
            yield f"event: agent_status\ndata: {json.dumps({'agent_name': 'TutorAgent', 'status': 'running'}, ensure_ascii=False)}\n\n"

            for chunk in llm.stream(messages):
                yield f"event: token\ndata: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"

            yield f"event: done\ndata: {json.dumps({'status': 'completed'})}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'message': str(exc)}, ensure_ascii=False)}\n\n"
        finally:
            db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
