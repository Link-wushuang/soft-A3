# AI 工具使用说明

## 大模型选用

最终提交版本以科大讯飞星火大模型（Spark）作为合规 AI 后端，通过 `sparkai` Python SDK 接入。

- Provider 名称：`spark`
- SDK：`sparkai==0.3.0`
- 接口方式：WebSocket
- 默认模型域：`generalv3.5`
- 配置位置：`backend/.env`

开发阶段曾保留 `deepseek` provider 作为临时调试通道；测试和离线演示默认使用 `mock` provider，不依赖外部网络。

## AI 辅助开发工具

开发过程中使用的 AI 辅助工具包括：

- 科大讯飞星火认知大模型：用于 Prompt 设计、教育资源表达方式调优和合规方案参考。
- iFlyCode 智能编程助手：辅助代码编写、错误定位和重构建议。
- Codex/Claude 类编程助手：用于执行计划、生成测试和补全文档。最终提交文档明确以 Spark 作为系统 AI 后端。

## 系统中的 AI 应用

1. 学生画像提取：`ProfileAgent`
2. 学习路径规划：`PathPlannerAgent`
3. 个性化资源生成：6 类 Resource Agent
4. 答案评估：`EvaluationAgent`
5. 学习反思：`ReflectionAgent`
6. 内容验证：`VerifierAgent`
7. 安全过滤：`ContentGuardAgent`
8. 智能辅导：`TutorAgent`（P1）

## 不提交密钥

仓库只提交 `.env.example`，真实 `SPARK_API_KEY`、`SPARK_API_SECRET`、`DEEPSEEK_API_KEY` 只存在本地 `.env` 或部署平台密钥管理中。

