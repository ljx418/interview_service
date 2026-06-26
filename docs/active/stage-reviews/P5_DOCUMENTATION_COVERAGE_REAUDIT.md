# P5 文档覆盖度复审

日期：2026-06-26
阶段：P5 真实资料本地闭环 / 文档开发阶段
结论：本轮修订后，文档可以支撑本阶段剩余开发、验收和冻结审计；真实资料路径授权仍是执行阻塞项，不是文档缺口。

## 1. 复审范围

本次复审覆盖以下文档族：

- `README.md`
- `TODO.md`
- `docs/active/00_README.md`
- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `docs/active/stage-reviews/P5_PRE_FREEZE_AUTOMATED_CANDIDATE_AUDIT.md`
- `docs/active/stage-reviews/P5_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md`
- `docs/active/stage-reviews/P5_FREEZE_EXIT_AUDIT_PLAN.md`
- `docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html`
- `docs/reports/P5_SYNTHETIC_PROFILE_REVIEW.html`

## 2. 多轮独立审计结论

### 2.1 PRD 规格审计

结论：通过。

已覆盖的 P5 核心体验：

- 本地导入简历、项目说明和经历材料。
- 粘贴或导入目标 JD。
- 展示资料解析、JD 解析、source refs 和待确认项。
- 使用 blocking/warning/optional 管理事实确认。
- 生成申请包、编辑、重新阻塞、确认后导出 Markdown/DOCX。
- 围绕当前资料、JD 和申请包继续多轮追问。
- 通过脱敏截图、HTML 报告、PRD 规格检视和人工体验审查完成验收。

未作为 P5 出门条件的内容也已明确：

- MCP Server、CLI、ASR、会议平台、自动投递、SaaS、多租户、Billing。
- 默认真实外部 provider。
- provider-backed 自由智能聊天，该能力转入 P6 opt-in。

### 2.2 目标架构审计

结论：通过。

目标架构已把 P5 关键能力映射到具体实现实体：

| 层级 | 代码或文档实体 | 覆盖结论 |
| --- | --- | --- |
| 前端工作台 | `apps/chatbox/src/App.jsx` 及其 UI 状态模型 | 已支撑三栏工作台、状态机、资料导入、JD 输入、产物展示、确认和导出入口。 |
| API 层 | `services/api/main.py` | 已支撑 workspace、chat、artifact、workflow、export 等 HTTP 入口。 |
| 编排层 | `services/chat_core.py`、PiAgent adapter | 已支撑本地/mock 连续对话和工具路由；真实 provider 不默认启用。 |
| Domain Tools | `services/tools.py` 等工具模块 | 已支撑资料解析、JD 解析、申请包、面试准备和事实安全。 |
| 数据层 | SQLite workspace schema | 已支撑 chat session、artifact、tool invocation、确认状态和版本记录。 |
| 证据层 | `scripts/browser_acceptance_*.mjs`、`docs/reports/*` | 已支撑多视口截图、HTML 报告和 PRD 规格检视。 |
| 文档层 | active docs、stage reviews、drawio | 已支撑阶段计划、验收门槛、风险边界和冻结审计。 |

### 2.3 验收门槛审计

结论：通过，但执行仍依赖用户授权真实资料路径。

已具备的验收门槛：

- 本地/mock 自动化候选报告已完成。
- P5-REAL 前置条件已明确：用户提供本地路径、允许字段、脱敏范围。
- P5-Freeze 前置条件已明确：真实授权资料审查、人工体验记录、pytest、前端 build、drawio parse 和 final closure audit。
- 禁止虚假验收：不得把脱敏 fixture 报告写成真实个人资料通过；不得把 P6 provider opt-in 写成 P5 默认能力。

### 2.4 drawio 审计

结论：通过。

`docs/active/jobpilot-stage-gap-and-acceptance.drawio` 的设计方向已被用户认可。当前图要求：

- 页数不超过 8。
- 中文书写。
- 覆盖目标架构与当前架构差异、开发及验收计划、项目里程碑、验收门槛和出门条件。
- 使用色块表达已实现、待新增、需修改、人工确认等状态。
- 架构条目必须是具体代码实现实体，不使用模糊能力描述替代工程结构。

### 2.5 现实性审计

结论：通过，剩余风险已被显式标注。

未发现以下高风险虚假口径：

- 声称 P5 已最终冻结。
- 声称真实个人资料路径已通过。
- 声称真实外部 provider 默认路径已通过。
- 声称 SaaS、自动投递、ASR、会议平台或 MCP 已属于 P5 出门条件。

