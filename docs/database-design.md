# 数据库设计文档

## 1. 概述

系统使用 SQLAlchemy ORM 进行数据库操作，支持 MySQL 和 SQLite 两种后端。数据库包含 14 张表，覆盖用户管理、课程知识库、学生画像、学习路径、智能体任务、资源生成、练习评估和安全审计等核心领域。

应用启动时通过 `Base.metadata.create_all()` 自动建表，并执行 `init_demo_data()` 初始化演示数据。

## 2. ER 关系图

```
User (用户)
 ├──1:N── StudentProfile (学生画像)
 ├──1:N── ProfileUpdateLog (画像更新日志)
 ├──1:N── LearningPath (学习路径)
 ├──1:N── AgentTask (Agent任务)
 ├──1:N── GeneratedResource (生成资源)
 └──1:N── AnswerRecord (答题记录)

Course (课程)
 ├──1:N── KnowledgePoint (知识点)
 ├──1:N── KnowledgeSource (知识来源)
 ├──1:N── StudentProfile (学生画像)
 └──1:N── LearningPath (学习路径)

KnowledgePoint (知识点)
 ├──1:N── Exercise (练习题)
 ├──1:N── GeneratedResource (生成资源)
 └──1:N── LearningPathNode (路径节点)

LearningPath (学习路径)
 └──1:N── LearningPathNode (路径节点)

AgentTask (Agent任务)
 ├──1:N── AgentTrace (Agent追踪)
 └──1:N── GeneratedResource (生成资源)

GeneratedResource (生成资源)
 └──1:N── SafetyAuditLog (安全审计日志)

Exercise (练习题)
 └──1:N── AnswerRecord (答题记录)
```

## 3. 表结构详细说明

