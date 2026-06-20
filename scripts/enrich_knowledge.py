"""Enrich knowledge base using OCR'd textbook text + LLM.

For each knowledge point in os_course_seed.json:
1. Read OCR context from textbook_ocr/
2. Send to LLM with structured prompt
3. Parse response into summary, key_content, common_mistakes, case_materials
4. Update the seed JSON file
"""
import json
import sys
from pathlib import Path

import os

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

# Must change to backend dir so pydantic-settings finds .env
os.chdir(str(BACKEND))

from app.services.llm_client import get_llm_client

SEED_PATH = ROOT / "data" / "os_course_seed.json"
ENRICH_PATH = ROOT / "data" / "textbook_ocr" / "enrichment_input.json"
OUTPUT_PATH = ROOT / "data" / "os_course_seed_enriched.json"

ENRICH_PROMPT = """你是一位操作系统课程的教学设计专家。请根据提供的教材OCR文本，为下面的知识点编写结构化的教学内容。

知识点标题：{title}
所属章节：{chapter}
教材参考文本（OCR识别，可能有文字错误，请结合你的专业知识理解）：
{context}

当前已有内容（很简略，需要扩充）：
- 当前摘要：{current_summary}
- 当前核心内容：{current_key_content}

请输出以下格式的JSON（不要输出其他内容，只输出JSON）：

{{
  "summary": "一段100-200字的知识点摘要，清晰说明该知识点的核心内容和在操作系统中的位置",
  "key_content": "详细的要点说明（200-500字），从概念、原理、实现、应用四个层面展开。如果教材OCR文本有相关内容，请优先引用",
  "common_mistakes": ["常见误区1", "常见误区2", "常见误区3"],
  "case_materials": "一个100-200字的实践案例或操作场景描述，让学生能动手验证该知识点",
  "example_question": "一道与该知识点相关的思考题或简答题",
  "example_answer": "上述思考题的参考答案"
}}

注意：common_mistakes 必须是3个具体的、教学实践中常见的错误理解。"""


def enrich_kp(llm, kp_data: dict) -> dict:
    """Enrich a single knowledge point using LLM."""
    prompt = ENRICH_PROMPT.format(
        title=kp_data["title"],
        chapter=kp_data["chapter"],
        context=kp_data["context"][:1500],
        current_summary=kp_data["current_summary"],
        current_key_content=kp_data["current_key_content"],
    )

    try:
        response = llm.chat([{"role": "user", "content": prompt}])
        # Extract JSON from response
        text = response if isinstance(response, str) else response.get("content", "")
        # Find JSON block
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(text[start:end])
            # Add difficulty (from original or default)
            result["difficulty"] = kp_data.get("difficulty", "medium")
            result["tags"] = kp_data.get("tags", [])
            return result
        else:
            print(f"    WARNING: No JSON found in LLM response, using defaults")
            return None
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def main():
    print("Loading enrichment data...")
    enrichment = json.loads(ENRICH_PATH.read_text(encoding="utf-8"))

    print("Loading seed data...")
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    print("Initializing LLM client...")
    llm = get_llm_client()
    print(f"  Provider: {type(llm).__name__}")

    # Build a map from chapter+title to KP index
    kp_index = {}
    for ch_idx, chapter in enumerate(seed["chapters"]):
        for kp_idx, kp in enumerate(chapter["knowledge_points"]):
            key = f"{chapter['name']}|{kp['title']}"
            kp_index[key] = (ch_idx, kp_idx)

    total = len(enrichment)
    enriched_count = 0

    for i, item in enumerate(enrichment):
        key = f"{item['chapter']}|{item['title']}"
        if key not in kp_index:
            print(f"  [{i+1}/{total}] SKIP: {item['title']} (not found in seed)")
            continue

        ch_idx, kp_idx = kp_index[key]
        print(f"  [{i+1}/{total}] {item['title'][:30]}...", end=" ", flush=True)

        result = enrich_kp(llm, item)
        if result:
            # Update seed data
            kp = seed["chapters"][ch_idx]["knowledge_points"][kp_idx]
            kp["summary"] = result.get("summary", kp.get("summary", ""))
            kp["key_content"] = result.get("key_content", kp.get("key_content", ""))
            kp["common_mistakes"] = result.get("common_mistakes", kp.get("common_mistakes", []))
            kp["case_materials"] = result.get("case_materials", kp.get("case_materials", ""))
            kp["example_question"] = result.get("example_question", kp.get("example_question", ""))
            kp["example_answer"] = result.get("example_answer", kp.get("example_answer", ""))
            enriched_count += 1
            print("OK")
        else:
            print("FAILED (kept original)")

    # Save enriched seed
    OUTPUT_PATH.write_text(
        json.dumps(seed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n=== Done ===")
    print(f"  Enriched: {enriched_count}/{total} knowledge points")
    print(f"  Output: {OUTPUT_PATH}")
    print(f"  To apply: copy {OUTPUT_PATH} -> {SEED_PATH}")
    print(f"  Then restart backend to re-initialize data")


if __name__ == "__main__":
    main()
