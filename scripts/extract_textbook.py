"""Extract key content from scanned OS textbook and enrich knowledge base.

Strategy: OCR key pages → map to knowledge points → LLM enrichment.
"""
import json
import re
from pathlib import Path

import easyocr
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "计算机操作系统（第4版）.pdf"
SEED_PATH = ROOT / "data" / "os_course_seed.json"
OUTPUT_DIR = ROOT / "data" / "textbook_ocr"

# Chapter index → (name, start_page_0b, end_page_0b)
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


def safe_name(ch_name: str) -> str:
    """Map chapter name to ASCII-safe identifier."""
    mapping = {
        "操作系统概述": "ch01_overview",
        "进程与线程": "ch02_process_thread",
        "进程同步与死锁": "ch03_sync_deadlock",
        "CPU 调度": "ch04_cpu_sched",
        "内存管理": "ch05_memory",
        "虚拟内存": "ch06_virtual_mem",
        "文件系统": "ch07_filesystem",
        "设备管理与磁盘调度": "ch08_io_disk",
    }
    return mapping.get(ch_name, ch_name)


def ocr_pages(reader, doc, pages: list[int], label: str) -> str:
    """OCR specific pages, return concatenated text. 'label' must be ASCII-safe."""
    texts = []
    for pg in pages:
        if pg < 0 or pg >= doc.page_count:
            continue
        pix = doc[pg].get_pixmap(dpi=120)
        img_path = str(OUTPUT_DIR / f"{label}_p{pg+1:03d}.png")
        pix.save(img_path)
        try:
            results = reader.readtext(img_path)
            page_text = " ".join(text for _, text, _ in results)
            texts.append(f"[p{pg+1}] {page_text}")
        except Exception as e:
            texts.append(f"[p{pg+1}] <OCR error: {e}>")
        print(f"    p{pg+1}", end=" ", flush=True)
    print()
    return "\n\n".join(texts)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Loading EasyOCR...")
    reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)

    print("Opening PDF...")
    doc = fitz.open(str(PDF_PATH))

    # === Step 1: TOC extraction ===
    print("\n=== Step 1: TOC (目录) ===")
    toc_cache = OUTPUT_DIR / "toc_full.txt"
    if toc_cache.exists():
        toc_text = toc_cache.read_text(encoding="utf-8")
        print(f"  Using cached TOC ({len(toc_text)} chars)")
    else:
        print("  OCR'ing TOC pages 8-12...")
        toc_pages = [7, 8, 9, 10, 11]  # pages 8-12
        toc_text = ocr_pages(reader, doc, toc_pages, "toc")
        toc_cache.write_text(toc_text, encoding="utf-8")
        print(f"  Saved ({len(toc_text)} chars)")

    # === Step 2: Extract key pages per chapter ===
    print("\n=== Step 2: Chapter content ===")
    all_chapter_text = {}

    for idx, (ch_name, start_pg, end_pg) in enumerate(CHAPTERS):
        sid = safe_name(ch_name)
        cache_file = OUTPUT_DIR / f"{sid}.txt"

        if cache_file.exists():
            all_chapter_text[ch_name] = cache_file.read_text(encoding="utf-8")
            print(f"  [{ch_name}] Using cached ({len(all_chapter_text[ch_name])} chars)")
            continue

        # First 4 pages + 1 middle + 1 end
        pages = list(range(start_pg, min(start_pg + 4, end_pg)))
        mid = (start_pg + end_pg) // 2
        pages.extend([mid, end_pg - 2])
        pages = sorted(set(p for p in pages if p < doc.page_count))

        print(f"  [{ch_name}] OCR {len(pages)} pages...")
        text = ocr_pages(reader, doc, pages, sid)
        cache_file.write_text(text, encoding="utf-8")
        all_chapter_text[ch_name] = text

    # === Step 3: Load seed data & build enrichment map ===
    print("\n=== Step 3: Map text to knowledge points ===")
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    enrichment_data = []
    for chapter in seed["chapters"]:
        ch_name = chapter["name"]
        ch_text = all_chapter_text.get(ch_name, "")
        kps = chapter["knowledge_points"]
        print(f"  {ch_name}: {len(kps)} KPs, {len(ch_text)} chars OCR")

        for kp in kps:
            title = kp["title"]
            # Find relevant section
            relevant = ""
            if title in ch_text:
                idx = ch_text.index(title)
                relevant = ch_text[max(0, idx - 100):idx + 800]
            enrichment_data.append({
                "chapter": ch_name,
                "title": title,
                "context": relevant or ch_text[:600],
                "current_summary": kp.get("summary", ""),
                "current_key_content": kp.get("key_content", ""),
                "current_mistakes": kp.get("common_mistakes", []),
                "current_case": kp.get("case_materials", ""),
            })

    # Save
    enrichment_path = OUTPUT_DIR / "enrichment_input.json"
    enrichment_path.write_text(
        json.dumps(enrichment_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n  Saved: {enrichment_path}")
    print(f"  {len(enrichment_data)} knowledge points to enrich")

    # === Summary ===
    print("\n" + "=" * 60)
    print("Extraction complete!")
    print(f"  TOC: {len(toc_text)} chars")
    for ch_name, text in all_chapter_text.items():
        print(f"  {ch_name}: {len(text)} chars")
    print(f"  Ready for LLM enrichment: {enrichment_path}")
    print("=" * 60)

    doc.close()


if __name__ == "__main__":
    main()
