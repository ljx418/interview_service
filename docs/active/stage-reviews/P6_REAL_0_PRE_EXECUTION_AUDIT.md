# P6-REAL-0 Pre-Execution Audit

日期：2026-06-30

## 1. 范围

本审计用于进入 P6-REAL 自动化验收前的准入检查。本轮不读取真实个人资料，不调用真实 provider，不展示 API Key。

## 2. 开发与验收计划

执行项：

- 使用 `scripts/generate_p6_real_provider_acceptance.py --mode gate-only` 生成 P6-REAL 门禁报告；
- 验证默认不外呼；
- 验证 provider configured 不等于 called；
- 验证缺少 consent 时 fallback；
- 验证报告不泄露 API Key、完整 prompt、完整真实资料或 raw provider response。

## 3. 审计意见

准入结论：可以进入 gate-only 自动化验收。

原因：

- 当前用户选择为真实 provider 单独授权，未授权时不得真实外呼；
- 当前用户选择为真实资料仅使用合成资料，因此不得读取真实个人资料；
- 计划中的 gate-only 路径可在不触发高风险流程的情况下验证 P6-REAL 门禁。

## 4. 打回条件

- 任何默认真实外呼；
- 报告出现 API Key 或 raw provider response；
- configured 被写成 called；
- fake provider 或 gate-only 被写成真实 LLM 质量通过。
