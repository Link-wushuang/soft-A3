# 安全与防幻觉设计

## 1. 风险目标

教育资源生成系统需要避免三类问题：事实幻觉、越界内容和不可追踪生成。EduPath Agent 将安全能力放入资源生成主链路，而不是事后人工检查。

## 2. Source-Bound Generation

生成类 Agent 的输入必须包含课程知识点的 `summary`、`key_content`、`common_mistakes`、`sources` 和 `case_materials`。Prompt 要求智能体只围绕已检索课程内容组织讲解、练习和案例。

## 3. Verification Pipeline

资源生成后进入两级检查：

1. `VerifierAgent`：检查资源是否与知识点上下文一致，输出 `confidence` 和 warning。
2. `ContentGuardAgent`：检查是否包含不安全、无关、过度承诺或越界内容，输出 `safety_status`。

检查结果写入 `GeneratedResource.warnings`、`GeneratedResource.safety_status` 和 `SafetyAuditLog`，前端以 `SafetyBadge` 展示。

## 4. Audit Log

`SafetyAuditLog` 记录：

- `resource_id`
- `check_type`
- `status`
- `details`
- `blocked_reason`
- `created_at`

这些字段用于演示“生成内容为何可信”和后续教师复核。

## 5. Fallback Behavior

- LLM JSON 解析失败时，Mock provider 和服务层应返回可展示的保底结构。
- 资源安全状态为 blocked 时，前端不展示原始资源内容。
- Spark 或 DeepSeek 不可用时，演示环境切回 `LLM_PROVIDER=mock`。
- SSE 断开时，前端仍可通过任务查询接口拉取最终状态和 trace。

## 6. Secret Handling

- `.env` 不允许提交。
- `.env.example` 只保留空配置示例。
- 导出脚本会扫描提交包中的 `SPARK_API_KEY`、`DEEPSEEK_API_KEY` 和常见 `sk-` token。

