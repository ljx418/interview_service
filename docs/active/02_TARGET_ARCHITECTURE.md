# JobPilot AI P5.5 Candidate Profile 目标架构

## -2. P5.5 当前阶段架构主线

P5.5 在 P5 本地资料闭环和 P6/P7 本地 Beta 自动化候选基线上推进。目标不是重写系统，也不是引入外部画像服务，而是在现有本地优先架构中增加一个可审查的 Candidate Profile 平面：

```text
User
→ Chatbox Experience Shell
  → Conversation Plane
  → Candidate Profile Workbench
  → Capability Matrix View
  → Project Credibility View
  → Job Gap View
→ FastAPI Agent Service
  → Profile Aggregation Routes
  → Artifact / Chat / Job / Workspace Routes
→ Profile Orchestrator
  → CandidateProfile Aggregator
  → Evidence Scorer
  → Project Credibility Evaluator
  → Job Gap Analyzer
  → Profile Refresh Guard
→ Domain Data Layer
  → candidate_profile
  → career_fact
  → skill_evidence
  → tech_project
  → job / match_report
  → artifact / artifact_version / source_refs
→ Evidence Layer
  → P5.5 Visual Acceptance Report
  → PRD Spec Review
  → Privacy and Fantasy-claim Audit
```

## -1. P5.5 代码实体与职责

| 层级 | 具体代码实体 | 当前状态 | P5.5 职责 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox UI | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 已实现自动化候选 | 展示画像概览、能力矩阵、项目可信度、岗位短板、source refs 和下一步建议 | 不直接推断敏感属性；不保存 API Key；不直连 provider |
| API 边界 | `services/api/main.py`, `services/api/schemas.py` | 已实现最小路由/Schema | 暴露 profile summary、capability matrix、project credibility、gap analysis 的读取/刷新入口 | 不返回完整未授权资料；不把缺证据写成已证实 |
| Profile Aggregator | `services/profile/candidate.py` | 已实现自动化候选 | 从 career_fact、skill_evidence、tech_project、job、match_report 聚合 CandidateProfile | 不引入复杂外部画像服务 |
| Evidence Scorer | `services/profile/candidate.py` | 已实现自动化候选 | 给技能和经历标注 strong / usable / weak / missing 或等价等级 | 不做人格、潜力或敏感属性评分 |
| Project Credibility Evaluator | `services/profile/candidate.py` | 已实现自动化候选 | 评估本人贡献、技术难点、可验证材料、量化结果缺口和风险标签 | 不把未确认贡献写成事实 |
| Job Gap Analyzer | `services/profile/candidate.py` | 已实现自动化候选 | 将能力矩阵与 JD must/nice requirements 对齐，输出短板和补强行动 | 不输出不可行动的否定性评价 |
| Storage | `candidate_profile`, `career_fact`, `skill_evidence`, `tech_project`, `job`, `match_report`, `artifact` | 基础表已存在 | 作为画像事实和证据来源；必要时写入 profile artifact/version | 不写 workspace 外路径；不丢 source refs |
| ChatCore | `services/chat/core.py` | 已复验自动化候选 | 支持画像状态查询和普通追问；明确画像刷新才触发工具 | 普通聊天不写画像 artifact |
| Evidence | `docs/reports/`, browser evidence scripts | 已生成 P5.5 报告 | 生成 P5.5 中文 HTML 报告、多视口截图、PRD 规格检视 | 不把合成资料写成真实个人资料通过 |

## -0.0.1 P5.5 最小接口和数据契约

P5.5 v1 采用最小可逆路线：新增 profile 读取/刷新 API，复用既有 SQLite 表和 artifact/version，不新增数据库表。

| 用户动作 | 默认接口 / 模块 | 输入 | 必须返回或产生 | 约束 |
| --- | --- | --- | --- | --- |
| 查看画像 | `GET /api/profile/candidate` | `workspace_id`, 可选 `job_id` | profile summary、capability matrix、project credibility、job gaps、source refs、artifact ref | 只读；无画像时返回空态和下一步 |
| 刷新画像 | `POST /api/profile/candidate/refresh` | `workspace_id`, 可选 `job_id`, `target_role` | 更新 `candidate_profile`，写入 `artifact_type=candidate_profile` artifact/version | 不访问 workspace 外路径；不调用真实 provider |
| 追问画像 | `POST /api/chat/message` | 普通自然语言问题 | 基于当前 profile/artifact 的解释性回复 | 普通追问不写画像 artifact |

`candidate_profile` 行保存摘要字段；完整能力矩阵、项目可信度、岗位短板和证据链保存为 `candidate_profile` artifact 的 `content_json`，并继承 artifact/version/source refs/confirmation 机制。

默认证据等级：

- `strong`：有 source refs 且用户确认或有明确项目/文档证据；
- `usable`：有来源但缺量化结果或本人贡献确认；
- `weak`：只有单一线索或表达模糊；
- `missing`：JD 要求中出现但 workspace 没有可追踪证据。

默认项目可信度：

- `verified`：本人贡献、技术难点、可验证材料均有来源；
- `plausible`：有项目来源但缺量化结果或验证材料；
- `needs_evidence`：缺本人贡献或技术细节；
- `risky`：存在未确认贡献、夸大风险或与 JD 表达冲突。

## -0.1 P5.5 当前架构与目标差距

| 当前实现 | P5.5 目标 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| 已有 `candidate_profile` 表，P5.5 已形成用户可见画像闭环 | CandidateProfile 聚合并在 Workbench 可读展示 | 已完成自动化候选 | profile summary API/UI 截图 |
| `career_fact` 可保存事实和技能线索 | 专业背景画像和经历可信边界 | 已完成自动化候选 | source refs 和待确认项截图 |
| `skill_evidence` 可保存技能证据 | 能力矩阵、证据强度、岗位相关性 | 已完成自动化候选 | capability matrix eval |
| `tech_project` 可保存项目卡 | 项目可信度、本人贡献、技术难点、验证材料缺口 | 已完成自动化候选 | project credibility eval |
| `job` / `match_report` 已有岗位解析和匹配 | 岗位短板、补强建议和优先级 | 已完成自动化候选 | gap analysis eval |
| Artifact/Export 已保留版本和 source refs | 画像 artifact 可追溯、可刷新、可报告 | 已复验自动化候选 | artifact/source refs eval |
| P5/P6/P7 报告链路成熟 | P5.5 可视化验收报告 | 已完成自动化候选 | 中文 HTML 报告和真实界面截图 |

## -0.2 P5.5 架构不变量

- source refs 是画像判断的核心，不得隐藏；
- 缺少证据时必须输出 missing / weak / needs confirmation，而不是补全事实；
- 能力评估只评价证据强弱、岗位相关性和补强行动，不评价人格、身份或敏感属性；
- 普通连续聊天不得误写画像产物；
- 真实个人资料和真实 provider 仍需用户确认；
- P5.5 完成不代表 P5-REAL、SaaS、ASR、会议平台、自动投递或 MCP/CLI 已通过。

## -1. P6+P7 自动化候选基线架构主线

以下 P6+P7 内容作为已完成自动化候选和后续复验边界保留。P6+P7 在 P4 已冻结 Chatbox 工作台和 P5 自动化候选本地资料闭环基线上推进。P5-REAL/P5-Freeze 当前为冻结延期复验，不作为 P6/P7 开发前置；P7 完成后再执行 P7-post 真实资料复验。