### 3.1 user — 用户表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 用户ID |
| username | String(64) | 唯一, 非空, 索引 | 用户名 |
| password_hash | String(256) | 非空 | bcrypt 哈希密码 |
| role | String(16) | 非空, 默认 "student" | 角色：student / teacher |
| display_name | String(64) | 默认 "" | 显示名称 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.2 course — 课程表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 课程ID |
| name | String(128) | 非空 | 课程名称 |
| description | Text | 默认 "" | 课程描述 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.3 knowledge_point — 知识点表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 知识点ID |
| course_id | Integer | 外键 course.id, 索引 | 所属课程 |
| chapter | String(128) | 非空 | 所属章节 |
| title | String(256) | 非空 | 知识点标题 |
| summary | Text | 默认 "" | 摘要 |
| key_content | Text | 默认 "" | 核心内容 |
| common_mistakes | JSON | 默认 [] | 常见误区列表 |
| example_question | Text | 默认 "" | 示例问题 |
| example_answer | Text | 默认 "" | 示例答案 |
| difficulty | String(16) | 默认 "medium" | 难度：easy/medium/hard |
| tags | JSON | 默认 [] | 标签列表 |
| sources | JSON | 默认 [] | 参考来源 |
| case_materials | Text | 默认 "" | 实操案例素材 |
| sort_order | Integer | 默认 0 | 排序序号 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.4 knowledge_source — 知识来源表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 来源ID |
| course_id | Integer | 外键 course.id, 索引 | 所属课程 |
| chapter | String(128) | 非空 | 对应章节 |
| source_name | String(256) | 非空 | 来源名称（教材/讲义） |
| source_url | String(512) | 默认 "" | 来源链接 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.5 student_profile — 学生画像表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 画像ID |
| user_id | Integer | 外键 user.id, 索引 | 用户ID |
| course_id | Integer | 外键 course.id, 索引 | 课程ID |
| base_level | String(16) | 默认 "medium" | 基础水平：low/medium/high |
| learning_goal | Text | 默认 "" | 学习目标 |
| knowledge_state | Text | 默认 "" | 知识状态描述 |
| weak_points | JSON | 默认 [] | 薄弱知识点列表 |
| mastered_points | JSON | 默认 [] | 已掌握知识点列表 |
| learning_preference | JSON | 默认 [] | 学习偏好列表 |
| cognitive_style | String(32) | 默认 "visual" | 认知风格 |
| time_budget | String(128) | 默认 "" | 时间预算 |
| confidence | String(16) | 默认 "low" | 置信度 |
| updated_at | DateTime | 自动更新 | 最后更新时间 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.6 profile_update_log — 画像更新日志表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 日志ID |
| user_id | Integer | 外键 user.id, 索引 | 用户ID |
| course_id | Integer | 外键 course.id | 课程ID |
| old_profile_json | JSON | 默认 {} | 更新前的画像快照 |
| new_profile_json | JSON | 默认 {} | 更新后的画像快照 |
| evidence | Text | 默认 "" | 更新依据 |
| change_reason | Text | 默认 "" | 变更原因 |
| updated_by | String(32) | 默认 "ProfileAgent" | 更新发起者 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.7 learning_path — 学习路径表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 路径ID |
| user_id | Integer | 外键 user.id, 索引 | 用户ID |
| course_id | Integer | 外键 course.id | 课程ID |
| status | String(16) | 默认 "active" | 状态：active/archived |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.8 learning_path_node — 学习路径节点表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 节点ID |
| path_id | Integer | 外键 learning_path.id, 索引 | 所属路径 |
| knowledge_point_id | Integer | 外键 knowledge_point.id | 关联知识点 |
| sort_order | Integer | 默认 0 | 排序序号 |
| status | String(16) | 默认 "pending" | 状态：pending/in_progress/completed/skipped |
| reason | Text | 默认 "" | 排序理由（Agent 生成） |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.9 agent_task — Agent 任务表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 任务ID |
| user_id | Integer | 外键 user.id, 索引 | 用户ID |
| task_type | String(64) | 非空 | 任务类型：resource_generation |
| status | String(32) | 非空, 默认 "pending" | 状态：pending/running/completed/failed |
| progress | Integer | 默认 0 | 当前进度 |
| total_steps | Integer | 默认 0 | 总步骤数 |
| error_message | Text | 默认 "" | 错误信息 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |
| updated_at | DateTime | 自动更新 | 最后更新时间 |

### 3.10 agent_trace — Agent 追踪表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 追踪ID |
| task_id | Integer | 外键 agent_task.id, 索引 | 所属任务 |
| agent_name | String(64) | 非空 | Agent 名称 |
| status | String(32) | 非空, 默认 "pending" | 状态：pending/running/success/failed |
| input_summary | Text | 默认 "" | 输入摘要 |
| output_summary | Text | 默认 "" | 输出摘要 |
| started_at | DateTime | 可空 | 开始时间 |
| finished_at | DateTime | 可空 | 结束时间 |
| duration_ms | Integer | 可空 | 耗时（毫秒） |
| warnings | JSON | 默认 [] | 警告列表 |
| confidence | String(16) | 可空 | 置信度 |

