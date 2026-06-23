# EduPath Agent - 个性化学习多智能体系统

EduPath Agent 是面向软件杯 A3 赛题的个性化学习资源生成系统。系统以"对话式学习画像 -> 个性化学习路径 -> 多智能体资源生成 -> 练习评估 -> 画像更新与补救推荐"为主线，覆盖学生端学习闭环和教师端知识库/学情分析。

## 核心能力

- 8 维对话式学习画像，包含置信度、证据和更新历史。
- 操作系统课程知识库，包含 8 章、40+ 知识点、60+ 练习和实操案例素材。
- 多智能体协同生成 6 类资源：讲义、思维导图、分层练习、实操案例、拓展阅读、视频分镜。
- 练习自动评分、错因标签、画像反思更新和学情分析。
- 内容验证、安全审计、Agent 执行轨迹和资源安全状态展示。
- AI 智能答疑助手，支持多轮对话。
- 教师端知识库文档导入（PDF/MD/TXT），支持 OCR。
- 支持 `mock`（离线演示）和 `spark`（科大讯飞 Spark 4.0Ultra）两种 LLM provider。

## 环境要求

- Python 3.11+
- Node.js 18+

数据库使用 SQLite，无需额外安装。

## 快速开始

### 1. 后端

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# 编辑 .env，填写讯飞 Spark API 凭证（或保持 LLM_PROVIDER=mock 离线演示）
python -m uvicorn app.main:app --reload --port 8000
```

首次启动时会自动创建数据库并导入演示数据。

### 2. 前端

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。

## 演示账号

- 学生：`demo_student` / `demo123456`
- 教师：`demo_teacher` / `teacher123456`

## 切换到真实 LLM

编辑 `backend/.env`，将 `LLM_PROVIDER` 改为 `spark`，并填写 `SPARK_APP_ID`、`SPARK_API_KEY`、`SPARK_API_SECRET`（从讯飞开放平台控制台获取）。

认证格式为 `Bearer {API_KEY}:{API_SECRET}`，使用 REST API（OpenAI 兼容格式）。

## 验证命令

```powershell
cd backend
python -m pytest -v
```

```powershell
cd frontend
npm run build
```

## 项目结构

```
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── agents/   # 8 个多智能体（画像、路径、知识、讲解、思维导图、练习、案例、视频分镜等）
│   │   ├── api/      # REST API 路由
│   │   ├── models/   # SQLAlchemy 数据模型
│   │   ├── prompts/  # Agent prompt 模板
│   │   └── services/ # LLM 客户端、资源生成等服务
│   └── tests/        # 单元测试
├── frontend/         # Vue 3 + TypeScript 前端
│   └── src/
│       ├── components/  # 通用组件（画像卡片、资源卡片、AI助手等）
│       └── views/       # 学生端 / 教师端页面
├── data/             # 知识库种子数据
├── docs/             # 配套文档
└── scripts/          # 工具脚本
```

## 文档

- 架构设计：[docs/architecture.md](docs/architecture.md)
- API 设计：[docs/api-design.md](docs/api-design.md)
- 数据库设计：[docs/database-design.md](docs/database-design.md)
- 智能体设计：[docs/agent-design.md](docs/agent-design.md)
- 安全设计：[docs/safety-design.md](docs/safety-design.md)
- 测试报告：[docs/test-report.md](docs/test-report.md)
- 演示脚本：[docs/demo-script.md](docs/demo-script.md)
- AI 工具使用说明：[docs/ai-tool-usage.md](docs/ai-tool-usage.md)
- 第三方许可：[docs/third-party-licenses.md](docs/third-party-licenses.md)

## 导出提交包

```powershell
.\scripts\export_submission.ps1
```

脚本会生成 `submission_package/`，并排除 `.env`、缓存、数据库文件、`node_modules` 和构建产物。