该历史阶段的目标不是重写系统，也不是把外部 provider 变成默认路径，而是在现有本地优先架构中增加四个可审计平面。P6+P7 已作为自动化候选基线保留，不是当前 P5.5 的新增开发目标：

```text
User
→ Chatbox Experience Shell
  → Model Settings / Provider Consent UI
  → Conversation Plane
  → Long-running Chat State View
  → Workbench and Artifact Review Plane
→ FastAPI Agent Service
  → Chat Routes
  → Provider Status / Consent Routes
  → Workspace Lifecycle Routes
  → Diagnostics Routes
  → Artifact / Export Routes
→ Chat Orchestrator
  → Intent Router
  → Long Context Manager
  → Provider-backed Dialogue Adapter
  → Local Fallback Dialogue
  → Tool Intent Confirmation
→ Provider Policy Gate
  → Opt-in authorization
  → API Key availability check
  → Redaction boundary
  → Budget / timeout / retry policy
  → External-call denial by default
→ Domain Tool Layer
  → Profile / Project / Job / Match / Application / Interview Tools
→ Artifact / Export / Storage Layer
  → Artifact Service
  → Export Service
  → SQLite Workspace
  → Workspace Backup / Cleanup / Migration Dry-run
→ Evidence and Operations Layer
  → Provider Invocation Log
  → Diagnostics Report
  → Visual Acceptance Report
  → Privacy / Redaction Audit
```

## -0. P6+P7 代码实体与职责

| 层级 | 具体代码实体 | P6/P7 状态 | 当前阶段职责 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox UI | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 待新增/修改 | 展示模型设置、provider opt-in、外呼确认、长对话状态、上下文摘要、失败降级、workspace 生命周期入口 | 不保存 API Key；不直连 provider；不伪造 provider called |
| API 边界 | `services/api/main.py` | 待新增/修改 | 增加 provider consent/status、chat provider mode、workspace backup/cleanup/diagnostics 等最小路由 | 不回传密钥；不允许未确认外呼；不执行不可逆操作默认确认 |
| Chat Orchestrator | `services/chat/core.py` | 待重构强化 | 统一自由聊天、状态查询、澄清、工具意图、provider-backed 回复和 local fallback | 普通聊天不写 artifact；不绕过 tool confirmation |
| Long Context Manager | 建议新增 `services/chat/context.py` 或等价模块 | 待新增 | 管理 recent message window、rolling summary、workspace context snapshot、artifact/JD/profile retrieval | 不把完整历史或完整个人资料无边界发送给 provider |
| Provider Adapter | `services/llm/` provider runtime 及新增 chat adapter | 待修改 | 接入 OpenAI-compatible/MiniMax/DeepSeek 类 provider，支持 timeout/retry/schema validation | 不在缺 consent 时调用；不把 raw response 直接写入 artifact |
| Provider Policy Gate | provider policy/runtime 相关模块 | 待强化 | 校验 opt-in、API Key、provider/model、脱敏、预算、外呼次数和失败降级策略 | 不把 provider configured 当作 provider called |
| Provider Invocation Log | tool invocation / provider log 相关存储 | 待强化 | 记录脱敏元数据、耗时、状态、错误类型、token 估算和 redaction 摘要 | 不记录 API Key、完整 prompt、完整个人资料、完整 raw response |
| Local Fallback Dialogue | `services/chat/core.py` | 已有基线，需接入降级 | provider 不可用时保持本地连续对话、状态查询和下一步建议 | 不声称 provider-backed 质量 |
| Artifact/Export Guard | artifact/export 相关服务 | 已有基线，需复验 | 确保 provider-backed chat 不绕过 confirmation、source refs、version 和 export preflight | 不允许 blocking confirmation 未处理仍正式导出 |
| Workspace Lifecycle | SQLite workspace、本地文件目录、建议新增 lifecycle service | 待新增 | 支持恢复、导出、清理、备份、迁移 dry-run 和不可逆操作确认 | 不默认删除 workspace；不写 workspace 外路径 |
| Diagnostics | 建议新增 diagnostics/report service | 待新增 | 生成脱敏诊断包、错误摘要、版本信息和本地环境检查 | 不包含密钥、完整个人资料或 provider raw response |
| Evidence | `docs/reports/`, screenshot/test scripts | 待新增报告 | 生成 P6/P7 中文 HTML 报告、真实界面截图、PRD 规格检视和未验证范围 | 不做虚假验收；不抢占焦点前静默截图 |

## -0.1 P6+P7 当前架构与目标差距

| 当前实现 | P6/P7 目标 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| P4/P5 本地 Chatbox 可用，mock/local 默认 | 支持 provider opt-in 且默认不外呼 | 待开发 | 初始页、模型设置、调用前确认截图 |
| P1 已有 OpenAI-compatible provider 基础 | provider-backed 自由聊天 adapter，覆盖 MiniMax/DeepSeek/OpenAI-compatible 配置 | 待开发 | fake provider eval、受控真实 provider 验收记录 |
| P4C/P5-FC 已有本地连续对话 | Long Context Manager 支持 20-50 轮、滚动摘要、刷新恢复 | 待开发 | 20-50 轮 eval、刷新恢复截图 |
| provider invocation/tool log 已有基础 | 脱敏 invocation log 明确 configured/called/failed/fallback | 待强化 | 日志脱敏 eval、报告扫描 |
| Artifact/Export guard 已支撑 P5 | provider-backed chat 不绕过 confirmation/export preflight | 待复验 | 普通聊天不写 artifact、blocking 仍拦截导出 |
| workspace 可初始化和恢复 | 生命周期管理、备份、导出、清理、迁移 dry-run | 待开发 | workspace lifecycle eval、不可逆确认截图 |
| 报告和截图链路成熟 | P6/P7 可视化验收报告，覆盖 provider、长对话、生命周期、诊断 | 待开发 | 中文 HTML 报告、真实截图证据 |
| P5-REAL/P5-Freeze 未真实执行 | P7 后按 P7-post 重新复验真实资料路径 | 冻结延期 | P7-post P5 复验计划和审计 |

## -0.2 P6+P7 架构不变量

- 默认路径永远是 local/mock，不得因 `.env` 中配置了 provider 就自动外呼；
- 真实外呼必须经过 Provider Policy Gate，并产生脱敏 Provider Invocation Log；
- API Key 只允许从本地环境读取，不进入前端 bundle、仓库、报告、截图说明、日志或 fixture；
- Long Context Manager 只发送必要上下文，必须优先使用摘要、source refs、artifact/JD/profile 摘要和近期消息窗口；
- provider-backed 回复不得绕过 `questions_to_confirm`、Artifact Service、Export Service 或 workspace 沙箱；
- Workspace cleanup、delete、migration apply 等不可逆操作必须显式确认；P7 默认只允许 dry-run 验收；
- Diagnostics report 必须先脱敏再落盘；
- 自动化截图、焦点抢占或弹窗必须提前告知用户；
- P7 完成不自动代表 P5-REAL 通过，P5 复验必须单独执行。

## -0.3 P6+P7 最小可执行接口契约

