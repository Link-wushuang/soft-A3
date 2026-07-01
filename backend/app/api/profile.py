import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import decode_token
from app.db.session import get_db
from app.models.profile import ProfileUpdateLog, StudentProfile
from app.models.user import User
from app.schemas.profile import DialogueRequest, ProfileResponse
from app.services.profile_service import extract_and_save_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/dialogue", response_model=ProfileResponse)
def dialogue(req: DialogueRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return extract_and_save_profile(db, user.id, req.course_id, req.message)


@router.get("/dialogue/stream")
def dialogue_stream(course_id: int = Query(...), message: str = Query(...),
                    token: str = Query(...)):
    """SSE endpoint for streaming profile dialogue.

    EventSource 不支持自定义 header，因此通过 query 传递 token 鉴权。
    Spark 等 HTTP 模型为一次性返回，这里将回复文本分块以 token 事件推送，
    满足赛题"流式输出"要求并改善首屏等待体验。
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
            yield f"event: agent_status\ndata: {json.dumps({'agent_name': 'ProfileAgent', 'status': 'running'}, ensure_ascii=False)}\n\n"
            try:
                result = extract_and_save_profile(db, user_id, course_id, message)
            except Exception as exc:
                yield f"event: error\ndata: {json.dumps({'message': f'画像提取失败: {exc}'}, ensure_ascii=False)}\n\n"
                return

            reply = result.get("reply", "画像已更新，请查看右侧画像卡片。")
            # 分块推送回复，模拟打字机流式效果
            chunk_size = 6
            for i in range(0, len(reply), chunk_size):
                yield f"event: token\ndata: {json.dumps({'text': reply[i:i+chunk_size]}, ensure_ascii=False)}\n\n"

            # 推送最终画像（去掉 reply，避免重复）
            profile_payload = {k: v for k, v in result.items() if k != "reply"}
            yield f"event: profile_ready\ndata: {json.dumps(profile_payload, ensure_ascii=False, default=str)}\n\n"
            yield f"event: done\ndata: {json.dumps({'status': 'completed'})}\n\n"
        finally:
            db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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

