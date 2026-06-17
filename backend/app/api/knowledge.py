from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.course import Course, KnowledgePoint
from app.models.user import User

router = APIRouter(prefix="", tags=["knowledge"])


@router.get("/courses")
def list_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return [{"id": c.id, "name": c.name, "description": c.description} for c in courses]


@router.get("/courses/{course_id}/knowledge-points")
def list_knowledge_points(course_id: int, db: Session = Depends(get_db)):
    kps = db.query(KnowledgePoint).filter_by(course_id=course_id).order_by(
        KnowledgePoint.sort_order
    ).all()
    return [
        {
            "id": kp.id, "chapter": kp.chapter, "title": kp.title,
            "summary": kp.summary, "difficulty": kp.difficulty,
            "tags": kp.tags,
        }
        for kp in kps
    ]


class KnowledgePointCreate(BaseModel):
    course_id: int
    chapter: str
    title: str
    summary: str = ""
    key_content: str = ""
    difficulty: str = "medium"
    tags: list[str] = []


@router.post("/knowledge-points")
def create_knowledge_point(req: KnowledgePointCreate,
                           user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    kp = KnowledgePoint(**req.model_dump())
    db.add(kp)
    db.commit()
    db.refresh(kp)
    return {"id": kp.id, "title": kp.title}


@router.put("/knowledge-points/{kp_id}")
def update_knowledge_point(kp_id: int, req: KnowledgePointCreate,
                           user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    kp = db.query(KnowledgePoint).filter_by(id=kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in req.model_dump(exclude={"course_id"}).items():
        setattr(kp, key, value)
    db.commit()
    db.refresh(kp)
    return {"id": kp.id, "title": kp.title}


@router.delete("/knowledge-points/{kp_id}")
def delete_knowledge_point(kp_id: int, user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teachers only")
    kp = db.query(KnowledgePoint).filter_by(id=kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(kp)
    db.commit()
    return {"deleted": kp_id}
