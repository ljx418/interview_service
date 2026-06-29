# P6-M4/M5 Tool Safety 与 Privacy/Invocation Log 审计

日期：2026-06-29  
阶段：P6-M4 Tool Safety / P6-M5 Privacy Redaction  
状态：自动化候选通过；真实 provider 和真实资料路径仍未执行。

## 1. 开发目标

- provider-backed 普通聊天不写 artifact；
- 明确 JD 解析、申请包、导出、面试准备等工具意图继续走本地工具链；
- provider-backed 回复不得绕过 `questions_to_confirm`、artifact confirmation 或 export preflight；
- provider chat invocation log 不记录 API Key、完整 prompt、完整资料或 raw response；
- 报告和测试能区分 fake provider、真实 provider 未执行和本地 fallback。

## 2. 审计结果

通过。当前代码将 provider free chat 与工具意图区分处理：

- 自由聊天：授权且 fake provider 启用时返回普通 assistant message，`artifacts=[]`；
- 工具意图：后端标记 `provider_invocation_status=skipped_tool_intent`，继续执行既有 Domain Tools；
- 失败降级：provider 错误只影响当前回复质量，不丢会话，不阻塞本地继续对话；
- 日志：新增 `provider_chat_invocation` 记录 status、session、consent、fallback、error、token estimate 和脱敏摘要。

## 3. 验收证据

- `tests/evals/test_p6_provider_backed_chat_eval.py::test_provider_mode_does_not_bypass_tool_intent_or_write_free_chat_artifact`
- `tests/evals/test_p1_export_preflight_eval.py`
- `tests/evals/test_p1_provider_redaction_eval.py`
- `docs/reports/P6P7_AUTOMATED_ACCEPTANCE_REPORT.html`

## 4. 未验证范围与不得声明

- 真实 provider 输出质量未验收；
- 真实 provider 可能返回不符合预期的自然语言质量，需要受控真实外呼单独验收；
- 真实个人资料不得进入 provider context，除非用户明确提供路径和允许字段。

结论：当前阶段可以进入 P6 可视化验收与 P7 Beta 非破坏性能力收口。
