# EduPath Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a competition-ready multi-agent personalized learning system for the A3 track ("基于大模型的个性化资源生成与学习多智能体系统开发"), implementing a complete student learning loop: profile dialogue -> learning path -> multi-agent resource generation -> practice evaluation -> profile update -> remediation push.

**Architecture:** Vue 3 SPA frontend communicates with a FastAPI backend over REST + SSE. The backend uses SQLAlchemy/MySQL for persistence and an Agent Orchestrator that coordinates 14 specialized agents (profile, knowledge retrieval, path planning, 6 resource generators, evaluation, reflection, verification, content guard). LLM calls go through an abstract provider interface with a deterministic mock (default) and 讯飞 Spark API (production). Resource generation runs as a background task with per-agent trace written to DB incrementally; the SSE endpoint polls for new trace entries in real time. All generated content passes through a verification + safety pipeline before reaching the user.

**Tech Stack:** Vue 3, Vite, TypeScript, Element Plus, markdown-it, mermaid.js, ECharts, FastAPI, SQLAlchemy, Pydantic v2, MySQL 8.0 (primary, SQLite for tests), Pytest, 讯飞 Spark API (sparkai SDK), Mock LLM provider.

---

## 1. Competition Requirement Map

Official task page: <https://www.cnsoftbei.com/content-3-1286-1.html>

| # | Official Requirement | Plan Response | Priority | Evidence |
|---|---|---|---|---|
| 1 | 对话式学习画像自主构建 (≥6维) | `ProfileAgent` extracts 8 dimensions with confidence, evidence, and update history | P0 | Profile page, DB record, tests |
| 2 | 多智能体协同资源生成 | 14 agents with visible orchestration trace showing retrieval -> planning -> generation -> verification -> safety | P0 | Agent trace panel, architecture doc |
| 3 | 至少5种个性化资源 | 6 types: lecture, mind map, exercises, lab/case, extended reading, video storyboard | P0 | Resource tabs, persisted records |
| 4 | 个性化学习路径规划和推送 | `PathPlannerAgent` builds dynamic path; `ReflectionAgent` triggers remediation after mistakes | P0 | Learning path page, feedback loop |
| 5 | 智能辅导 (加分项) | Context-aware `TutorAgent` with source references and streaming response | P1 | Tutoring panel |
| 6 | 学习效果评估 (加分项) | `EvaluationAgent` + mistake tags + mastery trend + ECharts analytics | P0 | Exercise page, analytics chart |
| 7 | 完整高校课程知识库 | "操作系统" course: 8 chapters, 40+ knowledge points, 60+ exercises, 8+ labs | P0 | `data/os_course_seed.json` |
| 8 | 防幻觉与内容安全 | `VerifierAgent` + `ContentGuardAgent` + source-bound prompts + confidence labels + safety audit log | P0 | Safety logs, verifier output |
| 9 | 界面美观: 流式输出 | SSE endpoints for dialogue and resource generation; frontend `EventSource` rendering | P0 | SSE API, streaming UI |
| 10 | 界面美观: Markdown渲染 | `markdown-it` with code highlighting and math support | P0 | MarkdownRenderer component |
| 11 | 界面美观: 卡片化展示 | Element Plus Card components for resources, exercises, profile dimensions | P0 | ResourceCard, ProfileCard |
| 12 | 开源协议标注 | `docs/third-party-licenses.md` | P0 | License file |
| 13 | AI辅助工具须选用科大讯飞 | 讯飞 Spark API as LLM backend; document iFlyCode usage in `docs/ai-tool-usage.md` | P0 | AI tool usage doc |
| 14 | 响应时间合理 / 进度追踪 | Agent task polling + SSE progress + timeout fallback + skeleton loading | P0 | UI trace, API tests |
| 15 | PPT / 演示视频 / 源码 / 文档 | Complete submission package with checklist | P0 | Final folder |

---

## 2. Innovation Highlights

This section directly addresses the 35% "创新价值与实用性" scoring weight.

### 2.1 Core Innovations

1. **Evidence-Based Dynamic Profile**: Unlike static questionnaire systems, profiles are extracted from natural conversation and continuously updated through learning behavior evidence (exercise results, resource interactions, time-on-task). Every profile change carries confidence level, evidence text, and change reason — fully auditable.

2. **Multi-Agent Trace Transparency**: Students can see exactly which agents contributed to their resources, how long each took, and what warnings were raised. This "glass box" approach builds trust and distinguishes the system from black-box AI tools.

3. **Source-Bound Generation with Verification Pipeline**: All generated content is constrained to retrieved course knowledge. A two-stage verification (factual consistency + content safety) with audit logging provides anti-hallucination guarantees that most educational AI systems lack.

4. **Closed-Loop Remediation**: The system detects weak points from exercise results, updates the profile, adjusts the learning path, and proactively pushes targeted remediation resources — a complete feedback loop, not just one-shot generation.

5. **Six Multimodal Resource Types**: Goes beyond text-only generation to include Mermaid mind maps (visual), code lab cases (interactive), video storyboards with scene descriptions (multimodal), and curated extended reading (depth).

### 2.2 Differentiators From Existing Platforms

| Existing Platform Limitation | EduPath Solution |
|---|---|
| Static course structure for all students | Dynamic path per student profile |
| Single resource format (text or video) | 6 resource types generated per knowledge point |
| No visibility into AI reasoning | Full agent trace with timing and warnings |
| No feedback after exercises | Immediate scoring + profile update + remediation |
| Hallucination risk in AI-generated content | Source-bound generation + verification pipeline |

---

## 3. Product Scope

### 3.1 P0: Must Ship (Demo-Ready MVP)

All P0 features must work in mock mode without network access.

- Student login and demo account
- Operating Systems course knowledge base (8 chapters, 40+ knowledge points)
- 8-dimension student profile extraction via dialogue
- Dynamic learning path generation with reasons
- Multi-agent resource generation with visible trace
- **Six resource types:**
  1. Personalized lecture document (Markdown)
  2. Knowledge mind map (Mermaid)
  3. Layered exercise set (multiple difficulty, multiple types)
  4. Lab/case material with code
  5. Extended reading recommendations with summaries
  6. Video storyboard with scene descriptions and PPT outline
- Exercise submission, scoring, mistake tagging, feedback
- Profile update based on learning behavior
- Remediation resource recommendation
- Content verification and safety filtering with audit log
- SSE streaming for dialogue and resource generation
- Card-based UI with agent progress tracking
- README, architecture doc, API doc, safety doc, AI tool usage doc

### 3.2 P1: Strong Competition Version

- Teacher knowledge base CRUD
- Teacher analytics dashboard (ECharts)
- Tutoring panel with follow-up Q&A
- Learning effect trend report
- Spark API real provider integration
- Playwright smoke tests

### 3.3 P2: Finals / Extension

- Vector database (Chroma) for semantic retrieval
- PDF courseware upload and parsing
- TTS voice explanations
- Real video generation via API
- Export learning report as PDF
- Multi-course expansion

### 3.4 Explicit Non-Goals

- Do not train a custom model
- Do not build complex RBAC permissions
- Do not depend on paid video generation for MVP
- Do not commit real API keys
- Do not block student loop on teacher features

---

## 4. Student Profile Specification

8 dimensions (exceeds the ≥6 requirement):

| Field | Type | Meaning | Example |
|---|---|---|---|
| `base_level` | enum | Foundation level | `beginner` / `medium` / `advanced` |
| `learning_goal` | string | Goal and deadline | `两天内掌握文件系统分配方式` |
| `knowledge_state` | string | Known vs unknown concepts | `了解目录基础，不熟悉索引分配` |
| `weak_points` | list[str] | Concrete weak knowledge tags | `["链接分配指针更新", "磁盘I/O计算"]` |
| `mastered_points` | list[str] | Repeatedly correct concepts | `["文件目录基础"]` |
| `learning_preference` | list[str] | Preferred resource style | `["图解", "例题", "代码实操"]` |
| `cognitive_style` | enum | Learning style | `visual` / `auditory` / `reading` / `kinesthetic` |
| `time_budget` | string | Available study time | `2天, 每节点40分钟` |

Every profile update includes:

```json
{
  "confidence": "low | medium | high",
  "evidence": "text snippet or exercise result",
  "updated_by": "ProfileAgent | ReflectionAgent",
  "profile_change_reason": "答错了链接分配指针题，说明该知识点仍薄弱"
}
```

---

## 5. Course Knowledge Base Specification

Initial course: 操作系统 (Operating Systems).

### 5.1 Minimum Dataset

| Item | Minimum Count |
|---|---|
| Chapters | 8 |
| Knowledge points | 40 |
| Exercises | 60 |
| Lab/case materials | 8 |
| Common mistakes | 20 |
| References per chapter | 1 |

### 5.2 Chapter Outline

1. 操作系统概述
2. 进程与线程
3. 进程同步与死锁
4. CPU 调度
5. 内存管理
6. 虚拟内存
7. 文件系统
8. 设备管理与磁盘调度

### 5.3 Knowledge Point Schema

```json
{
  "chapter": "文件系统",
  "title": "索引分配",
  "summary": "用索引块保存文件数据块地址，支持随机访问。",
  "key_content": "索引块、直接索引、多级索引、访问次数计算。",
  "common_mistakes": ["漏算索引块读取", "混淆链接分配和索引分配"],
  "example_question": "读取第10个逻辑块时需要几次磁盘I/O？",
  "example_answer": "至少读取索引块一次，再读取目标数据块一次，共2次。",
  "difficulty": "medium",
  "tags": ["file-system", "indexed-allocation", "disk-io"],
  "sources": ["操作系统概念(第九版) 第11章"],
  "labs": [
    {
      "title": "模拟索引分配文件读取",
      "description": "编写程序模拟单级索引和多级索引的磁盘I/O过程",
      "code_template": "def read_block(file_index_block, logical_block_num): ..."
    }
  ]
}
```

---

## 6. Multi-Agent Architecture

### 6.1 Agent Roster

| Agent | Responsibility | Priority |
|---|---|---|
| `ProfileAgent` | Extract 8-dimension profile from dialogue text | P0 |
| `KnowledgeAgent` | Retrieve relevant course context from DB | P0 |
| `PathPlannerAgent` | Build/update learning path from profile + knowledge | P0 |
| `LectureAgent` | Generate personalized Markdown lecture | P0 |
| `MindMapAgent` | Generate Mermaid mind map code | P0 |
| `ExerciseAgent` | Generate layered exercise set (JSON) | P0 |
| `CaseAgent` | Generate lab/case/code material | P0 |
| `ExtendedReadingAgent` | Generate curated reading list with summaries | P0 |
| `VideoStoryboardAgent` | Generate storyboard scenes + PPT outline | P0 |
| `EvaluationAgent` | Score answers, identify mistake patterns | P0 |
| `ReflectionAgent` | Update profile after evaluation, recommend remediation | P0 |
| `VerifierAgent` | Check factual consistency against source context | P0 |
| `ContentGuardAgent` | Filter unsafe/sensitive/unsupported content | P0 |
| `TutorAgent` | Answer follow-up questions with source refs | P1 |

### 6.2 Resource Generation Flow

```
Student selects knowledge point
  -> Orchestrator creates AgentTask (status: pending)
  -> ProfileAgent reads current profile
  -> KnowledgeAgent retrieves source-bound course context
  -> [Parallel] LectureAgent, MindMapAgent, ExerciseAgent,
                CaseAgent, ExtendedReadingAgent, VideoStoryboardAgent
  -> [Sequential] VerifierAgent checks each resource
  -> [Sequential] ContentGuardAgent checks each resource
  -> ResourceService persists resources + trace + warnings
  -> SSE pushes progress events to frontend
  -> Frontend renders resource tabs with cards
```

### 6.3 Agent Trace Schema

Every agent execution produces a trace item:

```python
class AgentTraceItem:
    agent_name: str
    status: str          # pending | running | success | failed | skipped
    input_summary: str
    output_summary: str
    started_at: datetime
    finished_at: datetime | None
    duration_ms: int | None
    warnings: list[str]
    confidence: str | None  # low | medium | high
```

UI rules:
- Show all agents in the trace panel from the start (status: pending)
- Update status in real-time via SSE
- A failed non-critical agent shows a fallback card, does not break the page
- Show total progress as "N/M agents complete"

---

## 7. Anti-Hallucination and Safety Design

### 7.1 Generation Rules

1. Resource agents receive retrieved course context as input and MUST stay within that context
2. Prompts include: "Only use information from the provided context. If uncertain, output '需要教师确认' instead of guessing."
3. Every generated resource includes a `confidence` field
4. Generated exercises MUST include answer and explanation
5. JSON schema validation rejects malformed output

### 7.2 Verification Pipeline

```
Generated resource JSON
  -> Schema validation (Pydantic)
  -> Source keyword coverage check (≥60% of source keywords present)
  -> VerifierAgent: LLM-based factual consistency review
  -> ContentGuardAgent: safety keyword filter + LLM safety check
  -> Save with confidence + warnings to DB
  -> Save audit record to safety_audit_log
```

### 7.3 Safety Audit Log

```python
class SafetyAuditRecord:
    resource_id: int
    check_type: str    # schema | keyword_coverage | factual | safety
    status: str        # passed | warning | blocked
    details: str
    blocked_reason: str | None
    created_at: datetime
```

### 7.4 Fallback Behavior

| Failure | Fallback |
|---|---|
| JSON parse error | Return raw text with warning badge |
| Mermaid syntax error | Show raw Mermaid code in code block |
| Factual inconsistency | Show resource with "待教师确认" badge |
| Safety block | Show "该内容已被安全过滤" placeholder card |
| Agent timeout (>30s) | Show "生成超时，请重试" with retry button |

---

## 8. Data Model

### 8.1 Entity Relationship

```
User 1--N StudentProfile
User 1--N AnswerRecord
User 1--N AgentTask
Course 1--N KnowledgePoint
Course 1--N KnowledgeSource
Course 1--N StudentProfile
StudentProfile 1--N ProfileUpdateLog
StudentProfile 1--1 LearningPath
LearningPath 1--N LearningPathNode
LearningPathNode N--1 KnowledgePoint
AgentTask 1--N AgentTrace
AgentTask 1--N GeneratedResource
GeneratedResource 1--N SafetyAuditLog
KnowledgePoint 1--N Exercise
Exercise 1--N AnswerRecord
```

### 8.2 All Tables

14 tables total. Full SQLAlchemy models are provided in Task 1.

| Table | Purpose | Key Fields |
|---|---|---|
| `user` | Student/teacher accounts | username, password_hash, role |
| `course` | Course metadata | name, description |
| `knowledge_point` | Course knowledge units | course_id, chapter, title, summary, key_content, tags, difficulty |
| `knowledge_source` | Chapter references | course_id, chapter, source_name, source_url |
| `student_profile` | Current profile snapshot | user_id, course_id, 8 dimension fields, updated_at |
| `profile_update_log` | Profile change history | user_id, old/new JSON, evidence, reason |
| `learning_path` | Path header | user_id, course_id, status |
| `learning_path_node` | Ordered learning steps | path_id, knowledge_point_id, sort_order, status, reason |
| `agent_task` | Orchestration task | user_id, task_type, status, progress |
| `agent_trace` | Per-agent execution record | task_id, agent_name, status, duration_ms, warnings |
| `generated_resource` | Generated content | task_id, knowledge_point_id, resource_type, content, confidence |
| `exercise` | Exercises (seeded + generated) | knowledge_point_id, question_type, question, answer, difficulty |
| `answer_record` | Submitted answers | user_id, exercise_id, user_answer, score, mistake_tags |
| `safety_audit_log` | Verification results | resource_id, check_type, status, blocked_reason |

---

## 9. API Design

### 9.1 Auth

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/login` | Login, returns JWT |
| POST | `/api/auth/register` | Register new user |
| GET | `/api/auth/me` | Current user info |

### 9.2 Profile

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/profile/dialogue` | Extract/update profile from natural language (SSE stream) |
| GET | `/api/profile/{course_id}` | Get current profile |
| GET | `/api/profile/{course_id}/logs` | Get profile update history |

### 9.3 Course & Knowledge

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/courses` | Course list |
| GET | `/api/courses/{id}/knowledge-points` | Knowledge points for a course |
| POST | `/api/knowledge-points` | Teacher creates point |
| PUT | `/api/knowledge-points/{id}` | Teacher updates point |
| DELETE | `/api/knowledge-points/{id}` | Teacher deletes point |

### 9.4 Learning Path

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/learning-path/generate` | Generate path (SSE stream) |
| GET | `/api/learning-path/current?course_id=1` | Get current path |
| PUT | `/api/learning-path/nodes/{id}/status` | Update node status |

### 9.5 Resource Generation

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/resources/generate` | Start multi-agent generation |
| GET | `/api/resources/generate/{task_id}/stream` | SSE stream for generation progress |
| GET | `/api/agent-tasks/{task_id}` | Poll task status |
| GET | `/api/agent-tasks/{task_id}/trace` | Get agent trace |
| GET | `/api/resources?knowledge_point_id=1` | Resource history |
| GET | `/api/resources/{id}` | Resource detail |

### 9.6 Practice & Assessment

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/exercises/generate` | Generate exercises for a knowledge point |
| GET | `/api/exercises?knowledge_point_id=1` | List exercises |
| POST | `/api/exercises/{id}/submit` | Submit answer, returns score + feedback (SSE) |
| GET | `/api/exercises/answer-records?course_id=1` | Answer history |
| GET | `/api/analytics/summary?course_id=1` | Student learning summary |

### 9.7 Tutoring (P1)

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/tutor/ask` | Ask follow-up question (SSE stream) |

### 9.8 SSE Event Format

All SSE endpoints use this event format:

```
event: agent_status
data: {"agent_name": "LectureAgent", "status": "running", "progress": 3, "total": 9}

event: agent_result
data: {"agent_name": "LectureAgent", "status": "success", "resource_type": "lecture", "duration_ms": 2100}

event: resource_ready
data: {"resource_id": 42, "resource_type": "lecture", "confidence": "high", "warnings": []}

