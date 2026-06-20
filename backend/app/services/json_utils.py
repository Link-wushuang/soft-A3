import json
import re


def extract_json(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:]
        stripped = stripped.strip()

    obj_start = stripped.find("{")
    obj_end = stripped.rfind("}")
    arr_start = stripped.find("[")
    arr_end = stripped.rfind("]")

    candidates: list[tuple[int, int]] = []
    if obj_start >= 0 and obj_end > obj_start:
        candidates.append((obj_start, obj_end))
    if arr_start >= 0 and arr_end > arr_start:
        candidates.append((arr_start, arr_end))

    if not candidates:
        return stripped

    start, end = min(candidates, key=lambda c: c[0])
    return stripped[start : end + 1]


def safe_parse_json(content: str, fallback=None):
    text = extract_json(content)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    cleaned = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    if fallback is not None:
        return fallback
    raise ValueError(f"Failed to parse JSON from LLM response: {content[:200]}")


def coerce_types(data, type_hints: dict):
    if not isinstance(data, dict):
        return data
    for key, expected in type_hints.items():
        if key not in data:
            continue
        val = data[key]
        if expected is bool and isinstance(val, str):
            data[key] = val.lower() in ("true", "yes", "1")
        elif expected is float and isinstance(val, str):
            try:
                data[key] = float(val)
            except ValueError:
                pass
        elif expected is list and isinstance(val, str):
            data[key] = [s.strip() for s in val.split(",") if s.strip()]
    return data
