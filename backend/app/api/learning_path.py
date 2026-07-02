from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.course import KnowledgePoint
from app.models.learning_path import LearningPath, LearningPathNode
from app.models.user import User
from app.schemas.learning_path import (
    GeneratePathRequest,
    LearningPathResponse,
    PathNodeResponse,
    UpdateNodeStatusRequest,
)
from app.services.path_service import generate_learning_path

router = APIRouter(prefix="/learning-path", tags=["learning-path"])


@router.post("/generate", response_model=LearningPathResponse)
def generate(req: GeneratePathRequest, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    path = generate_learning_path(db, user.id, req.course_id)
    return _path_to_response(db, path)


@router.get("/current", response_model=LearningPathResponse)
def current(course_id: int = Query(...), user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter_by(
        user_id=user.id, course_id=course_id, status="active"
    ).first()
    if not path:
        raise HTTPException(status_code=404, detail="No active learning path")
    return _path_to_response(db, path)


@router.get("/history")
def path_history(course_id: int = Query(...), user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """返回该用户+课程的所有学习路径历史（含已替换的旧路径），用于展示重规划历史。"""
    paths = db.query(LearningPath).filter_by(
        user_id=user.id, course_id=course_id
    ).order_by(LearningPath.created_at.desc()).limit(20).all()

    history = []
    for p in paths:
        nodes = db.query(LearningPathNode).filter_by(path_id=p.id).order_by(
            LearningPathNode.sort_order
        ).all()
        node_summaries = []
        for node in nodes:
            kp = db.query(KnowledgePoint).filter_by(id=node.knowledge_point_id).first()
            node_summaries.append({
                "knowledge_point_title": kp.title if kp else "Unknown",
                "status": node.status,
                "reason": node.reason,
            })
        history.append({
            "id": p.id,
            "status": p.status,
            "created_at": str(p.created_at) if p.created_at else None,
            "node_count": len(nodes),
            "nodes": node_summaries,
        })
    return {"history": history}


@router.put("/nodes/{node_id}/status")
def update_node_status(node_id: int, req: UpdateNodeStatusRequest,
                       user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    node = db.query(LearningPathNode).filter_by(id=node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = req.status
    db.commit()
    return {"id": node.id, "status": node.status}


def _path_to_response(db: Session, path: LearningPath) -> dict:
    nodes = db.query(LearningPathNode).filter_by(path_id=path.id).order_by(
        LearningPathNode.sort_order
    ).all()
    node_responses = []
    for node in nodes:
        kp = db.query(KnowledgePoint).filter_by(id=node.knowledge_point_id).first()
        node_responses.append(PathNodeResponse(
            id=node.id,
            knowledge_point_id=node.knowledge_point_id,
            knowledge_point_title=kp.title if kp else "Unknown",
            sort_order=node.sort_order,
            status=node.status,
            reason=node.reason,
        ))
    return LearningPathResponse(
        id=path.id, course_id=path.course_id,
        status=path.status, nodes=node_responses,
    )
