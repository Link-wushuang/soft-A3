# A3 EduPath Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable competition MVP for A3, "基于大模型的个性化资源生成与学习多智能体系统开发", with a clear student learning loop: profile -> path -> multi-agent resources -> practice -> feedback -> profile update.

**Architecture:** The system uses Vue 3 as the frontend, FastAPI as the backend, SQLAlchemy with SQLite/MySQL for persistence, and an Agent Orchestrator that coordinates profile, retrieval, planning, generation, evaluation, reflection, and safety agents. Spark/讯飞星火 is the preferred real LLM provider, while a deterministic mock provider is mandatory for demos and CI.

**Tech Stack:** Vue 3, Vite, TypeScript, Element Plus, Markdown-it, Mermaid, ECharts, FastAPI, SQLAlchemy, Pydantic, SQLite/MySQL, Pytest, Playwright, Spark API/mock LLM.

---

## 0. Plan Status

This plan replaces the previous broad roadmap with a Superpowers-style execution plan. The key changes are:

- Make official 赛题 hard requirements explicit and testable.
- Move anti-hallucination, content safety, Spark compliance, progress tracking, and open-source license disclosure into the core scope.
- Keep the first delivery focused on a stable student learning loop.
- Treat teacher analytics, vector database, PDF upload, and real video generation as later improvements unless the MVP is already stable.

Official task page: <https://www.cnsoftbei.com/content-3-1286-1.html>

---

## 1. Competition Requirement Map

| Official requirement | Project response | Priority | Evidence in final submission |
| --- | --- | --- | --- |
| 对话式学习画像自主构建，不少于 6 个维度 | `ProfileAgent` extracts 8 structured dimensions with confidence and update history | P0 | Profile page, DB record, prompt, tests |
| 多智能体协同资源生成 | Agent trace shows retrieval, planning, 5 resource agents, verifier, safety guard | P0 | Resource page trace, architecture doc |
| 至少 5 种个性化资源 | Lecture, mind map, exercise set, lab/case, video storyboard/PPT outline | P0 | Resource tabs and persisted records |
| 个性化学习路径规划和资源推送 | `PathPlannerAgent` builds a dynamic path and recommends remediation after mistakes | P0 | Learning path page, feedback loop demo |
| 智能辅导加分项 | Context-aware tutoring answer with references and safety check | P1 | Tutoring panel if time permits |
| 学习效果评估加分项 | Practice scoring, mistake tags, mastery trend, profile updates | P0/P1 | Exercise page, analytics chart |
| 完整高校课程知识库/文档集 | One complete "操作系统" course package with chapters, knowledge points, exercises, labs, references | P0 | `data/os_course_seed.json`, docs |
| 防幻觉与内容安全 | `VerifierAgent` + `ContentGuardAgent` + source-bound generation + confidence labels | P0 | Safety logs, verifier output |
| 响应时间合理，避免白屏 | Agent task state, polling/SSE-ready API, progress panel, timeout fallback | P0 | UI trace and API tests |
| 开源协议和 AI 工具说明 | Third-party license file and AI tool usage statement | P0 | `docs/third-party-licenses.md`, docs |
| PPT、视频、源码、文档 | Final package checklist | P0 | Final submission folder |

---

## 2. Product Scope

### 2.1 P0: Must Ship

The P0 product must be demoable without network access through mock mode.

- Student login and demo account.
- Operating Systems course knowledge base.
- 8-dimension student profile extraction and persistence.
- Dynamic learning path generation.
- Multi-agent resource generation with visible trace.
- Five resource types:
  - Personalized lecture document.
  - Mermaid mind map.
  - Layered exercise set.
  - Lab/case material with code or pseudocode.
  - Video storyboard and PPT-style teaching outline.
- Exercise submission, scoring, mistake tagging, and feedback.
- Profile update based on learning behavior.
- Remediation resource recommendation.
- Content verification and safety filtering.
- Agent task progress tracking.
- README, design docs, test report, PPT outline, 7-minute demo script.

### 2.2 P1: Strong Competition Version

- Teacher knowledge base CRUD.
- Teacher analytics dashboard.
- Tutoring panel for follow-up questions.
- Learning effect report with trend chart.
- Spark API real provider integration.
- Playwright smoke tests for the main demo flow.

