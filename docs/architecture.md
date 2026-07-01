# 系统架构设计

## 1. 整体架构

系统采用三层架构，前端负责展示和交互，后端负责业务逻辑和数据持久化，智能体协作层负责 LLM 驱动的个性化内容生成。

```
┌─────────────────────────────────────────────────────────────┐
│                     前端展示层 (Vue 3)                       │
│  Login / Dashboard / ProfileChat / LearningPath /           │
│  ResourceGenerate / Exercise / KnowledgeManage / Analytics  │
│  组件: ProfileCard, PathTimeline, AgentTracePanel,          │
│        ResourceCard, ExerciseCard, SafetyBadge,             │
│        MarkdownRenderer, MermaidRenderer                    │
├─────────────────────────────────────────────────────────────┤
│                   后端服务层 (FastAPI)                        │
│  API Router ─→ Service ─→ Agent ─→ LLM                     │
│  auth / profile / learning-path / resources /               │
│  exercises / knowledge / agent-tasks / analytics            │
├─────────────────────────────────────────────────────────────┤
│                 智能体协作层 (Orchestrator)                   │
│  ProfileAgent → KnowledgeAgent → PathPlannerAgent           │
│  LectureAgent / MindMapAgent / ExerciseAgent /              │
│  CaseAgent / ExtendedReadingAgent / VideoStoryboardAgent    │
│  → VerifierAgent → ContentGuardAgent                        │
│  EvaluationAgent → ReflectionAgent                          │
├─────────────────────────────────────────────────────────────┤
│                    数据层 (SQLAlchemy)                        │
│  MySQL / SQLite  +  os_course_seed.json 初始数据             │
└─────────────────────────────────────────────────────────────┘
```

## 2. 前端架构

### 2.1 技术栈

- **Vue 3** + Composition API + TypeScript
- **Vite** 构建工具
- **Pinia** 状态管理
- **Vue Router** 路由管理
- **Element Plus** UI 组件库
- **ECharts** 数据可视化
- **Mermaid.js** 思维导图渲染
- **markdown-it** Markdown 渲染
- **Axios** HTTP 请求

### 2.2 页面结构

```
src/
├── views/
│   ├── Login.vue              # 登录/注册页
│   ├── HomeView.vue           # 首页导航
│   └── student/
│   │   ├── Dashboard.vue      # 学生仪表盘
│   │   ├── ProfileChat.vue    # 对话建档
│   │   ├── LearningPath.vue   # 学习路径
│   │   ├── ResourceGenerate.vue  # 资源生成
│   │   └── Exercise.vue       # 练习与反馈
│   └── teacher/
│       ├── KnowledgeManage.vue  # 知识点管理
│       └── Analytics.vue      # 学情分析
├── components/
│   ├── ProfileCard.vue        # 画像卡片
│   ├── PathTimeline.vue       # 路径时间线
│   ├── AgentTracePanel.vue    # Agent 追踪面板
│   ├── ResourceCard.vue       # 资源展示卡片
│   ├── ExerciseCard.vue       # 练习卡片
│   ├── SafetyBadge.vue        # 安全/置信度标签
│   ├── MarkdownRenderer.vue   # Markdown 渲染器
│   └── MermaidRenderer.vue    # Mermaid 图表渲染器
├── stores/                    # Pinia 状态管理
├── api/                       # API 请求封装
└── router/                    # 路由配置
```

### 2.3 核心交互流程

1. 用户登录后进入 Dashboard，选择课程
2. 进入 ProfileChat 与系统对话，建立 8 维学习画像
3. 进入 LearningPath 查看系统规划的个性化学习路径
4. 选择知识点进入 ResourceGenerate，观看 Agent Trace 实时生成 6 种资源
5. 进入 Exercise 完成练习，获取评分和反馈
6. 系统自动更新画像并推送补救资源

## 3. 后端架构

### 3.1 技术栈

- **FastAPI** Web 框架
- **SQLAlchemy** ORM
- **Pydantic v2** 数据校验
- **MySQL / SQLite** 数据库
- **python-jose** JWT 认证
- **Passlib + bcrypt** 密码哈希
- **Uvicorn** ASGI 服务器

