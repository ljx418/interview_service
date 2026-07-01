# JobPilot AI P6 真实 Provider 与长程连续对话计划

日期：2026-06-27
状态：P6 fake provider 自动化候选已完成；当前文档阶段准备 P6-REAL 真实 provider 受控验收；任何真实外部 provider 调用仍需用户单独确认。
适用阶段：P6 provider opt-in / P6-FC 长程连续对话 / P7 产品化 Beta / P7-post P5 复验

## 1. 背景与产品目标

2026-06-30 状态更新：

- P6 provider-backed 自由聊天已具备 fake provider 自动化候选；
- P5.5 可视化验收材料已补充多身份合成资料与 20 轮 fake provider 连续对话 transcript；
- 上述证据只能证明 opt-in 状态机、长程对话边界、脱敏日志、fallback 和报告展示，不代表 MiniMax、DeepSeek、OpenAI-compatible 或其他真实 provider 质量通过；
- 当前阶段只补齐 P6-REAL 受控外呼执行单、验收门槛和报告边界，不触发真实调用。

用户已认可 P4 本地/mock Chatbox 体验基本 OK，并明确希望下一阶段实现：

- “无限对话聊天”；
- “真实 provider 聊天”。

这里的“无限对话”不能被写成真正无限 token、无限成本或无限上下文。P6 的可验收目标是“长程连续对话”：用户可以在同一 workspace 中持续围绕职业背景、项目、JD、申请包和面试准备追问，系统通过会话持久化、滚动摘要、上下文快照和检索来维持上下文连续性；当用户明确 opt-in 后，可调用真实 provider 改善自由聊天和复杂推理质量。

2026-06-27 阶段决策：

- P5-REAL 标记为冻结延期复验；
- P5-Freeze 标记为冻结延期复验；
- P5-REAL/P5-Freeze 在 P7 完成后作为 P7-post 复验；
- P6+P7 一体作为当前阶段目标；
- 本阶段文档开发完成前不进入实质代码开发；
- 后续任何真实 API Key、真实个人资料、真实外部 provider 调用、workspace 删除、不可逆迁移、ASR/会议平台/自动投递/SaaS 操作都必须先暂停找用户确认。

## 2. 成功标准

P6 完成后，用户应能体验到：

```text
打开 Chatbox
→ 明确看到当前 provider 模式、隐私边界、是否会外呼
→ 开启真实 provider 聊天前完成确认
→ 连续围绕求职方向、资料、JD、申请包追问 20-50 轮
→ 刷新页面后会话、摘要、关键上下文仍可恢复
→ 系统能解释当前上下文来自哪些资料、产物和近期对话
→ provider 失败或超时时自动降级到本地连续对话基线
→ 普通聊天不绕过 questions_to_confirm、导出 preflight 或工具确认
```

最低出门体验：

- 用户能明确判断本轮是否调用真实外部 provider；
- API Key 不进入仓库、报告、截图说明、日志或 fixture；
- 长对话不会因为消息过多导致 UI 卡死、上下文完全丢失或误触发工具；
- provider-backed 回复有来源边界，不能伪造不存在的履历事实；
- 所有真实外呼都有脱敏 invocation 记录和失败降级证据。

## 3. 非目标

P6 不做以下能力：

- 真正无限 token、无限历史逐字塞入模型；
- 默认外呼真实 provider；
- 自动读取用户个人目录；
- 未经确认把真实个人资料发送给外部 provider；
- SaaS 登录、多租户、Billing；
- ASR、会议平台、自动投递；
- 隐蔽式面试辅助或敏感属性分析。

## 4. 目标架构增量

建议在现有 Chatbox / FastAPI / ChatCore / Domain Tools / SQLite workspace 基线上增加以下边界：

```text
Chatbox UI
→ Provider Consent UI
→ Chat Session API
→ Chat Orchestrator
  → Intent Router
  → Long Context Manager
    → Recent Messages Window
    → Rolling Conversation Summary
    → Workspace Context Snapshot
    → Artifact / JD / Profile Retrieval
  → Provider-backed Dialogue Adapter
  → Local Fallback Dialogue
  → Tool Intent Confirmation
→ Provider Policy Gate
→ Provider Invocation Log
→ Domain Tools / Artifact / Export
→ Workspace Lifecycle and Diagnostics（P7）
```