### 2.3 P2: Finals / Extension

- Chroma or other vector database.
- PDF courseware upload and parsing.
- Export learning report.
- Voice explanation.
- Real video generation.
- Teacher review workflow for generated content.
- Multi-course expansion.

### 2.4 Explicit Non-Goals For MVP

- Do not train a custom large model.
- Do not build a complex permission system.
- Do not depend on paid video generation for the first demo.
- Do not make teacher analytics block the student loop.
- Do not use a real API key in committed files.

---

## 3. Student Profile Specification

The profile must contain at least 6 dimensions. This project uses 8.

| Field | Meaning | Example |
| --- | --- | --- |
| `base_level` | Current foundation | `medium` |
| `learning_goal` | Goal and deadline | `two_day_file_system_review` |
| `knowledge_state` | Known and unknown concepts | `knows directory basics, weak on indexed allocation` |
| `weak_points` | Concrete weak knowledge tags | `["linked allocation pointer update", "disk I/O count"]` |
| `mastered_points` | Concepts repeatedly answered correctly | `["file directory basics"]` |
| `learning_preference` | Preferred resource style | `["diagram", "worked example", "step by step"]` |
| `cognitive_style` | Learning style inferred from conversation | `visual_practical` |
| `time_budget` | Available time and intensity | `2 days, 40 minutes per node` |

Every profile update must include:

- `confidence`: `low`, `medium`, or `high`.
- `evidence`: text snippet, exercise result, or behavior event.
- `updated_by`: `ProfileAgent` or `ReflectionAgent`.
- `profile_change_reason`: short explanation for the UI and audit log.

---

## 4. Course Knowledge Base Specification

The initial course is "操作系统". It must look like a complete course, not a tiny demo list.

### 4.1 Minimum Dataset

- 8 chapters.
- At least 36 knowledge points.
- At least 60 exercises.
- At least 8 lab/case materials.
- At least 20 common mistakes.
- At least 1 reference/source per chapter.

### 4.2 Recommended Chapters

1. 操作系统概述
2. 进程与线程
3. 进程同步与死锁
4. CPU 调度
5. 内存管理
6. 虚拟内存
7. 文件系统
8. 设备管理与磁盘调度

### 4.3 Knowledge Point Fields

```json
{
  "chapter": "文件系统",
  "title": "索引分配",
  "summary": "用索引块保存文件数据块地址，支持随机访问。",
  "key_content": "索引块、直接索引、多级索引、访问次数计算。",
  "common_mistakes": ["漏算索引块读取", "混淆链接分配和索引分配"],
  "example_question": "读取第 10 个逻辑块时需要几次磁盘 I/O？",
  "example_answer": "至少读取索引块，再读取目标数据块。",
  "difficulty": "medium",
  "tags": ["file-system", "indexed-allocation", "disk-io"],
  "sources": ["操作系统课程讲义：文件系统章节"]
}
```

---

## 5. Multi-Agent Architecture

### 5.1 Agents

| Agent | Responsibility | P0/P1 |
| --- | --- | --- |
| `ProfileAgent` | Extract profile from conversation and history | P0 |
| `KnowledgeAgent` | Retrieve course context from database | P0 |
| `PathPlannerAgent` | Build and update learning path | P0 |
| `LectureAgent` | Generate personalized Markdown lecture | P0 |
| `MindMapAgent` | Generate Mermaid mind map | P0 |
| `ExerciseAgent` | Generate layered exercise JSON | P0 |
| `CaseAgent` | Generate lab/case/code material | P0 |
| `VideoStoryboardAgent` | Generate storyboard and PPT-style teaching outline | P0 |
| `EvaluationAgent` | Score answers and identify mistake tags | P0 |
| `ReflectionAgent` | Update profile after evaluation | P0 |
| `VerifierAgent` | Check generated content against retrieved sources | P0 |
| `ContentGuardAgent` | Check unsafe, sensitive, or unsupported content | P0 |
| `TutorAgent` | Answer follow-up questions with references | P1 |
| `QualityAgent` | Score generated resource quality | P2 |

