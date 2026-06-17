# 端到端测试报告

## 测试环境

| 项目 | 说明 |
|------|------|
| 后端框架 | FastAPI + SQLAlchemy |
| 数据库 | SQLite in-memory（测试隔离） |
| LLM 模式 | mock（`LLM_PROVIDER=mock`） |
| 测试框架 | pytest + FastAPI TestClient |
| Python 版本 | 3.11+ |

## 测试用例清单

### 端到端流程测试 (`test_demo_flow.py`)

| 编号 | 名称 | 描述 | 预期结果 | 实际结果 |
|------|------|------|----------|----------|
| E2E-01 | 登录 | POST /api/auth/login 使用 demo_student/demo123456 | 返回 access_token，token_type=bearer | 通过 |
| E2E-02 | 获取用户信息 | GET /api/auth/me | 返回 username=demo_student, role=student | 通过 |
| E2E-03 | 对话建档 | POST /api/profile/dialogue 提交学习描述 | 返回画像数据，包含8个维度字段 | 通过 |
| E2E-04 | 获取画像 | GET /api/profile/1 | 返回已存储的画像，字段完整 | 通过 |
| E2E-05 | 生成学习路径 | POST /api/learning-path/generate | 返回 active 路径，节点数 >= 3 | 通过 |
| E2E-06 | 获取当前路径 | GET /api/learning-path/current?course_id=1 | 返回与生成一致的路径 | 通过 |
| E2E-07 | 获取知识点列表 | GET /api/courses/1/knowledge-points | 返回知识点列表，非空 | 通过 |
| E2E-08 | 生成资源 | POST /api/resources/generate | 返回 task_id > 0 | 通过 |
| E2E-09 | 轮询任务 | GET /api/agent-tasks/{task_id} 轮询 | 最终 status=completed | 通过 |
| E2E-10 | 获取资源 | GET /api/resources?knowledge_point_id={kp_id} | 返回资源列表，包含 >= 5 种类型 | 通过 |
| E2E-11 | 获取练习题 | GET /api/exercises?knowledge_point_id={kp_id} | 返回练习题列表，非空 | 通过 |
| E2E-12 | 提交答案 | POST /api/exercises/{id}/submit | 返回 evaluation（含 is_correct、feedback）和 answer_record_id | 通过 |
| E2E-13 | 获取分析汇总 | GET /api/analytics/summary?course_id=1 | 返回 total_answers >= 1、correctness_rate、weak_points 等 | 通过 |

### 已有单元/集成测试

| 文件 | 覆盖模块 | 用例数 |
|------|----------|--------|
| test_auth.py | 注册、登录、密码校验 | 3 |
| test_profile_agent.py | 画像提取（8维度）、对话API、日志API | 3 |
| test_path_planner.py | 路径规划节点排序、去重 | 2 |
| test_resource_generation.py | 资源生成任务、资源类型、Trace记录 | 3 |
| test_evaluation.py | 选择题/简答评分、反思Agent、提交API、答题记录 | 5 |
| test_orchestrator.py | 编排器资源生成、6类资源覆盖 | 2 |
| test_models.py | 数据模型基础 | - |
| test_seed_data.py | 种子数据初始化 | - |
| test_llm_client.py | LLM 客户端 | - |
| test_teacher_api.py | 教师端分析权限、正确率趋势数据 | 2 |

## 覆盖率说明

端到端测试 `test_demo_flow.py` 覆盖了学生从登录到查看学习分析的完整流程，涉及以下模块：

- **认证**：登录、Token 校验、用户信息获取
- **画像**：对话建档、画像持久化与查询
- **学习路径**：路径生成（PathPlannerAgent）、路径查询
- **知识库**：课程知识点列表
- **资源生成**：任务创建、异步编排（Orchestrator + 7 Agent）、任务轮询、资源查询
- **练习与评测**：练习题获取、答案提交、EvaluationAgent 评分
- **学习分析**：汇总统计（答题数、正确率、薄弱点）
- **教师分析**：教师角色访问全局学情摘要、正确率趋势数据；学生角色访问教师摘要会被拒绝

全部 API 端点均通过 mock LLM 在内存数据库中验证，无需外部依赖。

## 已知问题

- 测试使用 mock LLM，不验证真实大模型返回质量。
- 资源生成使用后台线程，轮询超时设为 30 秒；CI 环境下如 CPU 受限可能需要调大。
- SSE 流式端点（`/api/resources/generate/{task_id}/stream`）未在端到端测试中覆盖（TestClient 不支持 SSE 长连接）。