| 用户动作 | 默认接口 / 模块 | 输入 | 必须返回或产生 | 约束 |
| --- | --- | --- | --- | --- |
| 查看 provider 状态 | `GET /api/provider/status` 或现有 provider status 路由 | workspace_id | configured、selected_provider、selected_model、called_in_session、last_error | configured 不等于 called |
| 保存模型偏好 | `POST /api/provider/preferences` | provider、model、base_url preset、mode | preference saved，redacted display | 不保存 API Key；只保存非敏感偏好 |
| 确认本轮外呼 | `POST /api/provider/consent` | workspace_id、session_id、scope、ttl、allowed_data_classes | consent token / policy snapshot | scope 必须可审计，可撤销或过期 |
| 发送 provider-backed 聊天 | `POST /api/chat/message` | workspace_id、session_id、message、provider_mode | assistant message、context summary、invocation status、fallback status | 未授权时必须走 local/mock 或返回确认请求 |
| 获取长对话摘要 | `GET /api/chat/session/{id}/context` | workspace_id、session_id | recent_count、rolling_summary、context_snapshot、source refs | 不返回完整敏感原文 |
| 刷新恢复会话 | `GET /api/chat/session/{id}` | workspace_id、session_id | messages、summary、artifacts、pending confirmations | 恢复后不重复外呼 |
| 导出诊断报告 | `POST /api/diagnostics/report` | workspace_id、include options | redacted diagnostics zip/html/json | 不含密钥、完整简历、raw response |
| workspace 备份 | `POST /api/workspace/backup` | workspace_id、target | backup path、manifest、redaction status | 只写允许路径 |
| workspace 清理 dry-run | `POST /api/workspace/cleanup/plan` | workspace_id、rules | affected files、risk labels、confirmation required | 不删除文件 |
| workspace 迁移 dry-run | `POST /api/workspace/migrate/plan` | workspace_id、target_version | migration plan、rollback notes | apply 必须另行确认 |
| P7-post P5 复验 | stage review script/report | 用户明确资料路径和允许展示字段 | P5-REAL report、closure audit | 未提供资料则保持未执行 |

## 0. P5 历史架构增补与 P7-post 复验依据

本节作为历史基线和 P7-post 复验依据保留。P5 在 P4 已冻结的 Chatbox 工作台、FastAPI、ChatCore、Domain Tools、Artifact/Export 和本地 workspace 基线上增加“真实资料本地闭环平面”。目标不是重写后端或默认启用外部 provider，而是让真实资料、真实 JD、事实确认、产物编辑、导出和多轮追问都沿同一条可审计链路闭合。

P5 架构主线：

```text
User
→ Chatbox Experience Shell
  → Composer / Upload Dock
  → Conversation Plane
  → Workbench Plane
  → Artifact Review / Edit / Export Plane
→ FastAPI Agent Service
  → Workspace Routes
  → File Upload Routes
  → Chat Routes
  → Workflow Routes
  → Artifact Routes
  → Export Routes
→ ChatCore and Intent Router
  → Context Snapshot
  → Real Data Intake Controller
  → Fact Confirmation Loop
  → Application Package Loop
→ Domain Tool Layer
  → Profile / Project / Job / Match / Application / Interview Tools
→ Artifact and Storage Layer
  → Artifact Service
  → ArtifactVersion
  → Confirmation Model
  → Export Service
  → SQLite Workspace / Local Files
→ Provider Policy Gate
  → Mock default
  → External provider denied unless P6 opt-in confirmation exists
→ Evidence Layer
  → P5 automation report
  → PRD spec review
  → privacy/redaction audit
```

## 0.1 P5 代码实体与职责

| 层级 | 当前代码实体 | P5 状态 | P5 职责 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox UI | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 自动化候选通过，待人工体验冻结 | 呈现上传/粘贴入口、资料解析状态、事实确认、申请包产物、编辑/再生成/导出、多轮追问 | 不生成求职内容；不直接写 SQLite；不直连 provider |
| API 边界 | `services/api/main.py` | 自动化候选通过，待真实资料复核 | 暴露 workspace、upload、chat、workflow、artifact、export 的 P5 路由和错误语义 | 不回传 API Key；不把完整敏感原文写入日志 |
| ChatCore | `services/chat/core.py` | 自动化候选通过，待人工体验复核 | 区分自由追问、状态查询、资料导入、JD 解析、事实确认、生成/再生成等意图 | 不在普通聊天中写 artifact；不绕过确认 |
| Workflow Orchestrator | `services/workflows/p2_demo.py` 及 P5 本地闭环路径 | 自动化候选通过，待真实资料路径复核 | 从 examples flow 扩展为真实资料本地 flow，保留可回归基线 | 不伪造真实资料路径通过 |
| Domain Tools | `services/tools/` | 自动化候选通过，待真实资料质量复核 | 执行资料解析、项目抽取、JD 解析、匹配、申请包生成、面试准备 | 不访问 workspace 外路径；不绕过 source refs |
| Artifact Service | artifact/version 相关服务 | 自动化候选通过，待版本 UI 人工复核 | 保留 source refs、`questions_to_confirm`、版本、编辑、再生成历史 | 不覆盖旧版本；不隐藏 blocking confirmation |
| Export Service | export 相关服务 | 自动化候选通过，待真实资料导出脱敏复核 | 导出 Markdown/DOCX，并在导出前执行 preflight | 不写 workspace 外路径；不导出未确认 blocking 内容 |
| Storage | SQLite workspace、本地文件目录 | 自动化候选通过，持续作为冻结门槛 | 持久化资料、会话、产物、版本、导出记录 | 不保存 API Key；不写完整 raw provider response |
| Provider Policy Gate | provider runtime/policy | 已实现需约束 | P5 默认 mock/local；真实外部 provider 归入 P6 opt-in | 不默认外呼；不把已配置误写为已调用 |
| Evidence | `docs/reports/`, screenshot/test scripts | 自动化候选通过，待真实资料报告复核 | 生成脱敏 P5 验收报告、截图和 PRD 规格检视 | 不暴露真实个人资料全文；不做未执行声明 |

## 0.2 P5 当前架构与目标差距

| 当前实现 | P5 目标 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| P4 Chatbox 已可用，默认 examples/mock 路径冻结 | 支持用户自己的资料和 JD 进入本地闭环 | 自动化候选通过，P5-REAL 待执行 | 上传/粘贴资料截图、脱敏解析结果、错误恢复截图 |
| 资料导入已有基础文件路径和示例数据 | 真实资料导入必须显示本地处理、支持格式、解析摘要、缺失项 | 脱敏 fixture 通过，真实资料路径待用户提供 | 资料导入 eval、隐私提示截图 |
| JD 解析已服务 examples 路径 | JD 粘贴/导入后给出岗位要求、风险、缺口和下一步 | 自动化候选通过，真实 JD 片段待复核 | JD 解析截图、缺失信息恢复测试 |
| Artifact 卡已可读 | 真实资料产物必须显示来源、待确认项、版本、编辑/再生成 | 自动化候选通过，人工体验待复核 | artifact card 截图、version/edit/regenerate 测试 |
| 自由连续对话已在本地/mock 基线通过 | 围绕当前资料/JD/申请包回答状态、建议和非执行型追问 | 自动化候选通过，不代表 provider-backed 聊天 | 多轮追问不误写 artifact 的 eval |
| Markdown/DOCX 导出已实现 | 导出前必须执行确认 preflight，并标明 warning/blocking | 自动化候选通过，真实资料导出待脱敏复核 | 导出 preflight、导出文件和截图 |
| Provider opt-in 基础存在 | P5 默认不外呼；P6 才验证真实 provider | 已实现需约束 | provider 状态截图、无外呼日志审计 |
| P4 报告和 drawio 已完成 | P5 报告必须脱敏并区分真实资料授权/示例数据 | P5 自动化报告已生成，真实资料报告复核待执行 | P5 HTML 报告、PRD 规格检视 |

