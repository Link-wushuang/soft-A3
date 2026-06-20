import json
import re
from collections.abc import Iterator

from app.services.llm_client import LLMClient


def _extract_topic(messages: list[dict[str, str]]) -> str:
    user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
    title_match = re.search(r'"title"\s*:\s*"([^"]+)"', user_text)
    if title_match:
        return title_match.group(1)
    for keyword in ["知识点", "关于", "讲解"]:
        idx = user_text.find(keyword)
        if idx >= 0:
            snippet = user_text[idx : idx + 20].strip()
            return snippet
    return user_text[:30] if user_text else "操作系统基础"


def _extract_level(messages: list[dict[str, str]]) -> str:
    user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
    if "beginner" in user_text or "初学" in user_text:
        return "beginner"
    if "advanced" in user_text or "高级" in user_text or "深入" in user_text:
        return "advanced"
    return "medium"


class MockLLM(LLMClient):
    def chat(self, messages: list[dict[str, str]]) -> str:
        user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
        topic = _extract_topic(messages)
        if "思维导图" in user_text or "Mermaid" in user_text or "mindmap" in user_text.lower():
            return (
                "graph TD\n"
                f"    A[{topic[:8]}] --> B[核心概念]\n"
                f"    A --> C[关键特性]\n"
                "    B --> D[定义与原理]\n"
                "    B --> E[实现方式]\n"
                "    C --> F[优缺点]\n"
                "    A --> G[常见误区]"
            )
        return (
            f"# {topic} — 个性化讲解\n\n"
            f"## 概述\n\n本节围绕**{topic}**展开，结合你的学习画像进行讲解。\n\n"
            f"## 核心内容\n\n{topic}是操作系统中的重要概念。"
            "以下从原理、实现和应用三个层面展开。\n\n"
            "### 原理\n\n基本工作原理及其在系统中的作用。\n\n"
            "### 实现\n\n常见的实现方式与算法。\n\n"
            f"## 示例\n\n以{topic}为例，演示典型操作流程。\n\n"
            "## 总结\n\n关键要点回顾与易错点提示。"
        )

    def chat_json(self, messages: list[dict[str, str]], schema_hint: str = "") -> dict:
        topic = _extract_topic(messages)
        level = _extract_level(messages)

        if schema_hint == "profile":
            user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
            weak = []
            for kw in ["不太会", "薄弱", "不懂", "困难", "搞不清"]:
                idx = user_text.find(kw)
                if idx >= 0:
                    weak.append(user_text[max(0, idx - 10) : idx + 10].strip())
            if not weak:
                weak = [topic]
            return {
                "base_level": level,
                "learning_goal": f"掌握{topic}核心知识",
                "knowledge_state": f"正在学习{topic}相关内容",
                "weak_points": weak[:3],
                "mastered_points": ["操作系统基础概念"],
                "learning_preference": ["图解", "例题", "代码实操"],
                "cognitive_style": "visual",
                "time_budget": "每天1-2小时",
                "confidence": "medium",
                "evidence": f"用户提到了{topic}相关学习需求",
                "profile_change_reason": "从对话中抽取学习目标与薄弱点",
            }
        if schema_hint == "path":
            user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
            kp_titles = []
            marker = user_text.find("可用知识点")
            if marker >= 0:
                after = user_text[marker:]
                arr_start = after.find("[")
                if arr_start >= 0:
                    arr_end = after.find("]", arr_start)
                    if arr_end >= 0:
                        try:
                            kp_titles = json.loads(after[arr_start : arr_end + 1])
                        except (json.JSONDecodeError, ValueError):
                            pass
            picked = kp_titles[:5] if len(kp_titles) >= 5 else kp_titles[:3] if kp_titles else [topic]
            return {
                "nodes": [
                    {"knowledge_point_title": t, "reason": f"学习{t}以巩固相关知识"}
                    for t in picked
                ],
            }
        if schema_hint == "evaluation":
            return {"score": 1.0, "is_correct": True, "feedback": "回答正确", "mistake_tags": []}
        if schema_hint == "exercise":
            return [
                {
                    "question_type": "choice",
                    "question": f"关于{topic}，以下哪个说法是正确的？",
                    "options": [f"A. {topic}的核心特征是高效性", f"B. {topic}不涉及资源管理",
                                f"C. {topic}只在用户态运行", f"D. {topic}不需要硬件支持"],
                    "answer": "A",
                    "explanation": f"{topic}的设计目标之一就是高效地管理系统资源。",
                    "difficulty": "easy" if level == "beginner" else "medium",
                    "tags": [topic],
                },
                {
                    "question_type": "short_answer",
                    "question": f"简述{topic}的基本工作原理。",
                    "options": None,
                    "answer": f"{topic}通过特定的数据结构和算法来实现其核心功能，兼顾效率与安全性。",
                    "explanation": f"理解{topic}的原理是掌握操作系统该部分内容的基础。",
                    "difficulty": "medium",
                    "tags": [topic, "原理"],
                },
                {
                    "question_type": "fill_blank",
                    "question": f"在{topic}中，系统通过____机制来保证数据的一致性。",
                    "options": None,
                    "answer": "同步",
                    "explanation": f"{topic}中同步机制是保证正确性的关键。",
                    "difficulty": "medium",
                    "tags": [topic],
                },
            ]
        if schema_hint == "case":
            return {
                "title": f"{topic}模拟实现",
                "description": f"编写程序模拟{topic}的核心操作流程，观察其行为特征。",
                "code": (
                    f"# {topic} 模拟示例\n"
                    "class Simulator:\n"
                    "    def __init__(self):\n"
                    "        self.state = {}\n\n"
                    "    def run(self, task):\n"
                    "        print(f'Processing: {task}')\n"
                    "        self.state[task] = 'done'\n"
                    "        return self.state\n\n"
                    "sim = Simulator()\n"
                    "result = sim.run('demo_task')\n"
                    "print(result)"
                ),
                "expected_output": "{'demo_task': 'done'}",
            }
        if schema_hint == "extended_reading":
            return [
                {
                    "title": f"{topic}深入解析",
                    "summary": f"深入探讨{topic}的设计原理、常见实现方案及其在现代操作系统中的演进。",
                    "source": "操作系统概念(第九版)",
                    "relevance": f"有助于从更深层次理解{topic}的设计哲学。",
                },
                {
                    "title": f"{topic}在Linux中的实现",
                    "summary": f"分析Linux内核中{topic}的具体实现细节和优化策略。",
                    "source": "Linux内核设计与实现",
                    "relevance": f"将{topic}的理论知识与实际内核实现对应，加深理解。",
                },
            ]
        if schema_hint == "video_storyboard":
            return {
                "title": f"{topic}原理动画讲解",
                "scenes": [
                    {
                        "scene_id": 1,
                        "duration_sec": 30,
                        "visual": f"{topic}的基本概念图示",
                        "narration": f"首先我们来了解{topic}的基本概念和它在操作系统中的角色。",
                        "animation": "概念元素依次浮现，建立整体框架",
                    },
                    {
                        "scene_id": 2,
                        "duration_sec": 40,
                        "visual": f"{topic}的工作流程示意图",
                        "narration": f"{topic}的核心工作流程可以分为几个关键步骤。",
                        "animation": "流程图逐步展开，箭头指示数据流向",
                    },
                    {
                        "scene_id": 3,
                        "duration_sec": 35,
                        "visual": "对比分析图表",
                        "narration": f"总结{topic}的优势与局限，以及与相关方案的对比。",
                        "animation": "对比表格逐行显示，配合高亮标注",
                    },
                ],
                "ppt_outline": [
                    f"Slide 1: {topic}概述",
                    f"Slide 2: {topic}核心原理",
                    f"Slide 3: {topic}实现方式",
                    f"Slide 4: {topic}优缺点对比",
                    "Slide 5: 总结与思考题",
                ],
            }
        if schema_hint == "verifier":
            return {"consistent": True, "issues": [], "confidence": "high"}
        if schema_hint == "reflection":
            return {
                "profile_changes": {
                    "weak_points": {"added": [topic], "removed": []},
                    "mastered_points": {"added": [], "removed": []},
                },
                "change_reason": f"答错了{topic}相关题目，需要加强",
                "remediation": {"type": "resource", "knowledge_point_title": topic},
            }
        if schema_hint == "content_guard":
            return {"safe": True, "issues": [], "blocked": False}
        return {"content": self.chat(messages)}

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        text = self.chat(messages)
        for index in range(0, len(text), 24):
            yield text[index : index + 24]


def dumps_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)