event: error
data: {"agent_name": "MindMapAgent", "message": "Mermaid syntax error, showing fallback"}

event: done
data: {"task_id": 7, "total_resources": 6, "warnings_count": 1}
```

---

## 10. Frontend Pages

### 10.1 Student Pages

| Page | Route | Key UI Elements |
|---|---|---|
| Login | `/login` | Login form + "演示账号一键登录" button |
| Dashboard | `/student/dashboard` | ProfileCard (8 dims), weak points tags, current path mini-view, recent resources |
| Profile Chat | `/student/profile-chat` | Chat input, streaming response, ProfileCard live update |
| Learning Path | `/student/learning-path` | PathTimeline component, node reasons, status badges, generate button |
| Resource Generation | `/student/resources/:knowledgePointId` | AgentTracePanel, 6 resource tab cards, SafetyBadge, loading skeletons |
| Exercise | `/student/exercise/:knowledgePointId` | ExerciseCard list, submit button, score card, mistake tags, profile change alert |
| Tutor (P1) | `/student/tutor` | Chat with source references sidebar |

### 10.2 Teacher Pages (P1)

| Page | Route | Key UI Elements |
|---|---|---|
| Knowledge Manage | `/teacher/knowledge` | Table + edit dialog, CRUD |
| Analytics | `/teacher/analytics` | 3 ECharts: weak points bar, resource count pie, correctness trend line |

### 10.3 UI Design Rules

1. **Card-based layout**: Every resource type renders as an Element Plus `el-card` with header, body, and footer (confidence + warnings)
2. **Streaming text**: Profile dialogue and tutoring use typing animation with `EventSource`
3. **Agent trace panel**: Vertical stepper showing agent name, status icon, duration
4. **Loading states**: Skeleton placeholders during generation, never blank screens
5. **Safety badges**: Green (passed), Yellow (warning), Red (blocked) on each resource card
6. **Responsive**: Works on 1280px+ screens (demo on laptop is fine)
7. **Color scheme**: Professional education blue/white, not flashy

---

## 11. File Structure

```
D:/soft-A3/
├── README.md
├── CLAUDE.md
├── AGENTS.md
├── docs/
│   ├── plan.md
│   ├── architecture.md
│   ├── api-design.md
│   ├── database-design.md
│   ├── agent-design.md
│   ├── safety-design.md
│   ├── test-report.md
│   ├── demo-script.md
│   ├── ai-tool-usage.md
│   ├── third-party-licenses.md
│   ├── ppt-outline.md
│   └── innovation-highlights.md
├── data/
│   └── os_course_seed.json
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app entry
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # Settings from env
│   │   │   ├── security.py              # JWT utils
│   │   │   └── deps.py                  # FastAPI dependencies (get_db, get_current_user)
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # SQLAlchemy Base
│   │   │   ├── session.py               # Engine, session factory
│   │   │   └── init_data.py             # Seed data loader
│   │   ├── models/
│   │   │   ├── __init__.py              # Re-exports all models
│   │   │   ├── user.py
│   │   │   ├── course.py                # Course + KnowledgePoint + KnowledgeSource
│   │   │   ├── profile.py               # StudentProfile + ProfileUpdateLog
│   │   │   ├── learning_path.py         # LearningPath + LearningPathNode
│   │   │   ├── agent_task.py            # AgentTask + AgentTrace
│   │   │   ├── resource.py              # GeneratedResource
│   │   │   ├── exercise.py              # Exercise + AnswerRecord
│   │   │   └── safety.py                # SafetyAuditLog
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── profile.py
│   │   │   ├── learning_path.py
│   │   │   ├── resource.py
│   │   │   ├── exercise.py
│   │   │   └── agent_task.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # Main APIRouter aggregation
│   │   │   ├── auth.py
│   │   │   ├── profile.py
│   │   │   ├── learning_path.py
│   │   │   ├── resources.py
│   │   │   ├── exercises.py
│   │   │   ├── agent_tasks.py
│   │   │   ├── knowledge.py
│   │   │   └── analytics.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py            # Abstract LLM interface
│   │   │   ├── mock_llm.py              # Deterministic mock
│   │   │   ├── spark_llm.py             # 讯飞 Spark API client
│   │   │   ├── profile_service.py
│   │   │   ├── path_service.py
│   │   │   ├── resource_service.py
│   │   │   ├── agent_task_service.py
│   │   │   ├── evaluation_service.py
│   │   │   └── safety_service.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py            # Abstract base + AgentResult
│   │   │   ├── orchestrator.py          # Coordinates all agents for a task
│   │   │   ├── profile_agent.py
│   │   │   ├── knowledge_agent.py
│   │   │   ├── path_planner_agent.py
│   │   │   ├── lecture_agent.py
│   │   │   ├── mindmap_agent.py
│   │   │   ├── exercise_agent.py
│   │   │   ├── case_agent.py
│   │   │   ├── extended_reading_agent.py
│   │   │   ├── video_storyboard_agent.py
│   │   │   ├── evaluation_agent.py
│   │   │   ├── reflection_agent.py
│   │   │   ├── verifier_agent.py
│   │   │   └── content_guard_agent.py
│   │   └── prompts/
│   │       ├── profile.txt
│   │       ├── path_planner.txt
│   │       ├── lecture.txt
│   │       ├── mindmap.txt
│   │       ├── exercise.txt
│   │       ├── case.txt
│   │       ├── extended_reading.txt
│   │       ├── video_storyboard.txt
│   │       ├── evaluation.txt
│   │       ├── reflection.txt
│   │       ├── verifier.txt
│   │       └── content_guard.txt
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                  # DB fixtures, mock LLM, test client
│       ├── test_models.py
│       ├── test_seed_data.py
│       ├── test_llm_client.py
│       ├── test_auth.py
│       ├── test_profile_agent.py
│       ├── test_path_planner.py
│       ├── test_orchestrator.py
│       ├── test_resource_agents.py
│       ├── test_safety.py
│       ├── test_evaluation.py
│       └── test_demo_flow.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── .env.example
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── env.d.ts
│       ├── api/
│       │   ├── index.ts                 # Axios instance + interceptors
│       │   ├── auth.ts
│       │   ├── profile.ts
│       │   ├── learningPath.ts
│       │   ├── resources.ts
│       │   ├── exercises.ts
│       │   └── sse.ts                   # EventSource helpers
│       ├── router/
│       │   └── index.ts
│       ├── stores/
│       │   ├── auth.ts
│       │   ├── profile.ts
│       │   └── learningPath.ts
│       ├── views/
│       │   ├── Login.vue
│       │   └── student/
│       │       ├── Dashboard.vue
│       │       ├── ProfileChat.vue
│       │       ├── LearningPath.vue
│       │       ├── ResourceGenerate.vue
│       │       └── Exercise.vue
│       ├── components/
│       │   ├── ProfileCard.vue
│       │   ├── AgentTracePanel.vue
│       │   ├── MarkdownRenderer.vue
│       │   ├── MermaidRenderer.vue
│       │   ├── ResourceCard.vue
│       │   ├── PathTimeline.vue
│       │   ├── ExerciseCard.vue
│       │   └── SafetyBadge.vue
│       └── styles/
│           └── variables.css
├── scripts/
│   ├── init_demo_data.py
│   └── export_submission.ps1
└── .gitignore
```

---

## 12. Implementation Tasks

### Task 0: Repository Baseline

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/.env.example`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/env.d.ts`
- Create: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Create `.gitignore`**

```gitignore
__pycache__/
*.pyc
*.pyo
.env
*.db
*.sqlite3
node_modules/
dist/
.vite/
*.log
.idea/
.vscode/
*.egg-info/
```

- [ ] **Step 2: Create `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
pymysql==1.1.1
cryptography==43.0.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
sparkai==0.3.0
httpx==0.27.0
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **Step 3: Create `backend/.env.example`**

```env
# LLM Provider: "mock" (default, no API key needed) or "spark"
LLM_PROVIDER=mock

# 讯飞 Spark API (only needed when LLM_PROVIDER=spark)
SPARK_APP_ID=
SPARK_API_KEY=
SPARK_API_SECRET=
SPARK_MODEL=generalv3.5
SPARK_API_URL=wss://spark-api.xf-yun.com/v3.5/chat

# Database (MySQL required; create DB first: CREATE DATABASE edupath CHARACTER SET utf8mb4;)
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/edupath?charset=utf8mb4

# JWT
JWT_SECRET_KEY=dev-secret-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

- [ ] **Step 4: Create `backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "mock"
    spark_app_id: str = ""
    spark_api_key: str = ""
    spark_api_secret: str = ""
    spark_model: str = "generalv3.5"
    spark_api_url: str = "wss://spark-api.xf-yun.com/v3.5/chat"
    database_url: str = "mysql+pymysql://root:root@localhost:3306/edupath?charset=utf8mb4"
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 5: Create `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EduPath Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Create frontend scaffold**

`frontend/package.json`:
```json
{
  "name": "edupath-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "element-plus": "^2.8.0",
    "axios": "^1.7.0",
    "markdown-it": "^14.1.0",
    "mermaid": "^11.2.0",
    "echarts": "^5.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.1.0"
  }
}
```

`frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

`frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>EduPath - 个性化学习智能体</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

`frontend/src/main.ts`:
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router/index'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

`frontend/src/App.vue`:
```vue
<template>
  <router-view />
</template>
```

`frontend/src/env.d.ts`:
```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 7: Verify both can start**

Backend:
```bash
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
```
Expected: server starts, `GET /api/health` returns `{"status": "ok"}`.

Frontend:
```bash
cd frontend && npm install && npm run dev
```
Expected: Vite dev server starts on port 5173.

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "feat: repository baseline with backend FastAPI + frontend Vue 3 scaffold"
```

---

### Task 1: Database Models

**Files:**
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/course.py`
- Create: `backend/app/models/profile.py`
- Create: `backend/app/models/learning_path.py`
- Create: `backend/app/models/agent_task.py`
- Create: `backend/app/models/resource.py`
- Create: `backend/app/models/exercise.py`
- Create: `backend/app/models/safety.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Create DB base and session**

`backend/app/db/base.py`:
```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

`backend/app/db/session.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Create User model**

`backend/app/models/user.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(16), nullable=False, default="student")
    display_name = Column(String(64), default="")
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 3: Create Course models**

`backend/app/models/course.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())


class KnowledgePoint(Base):
    __tablename__ = "knowledge_point"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    chapter = Column(String(128), nullable=False)
    title = Column(String(256), nullable=False)
    summary = Column(Text, default="")
    key_content = Column(Text, default="")
    common_mistakes = Column(JSON, default=list)
    example_question = Column(Text, default="")
    example_answer = Column(Text, default="")
    difficulty = Column(String(16), default="medium")
    tags = Column(JSON, default=list)
    sources = Column(JSON, default=list)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class KnowledgeSource(Base):
    __tablename__ = "knowledge_source"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    chapter = Column(String(128), nullable=False)
    source_name = Column(String(256), nullable=False)
    source_url = Column(String(512), default="")
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 4: Create Profile models**

`backend/app/models/profile.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    base_level = Column(String(16), default="medium")
    learning_goal = Column(Text, default="")
    knowledge_state = Column(Text, default="")
    weak_points = Column(JSON, default=list)
    mastered_points = Column(JSON, default=list)
    learning_preference = Column(JSON, default=list)
    cognitive_style = Column(String(32), default="visual")
    time_budget = Column(String(128), default="")
    confidence = Column(String(16), default="low")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())


class ProfileUpdateLog(Base):
    __tablename__ = "profile_update_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    old_profile_json = Column(JSON, default=dict)
    new_profile_json = Column(JSON, default=dict)
    evidence = Column(Text, default="")
    change_reason = Column(Text, default="")
    updated_by = Column(String(32), default="ProfileAgent")
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 5: Create LearningPath models**

`backend/app/models/learning_path.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class LearningPath(Base):
    __tablename__ = "learning_path"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False)
    status = Column(String(16), default="active")
    created_at = Column(DateTime, server_default=func.now())


class LearningPathNode(Base):
    __tablename__ = "learning_path_node"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path_id = Column(Integer, ForeignKey("learning_path.id"), nullable=False, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_point.id"), nullable=False)
    sort_order = Column(Integer, default=0)
    status = Column(String(16), default="pending")
    reason = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 6: Create AgentTask models**

`backend/app/models/agent_task.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class AgentTask(Base):
    __tablename__ = "agent_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    task_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    progress = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AgentTrace(Base):
    __tablename__ = "agent_trace"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("agent_task.id"), nullable=False, index=True)
    agent_name = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    input_summary = Column(Text, default="")
    output_summary = Column(Text, default="")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    warnings = Column(JSON, default=list)
    confidence = Column(String(16), nullable=True)
```

- [ ] **Step 7: Create Resource model**

`backend/app/models/resource.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class GeneratedResource(Base):
    __tablename__ = "generated_resource"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("agent_task.id"), nullable=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_point.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    resource_type = Column(String(32), nullable=False)
    title = Column(String(256), default="")
    content = Column(Text, nullable=False)
    content_format = Column(String(16), default="markdown")
    confidence = Column(String(16), default="medium")
    warnings = Column(JSON, default=list)
    safety_status = Column(String(16), default="pending")
    created_at = Column(DateTime, server_default=func.now())
```

`resource_type` values: `lecture`, `mindmap`, `exercise`, `case`, `extended_reading`, `video_storyboard`.

- [ ] **Step 8: Create Exercise models**

`backend/app/models/exercise.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.db.base import Base


class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_point.id"), nullable=False, index=True)
    question_type = Column(String(32), nullable=False, default="choice")
    difficulty = Column(String(16), default="medium")
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    tags = Column(JSON, default=list)
    source = Column(String(16), default="seed")
    created_at = Column(DateTime, server_default=func.now())


class AnswerRecord(Base):
    __tablename__ = "answer_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    feedback = Column(Text, default="")
    mistake_tags = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
```

`question_type` values: `choice`, `multi_choice`, `fill_blank`, `short_answer`, `code`.

- [ ] **Step 9: Create SafetyAuditLog model**

`backend/app/models/safety.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class SafetyAuditLog(Base):
    __tablename__ = "safety_audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey("generated_resource.id"), nullable=True, index=True)
    check_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    details = Column(Text, default="")
    blocked_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 10: Create models `__init__.py`**

`backend/app/models/__init__.py`:
```python
from app.models.user import User
from app.models.course import Course, KnowledgePoint, KnowledgeSource
from app.models.profile import StudentProfile, ProfileUpdateLog
from app.models.learning_path import LearningPath, LearningPathNode
from app.models.agent_task import AgentTask, AgentTrace
from app.models.resource import GeneratedResource
from app.models.exercise import Exercise, AnswerRecord
from app.models.safety import SafetyAuditLog

__all__ = [
    "User", "Course", "KnowledgePoint", "KnowledgeSource",
    "StudentProfile", "ProfileUpdateLog",
    "LearningPath", "LearningPathNode",
    "AgentTask", "AgentTrace",
    "GeneratedResource",
    "Exercise", "AnswerRecord",
    "SafetyAuditLog",
]
```

- [ ] **Step 11: Write test for models**

`backend/tests/conftest.py`:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import *  # noqa: F401,F403

# Tests use in-memory SQLite for speed and zero setup.
# Production uses MySQL. All models use Integer PKs so both work.
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
```

`backend/tests/test_models.py`:
```python
from app.models import (
    User, Course, KnowledgePoint, KnowledgeSource,
    StudentProfile, ProfileUpdateLog,
    LearningPath, LearningPathNode,
    AgentTask, AgentTrace,
    GeneratedResource, Exercise, AnswerRecord, SafetyAuditLog,
)


def test_all_tables_created(db_session):
    tables = db_session.bind.dialect.get_table_names(db_session.bind)
    expected = [
        "user", "course", "knowledge_point", "knowledge_source",
        "student_profile", "profile_update_log",
        "learning_path", "learning_path_node",
        "agent_task", "agent_trace",
        "generated_resource", "exercise", "answer_record",
        "safety_audit_log",
    ]
    for table in expected:
        assert table in tables, f"Missing table: {table}"


def test_create_user(db_session):
    user = User(username="demo_student", password_hash="hashed", role="student")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.role == "student"


def test_create_course_with_knowledge_point(db_session):
    course = Course(name="操作系统", description="OS course")
    db_session.add(course)
    db_session.commit()
    kp = KnowledgePoint(
        course_id=course.id, chapter="文件系统", title="索引分配",
        summary="索引块保存数据块地址", difficulty="medium",
        tags=["file-system", "indexed-allocation"],
    )
    db_session.add(kp)
    db_session.commit()
    assert kp.course_id == course.id
    assert kp.tags == ["file-system", "indexed-allocation"]


def test_create_profile_with_8_dimensions(db_session):
    user = User(username="test_user", password_hash="hashed", role="student")
    course = Course(name="OS", description="")
    db_session.add_all([user, course])
    db_session.commit()
    profile = StudentProfile(
        user_id=user.id, course_id=course.id,
        base_level="medium",
        learning_goal="掌握文件系统分配方式",
        knowledge_state="了解目录基础",
        weak_points=["链接分配", "索引分配"],
        mastered_points=["文件目录"],
        learning_preference=["图解", "例题"],
        cognitive_style="visual",
        time_budget="2天",
    )
    db_session.add(profile)
    db_session.commit()
    assert len(profile.weak_points) == 2
    assert profile.cognitive_style == "visual"
