import json
from collections.abc import Iterator

from app.services.llm_client import LLMClient


class MockLLM(LLMClient):
    def chat(self, messages: list[dict[str, str]]) -> str:
        user_text = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
        if "思维导图" in user_text or "Mermaid" in user_text or "mindmap" in user_text.lower():
            return (
                "graph TD\n"
                "    A[知识点] --> B[核心概念1]\n"
                "    A --> C[核心概念2]\n"
                "    B --> D[子概念]\n"
                "    B --> E[关键要素]\n"
                "    C --> F[应用场景]\n"
                "    A --> G[常见误区]"
            )
        return f"# 个性化讲解\n\n## 概述\n\n这是基于课程知识库为你生成的个性化讲解文档。\n\n{user_text[:80]}\n\n## 核心内容\n\n根据你的学习画像，以下是对该知识点的详细讲解。\n\n## 示例\n\n这里包含一个具体例子帮助你理解。\n\n## 总结\n\n关键要点回顾。"

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
            return {
                "nodes": [
                    {"knowledge_point_title": "文件系统基础", "reason": "巩固文件系统基础概念，为后续内容做铺垫"},
                    {"knowledge_point_title": "连续分配", "reason": "薄弱点：外部碎片理解需要加强"},
                    {"knowledge_point_title": "链接分配", "reason": "薄弱点：指针更新和遍历访问需要练习"},
                    {"knowledge_point_title": "索引分配", "reason": "薄弱点：多级索引I/O计算需要巩固"},
                    {"knowledge_point_title": "文件分配方式对比", "reason": "综合对比加深对三种分配方式的理解"},
                ],
            }
        if schema_hint == "evaluation":
            return {"score": 1.0, "is_correct": True, "feedback": "回答正确", "mistake_tags": []}
        if schema_hint == "exercise":
            return [
                {
                    "question_type": "choice",
                    "question": "在隐式链接分配中，读取文件第5个逻辑块需要几次磁盘I/O？",
                    "options": ["A. 1次", "B. 5次", "C. 6次", "D. 2次"],
                    "answer": "B",
                    "explanation": "隐式链接需要从头遍历到第n块，每次读一个块，共n次。",
                    "difficulty": "medium",
                    "tags": ["链接分配", "磁盘I/O"],
                },
                {
                    "question_type": "fill_blank",
                    "question": "索引分配中，访问一个文件块需要先读取____块获取数据块地址。",
                    "options": None,
                    "answer": "索引",
                    "explanation": "索引分配通过索引块保存所有数据块地址。",
                    "difficulty": "easy",
                    "tags": ["索引分配"],
                },
                {
                    "question_type": "short_answer",
                    "question": "简述链接分配与索引分配的主要区别。",
                    "options": None,
                    "answer": "链接分配将指针分散在各数据块中，只能顺序访问；索引分配将指针集中在索引块中，支持随机访问。",
                    "explanation": "两种分配方式的核心区别在于指针的存储位置和访问方式。",
                    "difficulty": "medium",
                    "tags": ["链接分配", "索引分配", "对比"],
                },
            ]
        if schema_hint == "case":
            return {
                "title": "模拟索引分配文件读取",
                "description": "编写程序模拟单级索引分配的磁盘I/O过程，给定索引块和逻辑块号，计算物理块号并统计I/O次数。",
                "code": (
                    "class IndexedFile:\n"
                    "    def __init__(self, index_block, data_blocks):\n"
                    "        self.index_block = index_block  # list of physical block numbers\n"
                    "        self.data_blocks = data_blocks  # dict: phys_block_num -> data\n\n"
                    "    def read_block(self, logical_block_num):\n"
                    "        io_count = 1  # read index block\n"
                    "        if logical_block_num >= len(self.index_block):\n"
                    "            raise IndexError('Block out of range')\n"
                    "        phys_block = self.index_block[logical_block_num]\n"
                    "        io_count += 1  # read data block\n"
                    "        data = self.data_blocks.get(phys_block, '')\n"
                    "        return data, io_count\n\n"
                    "# Example usage:\n"
                    "f = IndexedFile(\n"
                    "    index_block=[10, 25, 7, 42, 15],\n"
                    "    data_blocks={10: 'block0', 25: 'block1', 7: 'block2', 42: 'block3', 15: 'block4'}\n"
                    ")\n"
                    "data, io = f.read_block(3)\n"
                    "print(f'Data: {data}, I/O count: {io}')  # Data: block3, I/O count: 2"
                ),
                "expected_output": "Data: block3, I/O count: 2",
            }
        if schema_hint == "extended_reading":
            return [
                {
                    "title": "FAT文件系统详解",
                    "summary": "FAT使用文件分配表实现显式链接，将指针集中存储在内存中的FAT表里，解决了隐式链接的顺序访问效率问题。",
                    "source": "操作系统概念(第九版) 11.4节",
                    "relevance": "理解显式链接如何解决隐式链接的顺序访问问题，与当前知识点紧密相关。",
                },
                {
                    "title": "Unix inode与多级索引分配",
                    "summary": "Unix采用多级索引分配方案，通过直接块、一级间接块、二级间接块支持不同大小的文件。",
                    "source": "操作系统概念(第九版) 11.5节",
                    "relevance": "对比链接分配与索引分配的设计思想差异，加深对文件分配方式的理解。",
                },
            ]
        if schema_hint == "video_storyboard":
            return {
                "title": "文件分配方式原理动画讲解",
                "scenes": [
                    {
                        "scene_id": 1,
                        "duration_sec": 30,
                        "visual": "磁盘俯视图，高亮显示空闲块和已分配块",
                        "narration": "在文件系统中，文件的数据块可以分散存储在磁盘的各个位置。不同的分配方式决定了如何追踪这些块的位置。",
                        "animation": "散落的块依次亮起，展示文件数据块的分布",
                    },
                    {
                        "scene_id": 2,
                        "duration_sec": 45,
                        "visual": "连续分配、链接分配、索引分配三栏对比图",
                        "narration": "连续分配将文件块连续存储；链接分配通过链表连接块；索引分配通过索引块集中管理块地址。",
                        "animation": "三栏分别展示三种分配方式的块组织动画",
                    },
                    {
                        "scene_id": 3,
                        "duration_sec": 30,
                        "visual": "链接分配特写：块与块之间的指针箭头",
                        "narration": "链接分配中每个数据块末尾保存下一个块的地址，形成链表结构。读取第n块需要从头遍历n次。",
                        "animation": "箭头从块A指向块B，再从块B指向块C，高亮遍历路径",
                    },
                    {
                        "scene_id": 4,
                        "duration_sec": 35,
                        "visual": "优缺点对比表格",
                        "narration": "总结：连续分配简单但有外部碎片；链接分配无碎片但只能顺序访问；索引分配支持随机访问但索引块占用空间。",
                        "animation": "表格逐行显示，配合图标动画",
                    },
                ],
                "ppt_outline": [
                    "Slide 1: 文件分配方式概述",
                    "Slide 2: 连续分配原理与优缺点",
                    "Slide 3: 链接分配(隐式/显式)详解",
                    "Slide 4: 索引分配与多级索引",
                    "Slide 5: 三种方式对比总结",
                    "Slide 6: 课后思考题",
                ],
            }
        if schema_hint == "verifier":
            return {"consistent": True, "issues": [], "confidence": "high"}
        if schema_hint == "reflection":
            return {
                "profile_changes": {
                    "weak_points": {"added": ["链接分配I/O计算"], "removed": []},
                    "mastered_points": {"added": [], "removed": []},
                },
                "change_reason": "答错了链接分配I/O计算相关题目，说明该知识点仍需加强",
                "remediation": {
                    "type": "resource",
                    "knowledge_point_title": "链接分配",
                },
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