### 5.2 Resource Generation Flow

```text
Student selects knowledge point
  -> ProfileAgent reads current profile
  -> KnowledgeAgent retrieves source-bound course context
  -> LectureAgent / MindMapAgent / ExerciseAgent / CaseAgent / VideoStoryboardAgent generate resources
  -> VerifierAgent checks factual consistency and source coverage
  -> ContentGuardAgent checks safety and compliance
  -> ResourceService persists resources, trace, warnings, and confidence
  -> Frontend renders progress and resource tabs
```

### 5.3 Agent Trace Requirements

Each trace item must include:

- `agent_name`
- `status`: `pending`, `running`, `success`, `failed`, `fallback`
- `input_summary`
- `output_summary`
- `started_at`
- `finished_at`
- `duration_ms`
- `warnings`

The UI must show progress even when an agent is slow or fails. A failed non-critical resource agent should not break the whole page; it should show a fallback card.

---

## 6. Anti-Hallucination And Safety Design

This is P0 because the official task explicitly asks for it.

### 6.1 Generation Rules

- Resource agents receive retrieved course context and must stay within that context.
- Prompts require source-bound generation and a confidence field.
- Unknown facts must be expressed as "需要教师确认" instead of invented.
- Generated exercises must include answer and explanation.
- Generated content is rejected if JSON schema validation fails.

### 6.2 Verification Pipeline

```text
Generated resource
  -> schema validation
  -> source keyword coverage check
  -> VerifierAgent factual consistency review
  -> ContentGuardAgent safety review
  -> save with confidence/warnings
```

### 6.3 Safety Logs

Save every verification result to `safety_audit_log`.

Fields:

- `resource_id`
- `check_type`
- `status`
- `warnings`
- `blocked_reason`
- `created_at`

---

## 7. Data Model

### 7.1 Core Tables

- `user`: student/teacher/demo users.
- `course`: course metadata.
- `knowledge_point`: course knowledge points.
- `knowledge_source`: chapter references and source metadata.
- `student_profile`: current profile snapshot.
- `profile_update_log`: profile change history.
- `learning_path`: path header.
- `learning_path_node`: ordered learning steps.
- `agent_task`: one orchestration task.
- `agent_trace`: per-agent execution trace.
- `generated_resource`: generated resources.
- `exercise`: generated or seeded exercises.
- `answer_record`: submitted answers and scores.
- `safety_audit_log`: verifier and guard results.

### 7.2 Tables Missing From The Old Plan

The old plan mentioned `agent_task`, `course`, and `profile_update_log` but did not define them. They are now required.

```sql
CREATE TABLE course (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_task (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  task_type VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  progress INT DEFAULT 0,
  error_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profile_update_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  course_id BIGINT NOT NULL,
  old_profile_json JSON,
  new_profile_json JSON,
  evidence TEXT,
  profile_change_reason TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE safety_audit_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  resource_id BIGINT,
  check_type VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL,
  warnings JSON,
  blocked_reason TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. API Design

### 8.1 Auth

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/register` | Register |
| GET | `/api/auth/me` | Current user |

### 8.2 Profile

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/profile/dialogue` | Extract/update profile from natural language |
| GET | `/api/profile/{course_id}` | Get current profile |
| GET | `/api/profile/{course_id}/logs` | Get profile update history |

### 8.3 Course Knowledge

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/courses` | Course list |
| GET | `/api/knowledge-points?course_id=1` | Knowledge list |
| POST | `/api/knowledge-points` | Teacher creates point |
| PUT | `/api/knowledge-points/{id}` | Teacher updates point |
| DELETE | `/api/knowledge-points/{id}` | Teacher deletes point |

### 8.4 Learning Path

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/learning-path/generate` | Generate path |
| GET | `/api/learning-path/current?course_id=1` | Current path |
| PUT | `/api/learning-path/node/{id}/status` | Mark node status |

### 8.5 Resource Generation

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/resources/generate` | Start generation task |
| GET | `/api/agent-tasks/{task_id}` | Poll task progress |
| GET | `/api/agent-tasks/{task_id}/trace` | Get agent trace |
| GET | `/api/resources/history` | Resource history |
| GET | `/api/resources/{id}` | Resource detail |

