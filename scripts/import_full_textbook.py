"""Import full textbook content as document chunks (Option B).
OCR ~18 pages per chapter (130+ total), chunk, and insert into
course_document + document_chunk tables with knowledge point linking.

Usage: cd backend && python ../scripts/import_full_textbook.py
"""
import os
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
OCR_DIR = ROOT / "data" / "textbook_ocr"
PDF_PATH = ROOT / "计算机操作系统（第4版）.pdf"
SEED_PATH = ROOT / "data" / "os_course_seed.json"

sys.path.insert(0, str(BACKEND))
os.chdir(str(BACKEND))

import easyocr
import fitz

from app.db.session import SessionLocal
from app.models.document import CourseDocument, DocumentChunk
from app.models.course import KnowledgePoint

# ── Chapter definitions (name, start_page_0b, end_page_0b) ──
CHAPTERS = [
    ("操作系统概述",       11, 55),
    ("进程与线程",         55, 110),
    ("进程同步与死锁",     110, 165),
    ("CPU 调度",           165, 210),
    ("内存管理",           210, 265),
    ("虚拟内存",           265, 310),
    ("文件系统",           310, 370),
    ("设备管理与磁盘调度", 370, 416),
]

SAFE_NAMES = {
    "操作系统概述": "ch01_overview",
    "进程与线程": "ch02_process_thread",
    "进程同步与死锁": "ch03_sync_deadlock",
    "CPU 调度": "ch04_cpu_sched",
    "内存管理": "ch05_memory",
    "虚拟内存": "ch06_virtual_mem",
    "文件系统": "ch07_filesystem",
    "设备管理与磁盘调度": "ch08_io_disk",
}

PAGES_PER_CHAPTER = 18
CHUNK_SIZE = 500  # match documents.py


def select_pages(start_pg: int, end_pg: int, count: int) -> list[int]:
    """Select `count` pages evenly spread across [start_pg, end_pg)."""
    step = (end_pg - start_pg) / count
    pages = [start_pg + int(i * step) for i in range(count)]
    # Deduplicate and sort
    return sorted(set(p for p in pages if p < end_pg))


def chunk_text(text: str) -> list[str]:
    """Chunk text by paragraphs, ~500 chars per chunk. Matches documents.py logic."""
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


def ocr_pages(reader, doc, pages: list[int], label: str) -> dict[int, str]:
    """OCR specific pages. Returns {page_num: text}. Skips existing PNGs."""
    results = {}
    for pg in pages:
        if pg < 0 or pg >= doc.page_count:
            continue

        png_path = OCR_DIR / f"{label}_p{pg+1:03d}.png"
        existing_text_path = OCR_DIR / f"{label}_p{pg+1:03d}.txt"

        if existing_text_path.exists():
            results[pg] = existing_text_path.read_text(encoding="utf-8")
            continue

        # Render + OCR
        pix = doc[pg].get_pixmap(dpi=150)
        pix.save(str(png_path))
        try:
            ocr_results = reader.readtext(str(png_path))
            page_text = " ".join(text for _, text, _ in ocr_results)
            results[pg] = page_text
            # Cache per-page text for future reuse
            existing_text_path.write_text(page_text, encoding="utf-8")
        except Exception as e:
            results[pg] = f"(OCR error: {e})"
        print(f"  p{pg+1}", end=" ", flush=True)
    print()
    return results


def link_chunks_to_kps(chunks: list[dict], db) -> list[dict]:
    """For each chunk, try to find matching knowledge points by title mention."""
    kps = db.query(KnowledgePoint).filter_by(course_id=1).all()
    for chunk in chunks:
        text = chunk["content"]
        matched_ids = []
        for kp in kps:
            if kp.title in text:
                matched_ids.append(kp.id)
        # Also try partial match (first 4 chars of KP title)
        if not matched_ids:
            for kp in kps:
                short = kp.title[:6]
                if len(short) >= 4 and short in text:
                    matched_ids.append(kp.id)
        chunk["kp_ids"] = matched_ids[:3]  # max 3 KPs per chunk
    return chunks