职责：

- `Provider Consent UI`：展示 provider、模型、隐私、费用和本次是否外呼，不保存 API Key；
- `Chat Orchestrator`：统一选择自由聊天、澄清、工具计划或 provider-backed 回复；
- `Long Context Manager`：把近期消息、滚动摘要、workspace 摘要和相关 artifact 组合为模型上下文；
- `Provider-backed Dialogue Adapter`：只在用户 opt-in 且 policy gate 通过后调用外部模型；
- `Provider Policy Gate`：拦截未授权外呼、未脱敏真实资料、缺 API Key、超预算或不安全请求；
- `Provider Invocation Log`：只记录脱敏元数据、耗时、状态、错误类型和 token 估算；
- `Local Fallback Dialogue`：provider 不可用时保留本地/mock 连续对话体验。
- `Workspace Lifecycle and Diagnostics`：P7 管理 workspace 备份、导出、清理 dry-run、迁移 dry-run、诊断报告、发布/部署/回滚证据。

## 4.1 Long Context Manager 最小数据结构

P6 不需要一次性引入复杂向量数据库。默认路线是复用 SQLite workspace、chat session、artifact/source refs，并增加可审计的上下文摘要结构。

建议结构：

| 结构 | 字段 | 说明 |
| --- | --- | --- |
| RecentMessageWindow | session_id、message_ids、max_turns、token_estimate | 保留最近 N 轮原文，默认只进入当前 workspace |
| RollingConversationSummary | session_id、summary_text、covered_message_range、source_message_ids、updated_at | 用于长对话压缩，不替代原始消息 |
| WorkspaceContextSnapshot | workspace_id、latest_job_id、latest_package_id、artifact_ids、pending_confirmations、export_state | 回答“当前进展如何”和构造 provider 上下文 |
| RetrievedContextBlock | source_type、source_id、redacted_excerpt、source_refs、risk_label | 只取相关 artifact/JD/profile 摘要，避免完整原文外发 |
| ProviderContextEnvelope | provider、model、consent_scope、recent_window、rolling_summary、workspace_snapshot、retrieved_blocks | 真正传给 provider 前的可审计上下文包 |

验收约束：

- `ProviderContextEnvelope` 不得包含 API Key；
- 不得包含未授权完整真实简历、完整 JD 或完整 provider raw response；
- 每次 provider-backed 回复必须能说明上下文来自 recent messages、rolling summary、workspace snapshot 或 source refs；
- 刷新页面不得重复外呼，只恢复已持久化消息和摘要。

## 4.2 Provider Invocation Log 最小 schema

建议字段：

| 字段 | 要求 |
| --- | --- |
| invocation_id | UUID 或等价唯一标识 |
| workspace_id / session_id | 只记录本地 id |
| provider / model | 可读 provider 名称和模型名 |
| consent_id / consent_scope | 记录授权范围，不记录敏感原文 |
| status | configured / consented / called / failed / fallback |
| started_at / duration_ms | 性能和故障定位 |
| token_estimate | 可估算即可，不作为账单事实 |
| redaction_summary | 说明哪些数据类被遮蔽 |
| error_type | timeout / 429 / schema_error / network_error / policy_denied |
| fallback_used | true/false |

禁止字段：

- API Key；
- 完整 prompt；
- 完整真实资料；
- 完整 provider raw response；
- 未脱敏联系方式、账号、私密链接。

## 5. 工作包

