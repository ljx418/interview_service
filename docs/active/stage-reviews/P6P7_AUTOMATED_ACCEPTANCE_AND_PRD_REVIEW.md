# P6+P7 自动化验收与 PRD 规格检视

日期：2026-06-29  
状态：自动化候选通过；仍不代表真实 provider、真实个人资料或 SaaS/Beta GA 通过。

## 1. 本轮完成范围

- P6-M2：fake provider-backed free chat adapter、consent gate、失败 fallback；
- P6-M3：长上下文面板接入 recent window、rolling summary、workspace snapshot 和隐私边界；
- P6-M4/M5：tool safety、provider chat invocation 脱敏日志、隐私边界测试；
- P7-M1/M2：workspace backup manifest、cleanup dry-run、migration dry-run、diagnostics metadata-only 的前端入口和自动化截图；
- P6/P7 中文 HTML 自动化报告。

## 2. PRD 对照结论

| PRD / Gate | 当前证据 | 结论 |
| --- | --- | --- |
| Provider 默认安全 | 未授权 provider_opt_in 返回 consent_required；configured_is_called=false | 通过 |
| Provider-backed chat 可控降级 | fake provider called、timeout fallback 测试 | fake 路径通过 |
| 长程连续对话 | 24 轮用户输入、48+ 消息、recent_count=12、rolling summary 覆盖旧消息 | bounded context 通过 |
| Tool Safety | 普通聊天 artifacts=[]；JD 工具意图 skipped_tool_intent | 通过 |
| Privacy / Redaction | provider_chat_invocation 不含 API Key、邮箱被脱敏、raw response 未记录 | 通过 |
| Workspace Lifecycle | backup metadata-only、cleanup/migration dry-run | 非破坏路径通过 |
| Diagnostics | diagnostics metadata-only，不含 API Key/完整资料/raw response | 通过 |

## 3. 自动化命令

```bash
.venv/bin/python -m pytest tests/evals/test_p6_provider_backed_chat_eval.py tests/evals/test_p6_provider_opt_in_eval.py tests/evals/test_p6_long_context_manager_eval.py tests/evals/test_p7_workspace_lifecycle_eval.py
npm --prefix apps/chatbox run build
node scripts/browser_tools/browser-acceptance.mjs --start-chrome --scenario /tmp/p6p7-acceptance-scenario.json --output-dir docs/reports/evidence/p6p7_acceptance --report docs/reports/P6P7_AUTOMATED_ACCEPTANCE_REPORT.html --port 9240
```

## 4. 未验证范围

- 真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼；
- 真实个人资料路径；
- workspace 删除、清空、cleanup apply、migration apply；
- SaaS、多租户、Billing、ASR、会议平台、自动投递、MCP/CLI；
- 真正无限 token、无限上下文或无限成本对话。

## 5. 审计结论

当前实现可以作为 P6/P7 自动化候选验收证据。若要进入真实 provider 或真实个人资料复验，必须先暂停并获得用户明确确认。
