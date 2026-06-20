# API 设计文档

## 概述

EduPath Agent 后端基于 FastAPI 构建，所有 API 端点统一挂载在 `/api` 前缀下。认证采用 JWT Bearer Token，除登录和注册外的所有端点均需携带 `Authorization: Bearer <token>` 请求头。

基础地址：`http://localhost:8000/api`

---

## 1. 认证模块 `/api/auth`

### 1.1 POST /api/auth/register

用户注册。

**请求体：**
```json
{
  "username": "string (3-64字符)",
  "password": "string (6-128字符)",
  "display_name": "string (可选)"
}
```

**响应体：**
```json
{
  "access_token": "string (JWT token)",
  "token_type": "bearer"
}
```

**说明：** 注册成功后直接返回 JWT token，无需再次登录。用户名不可重复，重复返回 400。

---

### 1.2 POST /api/auth/login

用户登录。

**请求体：**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应体：**
```json
{
  "access_token": "string (JWT token)",
  "token_type": "bearer"
}
```

**说明：** 用户名或密码错误返回 401。

---

### 1.3 GET /api/auth/me

获取当前登录用户信息。

**请求头：** `Authorization: Bearer <token>`

**响应体：**
```json
{
  "id": 1,
  "username": "demo_student",
  "role": "student",
  "display_name": "演示学生"
}
```

---

## 2. 学生画像模块 `/api/profile`

### 2.1 POST /api/profile/dialogue

通过对话消息提取/更新学生画像。ProfileAgent 会从自然语言中抽取 8 维画像信息。

**请求体：**
```json
{
  "course_id": 1,
  "message": "我是计算机科学大三学生，想在两天内复习文件系统..."
}
```

**响应体：**
```json
{
  "base_level": "medium",
  "learning_goal": "两天内掌握文件系统核心知识",
  "knowledge_state": "了解基础概念，需要加强分配方式和磁盘I/O计算",
  "weak_points": ["索引分配", "链接分配", "磁盘I/O计算"],
  "mastered_points": ["文件与目录"],
  "learning_preference": ["图解", "例题", "代码实操"],
  "cognitive_style": "visual",
  "time_budget": "2天，每天1小时",
  "confidence": "medium",
  "reply": "我已经根据你的描述更新了学习画像..."
}
```

---

### 2.2 GET /api/profile/{course_id}

获取当前用户在指定课程的学习画像。

**路径参数：** `course_id` (int) - 课程ID

**响应体：** 同 2.1 的响应体（不含 reply 字段）。若画像不存在，返回默认值。

---

### 2.3 GET /api/profile/{course_id}/logs

获取画像更新历史日志。

**路径参数：** `course_id` (int) - 课程ID

**响应体：**
```json
[
  {
    "old_profile_json": { "weak_points": [...], ... },
    "new_profile_json": { "weak_points": [...], ... },
    "evidence": "用户表达了明确目标和偏好的学习方式",
    "change_reason": "从对话中抽取学习目标、薄弱点与偏好",
    "updated_by": "ProfileAgent",
    "created_at": "2026-06-17 10:30:00"
  }
]
```

---

## 3. 学习路径模块 `/api/learning-path`

### 3.1 POST /api/learning-path/generate

根据学生画像生成个性化学习路径。PathPlannerAgent 根据画像中的薄弱点和学习目标动态排序知识点。

**请求体：**
```json
{
  "course_id": 1
}
```

**响应体：**
```json
{
  "id": 1,
  "course_id": 1,
  "status": "active",
  "nodes": [
    {
      "id": 1,
      "knowledge_point_id": 5,
      "knowledge_point_title": "文件系统基础",
      "sort_order": 1,
      "status": "pending",
      "reason": "巩固文件系统基础概念，为后续内容做铺垫"
    }
  ]
}
```

---

### 3.2 GET /api/learning-path/current

获取当前活跃的学习路径。

**查询参数：** `course_id` (int, 必填)

**响应体：** 同 3.1。若无活跃路径返回 404。

---

### 3.3 PUT /api/learning-path/nodes/{node_id}/status

更新学习路径节点状态。

**路径参数：** `node_id` (int) - 节点ID

**请求体：**
```json
{
  "status": "completed"
}
```

**响应体：**
```json
{
  "id": 1,
  "status": "completed"
}
```

**说明：** status 可选值：`pending`、`in_progress`、`completed`、`skipped`。

---

## 4. 资源生成模块 `/api/resources`

### 4.1 POST /api/resources/generate

触发多智能体资源生成流程。在后台线程中启动 Orchestrator，依次运行 KnowledgeAgent、5 个资源 Agent、VerifierAgent 和 ContentGuardAgent。

**请求体：**
```json
{
  "knowledge_point_id": 1
}
```

**响应体：**
```json
{
  "task_id": 1
}
```

**说明：** 返回任务 ID，前端可通过 SSE 端点实时监听生成进度。

---

### 4.2 GET /api/resources/generate/{task_id}/stream

SSE（Server-Sent Events）实时推送 Agent Trace 和资源生成事件。

**路径参数：** `task_id` (int) - 任务ID

**查询参数：** `token` (string, 必填) - JWT token（因 EventSource 不支持 Authorization 头）

**事件类型：**

- `agent_status`：Agent 执行状态更新
  ```json
  {"agent_name": "LectureAgent", "status": "success", "duration_ms": 150, "progress": 3, "total": 9}
  ```
- `resource_ready`：单个资源生成完成
  ```json
  {"resource_id": 1, "resource_type": "lecture", "confidence": "high"}
  ```
- `done`：整体任务完成
  ```json
  {"task_id": 1, "status": "completed", "total_resources": 6}
  ```
- `error`：错误事件

---

### 4.3 GET /api/resources

查询已生成的资源列表。