### 8.6 Practice And Assessment

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/exercises/generate` | Generate exercises |
| POST | `/api/exercises/submit` | Submit answer and evaluate |
| GET | `/api/answer-records` | Answer history |
| GET | `/api/analytics/student-summary` | Student learning effect summary |

---

## 9. Frontend Pages

### 9.1 Student Pages

| Page | Path | Must show |
| --- | --- | --- |
| Login | `/login` | Demo account quick login |
| Student dashboard | `/student/dashboard` | Profile summary, weak points, current path |
| Profile chat | `/student/profile-chat` | Chat input, 8-dimension profile card |
| Learning path | `/student/learning-path` | Timeline, reasons, status, generate buttons |
| Resource generation | `/student/resources/generate/:id` | Agent trace, progress, 5 resource tabs, warnings |
| Exercise | `/student/exercise/:id` | Questions, score, mistake tags, profile changes |
| Tutor | `/student/tutor/:id` | Follow-up Q&A with source references, P1 |

### 9.2 Teacher Pages

| Page | Path | Priority |
| --- | --- | --- |
| Knowledge management | `/teacher/knowledge` | P1 |
| Analytics dashboard | `/teacher/analytics` | P1 |

### 9.3 UI Acceptance Rules

- No blank page during generation.
- Agent progress panel remains visible.
- Markdown and Mermaid render correctly or show fallback text.
- Safety warnings are visible but not noisy.
- Demo flow can be completed in 7 minutes.

---

## 10. File Structure

```text
edupath-agent/
├── README.md
├── docs/
│   ├── plan.md
│   ├── research.md
│   ├── architecture.md
│   ├── api-design.md
│   ├── database-design.md
│   ├── agent-design.md
│   ├── safety-design.md
│   ├── test-report.md
│   ├── demo-script.md
│   ├── ai-tool-usage.md
│   └── third-party-licenses.md
├── data/
│   └── os_course_seed.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   ├── agents/
│   │   └── prompts/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   └── views/
│   └── .env.example
└── scripts/
    ├── init-demo-data.py
    ├── run-smoke-tests.ps1
    └── export-submission-package.ps1
