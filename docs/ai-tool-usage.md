# AI 工具使用说明

## 大模型选用

最终提交版本以科大讯飞星火大模型（Spark）作为合规 AI 后端，通过 OpenAI 兼容 REST 接口接入，支持流式输出。

- Provider 名称：`spark`
- 接口方式：OpenAI 兼容 REST（`https://spark-api-open.xf-yun.com/v1/chat/completions`）
- 默认模型：`4.0Ultra`
- 流式输出：`stream=true` SSE 逐 token 返回（`SparkLLM.stream()`）
- 配置位置：`backend/.env`

开发阶段曾保留 `deepseek` provider 作为临时调试通道；测试和离线演示默认使用 `mock` provider，不依赖外部网络。

## 语音合成（TTS）

视频分镜旁白使用科大讯飞在线语音合成（TTS）服务，配合 SVG 分镜动画实现"图文+语音"伪视频，补齐多模态视频要求。

- 接口：讯飞 TTS WebSocket v2（`wss://tts-api.xfyun.cn/v2/tts`）
- 鉴权：HMAC-SHA256 签名，复用讯飞开放平台账号（`SPARK_APP_ID/API_KEY/API_SECRET`）
- 音频格式：mp3（`aue=lame`）
- 降级策略：TTS 不可用时前端自动降级到浏览器 Web Speech API（`speechSynthesis`）朗读
- 配置：需在讯飞开放平台额外开通"在线语音合成"服务

## AI 辅助开发工具

开发过程中使用的 AI 辅助工具包括：

- 科大讯飞星火认知大模型：用于 Prompt 设计、教育资源表达方式调优和合规方案参考。
- iFlyCode 智能编程助手：辅助代码编写、错误定位和重构建议。
- Codex/Claude 类编程助手：用于执行计划、生成测试和补全文档。最终提交文档明确以 Spark 作为系统 AI 后端。

## 系统中的 AI 应用

1. 学生画像提取：`ProfileAgent`（流式 SSE 输出画像对话）
2. 学习路径规划：`PathPlannerAgent`（反思触发自动重规划）
3. 个性化资源生成：6 类 Resource Agent（ThreadPoolExecutor 并行）
4. 答案评估：`EvaluationAgent`
5. 学习反思：`ReflectionAgent`（→ PathPlanner 协同闭环）
6. 内容验证：`VerifierAgent`
7. 安全过滤：`ContentGuardAgent`
8. 智能辅导：`TutorAgent`（真流式 SSE 逐 token 输出）
9. 视频分镜旁白：讯飞 TTS 语音合成

## 不提交密钥

仓库只提交 `.env.example`，真实 `SPARK_API_KEY`、`SPARK_API_SECRET`、`DEEPSEEK_API_KEY` 只存在本地 `.env` 或部署平台密钥管理中。