**查询参数：** `knowledge_point_id` (int, 必填)

**响应体：**
```json
[
  {
    "id": 1,
    "resource_type": "lecture",
    "title": "索引分配 - lecture",
    "content": "# 个性化讲解...",
    "content_format": "markdown",
    "confidence": "high",
    "warnings": [],
    "safety_status": "passed"
  }
]
```

---

### 4.4 GET /api/resources/{resource_id}

获取单个资源详情。

**路径参数：** `resource_id` (int)

**响应体：** 同 4.3 中的单个资源对象。

---

## 5. Agent 任务模块 `/api/agent-tasks`

### 5.1 GET /api/agent-tasks/{task_id}

获取 Agent 任务状态。

**路径参数：** `task_id` (int)

**响应体：**
```json
{
  "id": 1,
  "task_type": "resource_generation",
  "status": "completed",
  "progress": 9,
  "total_steps": 9,
  "error_message": ""
}
```

---

### 5.2 GET /api/agent-tasks/{task_id}/trace

获取任务的 Agent Trace 列表。

**路径参数：** `task_id` (int)

**响应体：**
```json
[
  {
    "agent_name": "KnowledgeAgent",
    "status": "success",
    "duration_ms": 50,
    "warnings": [],
    "confidence": "high"
  },
  {
    "agent_name": "LectureAgent",
    "status": "success",
    "duration_ms": 120,
    "warnings": [],
    "confidence": "high"
  }
]
```

---

## 6. 练习模块 `/api/exercises`

### 6.1 GET /api/exercises

获取指定知识点的练习题列表。

**查询参数：** `knowledge_point_id` (int, 必填)

**响应体：**
```json
[
  {
    "id": 1,
    "question_type": "choice",
    "difficulty": "medium",
    "question": "关于索引分配，下列说法最准确的是哪一项？",
    "options": ["A", "B", "C", "D"],
    "tags": ["索引分配"]
  }
]
```

---

### 6.2 POST /api/exercises/{exercise_id}/submit

提交答案并获取评估反馈。EvaluationAgent 评分后，若答错则 ReflectionAgent 会更新画像。

**路径参数：** `exercise_id` (int)

**请求体：**
```json
{
  "user_answer": "B"
}
```

**响应体：**
```json
{
  "evaluation": {
    "score": 1.0,
    "is_correct": true,
    "feedback": "回答正确",
    "mistake_tags": []
  },
  "reflection": {},
  "answer_record_id": 1
}
```

**说明：** 答错时 reflection 字段包含画像更新建议和补救资源推荐。

---

### 6.3 GET /api/exercises/answer-records

获取当前用户的答题记录（最近50条）。

**响应体：**
```json
[
  {
    "id": 1,
    "exercise_id": 1,
    "user_answer": "B",
    "is_correct": 1,
    "score": 1.0,
    "feedback": "回答正确",
    "mistake_tags": []
  }
]
```

---

## 7. 课程与知识点模块

### 7.1 GET /api/courses

获取课程列表。

**响应体：**
```json
[
  {
    "id": 1,
    "name": "操作系统",
    "description": "计算机操作系统课程"
  }
]
```

---

### 7.2 GET /api/courses/{course_id}/knowledge-points

获取课程下的所有知识点。

**路径参数：** `course_id` (int)

**响应体：**
```json
[
  {
    "id": 1,
    "chapter": "文件系统",
    "title": "索引分配",
    "summary": "用索引块保存文件数据块地址，支持随机访问。",
    "difficulty": "medium",
    "tags": ["file-system", "indexed-allocation"]
  }
]
```

---

### 7.3 POST /api/knowledge-points

创建知识点（仅教师角色）。

**请求体：**
```json
{
  "course_id": 1,
  "chapter": "文件系统",
  "title": "新知识点",
  "summary": "...",
  "key_content": "...",
  "difficulty": "medium",
  "tags": ["tag1"]
}
```

**响应体：**
```json
{
  "id": 42,
  "title": "新知识点"
}
```

**说明：** 非教师角色调用返回 403。

---

### 7.4 PUT /api/knowledge-points/{kp_id}

更新知识点（仅教师角色）。

**路径参数：** `kp_id` (int)

**请求体：** 同 7.3。

**响应体：** 同 7.3。

---

### 7.5 DELETE /api/knowledge-points/{kp_id}

删除知识点（仅教师角色）。

**路径参数：** `kp_id` (int)

**响应体：**
```json
{
  "deleted": 42
}
```

---

## 8. 学情分析模块 `/api/analytics`

### 8.1 GET /api/analytics/summary

获取学生个人学情摘要。

**查询参数：** `course_id` (int, 默认1)

**响应体：**
```json
{
  "total_answers": 10,
  "correct_answers": 7,
  "correctness_rate": 70.0,
  "total_resources": 12,
  "weak_points": ["索引分配", "链接分配"],
  "mastered_points": ["文件与目录"],
  "mistake_tag_counts": {"索引分配": 2, "磁盘I/O": 1}
}
```

---

### 8.2 GET /api/analytics/teacher-summary

获取教师端全局学情摘要（仅教师角色）。

**响应体：**
```json
{
  "total_students": 5,
  "total_answers": 50,
  "overall_correctness_rate": 65.0,
  "total_resources": 30,
  "resource_type_counts": {"lecture": 10, "mindmap": 5, ...},
  "top_mistake_tags": [{"tag": "索引分配", "count": 8}],
  "correctness_rate_trend": [
    {"date": "2026-06-17", "correctness_rate": 80.0, "total_answers": 5}
  ],
  "weak_points_summary": ["索引分配", "链接分配"]
}
```

---

## 9. 健康检查

### 9.1 GET /api/health

服务健康检查。

**响应体：**
```json
{
  "status": "ok"
}
```
