# P5 自动化验收候选审计

日期：2026-06-26
阶段：P5 真实资料本地闭环
结论：本地/mock + 脱敏 fixture 自动化候选通过；按本审计生成时口径，P5 尚未冻结，真实授权资料路径和人工体验审查仍是阻塞项。按 2026-06-27 最新口径，P5-REAL/P5-Freeze 已冻结延期到 P7-post 复验。

当前状态附注（2026-06-27）：用户已确认 P5-REAL/P5-Freeze 冻结延期到 P7 完成后复验。本审计保留为 P5 自动化候选历史证据，不再作为当前阶段继续推进 P5-Freeze 的执行入口；不得据此声明真实个人资料路径或真实外部 provider 默认路径已通过。

## 1. 审计范围

本审计评估 P5 在当前代码和证据下是否可以进入真实授权资料验收与人工体验冻结前检查。

纳入范围：

- 本地 workspace 内资料导入、资料解析、JD 解析、匹配报告；
- `questions_to_confirm` blocking/warning/optional 确认链路；
- 申请包生成、编辑后重新阻塞、确认后 Markdown/DOCX 导出；
- 围绕当前资料、JD 和申请包的本地连续追问；
- P5 HTML 自动化报告、截图证据、PRD 规格检视和未验证范围声明。

排除范围：

- 默认真实外部 provider；
- provider-backed 自由智能聊天；
- 未授权真实个人资料；
- SaaS、ASR、会议平台、自动投递、MCP/CLI、最终产品化发布。

## 2. 自动化候选证据

| 证据 | 结果 | 说明 |
| --- | --- | --- |
| P5 本地闭环 eval | `6 passed` | 覆盖本地资料闭环、阻塞确认、编辑后重新阻塞、自由追问不写 artifact、目标 JD 申请包路由、source refs preflight |
| P5 报告 eval | passed | 检查 HTML 报告、截图、未验证范围和虚假验收边界 |
| P5 HTML 报告 | `docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html` | 使用脱敏 fixture 和真实界面截图，不声明真实个人资料路径通过 |
| 当时全量回归 | `79 passed, 1 warning` | P0-P4 回归未发现失败；该行是本审计生成时的历史证据 |
| 最新增强证据 | `88 passed, 1 warning` | 见 `docs/active/stage-reviews/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_AUDIT.md` 和 `docs/reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html` |
| 前端构建 | passed | `npm --prefix apps/chatbox run build` 通过 |
| drawio XML parse | passed | 当前 drawio 为 6 页，未超过 8 页 |

## 3. PRD 规格检视

| PRD 要求 | 自动化候选状态 | 审计意见 |
| --- | --- | --- |
| 资料导入、解析摘要、source refs、待确认项 | 脱敏 fixture 通过 | 真实资料路径未提供，不能声明真实个人资料通过 |
| JD 解析、匹配报告、缺口和下一步 | 自动化通过 | 仍需真实授权 JD 局部片段复核 |
| blocking confirmation 影响导出 | 自动化通过 | 当前实现为硬门槛，符合 P5 |
| 申请包编辑、版本、导出 | 自动化覆盖核心路径 | UI 中编辑/再生成/版本切换仍需人工体验复核 |
| 本地多轮追问不误写 artifact | 自动化通过 | 不代表 provider-backed 自由智能聊天 |
| 报告脱敏和未验证范围 | 自动化通过 | 真实资料报告仍需逐张截图复核 |

## 4. 阻塞项

P5 不得冻结，直到以下条件全部闭合：

- 用户提供明确本地脱敏真实资料路径和允许展示字段；
- 真实资料验收只读取用户指定路径，不擅自搜索个人目录；
- 真实资料截图和报告不包含联系方式、账号、API Key、私密链接或未授权长原文；
- P5 人工体验审查清单完成；
- 冻结前再次运行 pytest、frontend build、drawio XML parse；
- P5 final closure audit 明确不包含 P6/P7/P8 能力。

## 5. 审计结论

当前 P5 可以进入“真实授权资料验收准备”和“人工体验审查准备”，但不得声明 P5 已冻结。若用户暂不提供真实资料路径，P5 可以保持为自动化候选状态，后续优先转入真实资料路径确认或 P6 opt-in 规划。
