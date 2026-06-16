import json
from collections.abc import Iterator

from app.services.llm_client import LLMClient


class MockLLM(LLMClient):
    def chat(self, messages: list[dict[str, str]]) -> str:
        user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
        return f"这是基于课程知识库生成的个性化说明：{user_text[:80]}"

    def chat_json(self, messages: list[dict[str, str]], schema_hint: str = "") -> dict:
        if schema_hint == "profile":
            return {
                "base_level": "medium",
                "learning_goal": "两天内掌握文件系统核心知识",
                "knowledge_state": "了解基础概念，需要加强分配方式和磁盘 I/O 计算",
                "weak_points": ["索引分配", "链接分配", "磁盘I/O计算"],
                "mastered_points": ["文件与目录"],
                "learning_preference": ["图解", "例题", "代码实操"],
                "cognitive_style": "visual",
                "time_budget": "2天，每天1小时",
                "confidence": "medium",
                "evidence": "用户表达了明确目标和偏好的学习方式",
                "profile_change_reason": "从对话中抽取学习目标、薄弱点与偏好",
            }
        if schema_hint == "path":
            return {"nodes": [], "reason": "mock path"}
        if schema_hint == "evaluation":
            return {"score": 1.0, "is_correct": True, "feedback": "回答正确", "mistake_tags": []}
        return {"content": self.chat(messages)}

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        text = self.chat(messages)
        for index in range(0, len(text), 24):
            yield text[index : index + 24]


def dumps_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)

