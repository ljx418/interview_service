# P6-M2 Provider-backed Chat Adapter 开发与验收审计

日期：2026-06-29  
阶段：P6-M2 Provider-backed Chat Adapter  
状态：自动化候选通过；当前只验证 fake provider-backed 路径，不执行真实外部 provider。

## 1. 开发目标

- 在 `/api/chat/message` 增加显式 `provider_mode=provider_opt_in` 分支；
- 只有当前 workspace/session 存在未过期 consent 时，才允许进入 provider-backed free chat；
- 普通聊天可以走 fake provider-backed 回复；
- 明确工具意图仍走本地 Domain Tools，不由 provider free chat 直接写 artifact；
- provider 失败时降级到 `KeywordChatCore` 本地连续对话；
- 记录脱敏 `provider_chat_invocation` 日志。

## 2. 当前实现边界

- 默认不真实外呼 MiniMax、DeepSeek 或 OpenAI-compatible provider；
- 自动化验收使用 `JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT=1`；
- 真实 provider chat 仍需要额外设置 `JOBPILOT_ALLOW_REAL_PROVIDER_CHAT=1`，并且必须有用户确认；
- 未读取真实个人资料；
- 未实现 SaaS、ASR、会议平台或自动投递。

## 3. 审计意见

未发现新增致命或重大规格偏差。当前实现符合 PRD 的安全默认要求：

- configured 不等于 called；
- 未授权时返回 `consent_required` 并 fallback；
- fake provider 成功调用会写 `provider_chat_invocation.status=called`；
- timeout/429/schema/network 类失败会写 failed 并 fallback；
- 日志只包含脱敏 input summary 和 redaction summary。

## 4. 验收证据

- `tests/evals/test_p6_provider_backed_chat_eval.py`
- `docs/reports/P6P7_AUTOMATED_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p6p7_acceptance/p6p7-fake-provider-chat.png`

## 5. 不得声明

- 不得声明真实 provider 聊天质量已通过；
- 不得声明真实个人资料外发已授权；
- 不得声明真正无限对话；
- 不得声明 P7 Beta 或 P5-REAL 已最终通过。