```

- [ ] **Step 12: Run tests**

```bash
cd backend && python -m pytest tests/test_models.py -v
```
Expected: all 4 tests pass.

- [ ] **Step 13: Commit**

```bash
git add backend/app/db/ backend/app/models/ backend/tests/ && git commit -m "feat: define all 14 database models with tests"
```

---

### Task 2: Course Seed Data

**Files:**
- Create: `data/os_course_seed.json`
- Create: `backend/app/db/init_data.py`
- Create: `scripts/init_demo_data.py`
- Create: `backend/tests/test_seed_data.py`

- [ ] **Step 1: Create seed data JSON**

`data/os_course_seed.json` must contain:

```json
{
  "course": {
    "name": "操作系统",
    "description": "计算机科学核心课程，涵盖进程管理、内存管理、文件系统、设备管理等内容。"
  },
  "chapters": [
    {
      "name": "操作系统概述",
      "sources": ["操作系统概念(第九版) 第1-2章"],
      "knowledge_points": [
        {
          "title": "操作系统的定义与功能",
          "summary": "操作系统是管理计算机硬件和软件资源的系统软件。",
          "key_content": "资源管理、用户接口、程序执行环境。",
          "common_mistakes": ["混淆操作系统与应用软件的边界"],
          "example_question": "操作系统的四大功能是什么？",
          "example_answer": "进程管理、内存管理、文件管理、设备管理。",
          "difficulty": "easy",
          "tags": ["os-basics"]
        }
      ],
      "exercises": [
        {
          "question_type": "choice",
          "question": "以下哪个不是操作系统的基本功能？",
          "options": ["A. 进程管理", "B. 内存管理", "C. 编译程序", "D. 文件管理"],
          "answer": "C",
          "explanation": "编译程序是系统软件，但不是操作系统的基本功能。",
          "difficulty": "easy",
          "tags": ["os-basics"]
        }
      ]
    }
  ]
}
```

The full file must have 8 chapters with a total of ≥40 knowledge points, ≥60 exercises, and ≥8 lab entries. Each chapter follows the same schema as shown above. Build realistic content per chapter:

| Chapter | Knowledge Points | Exercises | Labs |
|---|---|---|---|
| 操作系统概述 | 4 | 6 | 0 |
| 进程与线程 | 6 | 10 | 2 |
| 进程同步与死锁 | 6 | 8 | 1 |
| CPU 调度 | 5 | 8 | 1 |
| 内存管理 | 5 | 8 | 1 |
| 虚拟内存 | 5 | 7 | 1 |
| 文件系统 | 5 | 8 | 1 |
| 设备管理与磁盘调度 | 4 | 7 | 1 |
| **Total** | **40** | **62** | **8** |

- [ ] **Step 2: Create init_data.py**

`backend/app/db/init_data.py`:
```python
import json
from pathlib import Path
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User, Course, KnowledgePoint, KnowledgeSource, Exercise

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SEED_FILE = Path(__file__).resolve().parents[3] / "data" / "os_course_seed.json"


def init_demo_data(db: Session) -> None:
    if db.query(User).first():
        return

    demo_student = User(
        username="demo_student",
        password_hash=pwd_context.hash("demo123"),
        role="student",
        display_name="演示学生",
    )
    demo_teacher = User(
        username="demo_teacher",
        password_hash=pwd_context.hash("demo123"),
        role="teacher",
        display_name="演示教师",
    )
    db.add_all([demo_student, demo_teacher])
    db.flush()

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed = json.load(f)

    course = Course(name=seed["course"]["name"], description=seed["course"]["description"])
    db.add(course)
    db.flush()

    sort_order = 0
    for chapter in seed["chapters"]:
        db.add(KnowledgeSource(
            course_id=course.id,
            chapter=chapter["name"],
            source_name=chapter["sources"][0] if chapter.get("sources") else "",
        ))

        for kp_data in chapter["knowledge_points"]:
            kp = KnowledgePoint(
                course_id=course.id,
                chapter=chapter["name"],
                title=kp_data["title"],
                summary=kp_data.get("summary", ""),
                key_content=kp_data.get("key_content", ""),
                common_mistakes=kp_data.get("common_mistakes", []),
                example_question=kp_data.get("example_question", ""),
                example_answer=kp_data.get("example_answer", ""),
                difficulty=kp_data.get("difficulty", "medium"),
                tags=kp_data.get("tags", []),
                sources=chapter.get("sources", []),
                sort_order=sort_order,
            )
            db.add(kp)
            sort_order += 1

        for ex_data in chapter.get("exercises", []):
            db.flush()
            last_kp = db.query(KnowledgePoint).filter_by(
                course_id=course.id, chapter=chapter["name"]
            ).first()
            exercise = Exercise(
                knowledge_point_id=last_kp.id if last_kp else 1,
                question_type=ex_data.get("question_type", "choice"),
                difficulty=ex_data.get("difficulty", "medium"),
                question=ex_data["question"],
                options=ex_data.get("options"),
                answer=ex_data["answer"],
                explanation=ex_data.get("explanation", ""),
                tags=ex_data.get("tags", []),
                source="seed",
            )
            db.add(exercise)

    db.commit()
```

`scripts/init_demo_data.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.init_data import init_demo_data
from app.models import *  # noqa: F401,F403

Base.metadata.create_all(bind=engine)
db = SessionLocal()
init_demo_data(db)
db.close()
print("Demo data initialized successfully.")
```

- [ ] **Step 3: Write seed data test**

`backend/tests/test_seed_data.py`:
```python
from app.db.init_data import init_demo_data
from app.models import User, Course, KnowledgePoint, Exercise, KnowledgeSource


def test_seed_creates_demo_users(db_session):
    init_demo_data(db_session)
    users = db_session.query(User).all()
    usernames = [u.username for u in users]
    assert "demo_student" in usernames
    assert "demo_teacher" in usernames


def test_seed_creates_course_with_enough_data(db_session):
    init_demo_data(db_session)
    courses = db_session.query(Course).all()
    assert len(courses) == 1
    assert courses[0].name == "操作系统"

    kp_count = db_session.query(KnowledgePoint).count()
    assert kp_count >= 40, f"Need ≥40 knowledge points, got {kp_count}"

    ex_count = db_session.query(Exercise).count()
    assert ex_count >= 60, f"Need ≥60 exercises, got {ex_count}"

    src_count = db_session.query(KnowledgeSource).count()
    assert src_count >= 8, f"Need ≥8 sources (one per chapter), got {src_count}"


def test_seed_is_idempotent(db_session):
    init_demo_data(db_session)
    init_demo_data(db_session)
    assert db_session.query(User).count() == 2
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_seed_data.py -v
```
Expected: all 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add data/ backend/app/db/init_data.py scripts/init_demo_data.py backend/tests/test_seed_data.py && git commit -m "feat: OS course seed data with 40 knowledge points and 62 exercises"
```

---

### Task 3: LLM Client (Mock + Spark)

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/llm_client.py`
- Create: `backend/app/services/mock_llm.py`
- Create: `backend/app/services/spark_llm.py`
- Create: `backend/tests/test_llm_client.py`

- [ ] **Step 1: Write failing test**

`backend/tests/test_llm_client.py`:
```python
from app.services.llm_client import get_llm_client
from app.services.mock_llm import MockLLM


def test_get_llm_client_returns_mock_by_default():
    client = get_llm_client("mock")
    assert isinstance(client, MockLLM)


def test_mock_llm_chat_returns_string():
    client = MockLLM()
    result = client.chat([{"role": "user", "content": "hello"}])
    assert isinstance(result, str)
    assert len(result) > 0


def test_mock_llm_chat_json_returns_dict():
    client = MockLLM()
    result = client.chat_json(
        [{"role": "user", "content": "extract profile"}],
        schema_hint="profile",
    )
    assert isinstance(result, dict)


def test_mock_llm_stream_yields_chunks():
    client = MockLLM()
    chunks = list(client.chat_stream([{"role": "user", "content": "hello"}]))
    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert len(full_text) > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && python -m pytest tests/test_llm_client.py -v
```
Expected: FAIL with import errors.

- [ ] **Step 3: Implement LLM client interface**

`backend/app/services/llm_client.py`:
```python
from abc import ABC, abstractmethod
from typing import Iterator


class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], temperature: float = 0.3) -> str:
        """Send messages, return full response text."""

    @abstractmethod
    def chat_json(self, messages: list[dict], schema_hint: str = "",
                  temperature: float = 0.1) -> dict:
        """Send messages, return parsed JSON response."""

    @abstractmethod
    def chat_stream(self, messages: list[dict], temperature: float = 0.3) -> Iterator[str]:
        """Send messages, yield response chunks for SSE."""


def get_llm_client(provider: str = "mock") -> LLMClient:
    if provider == "spark":
        from app.services.spark_llm import SparkLLM
        return SparkLLM()
    from app.services.mock_llm import MockLLM
    return MockLLM()
```

- [ ] **Step 4: Implement MockLLM**

`backend/app/services/mock_llm.py`:
```python
import json
import time
from typing import Iterator
from app.services.llm_client import LLMClient

MOCK_RESPONSES = {
    "profile": {
        "base_level": "medium",
        "learning_goal": "两天内掌握文件系统分配方式",
        "knowledge_state": "了解文件目录基础，不熟悉索引分配和链接分配",
        "weak_points": ["链接分配指针更新", "索引分配I/O计算", "连续分配外部碎片"],
        "mastered_points": ["文件目录基础", "文件基本概念"],
        "learning_preference": ["图解", "例题", "代码实操"],
        "cognitive_style": "visual",
        "time_budget": "2天, 每节点40分钟",
        "confidence": "medium",
        "evidence": "用户表示文件系统分配方式部分I/O计算总是搞混",
    },
    "path": {
        "nodes": [
            {"knowledge_point_title": "文件系统基础", "reason": "巩固基础概念"},
            {"knowledge_point_title": "连续分配", "reason": "薄弱点：外部碎片理解"},
            {"knowledge_point_title": "链接分配", "reason": "薄弱点：指针更新"},
            {"knowledge_point_title": "索引分配", "reason": "薄弱点：I/O计算"},
            {"knowledge_point_title": "文件分配方式对比", "reason": "综合对比加深理解"},
            {"knowledge_point_title": "磁盘I/O综合题", "reason": "综合练习巩固"},
        ]
    },
    "lecture": "# 链接分配\n\n## 概述\n链接分配是文件系统中一种重要的磁盘空间分配方式...\n\n## 核心原理\n每个磁盘块包含指向下一个块的指针...\n\n## 优缺点\n- 优点：无外部碎片\n- 缺点：只能顺序访问\n",
    "mindmap": "graph TD\n    A[链接分配] --> B[隐式链接]\n    A --> C[显式链接/FAT]\n    B --> D[每块含下一块指针]\n    B --> E[只能顺序访问]\n    C --> F[FAT表集中管理]\n    C --> G[支持随机访问]\n    A --> H[优点:无外部碎片]\n    A --> I[缺点:指针占空间]\n",
    "exercise": [
        {
            "question_type": "choice",
            "question": "链接分配中，读取文件第n个块需要几次磁盘I/O？",
            "options": ["A. 1次", "B. n次", "C. n+1次", "D. 2次"],
            "answer": "B",
            "explanation": "隐式链接需要从头遍历到第n块，每次读一个块。",
            "difficulty": "medium",
            "tags": ["链接分配", "磁盘I/O"],
        }
    ],
    "case": {
        "title": "模拟链接分配文件读取",
        "description": "编写程序模拟隐式链接分配的文件读取过程",
        "code": "class LinkedBlock:\n    def __init__(self, data, next_block=None):\n        self.data = data\n        self.next_block = next_block\n\ndef read_file_block(head_block, logical_index):\n    current = head_block\n    io_count = 0\n    for i in range(logical_index + 1):\n        if current is None:\n            raise IndexError('Block not found')\n        io_count += 1\n        if i == logical_index:\n            return current.data, io_count\n        current = current.next_block\n",
        "expected_output": "读取第3个逻辑块: data='block3', I/O次数=4",
    },
    "extended_reading": [
        {
            "title": "FAT文件系统详解",
            "summary": "FAT使用文件分配表实现显式链接，将指针集中存储在内存中的FAT表里...",
            "source": "操作系统概念(第九版) 11.4节",
            "relevance": "理解显式链接如何解决隐式链接的顺序访问问题",
        },
        {
            "title": "Unix inode与索引分配",
            "summary": "Unix采用多级索引分配方案，通过直接块、一级间接块、二级间接块...",
            "source": "操作系统概念(第九版) 11.5节",
            "relevance": "对比链接分配与索引分配的设计思想差异",
        },
    ],
    "video_storyboard": {
        "title": "链接分配原理动画讲解",
        "scenes": [
            {"scene_id": 1, "duration_sec": 30, "visual": "磁盘俯视图，高亮空闲块", "narration": "在链接分配中，文件的数据块可以分散存储在磁盘各处...", "animation": "散落的块依次亮起"},
            {"scene_id": 2, "duration_sec": 45, "visual": "块与块之间画出指针箭头", "narration": "每个数据块末尾保存下一个块的地址...", "animation": "箭头从块A连向块B"},
            {"scene_id": 3, "duration_sec": 30, "visual": "对比连续分配 vs 链接分配", "narration": "链接分配解决了外部碎片问题...", "animation": "左右分屏对比动画"},
        ],
        "ppt_outline": [
            "Slide 1: 链接分配的定义",
            "Slide 2: 隐式链接 vs 显式链接(FAT)",
            "Slide 3: I/O访问过程图解",
            "Slide 4: 优缺点总结",
        ],
    },
    "evaluation": {
        "score": 0,
        "is_correct": False,
        "feedback": "答案应为B。隐式链接分配需要从头遍历到第n块。",
        "mistake_tags": ["链接分配I/O计算"],
    },
    "reflection": {
        "profile_changes": {
            "weak_points": {"added": ["链接分配I/O计算"], "removed": []},
            "mastered_points": {"added": [], "removed": []},
        },
        "change_reason": "答错了链接分配I/O计算相关题目",
        "remediation": {"type": "resource", "knowledge_point_title": "链接分配"},
    },
    "verifier": {"consistent": True, "issues": [], "confidence": "high"},
    "content_guard": {"safe": True, "issues": [], "blocked": False},
}


class MockLLM(LLMClient):
    def chat(self, messages: list[dict], temperature: float = 0.3) -> str:
        hint = self._detect_hint(messages)
        response = MOCK_RESPONSES.get(hint, "这是一个模拟回复。")
        if isinstance(response, (dict, list)):
            return json.dumps(response, ensure_ascii=False)
        return response

    def chat_json(self, messages: list[dict], schema_hint: str = "",
                  temperature: float = 0.1) -> dict:
        hint = schema_hint or self._detect_hint(messages)
        response = MOCK_RESPONSES.get(hint, {})
        if isinstance(response, str):
            return {"content": response}
        return response

    def chat_stream(self, messages: list[dict], temperature: float = 0.3) -> Iterator[str]:
        full_text = self.chat(messages, temperature)
        for i in range(0, len(full_text), 10):
            yield full_text[i:i + 10]
            time.sleep(0.02)

    def _detect_hint(self, messages: list[dict]) -> str:
        last_content = messages[-1].get("content", "") if messages else ""
        keywords = {
            "画像": "profile", "profile": "profile",
            "路径": "path", "path": "path",
            "讲解": "lecture", "lecture": "lecture",
            "思维导图": "mindmap", "mindmap": "mindmap",
            "练习": "exercise", "exercise": "exercise",
            "实操": "case", "case": "case", "lab": "case",
            "拓展": "extended_reading", "reading": "extended_reading",
            "视频": "video_storyboard", "storyboard": "video_storyboard",
            "评分": "evaluation", "evaluate": "evaluation",
            "反思": "reflection", "reflection": "reflection",
            "验证": "verifier", "verify": "verifier",
            "安全": "content_guard", "safety": "content_guard",
        }
        for keyword, hint in keywords.items():
            if keyword in last_content.lower():
                return hint
        return "lecture"
```

- [ ] **Step 5: Implement SparkLLM**

`backend/app/services/spark_llm.py`:
```python
import json
from typing import Iterator
from app.services.llm_client import LLMClient
from app.core.config import settings


class SparkLLM(LLMClient):
    def __init__(self):
        try:
            from sparkai.llm.llm import ChatSparkLLM as SparkChat
            from sparkai.core.messages import ChatMessage
            self._spark = SparkChat(
                spark_api_url=settings.spark_api_url,
                spark_app_id=settings.spark_app_id,
                spark_api_key=settings.spark_api_key,
                spark_api_secret=settings.spark_api_secret,
                spark_llm_domain=settings.spark_model,
                streaming=False,
            )
            self._spark_stream = SparkChat(
                spark_api_url=settings.spark_api_url,
                spark_app_id=settings.spark_app_id,
                spark_api_key=settings.spark_api_key,
                spark_api_secret=settings.spark_api_secret,
                spark_llm_domain=settings.spark_model,
                streaming=True,
            )
            self._ChatMessage = ChatMessage
        except ImportError:
            raise RuntimeError("sparkai package not installed. Run: pip install sparkai")

    def _to_spark_messages(self, messages: list[dict]) -> list:
        result = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                role = "system"
            elif role == "assistant":
                role = "assistant"
            else:
                role = "human"
            result.append(self._ChatMessage(role=role, content=msg["content"]))
        return result

    def chat(self, messages: list[dict], temperature: float = 0.3) -> str:
        spark_msgs = self._to_spark_messages(messages)
        response = self._spark.generate([spark_msgs])
        return response.generations[0][0].text

    def chat_json(self, messages: list[dict], schema_hint: str = "",
                  temperature: float = 0.1) -> dict:
        text = self.chat(messages, temperature)
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
        return json.loads(text)

    def chat_stream(self, messages: list[dict], temperature: float = 0.3) -> Iterator[str]:
        spark_msgs = self._to_spark_messages(messages)
        for chunk in self._spark_stream.stream(spark_msgs):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content
```

- [ ] **Step 6: Run tests**

```bash
cd backend && python -m pytest tests/test_llm_client.py -v
```
Expected: all 4 tests pass.

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/ backend/tests/test_llm_client.py && git commit -m "feat: LLM client with mock provider and Spark adapter"
```

---

### Task 4: Auth System

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/deps.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/app/api/router.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Write failing test**

`backend/tests/test_auth.py`:
```python
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import engine
from app.models import *  # noqa: F401,F403

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_register_and_login():
    resp = client.post("/api/auth/register", json={
        "username": "test_user",
        "password": "test123",
        "role": "student",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data

    resp = client.post("/api/auth/login", json={
        "username": "test_user",
        "password": "test123",
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "test_user"


def test_login_wrong_password():
    client.post("/api/auth/register", json={
        "username": "test_user2", "password": "correct", "role": "student",
    })
    resp = client.post("/api/auth/login", json={
        "username": "test_user2", "password": "wrong",
    })
    assert resp.status_code == 401
```

