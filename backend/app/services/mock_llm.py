import json
import re
from collections.abc import Iterator

from app.services.llm_client import LLMClient


def _mock_storyboard(topic: str) -> dict:
    t = topic[:12]
    svg1 = (
        "<svg viewBox='0 0 800 450' xmlns='http://www.w3.org/2000/svg'>"
        "<style>"
        ".bg{fill:#0f172a} .box{fill:#1e3a5f;stroke:#38bdf8;stroke-width:2;rx:12} "
        ".cbox{fill:#312e81;stroke:#818cf8;stroke-width:2;rx:12} "
        ".t{fill:#f1f5f9;font-family:sans-serif;font-size:18px;text-anchor:middle} "
        ".ts{fill:#94a3b8;font-family:sans-serif;font-size:13px;text-anchor:middle} "
        ".title{fill:#e0e7ff;font-family:sans-serif;font-size:24px;font-weight:bold;text-anchor:middle} "
        ".ln{stroke:#38bdf8;stroke-width:2;marker-end:url(#ah)} "
        "@keyframes fi{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}} "
        ".a1{animation:fi .6s ease both} .a2{animation:fi .6s ease .3s both} "
        ".a3{animation:fi .6s ease .6s both} .a4{animation:fi .6s ease .9s both} "
        ".a5{animation:fi .6s ease 1.2s both}"
        "</style>"
        "<rect width='800' height='450' class='bg'/>"
        "<defs><marker id='ah' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='6' markerHeight='6' orient='auto'>"
        "<path d='M0,0 L10,5 L0,10 Z' fill='#38bdf8'/></marker></defs>"
        f"<text x='400' y='52' class='title a1'>{t}</text>"
        "<line x1='300' y1='66' x2='500' y2='66' stroke='#818cf8' stroke-width='2' class='a1'/>"
        "<rect x='60' y='120' width='200' height='80' class='box a2'/>"
        f"<text x='160' y='155' class='t a2'>核心概念</text>"
        f"<text x='160' y='178' class='ts a2'>{t}的定义与原理</text>"
        "<rect x='300' y='120' width='200' height='80' class='cbox a3'/>"
        f"<text x='400' y='155' class='t a3'>关键特性</text>"
        f"<text x='400' y='178' class='ts a3'>功能与作用</text>"
        "<rect x='540' y='120' width='200' height='80' class='box a4'/>"
        f"<text x='640' y='155' class='t a4'>实现方式</text>"
        f"<text x='640' y='178' class='ts a4'>算法与数据结构</text>"
        "<line x1='260' y1='160' x2='300' y2='160' class='ln a3'/>"
        "<line x1='500' y1='160' x2='540' y2='160' class='ln a4'/>"
        "<rect x='200' y='280' width='180' height='70' class='cbox a4'/>"
        f"<text x='290' y='310' class='t a4'>优势</text>"
        f"<text x='290' y='333' class='ts a4'>性能·可靠性</text>"
        "<rect x='420' y='280' width='180' height='70' class='box a5'/>"
        f"<text x='510' y='310' class='t a5'>局限</text>"
        f"<text x='510' y='333' class='ts a5'>开销·复杂度</text>"
        "<line x1='400' y1='200' x2='290' y2='280' class='ln a4'/>"
        "<line x1='400' y1='200' x2='510' y2='280' class='ln a5'/>"
        "<circle cx='400' cy='400' r='4' fill='#818cf8' class='a5'/>"
        "<text x='400' y='430' class='ts a5'>场景 1 / 概念总览</text>"
        "</svg>"
    )
    svg2 = (
        "<svg viewBox='0 0 800 450' xmlns='http://www.w3.org/2000/svg'>"
        "<style>"
        ".bg{fill:#0f172a} "
        ".nd{fill:#1e3a5f;stroke:#38bdf8;stroke-width:2;rx:10} "
        ".hl{fill:#312e81;stroke:#a78bfa;stroke-width:2.5;rx:10} "
        ".t{fill:#f1f5f9;font-family:sans-serif;font-size:16px;text-anchor:middle} "
        ".ts{fill:#94a3b8;font-family:sans-serif;font-size:12px;text-anchor:middle} "
        ".title{fill:#e0e7ff;font-family:sans-serif;font-size:22px;font-weight:bold;text-anchor:middle} "
        ".ar{stroke:#38bdf8;stroke-width:2;marker-end:url(#ah2)} "
        ".ar2{stroke:#a78bfa;stroke-width:2;stroke-dasharray:6 3;marker-end:url(#ah3)} "
        "@keyframes si{from{opacity:0;transform:scale(.85)}to{opacity:1;transform:scale(1)}} "
        "@keyframes dr{from{stroke-dashoffset:200}to{stroke-dashoffset:0}} "
        ".s1{animation:si .5s ease both} .s2{animation:si .5s ease .25s both} "
        ".s3{animation:si .5s ease .5s both} .s4{animation:si .5s ease .75s both} "
        ".s5{animation:si .5s ease 1s both} "
        ".dl{stroke-dasharray:200;animation:dr 1s ease .6s both}"
        "</style>"
        "<rect width='800' height='450' class='bg'/>"
        "<defs><marker id='ah2' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='6' markerHeight='6' orient='auto'>"
        "<path d='M0,0 L10,5 L0,10 Z' fill='#38bdf8'/></marker>"
        "<marker id='ah3' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='6' markerHeight='6' orient='auto'>"
        "<path d='M0,0 L10,5 L0,10 Z' fill='#a78bfa'/></marker></defs>"
        f"<text x='400' y='45' class='title s1'>工作流程</text>"
        "<rect x='80' y='90' width='160' height='56' class='nd s1'/>"
        "<text x='160' y='123' class='t s1'>步骤 1：输入</text>"
        "<line x1='240' y1='118' x2='300' y2='118' class='ar dl'/>"
        "<rect x='300' y='90' width='200' height='56' class='hl s2'/>"
        f"<text x='400' y='123' class='t s2'>{t}处理</text>"
        "<line x1='500' y1='118' x2='560' y2='118' class='ar dl'/>"
        "<rect x='560' y='90' width='160' height='56' class='nd s3'/>"
        "<text x='640' y='123' class='t s3'>步骤 3：输出</text>"
        "<rect x='220' y='200' width='160' height='56' class='nd s3'/>"
        "<text x='300' y='233' class='t s3'>调度决策</text>"
        "<rect x='420' y='200' width='160' height='56' class='nd s4'/>"
        "<text x='500' y='233' class='t s4'>资源分配</text>"
        "<line x1='400' y1='146' x2='300' y2='200' class='ar2 dl'/>"
        "<line x1='400' y1='146' x2='500' y2='200' class='ar2 dl'/>"
        "<rect x='250' y='310' width='300' height='70' class='hl s5'/>"
        f"<text x='400' y='340' class='t s5'>结果验证与反馈</text>"
        f"<text x='400' y='362' class='ts s5'>确保{t}执行正确</text>"
        "<line x1='300' y1='256' x2='350' y2='310' class='ar dl'/>"
        "<line x1='500' y1='256' x2='450' y2='310' class='ar dl'/>"
        "<text x='400' y='430' class='ts s5'>场景 2 / 流程图</text>"
        "</svg>"
    )
    svg3 = (
        "<svg viewBox='0 0 800 450' xmlns='http://www.w3.org/2000/svg'>"
        "<style>"
        ".bg{fill:#0f172a} "
        ".t{fill:#f1f5f9;font-family:sans-serif;font-size:15px;text-anchor:middle} "
        ".th{fill:#e0e7ff;font-family:sans-serif;font-size:16px;font-weight:bold;text-anchor:middle} "
        ".ts{fill:#94a3b8;font-family:sans-serif;font-size:12px;text-anchor:middle} "
        ".title{fill:#e0e7ff;font-family:sans-serif;font-size:22px;font-weight:bold;text-anchor:middle} "
        ".r1{fill:#1e3a5f} .r2{fill:#172554} "
        ".hdr{fill:#312e81} .good{fill:#065f46} .warn{fill:#713f12} "
        "@keyframes ri{from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:translateX(0)}} "
        ".w1{animation:ri .4s ease both} .w2{animation:ri .4s ease .15s both} "
        ".w3{animation:ri .4s ease .3s both} .w4{animation:ri .4s ease .45s both} "
        ".w5{animation:ri .4s ease .6s both} .w6{animation:ri .4s ease .75s both}"
        "</style>"
        "<rect width='800' height='450' class='bg'/>"
        f"<text x='400' y='45' class='title w1'>对比分析</text>"
        "<rect x='100' y='80' width='250' height='36' class='hdr w1'/>"
        "<text x='225' y='103' class='th w1'>维度</text>"
        "<rect x='350' y='80' width='200' height='36' class='hdr w1'/>"
        f"<text x='450' y='103' class='th w1'>{t[:6]}</text>"
        "<rect x='550' y='80' width='200' height='36' class='hdr w1'/>"
        "<text x='650' y='103' class='th w1'>替代方案</text>"
        "<rect x='100' y='120' width='250' height='36' class='r1 w2'/>"
        "<text x='225' y='143' class='t w2'>执行效率</text>"
        "<rect x='350' y='120' width='200' height='36' class='good w2'/>"
        "<text x='450' y='143' class='t w2'>★★★★★</text>"
        "<rect x='550' y='120' width='200' height='36' class='r1 w2'/>"
        "<text x='650' y='143' class='t w2'>★★★☆☆</text>"
        "<rect x='100' y='160' width='250' height='36' class='r2 w3'/>"
        "<text x='225' y='183' class='t w3'>实现复杂度</text>"
        "<rect x='350' y='160' width='200' height='36' class='warn w3'/>"
        "<text x='450' y='183' class='t w3'>★★★★☆</text>"
        "<rect x='550' y='160' width='200' height='36' class='r2 w3'/>"
        "<text x='650' y='183' class='t w3'>★★☆☆☆</text>"
        "<rect x='100' y='200' width='250' height='36' class='r1 w4'/>"
        "<text x='225' y='223' class='t w4'>内存开销</text>"
        "<rect x='350' y='200' width='200' height='36' class='r1 w4'/>"
        "<text x='450' y='223' class='t w4'>★★★☆☆</text>"
        "<rect x='550' y='200' width='200' height='36' class='good w4'/>"
        "<text x='650' y='223' class='t w4'>★★★★☆</text>"
        "<rect x='100' y='240' width='250' height='36' class='r2 w5'/>"
        "<text x='225' y='263' class='t w5'>安全性</text>"
        "<rect x='350' y='240' width='200' height='36' class='good w5'/>"
        "<text x='450' y='263' class='t w5'>★★★★★</text>"
        "<rect x='550' y='240' width='200' height='36' class='r2 w5'/>"
        "<text x='650' y='263' class='t w5'>★★★☆☆</text>"
        "<rect x='180' y='320' width='220' height='60' rx='12' fill='#065f46' stroke='#34d399' stroke-width='2' class='w5'/>"
        f"<text x='290' y='346' class='th w5'>✓ 推荐场景</text>"
        f"<text x='290' y='366' class='ts w5'>高安全高性能需求</text>"
        "<rect x='420' y='320' width='220' height='60' rx='12' fill='#713f12' stroke='#fbbf24' stroke-width='2' class='w6'/>"
        "<text x='530' y='346' class='th w6'>⚡ 替代场景</text>"
        "<text x='530' y='366' class='ts w6'>低开销简单实现</text>"
        "<text x='400' y='430' class='ts w6'>场景 3 / 对比分析</text>"
        "</svg>"
    )
    return {
        "title": f"{topic}原理动画讲解",
        "scenes": [
            {
                "scene_id": 1,
                "duration_sec": 30,
                "visual": svg1,
                "narration": f"首先我们来了解{topic}的基本概念和它在操作系统中的角色。"
                f"这个知识点涵盖了核心概念、关键特性和具体实现方式三个方面。",
                "animation": "概念框依次浮现，箭头连接展示关系",
            },
            {
                "scene_id": 2,
                "duration_sec": 40,
                "visual": svg2,
                "narration": f"{topic}的核心工作流程可以分为输入、处理、输出三个阶段，"
                "其中处理阶段涉及调度决策和资源分配两个关键子过程。",
                "animation": "流程节点依次缩放出现，连线自动绘制",
            },
            {
                "scene_id": 3,
                "duration_sec": 35,
                "visual": svg3,
                "narration": f"最后我们对比{topic}与替代方案在效率、复杂度、"
                "内存开销和安全性等维度的差异，帮助你选择合适的方案。",
                "animation": "表格逐行滑入，关键项高亮标注",
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
            return _mock_storyboard(topic)
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
