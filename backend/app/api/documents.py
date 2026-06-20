import io

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.document import CourseDocument, DocumentChunk
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])

CHUNK_SIZE = 500


def _chunk_text(text: str) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) > CHUNK_SIZE and current:
            chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _extract_text_from_pdf(data: bytes) -> str:
    try:
        import fitz
    except ImportError:
        raise HTTPException(400, "PyMuPDF not installed; PDF upload unavailable")
    doc = fitz.open(stream=data, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


@router.post("/upload")
def upload_document(
    course_id: int = Query(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    filename = file.filename or "untitled"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
    data = file.file.read()

    if ext == "pdf":
        text = _extract_text_from_pdf(data)
        content_type = "pdf"
    elif ext in ("md", "markdown"):
        text = data.decode("utf-8", errors="replace")
        content_type = "markdown"
    else:
        text = data.decode("utf-8", errors="replace")
        content_type = "txt"

    chunks = _chunk_text(text)

    doc = CourseDocument(
        course_id=course_id,
        filename=filename,
        content_text=text[:10000],
        content_type=content_type,
        chunk_count=len(chunks),
    )
    db.add(doc)
    db.flush()

    for i, chunk_text in enumerate(chunks):
        db.add(DocumentChunk(
            document_id=doc.id,
            chunk_index=i,
            content=chunk_text,
        ))

    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "chunk_count": doc.chunk_count}


@router.get("")
def list_documents(
    course_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = db.query(CourseDocument).filter_by(course_id=course_id).order_by(
        CourseDocument.created_at.desc()
    ).all()
    return [
        {"id": d.id, "filename": d.filename, "content_type": d.content_type,
         "chunk_count": d.chunk_count, "created_at": str(d.created_at)}
        for d in docs
    ]


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(CourseDocument).filter_by(id=doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
    return {"ok": True}
