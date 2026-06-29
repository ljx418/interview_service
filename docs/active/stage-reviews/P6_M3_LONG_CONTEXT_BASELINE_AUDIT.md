# P6-M3 Long Context Manager 基线审计

日期：2026-06-29
阶段：P6-M3 Long Context Manager
状态：本地只读上下文摘要基线已进入实现；不触发真实 provider。

## 1. 本阶段目标

- 为长程连续对话提供 bounded context envelope；
- 返回 recent messages、rolling summary、workspace context snapshot 和 retrieved context blocks；
- 支持刷新恢复后的上下文检查；
- 不把完整历史、完整简历、完整 JD 或 provider raw response 无边界塞入上下文。

## 2. 当前实现边界

- 默认复用 SQLite chat session、chat message、artifact 和 workspace 状态；
- 不引入向量数据库；
- 不执行 provider-backed chat；
- 不持久化新的摘要表，当前摘要由只读接口按需计算；
- 输出包含 privacy boundary，便于验收报告证明未包含 API Key 或 raw provider response。

## 3. 验收口径

自动化测试必须证明：

- 20+ 轮消息后仍返回固定大小 recent window；
- rolling summary 覆盖旧消息；
- workspace snapshot 返回 artifact、pending confirmation、latest job/package 等状态；
- privacy boundary 标明未包含 API Key、raw provider response 和完整历史；
- 普通自由聊天不写 artifact。

## 4. 待后续完成

P6-M3 完整冻结前仍需要：

- 前端显示长对话摘要和刷新恢复状态；
- P6 HTML 报告截图展示 20-50 轮长对话摘要；
- 若 P6-M2 provider-backed chat 启用，ProviderContextEnvelope 必须经过 Provider Policy Gate。

## 5. 不得声明

- 不得声明真正无限上下文；
- 不得声明真实 provider 长对话已通过；
- 不得声明真实个人资料外发已授权。