```

---

## 11. Implementation Tasks

### Task 0: Repository Baseline

**Files:**

- Create/modify: `README.md`
- Create: `backend/.env.example`
- Create: `frontend/.env.example`
- Create: `docs/ai-tool-usage.md`
- Create: `docs/third-party-licenses.md`

- [ ] Add startup instructions for backend and frontend.
- [ ] Add `.env.example` with `LLM_PROVIDER=mock`.
- [ ] Document that Spark/讯飞星火 is the preferred real provider.
- [ ] Document AI coding tool usage and avoid real API keys.
- [ ] Verification: backend and frontend can start in mock mode.

### Task 1: Database And Seed Data

**Files:**

- Create/modify: `backend/app/models/*.py`
- Create/modify: `backend/app/db/session.py`
- Create: `backend/app/db/init_data.py`
- Create: `data/os_course_seed.json`
- Create: `scripts/init-demo-data.py`
- Test: `backend/tests/test_seed_data.py`

- [ ] Define all core tables listed in section 7.
- [ ] Build the complete OS course seed dataset.
- [ ] Add one-command demo data initialization.
- [ ] Test that course, knowledge points, exercises, and demo users are created.
- [ ] Verification: `pytest backend/tests/test_seed_data.py -v`.

### Task 2: LLM Client And Mock Provider

**Files:**

- Create: `backend/app/services/llm_client.py`
- Create: `backend/app/services/mock_llm.py`
- Create: `backend/app/services/spark_llm.py`
- Test: `backend/tests/test_llm_client.py`

- [ ] Implement a provider interface: `chat(messages, temperature=0.3)`.
- [ ] Implement deterministic mock responses for the demo flow.
- [ ] Add Spark provider adapter behind environment variables.
- [ ] Ensure no agent calls vendor SDKs directly.
- [ ] Verification: `pytest backend/tests/test_llm_client.py -v`.

### Task 3: Profile And Learning Path

**Files:**

- Create: `backend/app/agents/profile_agent.py`
- Create: `backend/app/agents/path_planner_agent.py`
- Create: `backend/app/prompts/profile_agent.txt`
- Create: `backend/app/prompts/path_planner_agent.txt`
- Create/modify: `backend/app/services/profile_service.py`
- Create/modify: `backend/app/services/path_service.py`
- Create/modify: `backend/app/api/profile.py`
- Create/modify: `backend/app/api/learning_path.py`
- Test: `backend/tests/test_profile_path_flow.py`

- [ ] Extract the 8-dimension profile from a natural-language learning difficulty.
- [ ] Persist profile with confidence and evidence.
- [ ] Generate a 5-8 node path based on weak points and time budget.
- [ ] Persist the path and node reasons.
- [ ] Verification: `pytest backend/tests/test_profile_path_flow.py -v`.

### Task 4: Agent Orchestrator And Trace

**Files:**

- Create: `backend/app/agents/base_agent.py`
- Create: `backend/app/services/agent_task_service.py`
- Create: `backend/app/api/agent_tasks.py`
- Test: `backend/tests/test_agent_task_service.py`

- [ ] Define `AgentResult` and `AgentTraceItem`.
- [ ] Create `agent_task` records for long-running flows.
- [ ] Record per-agent state and duration.
- [ ] Add polling endpoint for task status and trace.
- [ ] Verification: `pytest backend/tests/test_agent_task_service.py -v`.

### Task 5: Five Resource Agents

**Files:**

- Create: `backend/app/agents/knowledge_agent.py`
- Create: `backend/app/agents/lecture_agent.py`
- Create: `backend/app/agents/mindmap_agent.py`
- Create: `backend/app/agents/exercise_agent.py`
- Create: `backend/app/agents/case_agent.py`
- Create: `backend/app/agents/video_storyboard_agent.py`
- Create/modify: `backend/app/services/resource_service.py`
- Create/modify: `backend/app/api/resources.py`
- Test: `backend/tests/test_resource_generation.py`

- [ ] Retrieve source-bound knowledge context.
- [ ] Generate Markdown lecture.
- [ ] Generate Mermaid mind map.
- [ ] Generate layered exercises.
- [ ] Generate lab/case material.
- [ ] Generate storyboard and PPT-style outline.
- [ ] Persist resources and trace.
- [ ] Verification: `pytest backend/tests/test_resource_generation.py -v`.

### Task 6: Verification And Content Safety

**Files:**

- Create: `backend/app/agents/verifier_agent.py`
- Create: `backend/app/agents/content_guard_agent.py`
- Create: `backend/app/services/safety_service.py`
- Create: `backend/app/prompts/verifier_agent.txt`
- Create: `backend/app/prompts/content_guard_agent.txt`
- Test: `backend/tests/test_safety_service.py`

- [ ] Validate generated JSON and Mermaid output.
- [ ] Check whether resource content is grounded in retrieved source context.
- [ ] Add safety status and warnings to resource responses.
- [ ] Save safety audit logs.
- [ ] Provide fallback content when a resource is blocked.
- [ ] Verification: `pytest backend/tests/test_safety_service.py -v`.

### Task 7: Practice, Evaluation, And Reflection

**Files:**

- Create: `backend/app/agents/evaluation_agent.py`
- Create: `backend/app/agents/reflection_agent.py`
- Create: `backend/app/prompts/evaluation_agent.txt`
- Create: `backend/app/prompts/reflection_agent.txt`
- Create/modify: `backend/app/services/evaluation_service.py`
- Create/modify: `backend/app/api/exercises.py`
- Test: `backend/tests/test_practice_feedback_loop.py`

- [ ] Score objective questions locally.
- [ ] Score short answers with mock/LLM evaluation.
- [ ] Save answer records.
- [ ] Update weak and mastered points.
- [ ] Save profile update logs.
- [ ] Return remediation recommendation.
- [ ] Verification: `pytest backend/tests/test_practice_feedback_loop.py -v`.

### Task 8: Student Frontend

**Files:**

- Create/modify: `frontend/src/router/index.ts`
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/student/Dashboard.vue`
- Create: `frontend/src/views/student/ProfileChat.vue`
- Create: `frontend/src/views/student/LearningPath.vue`
- Create: `frontend/src/views/student/ResourceGenerate.vue`
- Create: `frontend/src/views/student/Exercise.vue`
- Create: `frontend/src/components/ProfileCard.vue`
- Create: `frontend/src/components/AgentTracePanel.vue`
- Create: `frontend/src/components/MarkdownRenderer.vue`
- Create: `frontend/src/components/MermaidRenderer.vue`
- Create: `frontend/src/api/*.ts`

- [ ] Add demo login.
- [ ] Render profile card with 8 dimensions.
- [ ] Render learning path timeline.
- [ ] Render generation progress and 5 resource tabs.
- [ ] Render safety warnings and fallback content.
- [ ] Render exercise scoring and profile change.
- [ ] Verification: run frontend dev server and complete the demo flow manually.

### Task 9: Teacher Frontend And Analytics

**Files:**

- Create: `frontend/src/views/teacher/KnowledgeManage.vue`
- Create: `frontend/src/views/teacher/Analytics.vue`
- Create/modify: `backend/app/api/knowledge.py`
- Create/modify: `backend/app/api/analytics.py`

- [ ] Build knowledge point list and edit form.
- [ ] Build at least 3 charts: weak points, resource count, correctness rate.
- [ ] Use real records when present and seed data when not.
- [ ] Verification: teacher demo account can view knowledge and charts.

### Task 10: End-To-End Quality Gate

**Files:**

- Create: `backend/tests/test_demo_flow.py`
- Create: `frontend/tests/demo-flow.spec.ts` if Playwright is added.
- Create: `docs/test-report.md`
- Create: `scripts/run-smoke-tests.ps1`

- [ ] Test the full backend flow: login -> profile -> path -> resources -> exercise -> reflection.
- [ ] Smoke test frontend pages for no blank screens.
- [ ] Record manual QA results and screenshots.
- [ ] Verification: backend tests pass and frontend demo flow works.

### Task 11: Submission Materials

**Files:**

- Create/modify: `docs/research.md`
- Create/modify: `docs/architecture.md`
- Create/modify: `docs/api-design.md`
- Create/modify: `docs/database-design.md`
- Create/modify: `docs/agent-design.md`
- Create/modify: `docs/safety-design.md`
- Create/modify: `docs/demo-script.md`
- Create: `docs/ppt-outline.md`
- Create: `scripts/export-submission-package.ps1`

- [ ] Write user research and pain-point analysis.
- [ ] Write architecture, API, database, agent, and safety docs.
- [ ] Write 7-minute demo script.
- [ ] Write PPT outline around judging criteria.
- [ ] Export source, docs, screenshots, demo account notes, `.env.example`, and license docs.
- [ ] Verification: final package contains no real secrets and can be run from README.

---

## 12. Recommended Timeline

### Survival MVP: 3 Days

- Day 1: backend skeleton, seed data, mock LLM, profile, path.
- Day 2: resource generation, trace, frontend student pages.
- Day 3: practice feedback loop, safety fallback, demo script.

### Competitive Initial Version: 7 Days

- Day 1: repository baseline and dataset.
- Day 2: profile/path backend and tests.
- Day 3: resource agents and orchestration.
- Day 4: safety/verification and practice reflection.
- Day 5: student frontend complete.
- Day 6: teacher pages, analytics, QA.
- Day 7: docs, PPT, video rehearsal, packaging.

### Strong Version: 14 Days

- Week 1: P0 full student loop with mock mode.
- Week 2: Spark provider, teacher analytics, tutoring, Playwright tests, better visuals, polished docs/video.

---

## 13. Demo Script

The final video must be under 7 minutes.

### Minute 1: Problem And System Value

- Explain that standard course resources do not adapt to student background, goals, weak points, or preferred learning style.
- Show that this system uses profile, course knowledge, multi-agent generation, and feedback loop.

### Minute 2: Dialogue Profile

Input:

```text
我最近在学操作系统，文件系统这一章比较不会。
尤其是连续分配、链接分配、索引分配的 I/O 次数计算总是搞混。
我比较喜欢通过图解和例题来学习，希望两天内补一下这部分。
```

Show:

- 8-dimension profile.
- Confidence and evidence.
- Weak points and time budget.

### Minute 3: Dynamic Learning Path

Show:

1. 文件系统基础
2. 文件目录与路径解析
3. 连续分配
4. 链接分配
5. 索引分配
6. 磁盘 I/O 综合题

Explain that path reasons come from profile and course knowledge.

### Minute 4: Multi-Agent Resource Generation

Select "链接分配".

Show trace:

- ProfileAgent
- KnowledgeAgent
- LectureAgent
- MindMapAgent
- ExerciseAgent
- CaseAgent
- VideoStoryboardAgent
- VerifierAgent
- ContentGuardAgent

Show five resource tabs and safety warnings if any.

### Minute 5: Practice And Feedback

Student answers one question incorrectly.

Show:

- Score.
- Specific mistake tags.
- Explanation.
- Recommended remediation.

### Minute 6: Profile Update And Resource Push

Show:

- `weak_points` changed.
- `profile_update_log` reason.
- New remediation node or recommended resource.

### Minute 7: Teacher/Docs/Wrap-Up

Show:

- Teacher knowledge base or analytics if ready.
- Final architecture slide.
- Anti-hallucination and mock/Spark support.
- Final statement: the system completes the personalized learning loop required by A3.

---

## 14. Risk Register

| Risk | Impact | Mitigation | Owner |
| --- | --- | --- | --- |
| Real LLM API unstable | Demo failure | Mock provider must be complete | AI/backend |
| Generated JSON invalid | Frontend breaks | Schema validation and fallback | Backend |
| Content hallucination | Low score / unsafe answer | Source-bound prompts, VerifierAgent, safety logs | AI/backend |
| Course data too thin | Looks like toy demo | Complete OS seed dataset before UI polish | All |
| Multi-agent not visible | Fails task theme | AgentTracePanel is P0 | Frontend |
| Teacher pages unfinished | Lower completeness | Student loop ships first, teacher pages P1 | Frontend |
| Video generation impossible | Missing multimodal signal | Use storyboard, PPT outline, Mermaid, lab code as concrete multimodal resources | AI/frontend |
| API key leak | Security issue | `.env.example`, secret scan, final package check | All |
| 7-minute demo too long | Judges miss core loop | Rehearse script and use seeded demo state | Docs/demo |

---

## 15. Definition Of Done

P0 is complete only when all items below are true:

```text
[ ] Student demo account can log in.
[ ] OS course dataset initializes with one command.
[ ] Natural-language dialogue creates an 8-dimension profile.
[ ] Learning path is generated from profile and knowledge points.
[ ] A selected knowledge point generates 5 resource types.
[ ] Agent trace shows multiple agents and progress states.
[ ] Verifier and content guard run for generated resources.
[ ] Exercise submission returns score, feedback, mistake tags.
[ ] Profile updates after practice.
[ ] Remediation resource or path update is shown.
[ ] Mock mode runs without network or API key.
[ ] README explains startup and demo steps.
[ ] Docs include architecture, API, database, agent, safety, AI tool usage, license notes.
[ ] Final package has no real secrets.
```

---

## 16. Final Submission Checklist

```text
[ ] Source code
[ ] README and startup guide
[ ] `.env.example`
[ ] Complete OS course seed dataset
[ ] System design document
[ ] API design document
[ ] Database design document
[ ] Multi-agent design document
[ ] Safety and anti-hallucination design document
[ ] User research / requirement analysis document
[ ] Test report
[ ] Third-party license statement
[ ] AI tool usage statement
[ ] PPT
[ ] 7-minute demo video
[ ] Screenshots
[ ] Demo account notes
[ ] Exported runnable package
```

---

## 17. Recommended Execution Order

Build in this order:

1. Dataset and mock mode.
2. Backend student loop.
3. Agent trace and five resources.
4. Safety verification.
5. Practice feedback and profile update.
6. Student frontend polish.
7. Teacher and analytics.
8. Docs, PPT, video.

The project wins or loses on whether the judges can clearly see this loop:

```text
画像 -> 路径 -> 多智能体资源 -> 练习评估 -> 画像更新 -> 补救推荐
```

Everything else should support that loop, not compete with it.