## 0.3 P5 架构不变量

- 用户资料和 JD 进入系统后必须先落在本地 workspace 边界内；
- 前端只能发起请求、展示状态、触发确认、编辑和导出，不能承担业务生成；
- ChatCore 只能决定意图和下一步，业务写入仍由 Python Domain Tools 执行；
- artifact 必须保留 source refs、`questions_to_confirm`、版本和导出状态；
- blocking confirmation 未处理时不得导出正式申请材料；
- P5 默认 provider 是 mock/local；真实外部 provider、API Key 和 provider-backed 自由智能聊天属于 P6 opt-in；
- 自动化报告不得包含完整真实简历、真实 JD、API Key 或外部 provider raw response；
- 任何涉及真实个人资料、真实外部调用、workspace 删除或不可逆迁移的验收都必须先获得用户确认。

## 0.4 P5 架构验收问题

每个 P5 实现或阶段验收必须回答：

- 用户是否能清楚知道资料会留在本地，外部 provider 未默认调用？
- 上传或粘贴资料后，系统是否返回可读摘要、来源和待确认项？
- JD 解析是否能给出岗位要求、缺口和下一步，而不是只生成内部 JSON？
- 普通追问是否不会误触发生成、解析或 artifact 写入？
- 明确“生成申请包 / 重新生成 / 导出”时，是否走确认和版本链路？
- Workbench 是否能让用户看到当前资料、目标 JD、产物、确认项、版本和导出状态？
- 导出前是否执行 blocking/warning/optional preflight？
- 报告是否区分真实授权资料、脱敏资料和 examples 真实感数据？
- 文档、drawio、测试和报告是否都没有把 P6/P7/P8 能力写成 P5 已完成？

## 0.5 P5 最小可执行接口契约

P5 优先复用当前 API 和 Domain Tools，不以新增复杂后端入口作为默认方案。只有现有接口无法表达验收状态时，才允许增加最小新接口；新增接口必须同步 schema、测试、报告和 drawio。

| P5 用户动作 | 默认接口 / 模块 | 请求输入 | 必须返回或产生 | P5 约束 |
| --- | --- | --- | --- | --- |
| 创建或恢复 workspace | `POST /api/workspace/init`, `GET /api/workspace/status` | name、root_path、privacy_mode | workspace_id、root_path、privacy_mode、next_actions | 默认 `privacy_mode=local_first`，不得默认外呼 |
| 上传资料 | `POST /api/files/upload` | workspace_id、file | document_id、kind、path 或安全错误 | 文件必须落在 workspace 内；报告不得暴露全文 |
| 导入本地资料 | `POST /api/files/ingest-local` | workspace_id、source_path、kind | document_id、source metadata | 必须拒绝 workspace 外逃逸路径 |
| 解析资料 | `POST /api/profile/extract-facts` | workspace_id、document_ids、target_roles | career_facts、skill_evidence、artifact_ref、source_refs、questions_to_confirm | 没有 document_ids 时可使用 workspace 现有文档，但必须可追踪来源 |
| 生成项目卡 | `POST /api/project/create-card` | workspace_id、project_name、source_document_ids、target_role | tech_project、artifact_ref、source_refs | 不得臆造未在资料中出现的项目事实 |
| 解析 JD | `POST /api/job/parse-jd` 或明确 JD chat intent | workspace_id、jd_text、source_url | job_id、requirements、risks、artifact_ref | 缺少 JD 时返回恢复动作，不伪造成解析成功 |
| 匹配岗位 | `POST /api/job/match-profile` | workspace_id、job_id | match_report、strengths、gaps、questions_to_confirm | 必须说明证据不足的项 |
| 生成申请包 | `POST /api/application/create-package` 或明确 chat intent | workspace_id、job_id、style、language | package_id、artifact_ref、draft、questions_to_confirm | blocking confirmation 未处理时仍可生成草稿，但不得正式导出 |
| 编辑产物 | `PATCH /api/artifacts/{artifact_id}` | workspace_id、content_json | 新 artifact version | 不覆盖旧版本，不丢 source_refs |
| 重新生成 | `POST /api/artifacts/{artifact_id}/regenerate` | workspace_id | 新 artifact version | 保留旧版本和失败恢复信息 |
| 确认事实 | `POST /api/artifacts/{artifact_id}/confirm` | workspace_id | confirmed status 或剩余 blocking 项 | 不允许隐藏未处理 blocking 项 |
| 导出申请包 | `POST /api/application/export-package` | workspace_id、package_id、formats、artifact_version_id | exports、preflight、download path | 只能写 workspace `exports/`，blocking 未处理时不得导出正式材料 |
| 多轮追问 | `POST /api/chat/message` | workspace_id、session_id、message | assistant message、chat_mode、artifacts | 普通追问不写 artifact；明确工具意图才执行 |

P5 前端状态机必须至少表达以下状态：

```text
idle
→ profile_importing
→ profile_ready 或 profile_needs_recovery
→ jd_importing
→ jd_ready 或 jd_needs_recovery
→ facts_need_confirmation
→ package_draft_ready
→ package_editing / regenerating
→ export_preflight_blocked 或 export_ready
→ exported
```

P5 不要求一次性引入新全局状态管理库。若现有 `main.tsx` 状态已难以维护，可以在 P5-M1 后按组件边界拆分；拆分必须保持行为不变，并优先服务资料导入、JD 解析、事实确认、产物和导出状态可读。

## 0.6 P5 数据、脱敏和验收资料策略

P5 自动化开发默认使用 `examples/` 真实感数据和测试临时 workspace。真实个人资料只能用于用户明确授权的人工体验审查；任何自动化报告、截图标题、日志、fixture 和提交内容都不得包含完整真实资料。

| 数据类型 | P5 默认处理 | 可进入报告 | 禁止事项 |
| --- | --- | --- | --- |
| examples 简历/JD/项目 | 可用于自动化验收 | 可摘要展示，并标注为真实感示例数据 | 不得写成真实个人资料 |
| 用户真实简历/JD | 仅用户明确授权后用于人工体验 | 只能脱敏摘要、截图局部或人工结论 | 不得全文写入仓库、报告、日志、fixture |
| API Key / provider 配置 | P5 不默认使用 | 只能写“未调用 / 需 P6 opt-in” | 不得写入报告、截图、日志或提交 |
| provider raw response | P5 默认不存在 | 不适用 | 不得伪造或声称已通过 |
| 导出文件 | 写入 workspace `exports/` | 可展示路径和脱敏片段 | 不得越过 workspace 或包含未授权隐私 |

P5 自动化报告必须包含“未验证范围”段落，并明确列出：真实外部 provider、provider-backed 自由智能聊天、SaaS、ASR、会议平台、自动投递、MCP/CLI、最终产品化发布。

以下 P4 内容作为已冻结基线和历史背景保留。

## 1. 历史 P4 UX 体验强化架构基线

P4 在 P0/P1/P2/P3 基线上增加“真实用户体验强化平面”。目标不是改变后端 Agent Tool-first 架构，而是把既有能力重新组织成清晰、低认知负担、可截图和可人工审查的前端体验架构。

P4 架构主线：

