# 第三方依赖与开源协议

本项目依赖均来自公开 npm/PyPI 包。正式提交前建议使用 `pip-licenses` 与 `npm license-checker` 再生成一次完整清单；下表为当前直接依赖的人工汇总。

## Backend

| 依赖 | 用途 | 常见许可 |
|---|---|---|
| fastapi | Web API 框架 | MIT |
| uvicorn | ASGI Server | BSD-3-Clause |
| sqlalchemy | ORM | MIT |
| pymysql | MySQL Driver | MIT |
| cryptography | 加密基础库 | Apache-2.0 / BSD |
| pydantic | 数据校验 | MIT |
| pydantic-settings | 配置管理 | MIT |
| python-jose | JWT | MIT |
| passlib | 密码哈希 | BSD |
| python-multipart | 表单解析 | Apache-2.0 |
| sparkai | 科大讯飞 Spark SDK | 以官方 SDK 发布协议为准 |
| httpx | HTTP Client | BSD-3-Clause |
| email-validator | 邮箱校验 | CC0 / Unlicense |
| pytest | 测试框架 | MIT |
| pytest-asyncio | 异步测试 | Apache-2.0 |

## Frontend

| 依赖 | 用途 | 常见许可 |
|---|---|---|
| Vue | 前端框架 | MIT |
| Vue Router | 路由 | MIT |
| Pinia | 状态管理 | MIT |
| Element Plus | UI 组件 | MIT |
| @element-plus/icons-vue | 图标 | MIT |
| Axios | HTTP Client | MIT |
| markdown-it | Markdown 渲染 | MIT |
| Mermaid | 图表渲染 | MIT |
| ECharts | 图表 | Apache-2.0 |
| Vite | 构建工具 | MIT |
| TypeScript | 类型系统 | Apache-2.0 |
| vue-tsc | Vue 类型检查 | MIT |

## 备注

- 不修改第三方库源码。
- 前端构建产物和 `node_modules` 不进入源码提交包。
- 如比赛要求更严格的 license 文件，可在提交前运行自动 license 工具生成机器可核验版本。