### 3.2 分层结构

```
backend/app/
├── main.py                # FastAPI 应用入口、CORS、Lifespan
├── core/
│   ├── config.py          # 全局配置 (BaseSettings)
│   ├── security.py        # JWT 生成/验证、密码哈希
│   └── deps.py            # 依赖注入 (get_current_user)
├── api/
│   ├── router.py          # 路由注册
│   ├── auth.py            # 认证 API
│   ├── profile.py         # 画像 API
│   ├── learning_path.py   # 学习路径 API
│   ├── resources.py       # 资源生成 API (含 SSE)
│   ├── exercises.py       # 练习 API
│   ├── knowledge.py       # 课程/知识点 API
│   ├── agent_tasks.py     # Agent 任务 API
│   └── analytics.py       # 学情分析 API
├── models/                # SQLAlchemy 模型 (14张表)
├── schemas/               # Pydantic 请求/响应模型
├── services/              # 业务逻辑层
│   ├── llm_client.py      # LLM 客户端抽象
│   ├── mock_llm.py        # Mock LLM 实现
│   ├── deepseek_llm.py    # DeepSeek LLM 实现
│   ├── spark_llm.py       # 讯飞星火 LLM 实现
│   ├── profile_service.py # 画像服务
│   ├── path_service.py    # 路径服务
│   ├── resource_service.py# 资源生成服务
│   └── evaluation_service.py # 评估服务
├── agents/                # 智能体实现
│   ├── base_agent.py      # Agent 基类
│   ├── orchestrator.py    # 编排器
│   └── ...                # 12个具体 Agent
├── db/                    # 数据库配置和初始化
└── prompts/               # Agent Prompt 模板
```

### 3.3 请求处理流程

```
HTTP 请求
  → FastAPI Router (路由分发)
    → Depends(get_current_user) (JWT 认证)
      → Service 层 (业务逻辑)
        → Agent 层 (LLM 调用)
          → LLMClient (mock / deepseek / spark)
        → Model 层 (数据库读写)
      → Pydantic Schema (响应序列化)
    → HTTP 响应
```

## 4. 数据流

系统核心数据流形成一个完整闭环：

```
用户输入（对话消息）
  → ProfileAgent 提取8维画像
    → PathPlannerAgent 规划个性化学习路径
      → 用户选择知识点
        → KnowledgeAgent 检索课程知识库
          → 6个资源 Agent 并行生成内容（ThreadPoolExecutor 并发执行）
            → VerifierAgent 事实一致性验证（与 ContentGuard 并行）
              → ContentGuardAgent 安全过滤（与 Verifier 并行）
                → 资源持久化 + SSE 推送前端
                  → 用户学习 + 练习
                    → EvaluationAgent 评分 + 错因分析
                      → ReflectionAgent 反思 + 画像更新
                        → 画像薄弱点变化时触发 PathPlannerAgent 重新规划学习路径（回到路径规划）
```

## 5. 技术选型理由

| 技术 | 选型理由 |
| --- | --- |
| Vue 3 | Composition API 提供良好的代码组织，国内生态活跃 |
| TypeScript | 类型安全，减少运行时错误 |
| Element Plus | 功能完善的企业级 Vue 3 组件库 |
| ECharts | 国内最主流的可视化库，适合展示学情分析 |
| Mermaid.js | 纯文本生成思维导图和流程图，LLM 可直接输出 |
| FastAPI | 高性能异步框架，自动生成 OpenAPI 文档，类型提示友好 |
| SQLAlchemy | Python 最成熟的 ORM，支持多种数据库后端 |
| Pydantic v2 | 数据校验性能优秀，与 FastAPI 深度集成 |
| JWT | 无状态认证，适合前后端分离架构 |
| Mock LLM | 确保离线演示和测试不依赖外部 API |
| SSE | 轻量级实时推送，比 WebSocket 更简单，适合单向 Agent Trace 推送 |