```text
用户任务意图
→ Experience Shell
→ Conversation Plane
  → Empty State Suggested Prompts
  → Composer and Upload Dock
  → Free Local Dialogue / Multi-turn Follow-up
  → Chat Intent Router
  → Loading / Error Recovery
→ Full-size Desktop Workbench Controller
→ Workbench Plane
→ Artifact Review Plane
→ Export / Confirmation Plane
→ Evidence and Review Plane
```

## 0.1 P4 目标 UX 架构模块

```text
User
  → Chatbox Experience Shell
    → Workspace / Mode / Provider Strip
    → Conversation Plane
      → Empty State Suggested Prompts
      → Free Local Dialogue
      → Clarification / Status / Next-step Replies
      → Loading / Thinking Steps
      → Error Recovery Actions
    → Composer and Upload Dock
    → Full-size Desktop Workbench Controller
    → Workbench Plane / Mobile Drawer
    → Artifact Review Cards
    → Confirmation and Export Bar
    → Responsive Layout Controller
  → FastAPI Agent Service
    → Chat Routes
    → Workflow Routes
    → Artifact Routes
    → Export Routes
    → Provider Routes
  → ChatCore and Flow Orchestration
    → KeywordChatCore
    → PiAgentChatCore
    → Chat Intent Router
    → Context Snapshot
    → Real User Flow Controller
  → Domain Tool Layer
    → Profile / Project / Job / Application / Interview / Realtime / Review Tools
  → Artifact and Storage Layer
    → ArtifactVersion
    → Confirmation Model
    → Export Service
    → SQLite Workspace
  → Evidence Layer
    → Chrome Screenshots
    → HTML UX Report
    → Gemini Review Package
    → PRD Spec Review
```

## 0.2 P4 模块职责、输入输出和禁止职责

| 模块 | 核心职责 | 输入 | 输出 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Experience Shell | 建立产品语境和整体布局，承载 mode/provider/workspace 状态 | workspace、provider status、viewport | 页面骨架、当前模式、隐私提示 | 不做营销首页；不隐藏外部调用状态 |
| Empty State Suggested Prompts | 在 Chatbox 空状态内把求职任务变成可点击建议 | 用户意图、examples 状态、资料状态 | 填入 composer 或直接触发对话 | 不作为割裂的独立任务区；不伪造已完成任务 |
| Conversation Plane | 展示用户消息、自由追问、系统计划、loading、结果、失败和下一步 | chat messages、tool summaries、errors、execution state、context snapshot | 人类可读对话流 | 不把裸 JSON 作为唯一反馈；不展示内部堆栈；不静默失败；不把普通聊天误触发为工具写入 |
| Chat Intent Router | 区分自由对话、状态查询、下一步、澄清和明确工具意图 | message、session history、workspace snapshot | free dialogue reply、clarification、tool intent | 不默认外呼 provider；不在未确认时写 artifact；不把“还没准备好 JD”误判为解析 JD |
| Context Snapshot | 为连续对话提供当前 workspace 摘要 | latest job、latest package、artifact count、pending confirmations | 状态摘要、下一步提示上下文 | 不暴露敏感原文；不替代 artifact/source refs |
| Composer and Upload Dock | 支持输入、上传和快捷任务触发 | 文本、文件、快捷动作 | chat/workflow request | 不直接解析简历/JD；不直连 provider |
| Loading / Error Recovery | 告诉用户 Agent 正在执行什么，失败后如何恢复 | running step、error code、missing input | thinking steps、retry/upload/fill action | 不用 spinner 替代解释；不让用户重复点击 |
| Full-size Desktop Workbench Controller | 管理 1200/1440/1600/1920 桌面宽度的信息密度、列宽、空白、快捷任务和推进台关系 | viewport、workflow state、artifact count、conversation state | 桌面工作台布局、状态指标、快捷任务带、推进台摘要 | 不把窄屏布局简单放大；不留下布局错误造成的大面积空白；不污染人工浏览器 viewport |
| Workbench Plane / Mobile Drawer | 管理当前任务状态、阶段、下一步、产物和导出；移动端折叠为抽屉或次级面板 | workflow state、artifact summaries、viewport | 状态摘要、行动列表、产物导航 | 不承担聊天输入；不复制业务生成逻辑；不在 390px 下压缩对话 |
| Artifact Review Cards | 以求职语义展示产物摘要、待确认项、版本和主次操作 | artifact/version/source refs | 可读卡片、primary action、secondary actions | 不隐藏待确认项；不暴露内部 id 作为主标题；不让所有按钮同等权重 |
| Confirmation and Export Bar | 在导出前展示 blocking/warning/optional 确认边界 | current artifact version、questions_to_confirm | 导出 preflight 结果、文件入口 | 不绕过 blocking confirmation |
| Responsive Layout Controller | 管理 1200/1440/1600/1920/720/390 多档布局、滚动和输入区 | viewport、content density | 可用且顺手的布局 | 不让关键操作被遮挡或截断；不把单一宽度截图当作全尺寸验收 |
| Gemini Review Package | 给外部模型和人类独立审查前端方案 | UX brief、prototype、checklist | 审查意见和风险清单 | 不声称代码已实现；不替代真实截图验收 |

## 0.3 当前架构与 P4 目标差距

| 当前实现 | P4 目标 | 风险 | 验收证据 |
| --- | --- | --- | --- |
| 首屏以工程状态和分区为主 | Chatbox 空状态优先呈现 suggested prompts 和下一步 | 用户不知道从哪里开始，任务入口与对话割裂 | 初始页截图、5 秒理解审查、点击 suggested prompt 证据 |
| Chatbox 和推进台虽已分离但层级仍重 | 对话负责反馈，推进台负责状态和产物 | 用户误以为 chatbot 无响应 | 发送任务截图、错误态截图 |
| 缺少 thinking / executing 过渡 | 显示正在读取资料、对比 JD、生成草稿等步骤 | 用户重复点击或误判卡死 | loading 状态截图 |
| Chatbox 偏固定任务控制台 | 增加本地/mock 自由连续对话基线：普通追问、状态查询、下一步不会误触发工具 | 用户觉得对话被中断，或无意中写入 artifact | 自由追问两轮测试、浏览器截图、会话恢复证据 |
| 产物卡暴露 `job`、`match_report`、内部版本等术语 | 产物卡用“岗位解析 / 匹配报告 / 申请包草稿”等求职语义，并突出阻塞操作 | 用户读不懂产物价值或不知道先点哪个按钮 | 产物卡 before/after 截图 |
| Provider 标签可能被理解为正在外呼 | 明确“外部模型未调用（隐私安全）/ 外部调用需确认” | 隐私和费用误解 | provider 状态截图 |
| 1200px 以上桌面宽度仍可能像窄屏布局停靠在左侧 | 全尺寸桌面必须呈现完整工作台：对话区、状态指标、快捷任务、推进台摘要和下一步建议协同展示 | 大面积空白让用户误判页面未完成，人工体验审查不通过 | 1200/1440/1600/1920 Chrome 截图和人工体验审查记录 |
| 移动端可以运行但信息堆叠较重 | 390px 下 Conversation 优先，Workbench 收为底部抽屉或折叠面板 | 移动可用但不顺手 | 390px 关键路径截图 |
| 截图脚本可能遗留 Chrome viewport emulation | 截图脚本必须隔离或在 finally 清理 emulation/touch override | 人工审查者浏览器被污染，产生“窄屏布局占据大屏”的虚假体验证据 | 截图脚本清理逻辑、真实浏览器宽度检查、报告说明 |
| 验收报告有截图但缺少设计审查包 | 提供 Gemini 可独立审查的页面方案 | 外部审查上下文不足 | `docs/gemini-frontend-review-package/` |