| 工作包 | 目标 | 主要产物 | 验收证据 |
| --- | --- | --- | --- |
| P6-M0 文档与风险审计 | 制定 P6 PRD、目标架构、验收门槛和高风险确认点 | P6 PRD、acceptance gates、drawio 更新 | 文档审计无重大规格偏差 |
| P6-M1 Provider opt-in UX | 用户显式选择 provider、模型和本次外呼确认 | 模型设置、调用前确认、隐私提示 | 截图证明默认不外呼，确认后才外呼 |
| P6-M2 Provider-backed Chat Adapter | 将真实 provider 接入自由聊天路径 | adapter、timeout/retry/schema validation | mock + fake provider eval，受控真实 provider 验收 |
| P6-M3 Long Context Manager | 支持长程连续对话，不把全部历史硬塞模型 | recent window、rolling summary、context snapshot | 20-50 轮连续对话 eval，刷新恢复 |
| P6-M4 Tool Safety | 聊天、工具和 artifact 写入保持边界 | tool intent confirmation、preflight guard | 普通聊天不写 artifact，确认后才执行工具 |
| P6-M5 Privacy / Redaction | 防止 API Key、完整真实资料和 provider raw response 泄露 | redaction、invocation log、report filter | 敏感信息扫描和日志脱敏 eval |
| P6-M6 Visual Acceptance | 生成真实界面 HTML 报告 | Chrome/CDP 截图、中文报告 | 报告可见、边界清楚、不虚假验收 |
| P6-Freeze | 完成 P6 出门审计 | final audit、README/TODO/drawio 同步 | pytest、build、drawio parse、人工体验记录 |
| P7-M0 Beta Readiness Plan | 产品化 Beta 启动审计 | P7 plan、数据生命周期、诊断和发布边界 | 审计无重大规格偏差 |
| P7-M1 Workspace Lifecycle | workspace 恢复、导出、备份、清理 dry-run、迁移 dry-run | lifecycle routes/UI | 生命周期 eval 和截图 |
| P7-M2 Diagnostics and Release | 脱敏诊断报告、启动/部署/回滚文档 | diagnostics report、release checklist | 文档可复现、敏感扫描通过 |
| P7-M3 Beta Freeze | Beta 使用说明、支持流程、隐私审计、P7 报告 | final audit、HTML 报告 | P7 出门门槛通过 |
| P7-post P5 Revalidation | P5-REAL/P5-Freeze 复验 | P5-REAL 报告、P5 closure audit | 只在用户提供真实资料路径后执行 |

## 5.1 P6-REAL 受控外呼执行单

真实 provider 验收前必须由用户明确确认以下字段。缺少任一关键字段时，不得执行真实外呼，不得生成真实 provider 通过结论。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| provider | 是 | MiniMax、DeepSeek、OpenAI-compatible 或其他明确 provider |
| model | 是 | 本次验收使用的模型名 |
| base_url preset | 视 provider 而定 | 只保存非敏感 preset，不保存 API Key |
| API Key 配置方式 | 是 | 仅允许本地 `.env` 或运行环境变量；不得写入仓库、报告、日志、截图说明 |
| 最大调用次数 | 是 | 小样本验收建议先限制为 3-10 次 |
| 最大预算或费用边界 | 是 | 可用金额、token 估算或人工确认的等价边界 |
| timeout / retry | 是 | 明确超时、重试次数、失败后 fallback |
| 允许发送的数据类别 | 是 | 近期消息、rolling summary、workspace 摘要、JD 摘要、profile/artifact 摘要 |
| 禁止发送的数据类别 | 是 | API Key、联系方式、账号、私密链接、完整简历长原文、完整 provider raw response |
| 报告允许展示字段 | 是 | provider/model、状态、耗时、脱敏摘要、截图；不得展示密钥和完整原文 |
| 失败打回条件 | 是 | 未授权外呼、泄露敏感信息、UI 卡死、fallback 不可用、报告虚假声明 |

真实 provider 小样本验收最低路径：

```text
默认进入 Chatbox，不外呼
→ 配置 provider 偏好，不外呼
→ 用户确认本轮数据范围和调用次数
→ 发送 3-10 轮真实 provider 普通求职对话
→ 检查 provider called / failed / fallback 证据
→ 验证普通聊天不写 artifact，导出和工具仍受 confirmation/preflight 约束
→ 生成脱敏 HTML 报告
```