## 3. 覆盖矩阵

| 开发或验收目标 | 文档覆盖 | 支撑程度 | 备注 |
| --- | --- | --- | --- |
| P5 本地资料导入 | PRD、目标架构、验收门槛、追踪矩阵 | 完整 | 真实路径待用户提供。 |
| P5 JD 解析和匹配报告 | PRD、目标架构、P5 自动化报告 | 完整 | 已有脱敏 fixture 证据。 |
| P5 事实确认闭环 | PRD、验收门槛、追踪矩阵、报告 | 完整 | blocking/warning/optional 口径一致。 |
| P5 申请包编辑和导出 | PRD、目标架构、验收门槛 | 完整 | 编辑后重新阻塞已纳入验收。 |
| P5 连续追问 | PRD、P4C/P5 报告、目标架构 | 完整 | provider-backed 自由智能聊天转入 P6。 |
| P5 真实授权资料验收 | 验收门槛、人工清单、final closure plan、合成资料审核页 | 计划完整，执行待授权 | 用户未提供路径前不得执行。 |
| P5 冻结审计 | final closure audit plan、TODO、README | 完整 | 需在 P5-REAL 后执行。 |
| P6 provider opt-in | roadmap、PRD 边界、README | 足够规划 | 不属于 P5 默认出门条件。 |
| P7 产品化 Beta | roadmap、README/TODO 后续计划 | 足够规划 | 需在 P5/P6 后细化。 |

## 4. 仍未实现或未验收内容

以下内容不是当前文档缺口，但仍是项目未完成开发或验收项：

1. P5-REAL：真实授权资料路径、本地导入、脱敏报告和人类审查尚未完成。
2. P5-Freeze：真实资料审查完成后的最终回归、人工体验记录和 final closure audit 尚未完成。
3. P6：真实外部 provider opt-in、API Key 边界、provider-backed 自由智能聊天和失败降级尚未启动。
4. P7：产品化 Beta 的 workspace 生命周期、备份/迁移、监控、隐私审计和发布流程尚未启动。
5. P8+：ASR、会议平台、自动投递、SaaS、多租户、Billing 等高风险能力仍为后续候选，不进入 P5。

## 5. 能否完整支撑本阶段开发

结论：可以。

原因：

- 本阶段剩余工作已经被拆分为 P5-REAL 和 P5-Freeze，且每项都有明确输入、执行动作、验收证据和打回条件。
- 文档已经明确哪些能力已自动化候选通过，哪些能力仍待真实授权，避免把测试 fixture 结果冒充真实资料验收。
- 目标架构、PRD、验收门槛、追踪矩阵和 drawio 之间没有发现关键概念冲突。
- 合成资料审核页补齐了真实资料验收前的资料结构确认材料。

## 6. 是否能完整达成预设目标

结论：在用户提供真实资料路径和允许展示字段后，可以支撑达成 P5 预设目标；在用户未授权前，只能达成“自动化候选 + 文档准备完成”，不能冻结 P5。

P5 可达成目标：

- 用户在本地完成真实资料和目标 JD 的资料闭环。
- 用户能看到来源、待确认项、阻塞原因和导出门槛。
- 用户能生成、编辑、确认并导出申请包。
- 用户能围绕当前资料继续多轮追问。
- 项目能用脱敏报告和截图证据说明实际体验路径。

P5 不承诺目标：

- 不承诺真实外部 provider 默认可用。
- 不承诺 SaaS、自动投递、ASR、会议平台或多租户。
- 不承诺未经用户授权的个人资料扫描或展示。

## 7. 需要 ChatGPT 审计吗

建议：非必须，但可以做轻量外部审计。

判断：

- 本地文档已经足以指导下一步 P5-REAL 和 P5-Freeze。
- 外部审计的价值在于发现概念冲突、过度承诺和验收口径虚假，不应替代用户对真实资料路径和隐私展示范围的授权。
- 若发送给 ChatGPT，应使用 `P5_EXTERNAL_REVIEW_REVISION_AUDIT.md` 中列出的 17 个文件，不发送真实资料、`.env`、API Key、日志、数据库或账号凭据。

## 8. 出门判断

文档开发阶段出门结论：通过。

后续进入自动化执行前的阻塞项：

1. 用户提供明确本地真实资料路径。
2. 用户确认允许展示字段、脱敏范围和报告可见内容。
3. 若涉及真实外部 provider，必须另行确认 provider、API Key 配置方式、调用次数、费用和报告脱敏范围；否则 P5 默认继续使用本地/mock。