## 0.4 P4 架构不变量

- Chatbox 仍是薄入口，只做输入、展示、确认、编辑和导出触发；
- 前端不得生成求职内容，不得直接写 SQLite，不得直连 provider；
- PiAgent / ChatCore 仍只负责意图和工具计划，业务写入仍由 Python Domain Tools 完成；
- 本地连续对话只作为 mock/offline 基线，不得被描述为完整 provider-backed 自由智能聊天；
- Chat Intent Router 只有在明确工具意图或用户确认后才允许触发 Domain Tools 写入 artifact；
- source refs、questions_to_confirm、artifact version、export preflight 不得因 UX 简化而丢失；
- mock provider 仍是默认验收基线，external provider 仍需用户确认；
- realtime 仍是 text-in / hint-out，不进入 ASR、会议平台或逐字代答；
- P4 不能用更好看的静态原型替代真实前端实现和 Chrome 截图验收。

## 0.5 P4 架构验收问题

每个 P4 实现 PR 或阶段验收必须回答：

- 用户是否能在首屏判断下一步？
- Suggested prompts 是否与 composer 形成闭环，而不是割裂任务区？
- Conversation Plane 是否对有效输入、缺资料和失败都有反馈？
- Conversation Plane 是否能承接普通自由追问、状态查询和下一步问题，而不误触发工具？
- Chat Intent Router 是否能区分“聊方向”与“解析 JD / 生成申请包”等明确工具意图？
- Conversation Plane 是否有 loading / thinking / executing 状态和错误恢复 action？
- Full-size Desktop Workbench Controller 是否覆盖 1200/1440/1600/1920，且没有布局错误造成的大面积空白？
- Workbench Plane 是否只展示状态、产物、确认项、版本和导出，且移动端不会压缩 Chatbox？
- Artifact Review Cards 是否保留 source refs 和 questions_to_confirm？
- Artifact Review Cards 是否区分 primary / secondary action？
- Provider 状态是否明确本次是否外呼，并使用用户语言？
- 390px 下输入、消息、当前任务和产物操作是否仍可达？
- Chrome 截图脚本是否隔离或清理 viewport emulation，避免污染人工审查者浏览器？
- mode toggle、状态区和按钮是否具备必要 ARIA 状态？
- Gemini 审查包和 HTML 报告是否明确“设计方案 / 已实现 / 未验证”的边界？

以下 P3 内容作为已完成基线和历史背景保留。

## 0.6 历史 P3 阶段架构增补

P3 在 P0/P1/P2 基线上增加“真实用户 Chatbox 体验平面”。目标不是新增底层入口，而是把已有 Agent Tool 能力变成用户能直接完成的求职工作台。

本阶段架构文档不再把阶段顺序作为主线。主线改为：

```text
模块职责
→ 模块输入 / 输出
→ 模块之间的调用关系
→ 数据所有权
→ 安全边界
→ 验收证据
```

## 0.1 目标架构模块总览

```text
User
  → Chatbox Client
    → Conversation View
    → Composer / Upload Entry
    → Workbench Panel
    → Artifact Cards
    → Mode / Provider Status
  → FastAPI Agent Service
    → Chat Routes
    → Workflow Routes
    → Artifact Routes
    → Export Routes
    → Provider Routes
  → ChatCore Facade
    → KeywordChatCore
    → PiAgentChatCore
  → Flow Orchestration
    → Intent Router
    → Real User Flow Controller
    → P2 Demo Workflow Orchestrator
  → Domain Tool Layer
    → Profile Tools
    → Project Tools
    → Job Tools
    → Application Tools
    → Interview Tools
    → Realtime Hint Tools
    → Review / Training Tools
  → Provider and Contract Layer
    → Provider Policy Gate
    → Mock / Fixture Provider
    → OpenAI-compatible Provider
    → Prompt Contract
    → Schema Validation
  → Artifact and Storage Layer
    → Artifact Service
    → Artifact Versioning
    → Confirmation Model
    → Export Service
    → SQLite Workspace
    → Local Files / Exports
  → Evidence Layer
    → Pytest Eval Gates
    → Chrome Screenshots
    → HTML Acceptance Reports
```

## 0.2 模块职责和禁止职责

| 模块 | 核心职责 | 输入 | 输出 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox Client | 呈现对话、上传、状态、产物和导出入口 | 用户消息、文件、按钮操作、API 响应 | UI 状态、API 请求、截图证据 | 不生成求职内容；不绕过后端确认；不保存 API Key |
| Conversation View | 展示消息、计划、执行结果和错误 | chat messages、tool result summary | 用户可读消息流 | 不展示不可解释的裸 JSON 作为唯一结果 |
| Composer / Upload Entry | 输入文本、上传资料、触发发送 | 文本、文件、快捷动作 | chat/workflow 请求 | 不直接解析简历或 JD |
| Workbench Panel | 展示阶段、下一步、产物、确认项、版本和导出 | artifact summary、workflow state | 可操作工作台 | 不承担聊天输入；不复制业务逻辑 |
| Artifact Cards | 管理单个产物的摘要、source refs、确认项和版本 | artifact、artifact_version | edit/regenerate/export 操作 | 不隐藏待确认项；不把 warning 变成 confirmed |
| FastAPI Agent Service | 提供 HTTP API、认证前边界、请求校验 | HTTP 请求、workspace id | 结构化响应、错误码 | 不把 provider 原始敏感内容写入日志 |
| Chat Routes | 接收对话请求并调用 ChatCore | session id、message、attachments | assistant message、tool/action refs | 不直接执行复杂业务工具 |
| Workflow Routes | 执行示例或真实用户流程 | workflow request、mode | steps、artifacts、exports、summary | 不伪造完成步骤 |
| Artifact Routes | 读取、确认、编辑、版本切换、regenerate | artifact id、version id、patch | artifact state | 不覆盖旧版本 |
| Export Routes | 预检并导出当前版本 | artifact version、format | export file path/download token | 不写 workspace 外路径 |
| Provider Routes | 显示 provider 状态和测试连接 | env config、provider preset | provider status | 不回传 API Key |
| ChatCore Facade | 隔离前端对具体编排器的依赖 | message context | intent/tool plan | 不写业务数据 |
| KeywordChatCore | 离线可验收 fallback 编排 | message text | deterministic plan | 不替代真实 provider-backed 产物 |
| PiAgentChatCore | 接入 Pi Agent Core 做意图和工具计划 | message、tool catalog | planned tool invocations | 不直接写 SQLite；不绕过 Python tools |
| Real User Flow Controller | 把自然语言任务转成可执行工具序列 | intent、workspace state | tool execution plan | 不越过确认/安全边界 |
| Domain Tools | 执行业务能力和写入领域数据 | typed tool input | typed tool output、artifact refs | 不访问 workspace 外文件 |
| Provider Policy Gate | 决定是否允许 provider 调用 | provider mode、consent、data class | allow/deny、redacted input | 不默认外部调用 |
| Provider Runtime | 调用 mock/fixture/external provider | prompt contract input | provider output | 不返回未校验内容给业务层 |
| Prompt Contract / Schema Validation | 约束 LLM 输入输出结构 | schema、raw output | validated output or error | 不把 malformed output 写库 |
| Artifact Service | 统一 artifact 元数据和版本 | domain object、version content | current version、history | 不丢 source refs / questions_to_confirm |
| Export Service | 生成 Markdown/DOCX 等文件 | current/selected version | local export file | 不绕过 blocking confirmation |
| SQLite Workspace | 本地持久化业务状态 | validated writes | query results | 不保存 API Key、完整敏感 raw response |
| Evidence Layer | 证明实现与 PRD 一致 | tests、screenshots、reports | acceptance evidence | 不做未执行声明 |