def main():
    print("=" * 60)
    print("Import Full Textbook — Option B (~18 pages/chapter)")
    print("=" * 60)

    # ── Load EasyOCR ──
    print("\n[1/4] Loading EasyOCR...")
    reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)

    # ── Open PDF ──
    print("[2/4] Opening PDF...")
    doc = fitz.open(str(PDF_PATH))
    print(f"  Total pages: {doc.page_count}")

    # ── OCR all chapters ──
    print(f"\n[3/4] OCR ~{PAGES_PER_CHAPTER} pages per chapter...")
    all_chapter_texts: dict[str, str] = {}

    for idx, (ch_name, start_pg, end_pg) in enumerate(CHAPTERS):
        sid = SAFE_NAMES[ch_name]
        pages = select_pages(start_pg, end_pg, PAGES_PER_CHAPTER)
        print(f"\n  [{ch_name}] ({len(pages)} pages: {pages[0]+1}-{pages[-1]+1})")
        page_texts = ocr_pages(reader, doc, pages, sid)
        combined = "\n\n".join(f"[p{pg+1}] {text}" for pg, text in sorted(page_texts.items()))
        all_chapter_texts[ch_name] = combined

        # Save full chapter text
        chapter_file = OCR_DIR / f"{sid}_full.txt"
        chapter_file.write_text(combined, encoding="utf-8")
        print(f"  → {chapter_file} ({len(combined)} chars)")

    doc.close()

    # ── Chunk and import to DB ──
    print("\n[4/4] Chunking and importing to database...")
    db = SessionLocal()

    try:
        # Clean old documents for course 1
        old_count = db.query(CourseDocument).filter_by(course_id=1).delete()
        db.commit()
        if old_count:
            print(f"  Deleted {old_count} old document(s)")

        total_chunks = 0
        for ch_name, text in all_chapter_texts.items():
            if not text.strip():
                continue

            chunks = chunk_text(text)
            if not chunks:
                continue

            # Create document
            doc_entry = CourseDocument(
                course_id=1,
                filename=f"{ch_name}.txt",
                content_text=text[:10000],
                content_type="textbook_ocr",
                chunk_count=len(chunks),
            )
            db.add(doc_entry)
            db.flush()

            # Create chunks with KP linking
            chunk_dicts = [{"content": c, "kp_ids": []} for c in chunks]
            chunk_dicts = link_chunks_to_kps(chunk_dicts, db)

            linked = 0
            for i, cd in enumerate(chunk_dicts):
                kp_ids = cd["kp_ids"]
                chunk_entry = DocumentChunk(
                    document_id=doc_entry.id,
                    chunk_index=i,
                    content=cd["content"],
                    knowledge_point_id=kp_ids[0] if kp_ids else None,
                )
                db.add(chunk_entry)
                if kp_ids:
                    linked += 1

            db.commit()
            db.refresh(doc_entry)
            total_chunks += len(chunks)
            print(f"  {ch_name}: {len(chunks)} chunks, {linked} linked to KPs (doc #{doc_entry.id})")

        print(f"\n{'=' * 60}")
        print(f"Import complete! {len(all_chapter_texts)} documents, {total_chunks} chunks")
        print(f"Course ID: 1 (操作系统)")

        # Show stats
        kp_count = db.query(KnowledgePoint).filter_by(course_id=1).count()
        linked_chunks = db.query(DocumentChunk).join(
            CourseDocument, DocumentChunk.document_id == CourseDocument.id
        ).filter(
            CourseDocument.course_id == 1,
            DocumentChunk.knowledge_point_id.isnot(None),
        ).count()
        print(f"Knowledge points: {kp_count}")
        print(f"Chunks linked to KPs: {linked_chunks}/{total_chunks}")

    finally:
        db.close()

    print("=" * 60)


if __name__ == "__main__":
    main()
