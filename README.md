# EduPath Agent - 个性化学习多智能体系统

EduPath Agent 是面向软件杯 A3 赛题的个性化学习资源生成系统。系统以“对话式学习画像 -> 个性化学习路径 -> 多智能体资源生成 -> 练习评估 -> 画像更新与补救推荐”为主线，覆盖学生端学习闭环和教师端知识库/学情分析。

## 核心能力

- 8 维对话式学习画像，包含置信度、证据和更新历史。
- 操作系统课程知识库，包含 8 章、40+ 知识点、60+ 练习和实操案例素材。
- 多智能体协同生成 6 类资源：讲义、思维导图、分层练习、实操案例、拓展阅读、视频分镜。
- 练习自动评分、错因标签、画像反思更新和学情分析。
- 内容验证、安全审计、Agent 执行轨迹和资源安全状态展示。
- 支持 `mock`、临时 `deepseek` 和最终提交用 `spark` 三种 LLM provider。

## 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+（本地或 Docker）

## 快速开始

### 1. 启动 MySQL

Docker 方式：

```powershell
docker run -d --name edupath-mysql -p 3306:3306 `
  -e MYSQL_ROOT_PASSWORD=root `
  -e MYSQL_DATABASE=edupath `
  mysql:8.0 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

本地 MySQL：

```sql
CREATE DATABASE IF NOT EXISTS edupath
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python ../scripts/init_demo_data.py
python -m uvicorn app.main:app --reload --port 8000
```

默认 `LLM_PROVIDER=mock`，不需要 API key。若演示真实模型，编辑 `backend/.env` 并切换到 `LLM_PROVIDER=spark`，填写科大讯飞 Spark 配置。

### 3. 前端

```powershell
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。

## 演示账号

- 学生：`demo_student` / `demo123456`
- 教师：`demo_teacher` / `teacher123456`

## 验证命令

```powershell
cd backend
python -m pytest -v
```

```powershell
cd frontend
npm audit --audit-level=high
npm run build
```

## 文档

- 架构设计：[docs/architecture.md](docs/architecture.md)
- API 设计：[docs/api-design.md](docs/api-design.md)
- 数据库设计：[docs/database-design.md](docs/database-design.md)
- 智能体设计：[docs/agent-design.md](docs/agent-design.md)
- 安全设计：[docs/safety-design.md](docs/safety-design.md)
- 演示脚本：[docs/demo-script.md](docs/demo-script.md)
- AI 工具使用说明：[docs/ai-tool-usage.md](docs/ai-tool-usage.md)
- 第三方许可：[docs/third-party-licenses.md](docs/third-party-licenses.md)

## 导出提交包

```powershell
.\scripts\export_submission.ps1
```

脚本会生成 `submission_package/`，并排除 `.env`、缓存、数据库文件、`node_modules` 和构建产物。