## 0.3 组件关系和依赖方向

依赖方向必须保持单向：

```text
Chatbox Client
→ FastAPI Routes
→ ChatCore / Flow Controller
→ Domain Tools
→ Provider / Artifact / Export / Storage
```

允许的反向关系只有“状态读取”和“事件结果返回”：

```text
Storage / Artifact
→ API response
→ Workbench rendering
```

禁止关系：

- Chatbox 直接调用 Provider；
- Chatbox 直接写 SQLite；
- PiAgent 直接写 SQLite；
- Provider Runtime 直接写 artifact；
- Export Service 从未校验 provider raw output 导出；
- Workflow 在失败后伪造后续步骤完成；
- 任何模块把完整 API Key、完整简历、完整 JD、完整 transcript 或完整 raw response 写入日志。

## 0.4 关键端到端控制流

### 0.4.1 用户发起求职任务

```text
Composer
→ Chat Route
→ ChatCore Facade
→ PiAgentChatCore 或 KeywordChatCore
→ Real User Flow Controller
→ Domain Tool Executor
→ Artifact Service
→ Conversation View + Workbench Panel
```

验收关注：

- 用户发送后必须有可见响应；
- 缺少资料时返回下一步，而不是静默失败；
- 执行计划和产物引用必须可追踪。

### 0.4.2 资料导入和事实抽取

```text
Upload Entry
→ File / Workspace Route
→ Document Store
→ profile.extract_facts / project.create_card
→ Provider Policy Gate
→ Provider Runtime or Mock
→ Schema Validation
→ CareerFact / SkillEvidence / TechProject
→ Artifact Version
→ Workbench Panel
```

验收关注：

- source refs 必须指向资料来源；
- 不确定内容进入 questions_to_confirm；
- 未确认内容不得作为确定事实导出。

### 0.4.3 JD 分析和申请包生成

```text
Conversation or Workflow request
→ job.parse_jd
→ job.match_profile
→ application.create_package
→ Artifact Service
→ Export Preflight
→ Markdown / DOCX Export
```

验收关注：

- MatchReport 必须区分 strengths、gaps、next actions；
- ApplicationPackage 必须保留 source refs 和 pending confirmations；
- blocking confirmation 未解决不得导出。

### 0.4.4 Artifact 编辑、重新生成和导出

```text
Artifact Card action
→ Artifact Route
→ Artifact Service
→ create new artifact_version
→ update current_version_id
→ Export Route
→ Export Service
→ workspace/exports
```

验收关注：

- 编辑和 regenerate 必须产生新版本；
- 旧版本不可覆盖；
- 导出只读取 current 或用户显式选择版本；
- 导出只写 workspace `exports/`。

### 0.4.5 Realtime 文本提示

```text
Text question
→ realtime.generate_hint
→ Prompt Contract
→ Safety boundary
→ structured hint
```

验收关注：

- P3 realtime 仍是 text-in / hint-out；
- formal_assist 不返回逐字代答；
- 不接入 ASR、系统音频、会议平台或视频解析。

## 0.5 数据所有权

| 数据 | 所有者 | 主要读者 | 关键不变量 |
| --- | --- | --- | --- |
| Workspace | Workspace Service | 所有后端服务 | 所有文件和导出必须在 workspace 内 |
| Chat Session / Message | Chat Service | Chatbox、ChatCore | 消息可恢复，不含 API Key |
| Document | File / Document Service | Profile、Project、Job tools | source refs 可追踪 |
| CareerFact / SkillEvidence | Profile Tools | Match、Application、Interview | 低置信事实必须待确认 |
| TechProject | Project Tools | Match、StoryCard、Interview | 项目描述必须有来源 |
| Job / MatchReport | Job Tools | Application、Workbench | must-have / nice-to-have / gaps 可解释 |
| ApplicationPackage | Application Tools | Export、Workbench | 导出前执行 confirmation preflight |
| StoryCard / InterviewPrep | Interview Tools | Realtime、Review | 不编造不存在项目 |
| Artifact / ArtifactVersion | Artifact Service | Workbench、Export | version 不覆盖，current 指向有效版本 |
| Export File | Export Service | User download | 只写 workspace/exports |
| ProviderInvocation | Provider Runtime | Audit / Debug | 只存摘要和错误，不存敏感原文 |

## 0.6 质量属性和架构验收

- 可维护性：前端只做展示和触发，业务逻辑在 Domain Tools；
- 可替换性：ChatCore 可在 Keyword 和 PiAgent 之间切换；
- 安全性：Provider Policy Gate 是外部调用唯一出口；
- 可追溯性：所有用户可见产物必须保留 source refs 或 artifact refs；
- 可恢复性：chat session、artifact 和 export 均可从 workspace 恢复；
- 可验收性：每条关键体验必须有测试或 Chrome 截图证据；
- 可扩展性：MCP/CLI/ASR 未来只能通过 API/Tool 层接入，不改变 P3 Chatbox-first 核心。

P3 目标架构按 6 个平面验收：

```text
体验壳层
  → 顶部状态、workspace 状态、provider 状态、示例/真实资料模式

对话平面
  → 消息流
  → 上传入口
  → JD / 申请包 / 面试准备自然语言意图
  → 可见响应、计划、执行状态、错误说明

推进台平面
  → 当前阶段
  → 待办和下一步
  → artifact 摘要、确认项、版本、导出
  → 不承载业务生成逻辑

编排平面
  → ChatCore Facade
  → PiAgentChatCore / KeywordChatCore
  → Real User Flow Controller
  → P2 Workflow Orchestrator

业务能力平面
  → profile / project / job / application / interview / realtime / training tools
  → Provider Policy Gate
  → Provider Runtime
  → Prompt Contract / Schema Validation
  → Artifact Versioning / Export Service

本地数据与验收平面
  → SQLite workspace
  → local files / exports
  → tool/provider invocation redaction
  → pytest eval
  → Chrome screenshots at desktop / narrow / mobile
  → HTML acceptance reports
```

当前完成状态：

- 绿色基线：P0/P1 工具链、Provider Runtime、Artifact Versioning、Export、PiAgent 编排、P2 Workflow Orchestrator、P2 HTML 报告；
- P3 正在完成：Chatbox 与推进台分离、真实用户输入响应、模式边界、响应式 UX、截图验收；
- P4+ 后续：MCP、CLI、ASR、会议平台、自动申请、SaaS。

P3 关键架构约束：

- Chatbox 前端不得复制业务生成逻辑，只能调用后端 chat/workflow/artifact/export API；
- 对话区负责输入和反馈，推进台负责状态和产物，二者必须视觉和职责分离；
- 真实资料模式默认仍使用本地 mock provider，外部 provider 必须显式 opt-in；
- provider 调用和个人资料处理必须经过安全边界，不能把 API Key、完整简历、完整 JD 或 transcript 写入日志；
- responsive layout 必须作为架构验收项，而不是事后美化；
- P3 自动验收可以使用 examples 真实感数据，真实个人资料只允许人工确认后进入验收。