报告必须同时展示 fake provider 自动化候选证据和真实 provider 小样本证据，并明确两者不可互相替代。

## 6. 验收场景

自动化场景至少覆盖：

1. 默认进入 Chatbox，不配置 provider，不发生外呼；
2. 配置 provider 但未确认本次外呼，仍不调用 provider；
3. 用户确认真实 provider 聊天，发送普通求职方向问题，得到 provider-backed 回复；
4. 连续 20-50 轮追问，系统维护滚动摘要和 workspace context；
5. 刷新页面后恢复历史消息、摘要和当前 workspace 状态；
6. provider 超时、结构错误或 429 时降级到本地连续对话基线；
7. 普通聊天不生成 artifact；
8. 明确要求“生成申请包”时进入工具确认或工具执行路径；
9. blocking confirmation 未处理时仍不能导出；
10. 报告中不出现 API Key、完整真实资料、完整 provider raw response。
11. workspace backup/export 可执行，cleanup/migration 默认只 dry-run；
12. diagnostics report 可生成且通过敏感信息扫描；
13. release/deploy/rollback 文档能在本地复现；
14. P7 完成后，P5-REAL/P5-Freeze 仍必须单独复验，未提供真实资料时保持未执行。

人工体验场景至少覆盖：

- 用户能理解“本轮是否外呼”；
- 用户能理解长对话为什么仍能记住当前求职上下文；
- 用户能区分自由聊天、资料处理、生成申请包和导出；
- provider 失败时不会丢失当前工作。

## 7. 打回条件

出现任一情况，P6 不得进入冻结：

- 默认外呼真实 provider；
- API Key 被写入仓库、日志、报告、截图说明或 fixture；
- 未经确认把真实个人资料发送给外部 provider；
- 报告把 provider configured 写成 provider called；
- 报告把 20-50 轮长程对话写成真正无限上下文；
- 普通聊天绕过 tool confirmation 写入 artifact；
- 自由聊天绕过 questions_to_confirm 或 export preflight；
- provider 失败后 Chatbox 卡死、丢 session 或不能降级；
- P6 文档把 SaaS、ASR、会议平台、自动投递写成已完成。
- P7 文档或报告把 workspace 删除、迁移 apply、真实资料复验写成已默认执行；
- P7 报告把 Beta 写成 SaaS GA；
- P7-post 用 synthetic personas、examples 或脱敏 fixture 替代真实个人资料复验。

## 8. 文档支撑度评估

当前 P4/P5 文档足以支撑本地/mock 连续对话和 P5 自动化候选验收，但不足以直接支撑 P6 真实 provider 长程聊天和 P7 产品化 Beta 开发。

本文件补齐了 P6/P7 的目标、非目标、架构边界、工作包、验收场景和打回条件。2026-06-29 复审后，又将 P6-M0/P7-M0 的开发前可执行细则补入第 9 节，避免后续自动化开发需要在多个文档之间拼接执行口径。

进入 P6/P7 实质开发前必须依赖以下文档形成闭环：

- P6+P7 阶段 PRD；
- Provider Policy Gate 详细规格；
- Long Context Manager 数据结构与压缩策略；
- Provider invocation schema；
- 真实外呼授权表和报告脱敏模板；
- P7 workspace lifecycle、diagnostics、release/rollback 和 support runbook 规格；
- drawio P6+P7 架构差异页。

当前主文档开发完成后，可以进入具体子阶段短启动审计和后续自动化开发准备；若任一子阶段审计发现默认外呼、密钥泄露、长对话虚假承诺、workspace 不可逆操作默认执行或 P5 复验替代风险，必须打回文档阶段。

## 9. P6-M0/P7-M0 开发前可执行细则

本节是进入实质代码开发前的执行规格。它不代表功能已实现，只定义后续每个子阶段必须按什么状态机、数据结构、测试证据和打回条件开发。

### 9.1 Provider Policy Gate 状态机

provider 状态必须至少包含：