### 3.11 generated_resource — 生成资源表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 资源ID |
| task_id | Integer | 外键 agent_task.id, 可空, 索引 | 所属任务 |
| knowledge_point_id | Integer | 外键 knowledge_point.id, 索引 | 关联知识点 |
| user_id | Integer | 外键 user.id, 索引 | 用户ID |
| resource_type | String(32) | 非空 | 类型：lecture/mindmap/exercise/case/extended_reading/video_storyboard |
| title | String(256) | 默认 "" | 资源标题 |
| content | Text | 非空 | 资源内容（Markdown 或 JSON） |
| content_format | String(16) | 默认 "markdown" | 内容格式：markdown/json |
| confidence | String(16) | 默认 "medium" | 置信度：low/medium/high |
| warnings | JSON | 默认 [] | 警告列表 |
| safety_status | String(16) | 默认 "pending" | 安全状态：pending/passed/warning/blocked |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.12 exercise — 练习题表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 练习题ID |
| knowledge_point_id | Integer | 外键 knowledge_point.id, 索引 | 关联知识点 |
| question_type | String(32) | 非空, 默认 "choice" | 题型：choice/fill_blank/short_answer |
| difficulty | String(16) | 默认 "medium" | 难度 |
| question | Text | 非空 | 题目内容 |
| options | JSON | 可空 | 选项列表（选择题） |
| answer | Text | 非空 | 正确答案 |
| explanation | Text | 默认 "" | 答案解析 |
| tags | JSON | 默认 [] | 标签列表 |
| source | String(16) | 默认 "seed" | 来源：seed（初始数据）/ generated（Agent生成） |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.13 answer_record — 答题记录表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 记录ID |
| user_id | Integer | 外键 user.id, 索引 | 用户ID |
| exercise_id | Integer | 外键 exercise.id | 练习题ID |
| user_answer | Text | 非空 | 用户答案 |
| is_correct | Integer | 默认 0 | 是否正确（0/1） |
| score | Float | 默认 0.0 | 得分 |
| feedback | Text | 默认 "" | 反馈内容 |
| mistake_tags | JSON | 默认 [] | 错因标签 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

### 3.14 safety_audit_log — 安全审计日志表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | Integer | 主键, 自增 | 日志ID |
| resource_id | Integer | 外键 generated_resource.id, 可空, 索引 | 关联资源 |
| check_type | String(64) | 非空 | 检查类型：overall/factual_inconsistency/safety_blocked |
| status | String(32) | 非空 | 状态：passed/warning/blocked |
| details | Text | 默认 "" | 检查详情 |
| blocked_reason | Text | 可空 | 拦截原因 |
| created_at | DateTime | 服务器默认 now() | 创建时间 |

## 4. 索引设计

| 表名 | 索引字段 | 索引类型 | 用途 |
| --- | --- | --- | --- |
| user | username | UNIQUE | 用户名唯一约束和查询 |
| knowledge_point | course_id | 普通索引 | 按课程查询知识点 |
| knowledge_source | course_id | 普通索引 | 按课程查询知识来源 |
| student_profile | user_id | 普通索引 | 按用户查询画像 |
| student_profile | course_id | 普通索引 | 按课程查询画像 |
| profile_update_log | user_id | 普通索引 | 按用户查询更新日志 |
| learning_path | user_id | 普通索引 | 按用户查询学习路径 |
| learning_path_node | path_id | 普通索引 | 按路径查询节点 |
| agent_task | user_id | 普通索引 | 按用户查询任务 |
| agent_trace | task_id | 普通索引 | 按任务查询追踪 |
| generated_resource | task_id | 普通索引 | 按任务查询资源 |
| generated_resource | knowledge_point_id | 普通索引 | 按知识点查询资源 |
| generated_resource | user_id | 普通索引 | 按用户查询资源 |
| exercise | knowledge_point_id | 普通索引 | 按知识点查询练习题 |
| answer_record | user_id | 普通索引 | 按用户查询答题记录 |
| safety_audit_log | resource_id | 普通索引 | 按资源查询审计日志 |

## 5. 数据初始化

系统启动时执行 `init_demo_data()` 自动初始化以下数据：

1. **演示账户**：
   - `demo_student` / `demo123456`（学生角色）
   - `demo_teacher` / `teacher123456`（教师角色）

2. **操作系统课程**：从 `data/os_course_seed.json` 加载
   - 1 门课程
   - 8 个章节
   - 40+ 个知识点（含 summary、key_content、common_mistakes、tags 等完整字段）
   - 每章 1 个知识来源（教材/讲义）

3. **练习题**：根据知识点自动生成
   - 每个知识点生成 1 道简答题
   - 前 22 个知识点额外生成 1 道选择题
   - 共计 60+ 道练习题

初始化是幂等的：如果 `demo_student` 用户已存在，则跳过初始化。