P3 目标数据流：

```text
User action
→ Chatbox Conversation Plane
→ /api/chat/sessions/{id}/messages 或 /api/workflows/*
→ ChatCore Facade
→ PiAgent / Keyword intent plan
→ Real User Flow Controller
→ Domain Tools
→ Provider Policy Gate
→ Provider Runtime or Mock
→ Schema validation
→ Artifact Version / Export
→ Conversation response + Workbench state
→ Chrome screenshot evidence
```

以下 P2 架构内容作为已完成基线和历史背景保留。

## 1. 架构目标

P2 目标是在 P0/P1 已完成的本地优先、Chatbox-first、Agent Tool-first 架构上，新增 Experience Flow 层，把底层能力组合成完整端到端用户体验。

P2 架构必须满足：

- Chatbox 继续只负责输入、展示、确认、编辑、导出触发和体验流程展示；
- Experience Flow 只编排现有 Domain Tools，不复制业务生成逻辑；
- Pi Agent Core 继续负责 Chat Intent Router / Domain Tool Planner 层；
- Python JobPilot Domain Tools 继续负责真实业务执行、写库、artifact 和 workspace 边界；
- Provider 默认仍为 mock，本阶段不默认触发真实外部调用；
- OpenAI-compatible provider 仍是 opt-in；
- workflow 输出必须来自真实工具执行结果；
- artifact 编辑和 regenerate 仍版本化，不覆盖旧产物；
- 导出只读取 current/selected version，只写 workspace `exports/`；
- P2 不引入 MCP、CLI、ASR、会议平台或 SaaS。

## 2. 当前架构实现

P1 当前已实现：

```text
React Chatbox
  → FastAPI Agent Service
    → ChatCore Facade
      → KeywordChatCore fallback
      → PiAgentChatCore optional
        → Node Pi Agent Core
        → jobpilot_orchestrate AgentTool
    → Python Domain Tool Executor
    → Domain Tools
      → profile / project / job / application / interview / realtime / training
    → LLM Provider Runtime
      → MockProvider / FixtureProvider / OpenAI-compatible opt-in
    → Prompt Contract / Schema Validation
    → Artifact Versioning / Regenerate
    → Export Service
    → SQLite Workspace / files / exports
    → pytest eval gates / frontend build / Chrome screenshot evidence
```

P2 已开始实现：

- `services/workflows/p2_demo.py`；
- `POST /api/workflows/p2-demo/run`；
- Chatbox `端到端体验路径` 工作流面板；
- `?autorun=1` 本地可见验收入口；
- 人类可读 artifact 摘要；
- P2 guided demo flow eval。

当前差距：

- P2 HTML 最终验收报告尚未完成；
- 截图证据需要整理到最终报告；
- 用户上传真实资料的分步引导仍弱于 examples 一键路径；
- artifact 摘要仍是最小实现，后续可继续增强；
- drawio 需要从 P1 图切换到 P2 端到端体验架构图。

## 3. P2 目标架构总览

```text
Chatbox Client
  → Experience Flow Panel
    → step list
    → current state
    → next action
    → run examples demo flow
    → artifact summary
    → exports summary
  → Artifact Cards
    → human-readable summary
    → source refs
    → confirmations
    → versions
    → edit / regenerate / export

FastAPI Agent Service
  → Workspace / File / Chat routes
  → Provider routes
  → Artifact version routes
  → Application export routes
  → Workflow routes
    → POST /api/workflows/p2-demo/run

Workflow Orchestrator
  → load examples
  → save documents
  → extract facts
  → create project card
  → parse JD
  → match profile
  → create application package
  → export Markdown + DOCX
  → prepare interview
  → realtime text hint
  → review transcript
  → collect steps / artifacts / exports / summary

Domain Tool Executor
  → profile / project / job / application / interview / realtime / training
  → provider call boundary
  → schema validation boundary
  → artifact writer
  → tool_invocation logger

Provider Runtime
  → MockProvider default
  → FixtureProvider tests
  → OpenAI-compatible opt-in
  → redaction / input summary
  → timeout / retry / error mapping

Artifact / Export / Storage
  → artifact
  → artifact_version
  → regenerate lineage
  → export preflight
  → Markdown / DOCX
  → SQLite workspace
  → local files / exports

Eval / Evidence
  → pytest
  → frontend build
  → P2 guided flow eval
  → Chrome screenshots
  → P2 HTML acceptance report
```

## 4. 分层职责

| 层 | 职责 | 代码区域 |
| --- | --- | --- |
| Chatbox Client | 展示工作流、产物、版本、待确认项和导出入口 | `apps/chatbox/src/main.tsx`, `styles.css` |
| Experience Flow Panel | 展示步骤、下一步、执行结果、导出文件 | `apps/chatbox/src/main.tsx` |
| FastAPI Routes | 暴露 workflow、artifact、chat、export 等 HTTP API | `services/api/main.py`, `schemas.py` |
| Workflow Orchestrator | 串联 examples 和 Domain Tools，生成体验摘要 | `services/workflows/p2_demo.py` |
| ChatCore / Pi Agent Core | 自然语言 intent/tool plan 编排 | `services/chat/*`, `services/chat/pi_node_bridge.mjs` |
| Domain Tools | 执行真实求职业务、写库和产物 | `services/tools/jobpilot.py` |
| Provider Runtime | mock/fixture/openai-compatible 结构化生成边界 | `services/llm/provider.py`, `contracts.py` |
| Artifact Versioning | 记录 current version、edit、regenerate lineage | `services/storage/db.py`, `jobpilot.py` |
| Export Service | Markdown/DOCX 导出和 preflight | `services/tools/jobpilot.py` |
| Storage | SQLite workspace、本地 files/exports | `services/storage/*` |
| Evidence Gates | 测试、截图、HTML 报告和 PRD 检视 | `tests/evals`, `docs/reports` |

## 5. 控制流与数据流边界

```text
用户控制流：
Chatbox → Workflow Panel → FastAPI Workflow Route → Workflow Orchestrator

业务执行流：
Workflow Orchestrator → Domain Tools → Artifact / Business Tables → Export Service

模型生成流：
Domain Tools → Prompt Contract → Provider Runtime → schema validation → structured output

证据流：
Tests / Chrome screenshots → stage review → P2 HTML report → human review
```

关键边界：

- Chatbox 不拼业务 prompt；
- Workflow Orchestrator 不直接写数据库，只调用 Domain Tools；
- Provider Runtime 不直接写数据库；
- Domain Tools 是唯一业务写入边界；
- Export Service 只写 workspace `exports/`；
- screenshots 证明可见体验，不替代业务测试；
- examples 数据是匿名真实感数据，不等于真实个人资料验收。

## 6. 失败回滚边界

P2 workflow 失败时：

- 已完成步骤可以保留在 workspace 中；
- API 必须返回失败步骤和可理解错误；
- 不得删除用户已有 workspace；
- 不得覆盖旧 artifact version；
- 不得因为某一步失败而伪造后续完成状态；
- HTML 报告必须标注失败或未验收范围。

## 7. 后续扩展边界

以下进入 P4+ 或独立阶段：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台；
- 自动申请；
- SaaS 多租户；
- 默认真实外部 Provider；
- 岗位数据源抓取和 Offer 分析。