| 状态 | 含义 | 可触发外呼 | UI 必须表达 |
| --- | --- | --- | --- |
| `mock_default` | 默认本地/mock 模式 | 否 | 外部模型未调用 |
| `configured` | 本地存在 provider 偏好或 `.env` 配置 | 否 | 已配置，不等于已调用 |
| `consent_required` | 用户请求真实 provider，但缺少本轮授权 | 否 | 需要确认外呼范围 |
| `consented` | 当前 workspace/session 获得可审计授权 | 是，仍需 policy check 通过 | 本轮允许外呼 |
| `called` | 已发生真实 provider 调用 | 已发生 | 显示 provider/model、耗时和脱敏状态 |
| `policy_denied` | policy gate 拒绝外呼 | 否 | 说明拒绝原因和本地 fallback |
| `failed` | provider 超时、429、网络或 schema 错误 | 否，除非重试策略允许 | 显示失败原因和恢复动作 |
| `fallback` | 已降级到本地连续对话 | 否 | 当前为本地回复，不声称 provider-backed |

Policy Gate 最小检查：

- provider 和 model 是否允许；
- API Key 是否仅在后端环境可用；
- 是否存在未过期 consent；
- consent scope 是否覆盖本次数据类别；
- prompt/context 是否通过脱敏边界；
- 预算、超时、最大重试、最大外呼次数是否满足；
- 请求是否试图绕过 tool confirmation、`questions_to_confirm` 或 export preflight。

### 9.2 外呼确认 UX 和证据要求

模型设置和调用前确认必须分开：

- 模型设置只保存非敏感偏好：provider、model、preset、base_url preset、默认模式；
- API Key 不在前端输入框长期保存，不进入 localStorage、截图说明、报告或日志；
- 调用前确认必须显示本次会发送的数据类别，例如近期消息、rolling summary、workspace 摘要、JD 摘要、artifact 摘要；
- 用户取消确认后，必须继续走本地/mock 连续对话；
- 自动化截图必须覆盖“已配置但未调用”和“确认后已调用”两个不同状态。

### 9.3 Long Context Manager 持久化模型

默认路线不引入向量数据库。P6 先使用 SQLite/chat session/artifact/source refs 实现可验收长程连续对话。

| 模型 | 最小字段 | 写入时机 | 验收点 |
| --- | --- | --- | --- |
| `ChatMessage` | session_id、role、content、created_at、metadata、redaction_status | 每轮消息 | 刷新后可恢复 |
| `RecentMessageWindow` | session_id、message_ids、max_turns、token_estimate | 构造上下文前 | 只包含近期窗口 |
| `RollingConversationSummary` | session_id、summary_text、covered_message_range、source_message_ids、updated_at | 超过窗口阈值或阶段切换 | 摘要不替代原始消息 |
| `WorkspaceContextSnapshot` | workspace_id、latest_job_id、latest_package_id、artifact_ids、pending_confirmations、export_state | 资料/JD/产物/确认项变化后 | 能回答当前进展 |
| `RetrievedContextBlock` | source_type、source_id、redacted_excerpt、source_refs、risk_label | provider 调用前按需提取 | 不发送完整敏感原文 |
| `ProviderContextEnvelope` | consent_scope、recent_window、rolling_summary、workspace_snapshot、retrieved_blocks | policy check 通过后 | 可审计、可脱敏、可复现 |

P6 验收的“连续对话”定义为 20-50 轮可恢复长程对话，不得写成真正无限 token、无限上下文或无限成本。

### 9.4 Provider Invocation Log schema

provider invocation log 只记录脱敏元数据。最小 schema：

| 字段 | 要求 |
| --- | --- |
| `invocation_id` | 唯一 id |
| `workspace_id` / `session_id` | 本地 id |
| `provider` / `model` | 可读名称，不含密钥 |
| `status` | configured / consented / called / failed / fallback / policy_denied |
| `consent_scope` | 授权数据类别和 TTL，不含原文 |
| `context_summary_hash` | 可选摘要 hash，不含完整 prompt |
| `redaction_summary` | 被遮蔽的数据类别 |
| `started_at` / `duration_ms` | 性能排查 |
| `token_estimate` | 估算值，不作为账单事实 |
| `error_type` | timeout / 429 / schema_error / network_error / policy_denied |
| `fallback_used` | true / false |