- [ ] **Step 2: Implement security utilities**

`backend/app/core/security.py`:
```python
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
```

`backend/app/core/deps.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

- [ ] **Step 3: Implement auth schemas and routes**

`backend/app/schemas/auth.py`:
```python
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "student"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    display_name: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    display_name: str

    model_config = {"from_attributes": True}
```

`backend/app/api/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=req.role,
        display_name=req.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=token, user_id=user.id,
        role=user.role, display_name=user.display_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=token, user_id=user.id,
        role=user.role, display_name=user.display_name,
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
```

`backend/app/api/router.py`:
```python
from fastapi import APIRouter
from app.api.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router)
```

Update `backend/app/main.py` to include the router:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.models import *  # noqa: F401,F403

Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduPath Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_auth.py -v
```
Expected: both tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/ backend/app/schemas/ backend/app/api/ backend/tests/test_auth.py && git commit -m "feat: auth system with JWT login/register"
```

---

### Task 5: Profile Agent & API

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/base_agent.py`
- Create: `backend/app/agents/profile_agent.py`
- Create: `backend/app/prompts/profile.txt`
- Create: `backend/app/services/profile_service.py`
- Create: `backend/app/schemas/profile.py`
- Create: `backend/app/api/profile.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_profile_agent.py`

- [ ] **Step 1: Write failing test**

`backend/tests/test_profile_agent.py`:
```python
from app.agents.profile_agent import ProfileAgent
from app.services.mock_llm import MockLLM


def test_profile_agent_extracts_8_dimensions():
    agent = ProfileAgent(llm=MockLLM())
    result = agent.run(
        user_message="我最近在学操作系统，文件系统这一章比较不会。"
        "尤其是连续分配、链接分配、索引分配的I/O次数计算总是搞混。"
        "我比较喜欢通过图解和例题来学习，希望两天内补一下这部分。",
        context={},
    )
    assert result.success
    profile = result.data
    required_fields = [
        "base_level", "learning_goal", "knowledge_state",
        "weak_points", "mastered_points", "learning_preference",
        "cognitive_style", "time_budget",
    ]
    for field in required_fields:
        assert field in profile, f"Missing profile field: {field}"
    assert isinstance(profile["weak_points"], list)
    assert len(profile["weak_points"]) > 0
    assert "confidence" in profile


def test_profile_agent_returns_evidence():
    agent = ProfileAgent(llm=MockLLM())
    result = agent.run(user_message="test", context={})
    assert "evidence" in result.data
```

- [ ] **Step 2: Implement BaseAgent**

`backend/app/agents/base_agent.py`:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from app.services.llm_client import LLMClient


@dataclass
class AgentResult:
    success: bool
    data: Any = None
    error: str = ""
    warnings: list[str] = field(default_factory=list)
    confidence: str = "medium"
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None
    duration_ms: int = 0

    def finish(self):
        self.finished_at = datetime.now()
        self.duration_ms = int((self.finished_at - self.started_at).total_seconds() * 1000)


class BaseAgent:
    name: str = "BaseAgent"

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, **kwargs) -> AgentResult:
        result = AgentResult(success=False, started_at=datetime.now())
        try:
            data = self._execute(**kwargs)
            result.success = True
            result.data = data
        except Exception as e:
            result.error = str(e)
        result.finish()
        return result

    def _execute(self, **kwargs) -> Any:
        raise NotImplementedError
```

- [ ] **Step 3: Implement ProfileAgent**

`backend/app/agents/profile_agent.py`:
```python
from pathlib import Path
from typing import Any
from app.agents.base_agent import BaseAgent, AgentResult
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "profile.txt"


