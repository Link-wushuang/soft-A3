import json
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import decode_token
from app.db.session import get_db
from app.models.agent_task import AgentTask, AgentTrace
from app.models.resource import GeneratedResource
from app.models.user import User
from app.schemas.resource import GenerateResourceRequest, ResourceResponse
from app.services.resource_service import start_resource_generation

import app.db.session as db_module

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/generate")
def generate(req: GenerateResourceRequest, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    task_id = start_resource_generation(db, user.id, req.knowledge_point_id)
    return {"task_id": task_id}


@router.get("/generate/{task_id}/stream")
def stream_generation(task_id: int, token: str = Query(...)):
    """SSE endpoint for real-time agent trace during resource generation.
    Uses query-string token auth because EventSource does not support
    Authorization headers."""
    if not token:
        return StreamingResponse(
            iter([f"event: error\ndata: {json.dumps({'message': 'Missing token'})}\n\n"]),
            media_type="text/event-stream",
        )
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        return StreamingResponse(
            iter([f"event: error\ndata: {json.dumps({'message': 'Invalid token'})}\n\n"]),
            media_type="text/event-stream",
        )

    user_id = int(payload["sub"])

    def event_stream():
        db = db_module.SessionLocal()
        try:
            task = db.query(AgentTask).filter_by(id=task_id).first()
            if not task or task.user_id != user_id:
                yield f"event: error\ndata: {json.dumps({'message': 'Task not found'})}\n\n"
                return

            seen_traces: set[str] = set()
            seen_resources: set[int] = set()

            for _ in range(120):
                db.expire_all()
                task_obj = db.query(AgentTask).filter_by(id=task_id).first()

                traces = db.query(AgentTrace).filter_by(task_id=task_id).all()
                for trace in traces:
                    key = f"{trace.agent_name}:{trace.status}"
                    if key not in seen_traces:
                        seen_traces.add(key)
                        yield (
                            f"event: agent_status\n"
                            f"data: {json.dumps({'agent_name': trace.agent_name, 'status': trace.status, 'duration_ms': trace.duration_ms, 'progress': task_obj.progress if task_obj else 0, 'total': task_obj.total_steps if task_obj else 0}, ensure_ascii=False)}\n\n"
                        )

                resources = db.query(GeneratedResource).filter_by(task_id=task_id).all()
                for resource in resources:
                    if resource.id not in seen_resources:
                        seen_resources.add(resource.id)
                        yield (
                            f"event: resource_ready\n"
                            f"data: {json.dumps({'resource_id': resource.id, 'resource_type': resource.resource_type, 'confidence': resource.confidence}, ensure_ascii=False)}\n\n"
                        )

                if task_obj and task_obj.status in ("completed", "failed"):
                    yield f"event: done\ndata: {json.dumps({'task_id': task_id, 'status': task_obj.status, 'total_resources': len(resources)})}\n\n"
                    return

                time.sleep(0.5)

            yield f"event: error\ndata: {json.dumps({'message': 'SSE timeout'})}\n\n"
        finally:
            db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("", response_model=list[ResourceResponse])
def list_resources(knowledge_point_id: int = Query(...),
                   user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    resources = db.query(GeneratedResource).filter_by(
        knowledge_point_id=knowledge_point_id, user_id=user.id
    ).order_by(GeneratedResource.created_at.desc()).all()
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    resource = db.query(GeneratedResource).filter_by(id=resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