禁止记录 API Key、完整 prompt、完整真实资料、完整 JD、完整 provider raw response、联系方式、账号和私密链接。

### 9.5 P6 子阶段开发和验收 checklist

| 子阶段 | 开发入口 | 必须新增或修改 | 自动化验收 | 打回条件 |
| --- | --- | --- | --- | --- |
| P6-M1 | Chatbox + provider status/consent routes | 模型设置、状态条、调用前确认 | 默认不外呼、configured 不等于 called、取消确认 fallback 截图 | 配置 provider 后自动调用 |
| P6-M2 | ChatCore + provider adapter | provider-backed reply selection、timeout/retry/schema validation | fake provider eval、policy denied eval、失败降级 eval | 未授权外呼或 raw response 写入 artifact |
| P6-M3 | Long Context Manager | recent window、rolling summary、workspace snapshot、refresh recovery | 20-50 轮 eval、刷新恢复截图 | 把完整历史/完整资料无边界发送给 provider |
| P6-M4 | Intent Router + Artifact/Export Guard | 普通聊天/工具意图区分、preflight 回归 | 普通聊天不写 artifact、blocking export 拦截 | provider-backed chat 绕过确认 |
| P6-M5 | Redaction + Invocation Log | 脱敏日志、敏感扫描、报告过滤 | API Key/raw response/完整资料扫描 | 报告或日志泄露敏感信息 |
| P6-M6 | Browser evidence + HTML report | 中文报告、多视口截图、PRD 规格检视 | 报告可读、截图可见、未验证范围清楚 | 把 20-50 轮写成真正无限或把 configured 写成 called |

### 9.6 P7 子阶段开发和验收 checklist

| 子阶段 | 开发入口 | 必须新增或修改 | 自动化验收 | 打回条件 |
| --- | --- | --- | --- | --- |
| P7-M0 | Beta readiness docs | workspace lifecycle、diagnostics、release/rollback/support 细则 | 文档审计无重大规格偏差 | P7 被扩大成 SaaS、多租户或 Billing |
| P7-M1 | Workspace lifecycle service/routes/UI | workspace 列表、恢复、导出、备份、cleanup dry-run、migration dry-run | 生命周期 eval、dry-run 截图 | 默认删除、默认迁移 apply、写出 workspace 外 |
| P7-M2 | Diagnostics + release docs/scripts | 脱敏诊断报告、健康检查、启动/部署/回滚说明 | diagnostics report eval、敏感扫描、文档复现 | 诊断报告泄露密钥、完整资料或 raw response |
| P7-M3 | Beta closure evidence | Beta 使用说明、支持流程、隐私审计、P7 HTML 报告 | P7 final report、PRD 规格检视、P0-P6 回归 | 把 Beta 写成 SaaS GA 或把 P5-REAL 写成默认通过 |

### 9.7 真实数据和真实 provider 验收策略

- 默认自动化开发使用 mock/fake provider 和 examples/脱敏 fixture；
- 受控真实 provider 验收必须由用户确认 provider、模型、调用次数、数据类别和报告展示范围；
- 若用户不提供 `.env` 或不允许真实外呼，P6 只能通过 mock/fake provider 证明 policy、adapter、fallback 和报告边界，真实 provider 质量保持未执行；
- P7-post P5-REAL 必须等用户提供真实/脱敏资料路径和允许展示字段；未提供时只能保持未执行。

### 9.8 开发前最终准入结论

当前文档已经可以支撑 P6+P7 的自动化开发启动和逐阶段验收。准入前不再需要继续扩大主文档范围，但每个子阶段必须生成独立阶段审计记录，证明：

- 本阶段开发计划和验收标准已对齐 PRD；
- 没有新增致命或重大规格偏差；
- 高风险动作已经被用户确认或明确保持未执行；
- 上一阶段端到端验收和 PRD 规格检视已通过。