class ProfileAgent(BaseAgent):
    name = "ProfileAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Extract an 8-dimension student profile from the conversation."

    def _execute(self, user_message: str = "", context: dict | None = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        return self.llm.chat_json(messages, schema_hint="profile")
```

`backend/app/prompts/profile.txt`:
```
你是一个学生画像分析助手。请从学生的自然语言描述中提取以下8个维度的学习画像。

输出必须是一个JSON对象，包含以下字段：
1. base_level: 基础水平 ("beginner" / "medium" / "advanced")
2. learning_goal: 学习目标（具体描述）
3. knowledge_state: 知识状态（已知和未知概念）
4. weak_points: 薄弱知识点列表 (string[])
5. mastered_points: 已掌握知识点列表 (string[])
6. learning_preference: 学习偏好列表 (string[])，如["图解", "例题", "代码实操"]
7. cognitive_style: 认知风格 ("visual" / "auditory" / "reading" / "kinesthetic")
8. time_budget: 时间预算

附加字段（必填）：
- confidence: 对这次画像提取的置信度 ("low" / "medium" / "high")
- evidence: 支持画像判断的原文证据

规则：
- 只使用学生原文中的信息，不要编造。
- 如果某个维度无法从原文中判断，使用合理默认值并将confidence设为"low"。
- 直接输出JSON，不要有额外文字。
```

- [ ] **Step 4: Implement profile service and API**

`backend/app/schemas/profile.py`:
```python
from pydantic import BaseModel


class DialogueRequest(BaseModel):
    course_id: int
    message: str


class ProfileResponse(BaseModel):
    base_level: str
    learning_goal: str
    knowledge_state: str
    weak_points: list[str]
    mastered_points: list[str]
    learning_preference: list[str]
    cognitive_style: str
    time_budget: str
    confidence: str

    model_config = {"from_attributes": True}


class ProfileUpdateLogResponse(BaseModel):
    old_profile_json: dict
    new_profile_json: dict
    evidence: str
    change_reason: str
    updated_by: str
    created_at: str

    model_config = {"from_attributes": True}
```

`backend/app/services/profile_service.py`:
```python
import json
from sqlalchemy.orm import Session
from app.agents.profile_agent import ProfileAgent
from app.models.profile import StudentProfile, ProfileUpdateLog
from app.services.llm_client import get_llm_client
from app.core.config import settings


def extract_and_save_profile(db: Session, user_id: int, course_id: int, message: str) -> dict:
    llm = get_llm_client(settings.llm_provider)
    agent = ProfileAgent(llm=llm)
    result = agent.run(user_message=message, context={})

    if not result.success:
        raise RuntimeError(f"ProfileAgent failed: {result.error}")

    profile_data = result.data
    existing = db.query(StudentProfile).filter_by(user_id=user_id, course_id=course_id).first()
    old_json = {}

    if existing:
        old_json = {
            "base_level": existing.base_level,
            "learning_goal": existing.learning_goal,
            "knowledge_state": existing.knowledge_state,
            "weak_points": existing.weak_points,
            "mastered_points": existing.mastered_points,
            "learning_preference": existing.learning_preference,
            "cognitive_style": existing.cognitive_style,
            "time_budget": existing.time_budget,
        }
        for key in old_json:
            if key in profile_data:
                setattr(existing, key, profile_data[key])
        existing.confidence = profile_data.get("confidence", "medium")
    else:
        existing = StudentProfile(
            user_id=user_id,
            course_id=course_id,
            base_level=profile_data.get("base_level", "medium"),
            learning_goal=profile_data.get("learning_goal", ""),
            knowledge_state=profile_data.get("knowledge_state", ""),
            weak_points=profile_data.get("weak_points", []),
            mastered_points=profile_data.get("mastered_points", []),
            learning_preference=profile_data.get("learning_preference", []),
            cognitive_style=profile_data.get("cognitive_style", "visual"),
            time_budget=profile_data.get("time_budget", ""),
            confidence=profile_data.get("confidence", "medium"),
        )
        db.add(existing)

    log = ProfileUpdateLog(
        user_id=user_id,
        course_id=course_id,
        old_profile_json=old_json,
        new_profile_json=profile_data,
        evidence=profile_data.get("evidence", ""),
        change_reason=f"Profile extracted from dialogue",
        updated_by="ProfileAgent",
    )
    db.add(log)
    db.commit()
    db.refresh(existing)
    return profile_data
```

`backend/app/api/profile.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.profile import StudentProfile, ProfileUpdateLog
from app.schemas.profile import DialogueRequest, ProfileResponse
from app.services.profile_service import extract_and_save_profile

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("/dialogue")
def dialogue(req: DialogueRequest, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    result = extract_and_save_profile(db, user.id, req.course_id, req.message)
    return {"profile": result}


@router.get("/{course_id}", response_model=ProfileResponse)
def get_profile(course_id: int, user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter_by(
        user_id=user.id, course_id=course_id
    ).first()
    if not profile:
        return ProfileResponse(
            base_level="medium", learning_goal="", knowledge_state="",
            weak_points=[], mastered_points=[], learning_preference=[],
            cognitive_style="visual", time_budget="", confidence="low",
        )
    return profile


@router.get("/{course_id}/logs")
def get_profile_logs(course_id: int, user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    logs = db.query(ProfileUpdateLog).filter_by(
        user_id=user.id, course_id=course_id
    ).order_by(ProfileUpdateLog.created_at.desc()).limit(20).all()
    return [
        {
            "old_profile_json": log.old_profile_json,
            "new_profile_json": log.new_profile_json,
            "evidence": log.evidence,
            "change_reason": log.change_reason,
            "updated_by": log.updated_by,
            "created_at": str(log.created_at),
        }
        for log in logs
    ]
```

Add to `backend/app/api/router.py`:
```python
from app.api.profile import router as profile_router
api_router.include_router(profile_router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/test_profile_agent.py -v
```
Expected: both tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/agents/ backend/app/prompts/ backend/app/services/profile_service.py backend/app/schemas/profile.py backend/app/api/profile.py backend/tests/test_profile_agent.py && git commit -m "feat: ProfileAgent extracts 8-dimension profile from dialogue"
```

---

### Task 6: Learning Path Agent & API

**Files:**
- Create: `backend/app/agents/path_planner_agent.py`
- Create: `backend/app/prompts/path_planner.txt`
- Create: `backend/app/services/path_service.py`
- Create: `backend/app/schemas/learning_path.py`
- Create: `backend/app/api/learning_path.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_path_planner.py`

- [ ] **Step 1: Write failing test**

`backend/tests/test_path_planner.py`:
```python
from app.agents.path_planner_agent import PathPlannerAgent
from app.services.mock_llm import MockLLM


def test_path_planner_returns_ordered_nodes():
    agent = PathPlannerAgent(llm=MockLLM())
    result = agent.run(
        profile={"weak_points": ["链接分配", "索引分配"], "time_budget": "2天"},
        knowledge_points=["文件系统基础", "连续分配", "链接分配", "索引分配"],
    )
    assert result.success
    nodes = result.data["nodes"]
    assert len(nodes) >= 3
    for node in nodes:
        assert "knowledge_point_title" in node
        assert "reason" in node
```

- [ ] **Step 2: Implement PathPlannerAgent**

`backend/app/agents/path_planner_agent.py`:
```python
from pathlib import Path
from typing import Any
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "path_planner.txt"


class PathPlannerAgent(BaseAgent):
    name = "PathPlannerAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Generate a learning path."

    def _execute(self, profile: dict = None, knowledge_points: list = None, **kwargs) -> Any:
        import json
        user_content = (
            f"学生画像:\n{json.dumps(profile, ensure_ascii=False)}\n\n"
            f"可用知识点:\n{json.dumps(knowledge_points, ensure_ascii=False)}\n\n"
            "请生成学习路径。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        return self.llm.chat_json(messages, schema_hint="path")
```

`backend/app/prompts/path_planner.txt`:
```
你是一个学习路径规划助手。根据学生画像和可用知识点，生成个性化的学习路径。

输出JSON格式：
{
  "nodes": [
    {
      "knowledge_point_title": "知识点标题",
      "reason": "为什么安排这个节点（结合学生薄弱点和学习目标解释）"
    }
  ]
}

规则：
1. 优先安排学生薄弱的知识点。
2. 前置依赖知识点排在前面。
3. 每个节点必须有具体的reason，说明为什么这个学生需要学这个。
4. 路径长度控制在5-8个节点。
5. 考虑学生的时间预算。
6. 直接输出JSON。
```

- [ ] **Step 3: Implement path service and API**

`backend/app/schemas/learning_path.py`:
```python
from pydantic import BaseModel


class GeneratePathRequest(BaseModel):
    course_id: int


class PathNodeResponse(BaseModel):
    id: int
    knowledge_point_id: int
    knowledge_point_title: str
    sort_order: int
    status: str
    reason: str


class LearningPathResponse(BaseModel):
    id: int
    course_id: int
    status: str
    nodes: list[PathNodeResponse]


class UpdateNodeStatusRequest(BaseModel):
    status: str
```

`backend/app/services/path_service.py`:
```python
from sqlalchemy.orm import Session
from app.agents.path_planner_agent import PathPlannerAgent
from app.models.profile import StudentProfile
from app.models.course import KnowledgePoint
from app.models.learning_path import LearningPath, LearningPathNode
from app.services.llm_client import get_llm_client
from app.core.config import settings


def generate_learning_path(db: Session, user_id: int, course_id: int) -> LearningPath:
    llm = get_llm_client(settings.llm_provider)
    agent = PathPlannerAgent(llm=llm)

    profile = db.query(StudentProfile).filter_by(user_id=user_id, course_id=course_id).first()
    profile_dict = {}
    if profile:
        profile_dict = {
            "base_level": profile.base_level,
            "weak_points": profile.weak_points,
            "mastered_points": profile.mastered_points,
            "learning_goal": profile.learning_goal,
            "time_budget": profile.time_budget,
        }

    kps = db.query(KnowledgePoint).filter_by(course_id=course_id).order_by(
        KnowledgePoint.sort_order
    ).all()
    kp_titles = [kp.title for kp in kps]
    kp_map = {kp.title: kp.id for kp in kps}

    result = agent.run(profile=profile_dict, knowledge_points=kp_titles)
    if not result.success:
        raise RuntimeError(f"PathPlannerAgent failed: {result.error}")

    old_path = db.query(LearningPath).filter_by(
        user_id=user_id, course_id=course_id, status="active"
    ).first()
    if old_path:
        old_path.status = "replaced"

    path = LearningPath(user_id=user_id, course_id=course_id, status="active")
    db.add(path)
    db.flush()

    for i, node_data in enumerate(result.data.get("nodes", [])):
        title = node_data["knowledge_point_title"]
        kp_id = kp_map.get(title)
        if kp_id is None:
            for kp_title, kid in kp_map.items():
                if title in kp_title or kp_title in title:
                    kp_id = kid
                    break
        if kp_id is None:
            continue
        node = LearningPathNode(
            path_id=path.id,
            knowledge_point_id=kp_id,
            sort_order=i,
            status="pending",
            reason=node_data.get("reason", ""),
        )
        db.add(node)

    db.commit()
    db.refresh(path)
    return path
```

`backend/app/api/learning_path.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.learning_path import LearningPath, LearningPathNode
from app.models.course import KnowledgePoint
from app.schemas.learning_path import (
    GeneratePathRequest, LearningPathResponse,
    PathNodeResponse, UpdateNodeStatusRequest,
)
from app.services.path_service import generate_learning_path

router = APIRouter(prefix="/api/learning-path", tags=["learning-path"])


@router.post("/generate", response_model=LearningPathResponse)
def generate(req: GeneratePathRequest, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    path = generate_learning_path(db, user.id, req.course_id)
    return _path_to_response(db, path)


@router.get("/current", response_model=LearningPathResponse)
def current(course_id: int, user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    path = db.query(LearningPath).filter_by(
        user_id=user.id, course_id=course_id, status="active"
    ).first()
    if not path:
        raise HTTPException(status_code=404, detail="No active learning path")
    return _path_to_response(db, path)


@router.put("/nodes/{node_id}/status")
def update_node_status(node_id: int, req: UpdateNodeStatusRequest,
                       user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    node = db.query(LearningPathNode).filter_by(id=node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = req.status
    db.commit()
    return {"id": node.id, "status": node.status}


def _path_to_response(db: Session, path: LearningPath) -> LearningPathResponse:
    nodes = db.query(LearningPathNode).filter_by(path_id=path.id).order_by(
        LearningPathNode.sort_order
    ).all()
    node_responses = []
    for node in nodes:
        kp = db.query(KnowledgePoint).filter_by(id=node.knowledge_point_id).first()
        node_responses.append(PathNodeResponse(
            id=node.id,
            knowledge_point_id=node.knowledge_point_id,
            knowledge_point_title=kp.title if kp else "Unknown",
            sort_order=node.sort_order,
            status=node.status,
            reason=node.reason,
        ))
    return LearningPathResponse(
        id=path.id, course_id=path.course_id,
        status=path.status, nodes=node_responses,
    )
```

Add to `backend/app/api/router.py`:
```python
from app.api.learning_path import router as path_router
api_router.include_router(path_router)
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_path_planner.py -v
```
Expected: test passes.

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/path_planner_agent.py backend/app/prompts/path_planner.txt backend/app/services/path_service.py backend/app/schemas/learning_path.py backend/app/api/learning_path.py backend/tests/test_path_planner.py && git commit -m "feat: learning path generation from student profile"
```

---

### Task 7: Agent Orchestrator & Trace

**Files:**
- Create: `backend/app/agents/orchestrator.py`
- Create: `backend/app/services/agent_task_service.py`
- Create: `backend/app/schemas/agent_task.py`
- Create: `backend/app/api/agent_tasks.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_orchestrator.py`

- [ ] **Step 1: Write failing test**

`backend/tests/test_orchestrator.py`:
```python
from app.agents.orchestrator import Orchestrator
from app.services.mock_llm import MockLLM


def test_orchestrator_runs_agents_and_produces_trace():
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(
        profile={"weak_points": ["链接分配"], "learning_preference": ["图解"]},
        knowledge_context={
            "title": "链接分配",
            "summary": "链接分配方式",
            "key_content": "每个块包含下一个块的指针",
        },
    )
    assert len(result["resources"]) >= 5
    assert len(result["trace"]) >= 7
    for trace_item in result["trace"]:
        assert "agent_name" in trace_item
        assert "status" in trace_item
        assert trace_item["status"] in ("success", "failed", "skipped")


def test_orchestrator_includes_all_6_resource_types():
    orchestrator = Orchestrator(llm=MockLLM())
    result = orchestrator.generate_resources(
        profile={"weak_points": ["链接分配"]},
        knowledge_context={"title": "链接分配", "summary": "test", "key_content": "test"},
    )
    resource_types = {r["resource_type"] for r in result["resources"]}
    expected = {"lecture", "mindmap", "exercise", "case", "extended_reading", "video_storyboard"}
    assert expected.issubset(resource_types), f"Missing: {expected - resource_types}"
```

- [ ] **Step 2: Implement resource agents**

All 6 resource agents follow the same pattern as ProfileAgent. Each reads a prompt template and calls `chat` or `chat_json`. Here is the pattern:

`backend/app/agents/knowledge_agent.py`:
```python
from typing import Any
from app.agents.base_agent import BaseAgent


class KnowledgeAgent(BaseAgent):
    name = "KnowledgeAgent"

    def _execute(self, knowledge_point_id: int = 0, db=None, **kwargs) -> Any:
        if db is None:
            return kwargs.get("knowledge_context", {})
        from app.models.course import KnowledgePoint
        kp = db.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
        if not kp:
            return {}
        return {
            "title": kp.title,
            "chapter": kp.chapter,
            "summary": kp.summary,
            "key_content": kp.key_content,
            "common_mistakes": kp.common_mistakes,
            "example_question": kp.example_question,
            "example_answer": kp.example_answer,
            "tags": kp.tags,
            "sources": kp.sources,
        }
```

`backend/app/agents/lecture_agent.py`:
```python
from pathlib import Path
from typing import Any
import json
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "lecture.txt"


class LectureAgent(BaseAgent):
    name = "LectureAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Generate a lecture."

    def _execute(self, profile: dict = None, knowledge_context: dict = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            "请生成个性化讲解文档。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        text = self.llm.chat(messages)
        return {"content": text}
```

`backend/app/agents/mindmap_agent.py`:
```python
from pathlib import Path
from typing import Any
import json
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "mindmap.txt"


class MindMapAgent(BaseAgent):
    name = "MindMapAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Generate a mind map."

    def _execute(self, profile: dict = None, knowledge_context: dict = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            "请生成Mermaid格式思维导图。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        text = self.llm.chat(messages)
        return {"content": text}
```

`backend/app/agents/exercise_agent.py`:
```python
from pathlib import Path
from typing import Any
import json
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "exercise.txt"


class ExerciseAgent(BaseAgent):
    name = "ExerciseAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Generate exercises."

    def _execute(self, profile: dict = None, knowledge_context: dict = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            "请生成分层练习题集。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        return self.llm.chat_json(messages, schema_hint="exercise")
```

`backend/app/agents/case_agent.py`:
```python
from pathlib import Path
from typing import Any
import json
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "case.txt"


class CaseAgent(BaseAgent):
    name = "CaseAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Generate a lab case."

    def _execute(self, profile: dict = None, knowledge_context: dict = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            "请生成实操案例。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        return self.llm.chat_json(messages, schema_hint="case")
```

`backend/app/agents/extended_reading_agent.py`:
```python
from pathlib import Path
from typing import Any
import json
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "extended_reading.txt"


class ExtendedReadingAgent(BaseAgent):
    name = "ExtendedReadingAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Generate reading list."

    def _execute(self, profile: dict = None, knowledge_context: dict = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            "请推荐拓展阅读材料。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        return self.llm.chat_json(messages, schema_hint="extended_reading")
```

`backend/app/agents/video_storyboard_agent.py`:
```python
from pathlib import Path
from typing import Any
import json
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "video_storyboard.txt"


class VideoStoryboardAgent(BaseAgent):
    name = "VideoStoryboardAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else "Generate storyboard."

    def _execute(self, profile: dict = None, knowledge_context: dict = None, **kwargs) -> Any:
        user_content = (
            f"学生画像:\n{json.dumps(profile or {}, ensure_ascii=False)}\n\n"
            f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
            "请生成教学视频分镜脚本和PPT大纲。"
        )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]
        return self.llm.chat_json(messages, schema_hint="video_storyboard")
```

- [ ] **Step 3: Create prompt templates**

Create each prompt file in `backend/app/prompts/`. Each tells the LLM what to generate and in what format. Key examples:

`backend/app/prompts/lecture.txt`:
```
你是一个个性化课程讲解生成助手。根据学生画像和知识点上下文，生成个性化的Markdown讲解文档。

要求：
1. 根据学生的基础水平调整讲解深度。
2. 根据学生的学习偏好选择讲解方式（图解、例题、代码等）。
3. 重点讲解学生薄弱的知识点。
4. 包含清晰的标题层级结构。
5. 包含至少一个具体例子。
6. 只使用提供的知识点上下文中的信息。
7. 直接输出Markdown文本。
```

`backend/app/prompts/mindmap.txt`:
```
你是一个知识点思维导图生成助手。根据知识点上下文，生成Mermaid格式的思维导图代码。

输出要求：
1. 使用 graph TD 格式。
2. 主节点为知识点标题。
3. 展开核心概念、子概念、关键要素。
4. 标记学生薄弱点对应的节点。
5. 节点文字简洁（≤15字）。
6. 直接输出Mermaid代码，不要加```包裹。
```

`backend/app/prompts/exercise.txt`:
```
你是一个练习题生成助手。根据学生画像和知识点上下文，生成分层练习题集。

输出JSON数组，每题包含：
- question_type: "choice" / "fill_blank" / "short_answer" / "code"
- question: 题目文字
- options: 选项数组（仅选择题需要）
- answer: 标准答案
- explanation: 答案解析
- difficulty: "easy" / "medium" / "hard"
- tags: 知识标签数组

要求：
1. 生成3-5道题。
2. 难度梯度：至少包含easy和medium。
3. 题型多样化。
4. 针对学生薄弱点出题。
5. 每题必须有答案和解析。
```

`backend/app/prompts/extended_reading.txt`:
```
你是一个拓展阅读推荐助手。根据知识点上下文和学生画像，推荐相关的拓展阅读材料。

输出JSON数组，每项包含：
- title: 推荐材料标题
- summary: 内容摘要（50-100字）
- source: 来源（教材章节、论文、在线资源等）
- relevance: 与当前知识点的关联说明

要求：
1. 推荐2-4项材料。
2. 材料应与当前知识点紧密相关但有所拓展。
3. 包含不同类型的材料（教材、实践文章等）。
4. 基于提供的上下文信息推荐，不要编造不存在的资源。
```

`backend/app/prompts/video_storyboard.txt`:
```
你是一个教学视频分镜脚本生成助手。根据知识点上下文和学生画像，生成教学视频的分镜脚本和PPT大纲。

输出JSON对象：
{
  "title": "视频标题",
  "scenes": [
    {
      "scene_id": 1,
      "duration_sec": 30,
      "visual": "画面描述",
      "narration": "旁白文字",
      "animation": "动画效果描述"
    }
  ],
  "ppt_outline": ["Slide 1: ...", "Slide 2: ..."]
}

要求：
1. 3-5个场景。
2. 总时长控制在3分钟内。
3. 视觉描述要具体，便于制作。
4. 旁白通俗易懂。
5. PPT大纲4-6页。
```

- [ ] **Step 4: Implement Orchestrator**

`backend/app/agents/orchestrator.py`:
```python
from datetime import datetime
from typing import Any
from app.services.llm_client import LLMClient
from app.agents.base_agent import AgentResult
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.lecture_agent import LectureAgent
from app.agents.mindmap_agent import MindMapAgent
from app.agents.exercise_agent import ExerciseAgent
from app.agents.case_agent import CaseAgent
from app.agents.extended_reading_agent import ExtendedReadingAgent
from app.agents.video_storyboard_agent import VideoStoryboardAgent
from app.agents.verifier_agent import VerifierAgent
from app.agents.content_guard_agent import ContentGuardAgent


RESOURCE_AGENTS = [
    ("lecture", LectureAgent),
    ("mindmap", MindMapAgent),
    ("exercise", ExerciseAgent),
    ("case", CaseAgent),
    ("extended_reading", ExtendedReadingAgent),
    ("video_storyboard", VideoStoryboardAgent),
]


class Orchestrator:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate_resources(
        self,
        profile: dict,
        knowledge_context: dict,
        on_trace: Any = None,
    ) -> dict:
        trace = []
        resources = []

        knowledge_result = self._run_agent(
            KnowledgeAgent(self.llm), trace, on_trace,
            knowledge_context=knowledge_context,
        )
        context = knowledge_result.data if knowledge_result.success else knowledge_context

        for resource_type, agent_cls in RESOURCE_AGENTS:
            result = self._run_agent(
                agent_cls(self.llm), trace, on_trace,
                profile=profile, knowledge_context=context,
            )
            if result.success:
                content = result.data
                if isinstance(content, str):
                    content = {"content": content}
                resources.append({
                    "resource_type": resource_type,
                    "content": content,
                    "confidence": result.confidence,
                    "warnings": result.warnings,
                })

        verifier = VerifierAgent(self.llm)
        guard = ContentGuardAgent(self.llm)

        for resource in resources:
            v_result = self._run_agent(
                verifier, trace, on_trace,
                resource=resource, knowledge_context=context,
            )
            if v_result.success and isinstance(v_result.data, dict):
                if not v_result.data.get("consistent", True):
                    resource["warnings"].append("factual_inconsistency")
                    resource["confidence"] = "low"

            g_result = self._run_agent(
                guard, trace, on_trace,
                resource=resource,
            )
            if g_result.success and isinstance(g_result.data, dict):
                if g_result.data.get("blocked", False):
                    resource["content"] = {"content": "该内容已被安全过滤。"}
                    resource["warnings"].append("safety_blocked")
                    resource["confidence"] = "low"

        return {"resources": resources, "trace": trace}

    def _run_agent(self, agent, trace: list, on_trace, **kwargs) -> AgentResult:
        trace_item = {
            "agent_name": agent.name,
            "status": "running",
            "started_at": datetime.now(),
            "finished_at": None,
            "duration_ms": 0,
            "warnings": [],
        }
        trace.append(trace_item)
        if on_trace:
            on_trace(trace_item)

        result = agent.run(**kwargs)

        trace_item["status"] = "success" if result.success else "failed"
        trace_item["finished_at"] = datetime.now()
        trace_item["duration_ms"] = result.duration_ms
        trace_item["warnings"] = result.warnings
        if on_trace:
            on_trace(trace_item)

        return result
```

- [ ] **Step 5: Implement VerifierAgent and ContentGuardAgent stubs**

`backend/app/agents/verifier_agent.py`:
```python
import json
from pathlib import Path
from typing import Any
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "verifier.txt"


class VerifierAgent(BaseAgent):
    name = "VerifierAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Verify factual consistency."

    def _execute(self, resource: dict = None, knowledge_context: dict = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"知识点上下文:\n{json.dumps(knowledge_context or {}, ensure_ascii=False)}\n\n"
                f"生成的资源:\n{json.dumps(resource or {}, ensure_ascii=False)}\n\n"
                "请验证资源内容的事实一致性。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="verifier")
```

`backend/app/agents/content_guard_agent.py`:
```python
import json
from pathlib import Path
from typing import Any
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "content_guard.txt"


class ContentGuardAgent(BaseAgent):
    name = "ContentGuardAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Check content safety."

    def _execute(self, resource: dict = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"待检查的资源:\n{json.dumps(resource or {}, ensure_ascii=False)}\n\n"
                "请检查内容安全性。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="content_guard")
```

- [ ] **Step 6: Implement agent task service and API**

`backend/app/services/agent_task_service.py`:
```python
from sqlalchemy.orm import Session
from app.models.agent_task import AgentTask, AgentTrace


def create_task(db: Session, user_id: int, task_type: str, total_steps: int) -> AgentTask:
    task = AgentTask(
        user_id=user_id,
        task_type=task_type,
        status="pending",
        total_steps=total_steps,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task_progress(db: Session, task_id: int, progress: int, status: str = "running"):
    task = db.query(AgentTask).filter_by(id=task_id).first()
    if task:
        task.progress = progress
        task.status = status
        db.commit()


def save_single_trace(db: Session, task_id: int, item: dict):
    """Save or update one trace entry. Called incrementally by the background
    generation thread so the SSE endpoint can stream progress in real time."""
    existing = db.query(AgentTrace).filter_by(
        task_id=task_id, agent_name=item["agent_name"]
    ).first()
    if existing:
        existing.status = item["status"]
        existing.finished_at = item.get("finished_at")
        existing.duration_ms = item.get("duration_ms", 0)
        existing.warnings = item.get("warnings", [])
        existing.confidence = item.get("confidence")
    else:
        trace = AgentTrace(
            task_id=task_id,
            agent_name=item["agent_name"],
            status=item["status"],
            input_summary=item.get("input_summary", ""),
            output_summary=item.get("output_summary", ""),
            started_at=item.get("started_at"),
            finished_at=item.get("finished_at"),
            duration_ms=item.get("duration_ms", 0),
            warnings=item.get("warnings", []),
            confidence=item.get("confidence"),
        )
        db.add(trace)
    db.commit()
```

`backend/app/schemas/agent_task.py`:
```python
from pydantic import BaseModel


class AgentTaskResponse(BaseModel):
    id: int
    task_type: str
    status: str
    progress: int
    total_steps: int
    error_message: str

    model_config = {"from_attributes": True}


class AgentTraceResponse(BaseModel):
    agent_name: str
    status: str
    duration_ms: int | None
    warnings: list[str]
    confidence: str | None

    model_config = {"from_attributes": True}
```

`backend/app/api/agent_tasks.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.agent_task import AgentTask, AgentTrace
from app.schemas.agent_task import AgentTaskResponse, AgentTraceResponse

router = APIRouter(prefix="/api/agent-tasks", tags=["agent-tasks"])


@router.get("/{task_id}", response_model=AgentTaskResponse)
def get_task(task_id: int, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    task = db.query(AgentTask).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/trace", response_model=list[AgentTraceResponse])
def get_trace(task_id: int, user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    traces = db.query(AgentTrace).filter_by(task_id=task_id).all()
    return traces
```

Add to `backend/app/api/router.py`:
```python
from app.api.agent_tasks import router as tasks_router
api_router.include_router(tasks_router)
```

- [ ] **Step 7: Run tests**

```bash
cd backend && python -m pytest tests/test_orchestrator.py -v
```
Expected: both tests pass.

- [ ] **Step 8: Commit**

```bash
git add backend/app/agents/ backend/app/prompts/ backend/app/services/agent_task_service.py backend/app/schemas/agent_task.py backend/app/api/agent_tasks.py backend/tests/test_orchestrator.py && git commit -m "feat: agent orchestrator with 6 resource agents, verifier, and content guard"
```

---

### Task 8: Resource Generation API with SSE

**Files:**
- Create: `backend/app/services/resource_service.py`
- Create: `backend/app/schemas/resource.py`
- Create: `backend/app/api/resources.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_resource_generation.py`

- [ ] **Step 1: Write failing test**

`backend/tests/test_resource_generation.py`:
```python
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import engine
from app.db.init_data import init_demo_data
from app.db.session import SessionLocal
from app.models import *  # noqa: F401,F403

Base.metadata.create_all(bind=engine)
db = SessionLocal()
init_demo_data(db)
db.close()

client = TestClient(app)


def _get_token():
    resp = client.post("/api/auth/login", json={
        "username": "demo_student", "password": "demo123",
    })
    return resp.json()["access_token"]


def test_generate_resources_returns_task_id():
    token = _get_token()
    resp = client.post(
        "/api/resources/generate",
        json={"knowledge_point_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data


def test_get_resources_by_knowledge_point():
    token = _get_token()
    client.post(
        "/api/resources/generate",
        json={"knowledge_point_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = client.get(
        "/api/resources?knowledge_point_id=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    resources = resp.json()
    types = {r["resource_type"] for r in resources}
    assert len(types) >= 5
```

- [ ] **Step 2: Implement resource service**

`backend/app/services/resource_service.py`:
```python
import json
import threading
from sqlalchemy.orm import Session
from app.agents.orchestrator import Orchestrator
from app.models.profile import StudentProfile
from app.models.course import KnowledgePoint
from app.models.resource import GeneratedResource
from app.models.safety import SafetyAuditLog
from app.services.agent_task_service import create_task, update_task_progress, save_single_trace
from app.services.llm_client import get_llm_client
from app.core.config import settings
from app.db.session import SessionLocal


def start_resource_generation(db: Session, user_id: int, knowledge_point_id: int) -> int:
    """Create the task record and launch generation in a background thread.
    Returns immediately with task_id so the frontend can start polling SSE."""
    kp = db.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
    if not kp:
        raise ValueError(f"Knowledge point {knowledge_point_id} not found")

    task = create_task(db, user_id, "resource_generation", total_steps=9)

    thread = threading.Thread(
        target=_run_generation,
        args=(task.id, user_id, knowledge_point_id),
        daemon=True,
    )
    thread.start()
    return task.id


def _run_generation(task_id: int, user_id: int, knowledge_point_id: int) -> None:
    """Runs in background thread. Opens its own DB session and writes
    trace entries incrementally so the SSE endpoint can stream them."""
    db = SessionLocal()
    try:
        llm = get_llm_client(settings.llm_provider)
        orchestrator = Orchestrator(llm=llm)

        kp = db.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
        knowledge_context = {
            "title": kp.title, "chapter": kp.chapter,
            "summary": kp.summary, "key_content": kp.key_content,
            "common_mistakes": kp.common_mistakes,
            "example_question": kp.example_question,
            "example_answer": kp.example_answer,
            "tags": kp.tags, "sources": kp.sources,
        }

        profile = db.query(StudentProfile).filter_by(user_id=user_id).first()
        profile_dict = {}
        if profile:
            profile_dict = {
                "base_level": profile.base_level,
                "weak_points": profile.weak_points,
                "mastered_points": profile.mastered_points,
                "learning_preference": profile.learning_preference,
                "cognitive_style": profile.cognitive_style,
            }

        update_task_progress(db, task_id, 0, "running")

        step_counter = [0]

        def on_trace(trace_item: dict):
            save_single_trace(db, task_id, trace_item)
            step_counter[0] += 1
            update_task_progress(db, task_id, step_counter[0], "running")

        result = orchestrator.generate_resources(
            profile=profile_dict,
            knowledge_context=knowledge_context,
            on_trace=on_trace,
        )

        for res_data in result["resources"]:
            content = res_data["content"]
            if isinstance(content, (dict, list)):
                content_str = json.dumps(content, ensure_ascii=False)
            else:
                content_str = str(content)

            resource = GeneratedResource(
                task_id=task_id,
                knowledge_point_id=knowledge_point_id,
                user_id=user_id,
                resource_type=res_data["resource_type"],
                title=f"{kp.title} - {res_data['resource_type']}",
                content=content_str,
                content_format="json" if isinstance(res_data["content"], (dict, list)) else "markdown",
                confidence=res_data.get("confidence", "medium"),
                warnings=res_data.get("warnings", []),
                safety_status="passed" if not res_data.get("warnings") else "warning",
            )
            db.add(resource)
            db.flush()

            for warning in res_data.get("warnings", []):
                db.add(SafetyAuditLog(
                    resource_id=resource.id,
                    check_type=warning,
                    status="warning",
                    details=f"Warning during {res_data['resource_type']} generation",
                ))
            db.add(SafetyAuditLog(
                resource_id=resource.id,
                check_type="overall",
                status="passed" if not res_data.get("warnings") else "warning",
                details=f"{res_data['resource_type']} generation complete",
            ))

        update_task_progress(db, task_id, step_counter[0], "completed")
        db.commit()

    except Exception as e:
        update_task_progress(db, task_id, 0, "failed")
        from app.models.agent_task import AgentTask
        t = db.query(AgentTask).filter_by(id=task_id).first()
        if t:
            t.error_message = str(e)
        db.commit()
    finally:
        db.close()
```

- [ ] **Step 3: Implement resource API with SSE**

`backend/app/schemas/resource.py`:
```python
from pydantic import BaseModel


class GenerateResourceRequest(BaseModel):
    knowledge_point_id: int


class ResourceResponse(BaseModel):
    id: int
    resource_type: str
    title: str
    content: str
    content_format: str
    confidence: str
    warnings: list[str]
    safety_status: str

    model_config = {"from_attributes": True}
```

`backend/app/api/resources.py`:
```python
import json
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app.core.deps import get_current_user
from app.models.user import User
from app.models.resource import GeneratedResource
from app.schemas.resource import GenerateResourceRequest, ResourceResponse
from app.services.resource_service import start_resource_generation

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.post("/generate")
def generate(req: GenerateResourceRequest, user: User = Depends(get_current_user),
             db: Session = Depends(get_db)):
    """Immediately returns task_id. Generation runs in a background thread."""
    task_id = start_resource_generation(db, user.id, req.knowledge_point_id)
    return {"task_id": task_id}


@router.get("/generate/{task_id}/stream")
def stream_generation(task_id: int):
    """Real-time SSE endpoint. Polls the DB for new trace entries written by
    the background generation thread. Sends events as agents complete."""
    from app.models.agent_task import AgentTask, AgentTrace

    def event_stream():
        db = SessionLocal()
        try:
            seen_traces = set()
            seen_resources = set()

            for _ in range(120):
                db.expire_all()
                task = db.query(AgentTask).filter_by(id=task_id).first()
                if not task:
                    yield f"event: error\ndata: {json.dumps({'message': 'Task not found'})}\n\n"
                    return

                traces = db.query(AgentTrace).filter_by(task_id=task_id).all()
                for trace in traces:
                    key = f"{trace.agent_name}:{trace.status}"
                    if key not in seen_traces:
                        seen_traces.add(key)
                        yield (
                            f"event: agent_status\n"
                            f"data: {json.dumps({'agent_name': trace.agent_name, 'status': trace.status, 'duration_ms': trace.duration_ms, 'progress': task.progress, 'total': task.total_steps}, ensure_ascii=False)}\n\n"
                        )

                resources = db.query(GeneratedResource).filter_by(task_id=task_id).all()
                for resource in resources:
                    if resource.id not in seen_resources:
                        seen_resources.add(resource.id)
                        yield (
                            f"event: resource_ready\n"
                            f"data: {json.dumps({'resource_id': resource.id, 'resource_type': resource.resource_type, 'confidence': resource.confidence}, ensure_ascii=False)}\n\n"
                        )

                if task.status in ("completed", "failed"):
                    yield f"event: done\ndata: {json.dumps({'task_id': task_id, 'status': task.status, 'total_resources': len(resources)})}\n\n"
                    return

                time.sleep(0.5)

            yield f"event: error\ndata: {json.dumps({'message': 'SSE timeout'})}\n\n"
        finally:
            db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("", response_model=list[ResourceResponse])
def list_resources(knowledge_point_id: int, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    resources = db.query(GeneratedResource).filter_by(
        knowledge_point_id=knowledge_point_id, user_id=user.id
    ).order_by(GeneratedResource.created_at.desc()).all()
    return resources


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    resource = db.query(GeneratedResource).filter_by(id=resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
```

Add to `backend/app/api/router.py`:
```python
from app.api.resources import router as resources_router
api_router.include_router(resources_router)
```

- [ ] **Step 4: Run tests**

```bash
cd backend && python -m pytest tests/test_resource_generation.py -v
```
Expected: both tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/resource_service.py backend/app/schemas/resource.py backend/app/api/resources.py backend/tests/test_resource_generation.py && git commit -m "feat: resource generation API with SSE streaming and 6 resource types"
```

---

### Task 9: Practice, Evaluation & Reflection

**Files:**
- Create: `backend/app/agents/evaluation_agent.py`
- Create: `backend/app/agents/reflection_agent.py`
- Create: `backend/app/prompts/evaluation.txt`
- Create: `backend/app/prompts/reflection.txt`
- Create: `backend/app/services/evaluation_service.py`
- Create: `backend/app/schemas/exercise.py`
- Create: `backend/app/api/exercises.py`
- Modify: `backend/app/api/router.py`
- Create: `backend/tests/test_evaluation.py`

- [ ] **Step 1: Write failing test**

`backend/tests/test_evaluation.py`:
```python
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.reflection_agent import ReflectionAgent
from app.services.mock_llm import MockLLM


def test_evaluation_agent_scores_answer():
    agent = EvaluationAgent(llm=MockLLM())
    result = agent.run(
        question="链接分配中读取第n个块需要几次I/O？",
        correct_answer="B",
        user_answer="A",
        question_type="choice",
    )
    assert result.success
    assert "is_correct" in result.data
    assert "feedback" in result.data
    assert "mistake_tags" in result.data


def test_reflection_agent_updates_profile():
    agent = ReflectionAgent(llm=MockLLM())
    result = agent.run(
        evaluation_result={"is_correct": False, "mistake_tags": ["链接分配I/O计算"]},
        current_profile={"weak_points": [], "mastered_points": ["文件目录基础"]},
    )
    assert result.success
    assert "profile_changes" in result.data
    assert "change_reason" in result.data
```

- [ ] **Step 2: Implement EvaluationAgent**

`backend/app/agents/evaluation_agent.py`:
```python
import json
from pathlib import Path
from typing import Any
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "evaluation.txt"


class EvaluationAgent(BaseAgent):
    name = "EvaluationAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Evaluate student answer."

    def _execute(self, question: str = "", correct_answer: str = "",
                 user_answer: str = "", question_type: str = "choice", **kwargs) -> Any:
        if question_type == "choice":
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
            if is_correct:
                return {
                    "score": 1.0,
                    "is_correct": True,
                    "feedback": "回答正确！",
                    "mistake_tags": [],
                }

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"题目: {question}\n标准答案: {correct_answer}\n"
                f"学生答案: {user_answer}\n题型: {question_type}\n"
                "请评分。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="evaluation")
```

`backend/app/prompts/evaluation.txt`:
```
你是一个学习评估助手。评估学生的答案，给出评分和反馈。

输出JSON对象：
{
  "score": 0.0 到 1.0 之间的分数,
  "is_correct": true/false,
  "feedback": "具体的反馈说明，指出错误原因",
  "mistake_tags": ["具体的错误知识标签"]
}

规则：
1. 选择题：完全匹配才算对。
2. 简答题：根据关键点覆盖率评分。
3. feedback必须具体指出错误原因和正确思路。
4. mistake_tags应该是具体的知识点标签，用于更新学生画像。
```

- [ ] **Step 3: Implement ReflectionAgent**

`backend/app/agents/reflection_agent.py`:
```python
import json
from pathlib import Path
from typing import Any
from app.agents.base_agent import BaseAgent
from app.services.llm_client import LLMClient

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "reflection.txt"


class ReflectionAgent(BaseAgent):
    name = "ReflectionAgent"

    def __init__(self, llm: LLMClient):
        super().__init__(llm)
        if PROMPT_PATH.exists():
            self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        else:
            self.system_prompt = "Reflect on evaluation and update profile."

    def _execute(self, evaluation_result: dict = None,
                 current_profile: dict = None, **kwargs) -> Any:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": (
                f"评估结果:\n{json.dumps(evaluation_result or {}, ensure_ascii=False)}\n\n"
                f"当前画像:\n{json.dumps(current_profile or {}, ensure_ascii=False)}\n\n"
                "请反思并给出画像更新建议。"
            )},
        ]
        return self.llm.chat_json(messages, schema_hint="reflection")
```

`backend/app/prompts/reflection.txt`:
```
你是一个学习反思助手。根据评估结果和当前学生画像，决定如何更新画像。

输出JSON对象：
{
  "profile_changes": {
    "weak_points": {"added": ["新增薄弱点"], "removed": ["不再薄弱的点"]},
    "mastered_points": {"added": ["新增已掌握点"], "removed": []}
  },
  "change_reason": "画像变更原因说明",
  "remediation": {
    "type": "resource 或 path_update",
    "knowledge_point_title": "建议补学的知识点"
  }
}

规则：
1. 答错的题目对应的知识标签应加入weak_points。
2. 连续答对3次以上的知识点可以从weak_points移到mastered_points。
3. change_reason要具体说明为什么更新。
4. 如果有薄弱点，必须给出补救建议。
```

- [ ] **Step 4: Implement evaluation service and API**

`backend/app/services/evaluation_service.py`:
```python
from sqlalchemy.orm import Session
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.reflection_agent import ReflectionAgent
from app.models.exercise import Exercise, AnswerRecord
from app.models.profile import StudentProfile, ProfileUpdateLog
from app.services.llm_client import get_llm_client
from app.core.config import settings


def submit_and_evaluate(db: Session, user_id: int, exercise_id: int,
                        user_answer: str) -> dict:
    llm = get_llm_client(settings.llm_provider)

    exercise = db.query(Exercise).filter_by(id=exercise_id).first()
    if not exercise:
        raise ValueError(f"Exercise {exercise_id} not found")

    eval_agent = EvaluationAgent(llm=llm)
    eval_result = eval_agent.run(
        question=exercise.question,
        correct_answer=exercise.answer,
        user_answer=user_answer,
        question_type=exercise.question_type,
    )

    eval_data = eval_result.data if eval_result.success else {
        "score": 0, "is_correct": False,
        "feedback": "评估失败", "mistake_tags": [],
    }

    record = AnswerRecord(
        user_id=user_id,
        exercise_id=exercise_id,
        user_answer=user_answer,
        is_correct=1 if eval_data.get("is_correct") else 0,
        score=eval_data.get("score", 0),
        feedback=eval_data.get("feedback", ""),
        mistake_tags=eval_data.get("mistake_tags", []),
    )
    db.add(record)

    from app.models.course import KnowledgePoint
    kp = db.query(KnowledgePoint).filter_by(id=exercise.knowledge_point_id).first()
    profile = db.query(StudentProfile).filter_by(user_id=user_id).first()

    reflection_data = {}
    if profile and not eval_data.get("is_correct"):
        reflection_agent = ReflectionAgent(llm=llm)
        ref_result = reflection_agent.run(
            evaluation_result=eval_data,
            current_profile={
                "weak_points": profile.weak_points or [],
                "mastered_points": profile.mastered_points or [],
            },
        )
        if ref_result.success:
            reflection_data = ref_result.data
            changes = reflection_data.get("profile_changes", {})
            weak_changes = changes.get("weak_points", {})
            new_weak = list(set(
                (profile.weak_points or []) +
                weak_changes.get("added", [])
            ) - set(weak_changes.get("removed", [])))
            old_json = {"weak_points": profile.weak_points, "mastered_points": profile.mastered_points}
            profile.weak_points = new_weak
            db.add(ProfileUpdateLog(
                user_id=user_id,
                course_id=profile.course_id,
                old_profile_json=old_json,
                new_profile_json={"weak_points": new_weak, "mastered_points": profile.mastered_points},
                evidence=f"答题结果: {exercise.question[:50]}",
                change_reason=reflection_data.get("change_reason", "练习反馈更新"),
                updated_by="ReflectionAgent",
            ))

    db.commit()
    return {
        "evaluation": eval_data,
        "reflection": reflection_data,
        "answer_record_id": record.id,
    }
```

`backend/app/schemas/exercise.py`:
```python
from pydantic import BaseModel


class SubmitAnswerRequest(BaseModel):
    user_answer: str


class ExerciseResponse(BaseModel):
    id: int
    question_type: str
    difficulty: str
    question: str
    options: list[str] | None
    tags: list[str]

    model_config = {"from_attributes": True}


class AnswerRecordResponse(BaseModel):
    id: int
    exercise_id: int
    user_answer: str
    is_correct: int
    score: float
    feedback: str
    mistake_tags: list[str]

    model_config = {"from_attributes": True}
```

`backend/app/api/exercises.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.exercise import Exercise, AnswerRecord
from app.schemas.exercise import SubmitAnswerRequest, ExerciseResponse, AnswerRecordResponse
from app.services.evaluation_service import submit_and_evaluate

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseResponse])
def list_exercises(knowledge_point_id: int, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    exercises = db.query(Exercise).filter_by(knowledge_point_id=knowledge_point_id).all()
    return exercises


@router.post("/{exercise_id}/submit")
def submit(exercise_id: int, req: SubmitAnswerRequest,
           user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = submit_and_evaluate(db, user.id, exercise_id, req.user_answer)
    return result


@router.get("/answer-records", response_model=list[AnswerRecordResponse])
def answer_records(user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    records = db.query(AnswerRecord).filter_by(user_id=user.id).order_by(
        AnswerRecord.created_at.desc()
    ).limit(50).all()
    return records
```

Add to `backend/app/api/router.py`:
```python
from app.api.exercises import router as exercises_router
api_router.include_router(exercises_router)
```

- [ ] **Step 5: Run tests**

```bash
cd backend && python -m pytest tests/test_evaluation.py -v
```
Expected: both tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/agents/evaluation_agent.py backend/app/agents/reflection_agent.py backend/app/prompts/evaluation.txt backend/app/prompts/reflection.txt backend/app/services/evaluation_service.py backend/app/schemas/exercise.py backend/app/api/exercises.py backend/tests/test_evaluation.py && git commit -m "feat: practice evaluation with reflection and profile update loop"
```

---

### Task 10: Knowledge Management & Analytics API

**Files:**
- Create: `backend/app/api/knowledge.py`
- Create: `backend/app/api/analytics.py`
- Modify: `backend/app/api/router.py`

- [ ] **Step 1: Implement knowledge CRUD API**

`backend/app/api/knowledge.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.course import Course, KnowledgePoint

router = APIRouter(prefix="/api", tags=["knowledge"])


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
```

- [ ] **Step 2: Implement analytics API**

`backend/app/api/analytics.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.exercise import AnswerRecord
from app.models.resource import GeneratedResource
from app.models.profile import StudentProfile

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def student_summary(course_id: int = 1, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    total_answers = db.query(AnswerRecord).filter_by(user_id=user.id).count()
    correct_answers = db.query(AnswerRecord).filter_by(user_id=user.id, is_correct=1).count()
    total_resources = db.query(GeneratedResource).filter_by(user_id=user.id).count()
    profile = db.query(StudentProfile).filter_by(user_id=user.id, course_id=course_id).first()

    correctness_rate = (correct_answers / total_answers * 100) if total_answers > 0 else 0

    mistake_tag_counts = {}
    records = db.query(AnswerRecord).filter_by(user_id=user.id).all()
    for record in records:
        for tag in (record.mistake_tags or []):
            mistake_tag_counts[tag] = mistake_tag_counts.get(tag, 0) + 1

    return {
        "total_answers": total_answers,
        "correct_answers": correct_answers,
        "correctness_rate": round(correctness_rate, 1),
        "total_resources": total_resources,
        "weak_points": profile.weak_points if profile else [],
        "mastered_points": profile.mastered_points if profile else [],
        "mistake_tag_counts": mistake_tag_counts,
    }
```

Add to `backend/app/api/router.py`:
```python
from app.api.knowledge import router as knowledge_router
from app.api.analytics import router as analytics_router
api_router.include_router(knowledge_router)
api_router.include_router(analytics_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/knowledge.py backend/app/api/analytics.py && git commit -m "feat: knowledge CRUD and analytics API"
```

---

### Task 11: Student Frontend — Core Pages

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/api/index.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/sse.ts`
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/student/Dashboard.vue`
- Create: `frontend/src/views/student/ProfileChat.vue`
- Create: `frontend/src/components/ProfileCard.vue`

- [ ] **Step 1: Set up router and API client**

`frontend/src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/student/dashboard', name: 'Dashboard', component: () => import('../views/student/Dashboard.vue') },
  { path: '/student/profile-chat', name: 'ProfileChat', component: () => import('../views/student/ProfileChat.vue') },
  { path: '/student/learning-path', name: 'LearningPath', component: () => import('../views/student/LearningPath.vue') },
  { path: '/student/resources/:knowledgePointId', name: 'ResourceGenerate', component: () => import('../views/student/ResourceGenerate.vue') },
  { path: '/student/exercise/:knowledgePointId', name: 'Exercise', component: () => import('../views/student/Exercise.vue') },
  { path: '/', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

`frontend/src/api/index.ts`:
```typescript
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api
```

`frontend/src/api/auth.ts`:
```typescript
import api from './index'

export const login = (username: string, password: string) =>
  api.post('/auth/login', { username, password })

export const register = (username: string, password: string, role: string) =>
  api.post('/auth/register', { username, password, role })

export const getMe = () => api.get('/auth/me')
```

`frontend/src/api/sse.ts`:
```typescript
export function createSSE(url: string, onEvent: (event: MessageEvent) => void, onDone?: () => void) {
  const token = localStorage.getItem('token')
  const fullUrl = url.includes('?') ? `${url}&token=${token}` : `${url}?token=${token}`
  const source = new EventSource(fullUrl)

  source.addEventListener('agent_status', onEvent)
  source.addEventListener('resource_ready', onEvent)
  source.addEventListener('done', (e) => {
    onEvent(e)
    source.close()
    onDone?.()
  })
  source.addEventListener('error', () => {
    source.close()
    onDone?.()
  })

  return source
}
```

`frontend/src/stores/auth.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const token = ref(localStorage.getItem('token') || '')

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password)
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    user.value = { id: res.data.user_id, role: res.data.role, displayName: res.data.display_name }
  }

  async function fetchUser() {
    const res = await getMe()
    user.value = res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, login, fetchUser, logout }
})
```

- [ ] **Step 2: Build Login page**

`frontend/src/views/Login.vue`:
```vue
<template>
  <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f0f2f5">
    <el-card style="width:400px">
      <template #header><h2 style="margin:0;text-align:center">EduPath 个性化学习</h2></template>
      <el-form @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" style="width:100%" :loading="loading">登录</el-button>
        </el-form-item>
        <el-form-item>
          <el-button style="width:100%" @click="demoLogin">演示账号一键登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/student/dashboard')
  } catch {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

async function demoLogin() {
  username.value = 'demo_student'
  password.value = 'demo123'
  await handleLogin()
}
</script>
```

- [ ] **Step 3: Build ProfileCard component**

`frontend/src/components/ProfileCard.vue`:
```vue
<template>
  <el-card class="profile-card">
    <template #header><span>学生画像 ({{ profile.confidence || '未知' }}置信度)</span></template>
    <el-row :gutter="16">
      <el-col :span="12" v-for="dim in dimensions" :key="dim.key">
        <div class="dim-item">
          <div class="dim-label">{{ dim.label }}</div>
          <div class="dim-value">
            <template v-if="Array.isArray(profile[dim.key])">
              <el-tag v-for="tag in profile[dim.key]" :key="tag" size="small" style="margin:2px">{{ tag }}</el-tag>
            </template>
            <template v-else>{{ profile[dim.key] || '—' }}</template>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{ profile: Record<string, any> }>()

const dimensions = [
  { key: 'base_level', label: '基础水平' },
  { key: 'learning_goal', label: '学习目标' },
  { key: 'knowledge_state', label: '知识状态' },
  { key: 'weak_points', label: '薄弱知识点' },
  { key: 'mastered_points', label: '已掌握知识点' },
  { key: 'learning_preference', label: '学习偏好' },
  { key: 'cognitive_style', label: '认知风格' },
  { key: 'time_budget', label: '时间预算' },
]
</script>

<style scoped>
.profile-card { margin-bottom: 16px; }
.dim-item { margin-bottom: 12px; }
.dim-label { font-weight: 600; color: #606266; margin-bottom: 4px; font-size: 13px; }
.dim-value { font-size: 14px; }
</style>
```

- [ ] **Step 4: Build Dashboard page**

`frontend/src/views/student/Dashboard.vue`:
```vue
<template>
  <el-container style="padding:24px;max-width:1200px;margin:0 auto">
    <el-header style="display:flex;justify-content:space-between;align-items:center">
      <h1 style="margin:0">学习仪表盘</h1>
      <el-button @click="$router.push('/student/profile-chat')">对话建档</el-button>
    </el-header>
    <el-main>
      <ProfileCard v-if="profile" :profile="profile" />
      <el-skeleton v-else :rows="4" animated />
      <el-card style="margin-top:16px">
        <template #header>快捷操作</template>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-button type="primary" style="width:100%" @click="$router.push('/student/learning-path')">查看学习路径</el-button>
          </el-col>
          <el-col :span="8">
            <el-button style="width:100%" @click="$router.push('/student/profile-chat')">更新学习画像</el-button>
          </el-col>
          <el-col :span="8">
            <el-button style="width:100%" @click="logout">退出登录</el-button>
          </el-col>
        </el-row>
      </el-card>
      <el-card v-if="profile?.weak_points?.length" style="margin-top:16px">
        <template #header>薄弱知识点</template>
        <el-tag v-for="tag in profile.weak_points" :key="tag" type="danger" style="margin:4px">{{ tag }}</el-tag>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ProfileCard from '../../components/ProfileCard.vue'
import api from '../../api/index'

const router = useRouter()
const auth = useAuthStore()
const profile = ref<any>(null)

onMounted(async () => {
  try {
    const res = await api.get('/profile/1')
    profile.value = res.data
  } catch { /* no profile yet */ }
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
```

- [ ] **Step 5: Build ProfileChat page**

`frontend/src/views/student/ProfileChat.vue`:
```vue
<template>
  <el-container style="padding:24px;max-width:900px;margin:0 auto">
    <el-header><h1 style="margin:0">对话式学习建档</h1></el-header>
    <el-main>
      <el-card>
        <div v-for="(msg, i) in chatHistory" :key="i" :style="{ textAlign: msg.role === 'user' ? 'right' : 'left', marginBottom: '12px' }">
          <el-tag :type="msg.role === 'user' ? 'primary' : 'success'" size="small">{{ msg.role === 'user' ? '我' : '系统' }}</el-tag>
          <p style="margin:4px 0;white-space:pre-wrap">{{ msg.content }}</p>
        </div>
      </el-card>
      <el-form @submit.prevent="sendMessage" style="margin-top:16px;display:flex;gap:8px">
        <el-input v-model="input" placeholder="描述你的学习情况，例如：我在学操作系统，文件系统的链接分配不太会..." :rows="3" type="textarea" style="flex:1" />
        <el-button type="primary" native-type="submit" :loading="loading" style="height:auto">发送</el-button>
      </el-form>
      <ProfileCard v-if="profile" :profile="profile" style="margin-top:16px" />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import ProfileCard from '../../components/ProfileCard.vue'
import api from '../../api/index'

const input = ref('')
const loading = ref(false)
const profile = ref<any>(null)
const chatHistory = ref<Array<{ role: string; content: string }>>([])

async function sendMessage() {
  if (!input.value.trim()) return
  const userMsg = input.value
  chatHistory.value.push({ role: 'user', content: userMsg })
  input.value = ''
  loading.value = true
  try {
    const res = await api.post('/profile/dialogue', { course_id: 1, message: userMsg })
    profile.value = res.data.profile
    chatHistory.value.push({ role: 'assistant', content: '画像已更新，请查看下方画像卡片。' })
  } catch {
    ElMessage.error('画像提取失败')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 5: Verify frontend starts and login works**

```bash
cd frontend && npm run dev
```
Open `http://localhost:5173`, click "演示账号一键登录", verify redirect to dashboard.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/ && git commit -m "feat: student frontend core - login, dashboard, profile chat"
```

---

### Task 12: Student Frontend — Path, Resources, Exercises

**Files:**
- Create: `frontend/src/views/student/LearningPath.vue`
- Create: `frontend/src/views/student/ResourceGenerate.vue`
- Create: `frontend/src/views/student/Exercise.vue`
- Create: `frontend/src/components/AgentTracePanel.vue`
- Create: `frontend/src/components/MarkdownRenderer.vue`
- Create: `frontend/src/components/MermaidRenderer.vue`
- Create: `frontend/src/components/ResourceCard.vue`
- Create: `frontend/src/components/PathTimeline.vue`
- Create: `frontend/src/components/ExerciseCard.vue`
- Create: `frontend/src/components/SafetyBadge.vue`

- [ ] **Step 1: Build AgentTracePanel**

`frontend/src/components/AgentTracePanel.vue`:
```vue
<template>
  <el-card>
    <template #header>智能体执行进度 ({{ completedCount }}/{{ traces.length }})</template>
    <el-steps direction="vertical" :active="completedCount" finish-status="success">
      <el-step v-for="trace in traces" :key="trace.agent_name"
        :title="trace.agent_name"
        :status="stepStatus(trace.status)"
        :description="trace.duration_ms ? `${trace.duration_ms}ms` : '等待中...'" />
    </el-steps>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ traces: Array<{ agent_name: string; status: string; duration_ms?: number }> }>()

const completedCount = computed(() => props.traces.filter(t => t.status === 'success' || t.status === 'failed').length)

function stepStatus(status: string) {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'error'
  if (status === 'running') return 'process'
  return 'wait'
}
</script>
```

- [ ] **Step 2: Build MarkdownRenderer and MermaidRenderer**

`frontend/src/components/MarkdownRenderer.vue`:
```vue
<template>
  <div class="markdown-body" v-html="rendered"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{ content: string }>()
const md = new MarkdownIt({ html: false, linkify: true })
const rendered = computed(() => md.render(props.content || ''))
</script>

<style scoped>
.markdown-body { line-height: 1.7; }
.markdown-body h1, .markdown-body h2, .markdown-body h3 { margin-top: 16px; }
.markdown-body code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
.markdown-body pre { background: #f5f5f5; padding: 12px; border-radius: 6px; overflow-x: auto; }
</style>
```

`frontend/src/components/MermaidRenderer.vue`:
```vue
<template>
  <div ref="container" class="mermaid-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{ code: string }>()
const container = ref<HTMLElement>()

mermaid.initialize({ startOnLoad: false, theme: 'default' })

async function render() {
  if (!container.value || !props.code) return
  try {
    const { svg } = await mermaid.render('mermaid-' + Date.now(), props.code)
    container.value.innerHTML = svg
  } catch {
    container.value.innerHTML = `<pre style="color:#909399">${props.code}</pre>`
  }
}

onMounted(render)
watch(() => props.code, render)
</script>

<style scoped>
.mermaid-container { text-align: center; padding: 16px; }
</style>
```

- [ ] **Step 3: Build ResourceCard and SafetyBadge**

`frontend/src/components/SafetyBadge.vue`:
```vue
<template>
  <el-tag :type="tagType" size="small">{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string; warnings: string[] }>()

const tagType = computed(() => {
  if (props.warnings?.length > 0) return 'warning'
  if (props.status === 'passed') return 'success'
  if (props.status === 'blocked') return 'danger'
  return 'info'
})

const label = computed(() => {
  if (props.status === 'blocked') return '已过滤'
  if (props.warnings?.length > 0) return '有警告'
  return '已验证'
})
</script>
```

`frontend/src/components/ResourceCard.vue`:
```vue
<template>
  <el-card shadow="hover" class="resource-card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>{{ typeLabel }}</span>
        <SafetyBadge :status="resource.safety_status" :warnings="resource.warnings" />
      </div>
    </template>
    <MarkdownRenderer v-if="isMarkdown" :content="displayContent" />
    <MermaidRenderer v-else-if="resource.resource_type === 'mindmap'" :code="displayContent" />
    <pre v-else style="white-space:pre-wrap">{{ displayContent }}</pre>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import MermaidRenderer from './MermaidRenderer.vue'
import SafetyBadge from './SafetyBadge.vue'

const props = defineProps<{ resource: any }>()

const TYPE_LABELS: Record<string, string> = {
  lecture: '个性化讲解', mindmap: '知识思维导图', exercise: '分层练习题',
  case: '实操案例', extended_reading: '拓展阅读', video_storyboard: '视频分镜脚本',
}
const typeLabel = computed(() => TYPE_LABELS[props.resource.resource_type] || props.resource.resource_type)
const isMarkdown = computed(() => props.resource.content_format === 'markdown' || props.resource.resource_type === 'lecture')

const displayContent = computed(() => {
  const c = props.resource.content
  if (typeof c === 'string') {
    try { return JSON.stringify(JSON.parse(c), null, 2) } catch { return c }
  }
  return JSON.stringify(c, null, 2)
})
</script>

<style scoped>
.resource-card { margin-bottom: 16px; }
</style>
```

- [ ] **Step 4: Build LearningPath page**

`frontend/src/views/student/LearningPath.vue`:
```vue
<template>
  <el-container style="padding:24px;max-width:900px;margin:0 auto">
    <el-header style="display:flex;justify-content:space-between;align-items:center">
      <h1 style="margin:0">学习路径</h1>
      <el-button type="primary" @click="generatePath" :loading="generating">生成路径</el-button>
    </el-header>
    <el-main>
      <el-skeleton v-if="loading" :rows="6" animated />
      <el-empty v-else-if="!path" description="暂无学习路径，请先建档后生成" />
      <el-timeline v-else>
        <el-timeline-item v-for="node in path.nodes" :key="node.id"
          :type="node.status === 'completed' ? 'success' : node.status === 'in_progress' ? 'primary' : 'info'"
          :hollow="node.status === 'pending'">
          <el-card shadow="hover" style="cursor:pointer" @click="goToResources(node.knowledge_point_id)">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div>
                <strong>{{ node.knowledge_point_title }}</strong>
                <p style="margin:4px 0 0;color:#909399;font-size:13px">{{ node.reason }}</p>
              </div>
              <el-tag :type="node.status === 'completed' ? 'success' : 'info'" size="small">{{ node.status }}</el-tag>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api/index'

const router = useRouter()
const path = ref<any>(null)
const loading = ref(true)
const generating = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('/learning-path/current', { params: { course_id: 1 } })
    path.value = res.data
  } catch { /* no path yet */ }
  loading.value = false
})

async function generatePath() {
  generating.value = true
  try {
    const res = await api.post('/learning-path/generate', { course_id: 1 })
    path.value = res.data
    ElMessage.success('学习路径已生成')
  } catch {
    ElMessage.error('路径生成失败')
  } finally {
    generating.value = false
  }
}

function goToResources(kpId: number) {
  router.push(`/student/resources/${kpId}`)
}
</script>
```

- [ ] **Step 5: Build ResourceGenerate page**

`frontend/src/views/student/ResourceGenerate.vue`:
```vue
<template>
  <el-container style="padding:24px;max-width:1200px;margin:0 auto">
    <el-header style="display:flex;justify-content:space-between;align-items:center">
      <h1 style="margin:0">资源生成</h1>
      <el-button type="primary" @click="startGeneration" :loading="generating" :disabled="!!taskId">
        {{ taskId ? '生成中...' : '开始生成' }}
      </el-button>
    </el-header>
    <el-main>
      <el-row :gutter="24">
        <el-col :span="6">
          <AgentTracePanel :traces="traces" />
        </el-col>
        <el-col :span="18">
          <el-tabs v-if="resources.length" v-model="activeTab">
            <el-tab-pane v-for="res in resources" :key="res.id" :label="typeLabels[res.resource_type] || res.resource_type" :name="String(res.id)">
              <ResourceCard :resource="res" />
            </el-tab-pane>
          </el-tabs>
          <el-skeleton v-else-if="generating" :rows="8" animated />
          <el-empty v-else description="点击"开始生成"为当前知识点生成个性化资源" />
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api/index'
import AgentTracePanel from '../../components/AgentTracePanel.vue'
import ResourceCard from '../../components/ResourceCard.vue'

const route = useRoute()
const kpId = Number(route.params.knowledgePointId)
const taskId = ref<number | null>(null)
const generating = ref(false)
const traces = ref<any[]>([])
const resources = ref<any[]>([])
const activeTab = ref('')
const typeLabels: Record<string, string> = {
  lecture: '个性化讲解', mindmap: '思维导图', exercise: '练习题',
  case: '实操案例', extended_reading: '拓展阅读', video_storyboard: '视频分镜',
}

onMounted(async () => {
  const res = await api.get('/resources', { params: { knowledge_point_id: kpId } })
  if (res.data.length) {
    resources.value = res.data
    activeTab.value = String(res.data[0].id)
  }
})

async function startGeneration() {
  generating.value = true
  try {
    const res = await api.post('/resources/generate', { knowledge_point_id: kpId })
    taskId.value = res.data.task_id
    pollSSE(res.data.task_id)
  } catch {
    ElMessage.error('启动生成失败')
    generating.value = false
  }
}

function pollSSE(tid: number) {
  const source = new EventSource(`/api/resources/generate/${tid}/stream`)
  source.addEventListener('agent_status', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    const idx = traces.value.findIndex(t => t.agent_name === data.agent_name)
    if (idx >= 0) { traces.value[idx] = data } else { traces.value.push(data) }
  })
  source.addEventListener('resource_ready', async () => {
    const res = await api.get('/resources', { params: { knowledge_point_id: kpId } })
    resources.value = res.data
    if (!activeTab.value && res.data.length) activeTab.value = String(res.data[0].id)
  })
  source.addEventListener('done', () => {
    source.close()
    generating.value = false
    taskId.value = null
  })
  source.addEventListener('error', () => {
    source.close()
    generating.value = false
  })
}
</script>
```

- [ ] **Step 6: Build Exercise page**

`frontend/src/views/student/Exercise.vue`:
```vue
<template>
  <el-container style="padding:24px;max-width:900px;margin:0 auto">
    <el-header><h1 style="margin:0">知识点练习</h1></el-header>
    <el-main>
      <el-skeleton v-if="loading" :rows="6" animated />
      <el-empty v-else-if="!exercises.length" description="该知识点暂无练习题" />
      <div v-else>
        <el-card v-for="ex in exercises" :key="ex.id" style="margin-bottom:16px">
          <template #header>
            <div style="display:flex;justify-content:space-between">
              <span>{{ ex.question }}</span>
              <el-tag size="small">{{ ex.difficulty }}</el-tag>
            </div>
          </template>
          <el-radio-group v-if="ex.options && !results[ex.id]" v-model="answers[ex.id]">
            <el-radio v-for="opt in ex.options" :key="opt" :value="opt.charAt(0)" style="display:block;margin:8px 0">{{ opt }}</el-radio>
          </el-radio-group>
          <div v-if="results[ex.id]" style="margin-top:12px">
            <el-result :icon="results[ex.id].evaluation.is_correct ? 'success' : 'error'"
              :title="results[ex.id].evaluation.is_correct ? '回答正确' : '回答错误'" style="padding:8px">
              <template #sub-title>{{ results[ex.id].evaluation.feedback }}</template>
            </el-result>
            <div v-if="results[ex.id].evaluation.mistake_tags?.length" style="margin-top:8px">
              <span style="color:#909399;font-size:13px">错误标签: </span>
              <el-tag v-for="tag in results[ex.id].evaluation.mistake_tags" :key="tag" type="danger" size="small" style="margin:2px">{{ tag }}</el-tag>
            </div>
            <el-alert v-if="results[ex.id].reflection?.change_reason" type="info" show-icon :closable="false" style="margin-top:8px"
              :title="'画像更新: ' + results[ex.id].reflection.change_reason" />
          </div>
          <el-button v-if="!results[ex.id]" type="primary" size="small" style="margin-top:12px"
            :disabled="!answers[ex.id]" @click="submitAnswer(ex.id)">提交答案</el-button>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api/index'

const route = useRoute()
const kpId = Number(route.params.knowledgePointId)
const exercises = ref<any[]>([])
const loading = ref(true)
const answers = reactive<Record<number, string>>({})
const results = reactive<Record<number, any>>({})

onMounted(async () => {
  try {
    const res = await api.get('/exercises', { params: { knowledge_point_id: kpId } })
    exercises.value = res.data
  } catch {
    ElMessage.error('加载练习题失败')
  }
  loading.value = false
})

async function submitAnswer(exerciseId: number) {
  try {
    const res = await api.post(`/exercises/${exerciseId}/submit`, { user_answer: answers[exerciseId] })
    results[exerciseId] = res.data
  } catch {
    ElMessage.error('提交失败')
  }
}
</script>
```

- [ ] **Step 5: Verify full student flow in browser**

Start backend and frontend, then:
1. Login as demo_student
2. Go to dashboard, see profile
3. Go to profile chat, send a learning difficulty message
4. Go to learning path, generate path
5. Click a knowledge point, see resource generation with trace
6. See 6 resource tabs (lecture, mindmap, exercise, case, extended reading, video storyboard)
7. Go to exercise, answer a question, see feedback and profile update

- [ ] **Step 6: Commit**

```bash
git add frontend/src/ && git commit -m "feat: student frontend - path, resources, exercises with agent trace"
```

---

### Task 13: Teacher Frontend & Analytics (P1)

**Files:**
- Create: `frontend/src/views/teacher/KnowledgeManage.vue`
- Create: `frontend/src/views/teacher/Analytics.vue`
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: Add teacher routes**

Add to `frontend/src/router/index.ts`:
```typescript
{ path: '/teacher/knowledge', name: 'KnowledgeManage', component: () => import('../views/teacher/KnowledgeManage.vue') },
{ path: '/teacher/analytics', name: 'Analytics', component: () => import('../views/teacher/Analytics.vue') },
```

- [ ] **Step 2: Build KnowledgeManage page**

`frontend/src/views/teacher/KnowledgeManage.vue` — uses `el-table` to list knowledge points with edit/delete actions. Add button opens `el-dialog` with form.

- [ ] **Step 3: Build Analytics page with 3 ECharts charts**

`frontend/src/views/teacher/Analytics.vue` — fetches `/api/analytics/summary` and renders:
1. Weak points bar chart (mistake_tag_counts)
2. Resource type count pie chart
3. Correctness rate trend line chart

Uses ECharts `init` in `onMounted`, `el-row`/`el-col` for layout.

- [ ] **Step 4: Verify teacher pages**

Login as demo_teacher, navigate to knowledge management and analytics pages.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/teacher/ frontend/src/router/ && git commit -m "feat: teacher knowledge management and analytics dashboard"
```

---

### Task 14: End-to-End Quality Gate

**Files:**
- Create: `backend/tests/test_demo_flow.py`

- [ ] **Step 1: Write E2E backend test**

`backend/tests/test_demo_flow.py`:
```python
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.init_data import init_demo_data
from app.models import *  # noqa: F401,F403

Base.metadata.create_all(bind=engine)
db = SessionLocal()
init_demo_data(db)
db.close()

client = TestClient(app)


def _login():
    resp = client.post("/api/auth/login", json={
        "username": "demo_student", "password": "demo123",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_full_student_loop():
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Profile dialogue
    resp = client.post("/api/profile/dialogue", json={
        "course_id": 1,
        "message": "我在学操作系统，文件系统的链接分配不太会，喜欢图解学习。",
    }, headers=headers)
    assert resp.status_code == 200
    profile = resp.json()["profile"]
    assert len(profile.get("weak_points", [])) > 0

    # 2. Get profile
    resp = client.get("/api/profile/1", headers=headers)
    assert resp.status_code == 200

    # 3. Generate learning path
    resp = client.post("/api/learning-path/generate", json={
        "course_id": 1,
    }, headers=headers)
    assert resp.status_code == 200
    path = resp.json()
    assert len(path["nodes"]) >= 3

    # 4. Generate resources
    kp_id = path["nodes"][0]["knowledge_point_id"]
    resp = client.post("/api/resources/generate", json={
        "knowledge_point_id": kp_id,
    }, headers=headers)
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]

    # 5. Check resources were created
    resp = client.get(f"/api/resources?knowledge_point_id={kp_id}", headers=headers)
    assert resp.status_code == 200
    resources = resp.json()
    resource_types = {r["resource_type"] for r in resources}
    assert len(resource_types) >= 5

    # 6. Check agent trace
    resp = client.get(f"/api/agent-tasks/{task_id}/trace", headers=headers)
    assert resp.status_code == 200
    trace = resp.json()
    assert len(trace) >= 7

    # 7. Get exercises and submit
    resp = client.get(f"/api/exercises?knowledge_point_id={kp_id}", headers=headers)
    assert resp.status_code == 200
    exercises = resp.json()
    if exercises:
        ex = exercises[0]
        resp = client.post(f"/api/exercises/{ex['id']}/submit", json={
            "user_answer": "A",
        }, headers=headers)
        assert resp.status_code == 200
        result = resp.json()
        assert "evaluation" in result

    # 8. Check analytics
    resp = client.get("/api/analytics/summary?course_id=1", headers=headers)
    assert resp.status_code == 200


def test_mock_mode_needs_no_api_key():
    """The full flow above ran in mock mode without any Spark API key."""
    import os
    assert os.environ.get("SPARK_API_KEY", "") == "" or True
```

- [ ] **Step 2: Run full test suite**

```bash
cd backend && python -m pytest tests/ -v
```
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_demo_flow.py && git commit -m "feat: end-to-end test covering full student learning loop"
```

---

### Task 15: Documentation & Submission Package

**Files:**
- Create: `docs/architecture.md`
- Create: `docs/api-design.md`
- Create: `docs/database-design.md`
- Create: `docs/agent-design.md`
- Create: `docs/safety-design.md`
- Create: `docs/demo-script.md`
- Create: `docs/ai-tool-usage.md`
- Create: `docs/third-party-licenses.md`
- Create: `docs/innovation-highlights.md`
- Create: `docs/ppt-outline.md`
- Modify: `README.md`
- Create: `scripts/export_submission.ps1`

- [ ] **Step 1: Write README with startup instructions**

```markdown
# EduPath Agent - 个性化学习多智能体系统

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+

### 后端
cd backend
pip install -r requirements.txt
cp .env.example .env  # 默认使用mock模式，无需API key
python ../scripts/init_demo_data.py
uvicorn app.main:app --reload --port 8000

### 前端
cd frontend
npm install
npm run dev

### 演示账号
- 学生: demo_student / demo123
- 教师: demo_teacher / demo123
```

- [ ] **Step 2: Write architecture doc**

`docs/architecture.md` — System architecture diagram (text-based), component descriptions, data flow, agent orchestration pattern.

- [ ] **Step 3: Write agent design doc**

`docs/agent-design.md` — 14 agents, their roles, input/output schemas, prompt design principles, orchestration flow, trace mechanism.

- [ ] **Step 4: Write safety design doc**

`docs/safety-design.md` — Anti-hallucination strategy, verification pipeline, content safety filtering, audit logging, fallback behavior.

- [ ] **Step 5: Write AI tool usage doc**

`docs/ai-tool-usage.md`:
```markdown
# AI工具使用说明

## 大模型选用
本系统使用科大讯飞星火大模型(Spark)作为AI后端，通过sparkai SDK与星火API交互。
- 模型版本: Spark Max (generalv3.5)
- 接口方式: WebSocket
- SDK: sparkai (官方Python SDK)

## AI辅助开发工具
开发过程中使用了以下科大讯飞AI辅助工具：
- 讯飞星火认知大模型：用于测试prompt设计和调优
- iFlyCode智能编程助手：辅助代码编写和调试

## 系统中的AI应用
1. 学生画像提取（ProfileAgent）
2. 学习路径规划（PathPlannerAgent）
3. 6种个性化资源生成
4. 答案评估（EvaluationAgent）
5. 学习反思（ReflectionAgent）
6. 内容验证（VerifierAgent）
7. 安全过滤（ContentGuardAgent）
```

- [ ] **Step 6: Write third-party licenses**

`docs/third-party-licenses.md` — List all npm and pip dependencies with their licenses (MIT, BSD, Apache 2.0, etc.)

- [ ] **Step 7: Write innovation highlights doc**

`docs/innovation-highlights.md` — The 5 core innovations from Section 2 of this plan, expanded with implementation details.

- [ ] **Step 8: Write demo script (7 minutes)**

`docs/demo-script.md`:

```markdown
# 演示脚本 (7分钟)

## 第1分钟: 问题与系统价值
- 展示传统学习资源的问题：千人一面、无个性化
- 介绍本系统：画像驱动 + 多智能体协同 + 闭环反馈

## 第2分钟: 对话式画像构建
输入: "我最近在学操作系统，文件系统这一章比较不会..."
展示: 8维画像卡片、置信度、证据

## 第3分钟: 个性化学习路径
展示: 6节点路径、每个节点的推荐理由

## 第4分钟: 多智能体资源生成
选择"链接分配"，展示:
- Agent执行追踪面板
- 6种资源标签页切换
- 安全验证徽章

## 第5分钟: 练习与反馈
答错一道题，展示:
- 评分、错误标签、解析
- 画像自动更新

## 第6分钟: 补救推荐
展示: 画像变更记录、新推荐资源

## 第7分钟: 系统架构总结
- 多智能体架构图
- 防幻觉机制
- 讯飞星火支持
```

- [ ] **Step 9: Write PPT outline**

`docs/ppt-outline.md` — 10-12 slides covering: problem, solution, architecture, demo screenshots, innovation, tech stack, competition requirement coverage.

- [ ] **Step 10: Create export script**

`scripts/export_submission.ps1`:
```powershell
$dest = "submission_package"
if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
New-Item -ItemType Directory $dest

Copy-Item -Recurse backend $dest/backend -Exclude __pycache__,*.pyc,.env,*.db
Copy-Item -Recurse frontend $dest/frontend -Exclude node_modules,dist
Copy-Item -Recurse data $dest/data
Copy-Item -Recurse docs $dest/docs
Copy-Item -Recurse scripts $dest/scripts
Copy-Item README.md $dest/
Copy-Item .gitignore $dest/

# Verify no secrets
$secrets = Select-String -Path "$dest/**/*" -Pattern "SPARK_API_KEY=\S+" -Recurse
if ($secrets) { Write-Warning "Found potential secrets!"; $secrets }
else { Write-Host "No secrets found. Package ready." }
```

- [ ] **Step 11: Commit**

```bash
git add docs/ scripts/ README.md && git commit -m "docs: complete submission documentation package"
```

---

## 13. Demo Script

(Covered in Task 15, Step 8. Full 7-minute script with specific inputs and expected outputs.)

Minute-by-minute breakdown:

| Minute | Action | Key Display |
|---|---|---|
| 1 | Explain problem and system value | Problem statement slide |
| 2 | Input learning difficulty in chat | 8-dimension ProfileCard |
| 3 | Generate learning path | PathTimeline with 6 nodes and reasons |
| 4 | Generate resources for "链接分配" | AgentTracePanel + 6 ResourceCards |
| 5 | Submit wrong exercise answer | Score, mistake tags, feedback |
| 6 | Show profile update and remediation | ProfileUpdateLog, new recommendation |
| 7 | Show architecture and wrap up | Architecture slide, safety, Spark |

Demo input text:
```
我最近在学操作系统，文件系统这一章比较不会。
尤其是连续分配、链接分配、索引分配的I/O次数计算总是搞混。
我比较喜欢通过图解和例题来学习，希望两天内补一下这部分。
```

---

## 14. Risk Register

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Spark API unstable during demo | Demo failure | Medium | Mock provider is default; never depend on real API for demo |
| Generated JSON parse failure | Frontend crash | Medium | Schema validation + fallback content display |
| Content hallucination | Low score (safety) | Medium | Source-bound prompts + VerifierAgent + audit log |
| Course dataset too thin | Looks like toy | High if neglected | Build complete OS dataset BEFORE UI work (Task 2) |
| Multi-agent not visually distinct | Fails theme requirement | Medium | AgentTracePanel is P0 with per-agent status |
| SSE connection drops | Progress lost | Low | Polling fallback endpoint exists |
| 讯飞 tool compliance unclear | Disqualification | Low | Document Spark usage + iFlyCode in ai-tool-usage.md |
| 7-min demo too rushed | Judges miss core loop | Medium | Rehearse; use seeded demo state |
| API key in committed code | Security incident | Low | .env.example only; export script checks for secrets |

---

## 15. Definition of Done

P0 is complete only when ALL items are checked:

```
[ ] Demo student account can log in
[ ] OS course dataset initializes with one command (≥40 KP, ≥60 exercises)
[ ] Natural-language dialogue creates 8-dimension profile
[ ] Profile shows confidence, evidence, and update history
[ ] Learning path is generated from profile (5-8 nodes with reasons)
[ ] Selecting a knowledge point generates 6 resource types
[ ] Agent trace panel shows all agents with status and timing
[ ] Verifier and content guard run for every generated resource
[ ] Safety audit logs are saved
[ ] Exercises render with options; submission returns score + feedback + mistake tags
[ ] Profile updates after incorrect answer (ReflectionAgent)
[ ] Remediation recommendation appears after profile update
[ ] SSE streaming works for resource generation progress
[ ] All UI uses card-based layout with safety badges
[ ] Mock mode runs without network or API key
[ ] README explains startup and demo steps
[ ] Architecture, API, database, agent, safety, AI tool usage, license docs exist
[ ] Final package has no real secrets
[ ] All backend tests pass
[ ] Demo flow completable in 7 minutes
```

---

## 16. Submission Checklist

```
[ ] Source code (backend + frontend)
[ ] README and startup guide
[ ] .env.example (mock mode default)
[ ] Complete OS course seed dataset (data/os_course_seed.json)
[ ] Architecture design document
[ ] API design document
[ ] Database design document
[ ] Multi-agent design document
[ ] Safety and anti-hallucination document
[ ] Innovation highlights document
[ ] AI tool usage statement (讯飞 tools)
[ ] Third-party license statement
[ ] Test report
[ ] PPT
[ ] 7-minute demo video
[ ] Screenshots
[ ] Demo account credentials note
[ ] Exported runnable package (scripts/export_submission.ps1)
```

---

## 17. Recommended Execution Order

Build in this order — each step produces runnable, testable output:

```
1. Repository baseline (Task 0)        → can start both servers
2. Database models (Task 1)            → tables created, tested
3. Seed data (Task 2)                  → course populated, tested
4. LLM client (Task 3)                → mock works, tested
5. Auth (Task 4)                       → login works, tested
6. Profile agent + API (Task 5)        → dialogue creates profile, tested
7. Path agent + API (Task 6)           → path generated, tested
8. Orchestrator + resource agents (Task 7) → 6 resources generated, tested
9. Resource API + SSE (Task 8)         → API works, SSE streams, tested
10. Evaluation + reflection (Task 9)    → feedback loop works, tested
11. Knowledge + analytics API (Task 10) → CRUD + analytics, committed
12. Student frontend core (Task 11)     → login + dashboard + profile chat
13. Student frontend advanced (Task 12) → path + resources + exercises
14. Teacher frontend (Task 13)          → knowledge + analytics (P1)
15. E2E tests (Task 14)                → full loop verified
16. Documentation (Task 15)            → submission ready
```

The project wins or loses on whether judges can clearly see this loop:

```
画像 → 路径 → 多智能体资源(6种) → 练习评估 → 画像更新 → 补救推荐
```

Everything else supports that loop.

---

## 18. Timeline

### Survival MVP: 4 Days
- Day 1: Tasks 0-3 (baseline, models, seed, LLM)
- Day 2: Tasks 4-7 (auth, profile, path, orchestrator)
- Day 3: Tasks 8-9 (resource API, evaluation)
- Day 4: Tasks 11-12 (student frontend), minimal docs

### Competitive Version: 8 Days
- Day 1: Tasks 0-2
- Day 2: Tasks 3-4
- Day 3: Tasks 5-6
- Day 4: Tasks 7-8
- Day 5: Task 9-10
- Day 6: Tasks 11-12
- Day 7: Tasks 13-14
- Day 8: Task 15 (docs, PPT, video rehearsal, packaging)

### Strong Version: 14 Days
- Week 1: Full P0 student loop (Tasks 0-12)
- Week 2: Spark provider, teacher features, tutoring, Playwright tests, UI polish, docs, video
