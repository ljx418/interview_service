# P5 外部意见修订审计

日期：2026-06-26
阶段：P5 真实资料本地闭环 / 文档开发阶段
状态：已落盘为后续自动化开发和真实资料验收的前置审计依据

## 1. 输入意见

用户给出的外部意见与约束如下：

1. 先生成一份合成简历和需要提供的背景资料，用 HTML 页面列出，供人类审核。
2. 已认可 `docs/active/jobpilot-stage-gap-and-acceptance.drawio` 给出的开发方向。
3. 重新阅读 PRD 和目标架构，评估当前文档是否能完整支撑本阶段开发。
4. 若文档不能完整指导后续开发，则继续文档开发直到满足后续全部开发计划。
5. 给出剩余开发及验收计划、待验收审查结论，以及可交给 ChatGPT 审计的文档路径，文档数小于 20。
6. 当前仍为文档开发阶段，不进入实际代码开发。

## 2. 修订动作

| 动作 | 文件 | 结论 |
| --- | --- | --- |
| 新增合成资料审核页 | `docs/reports/P5_SYNTHETIC_PROFILE_REVIEW.html` | 已完成。页面明确标注人物、公司、联系方式和项目均为合成示例，不代表真实个人资料验收通过。 |
| 新增外部意见修订审计 | `docs/active/stage-reviews/P5_EXTERNAL_REVIEW_REVISION_AUDIT.md` | 已完成。记录本轮外部意见、采纳方式、风险边界和审计包。 |
| 新增 P5 文档覆盖复审 | `docs/active/stage-reviews/P5_DOCUMENTATION_COVERAGE_REAUDIT.md` | 已完成。重新评估 PRD、目标架构、验收门槛、drawio 和 P5 final closure plan 的支撑度。 |
| 更新索引 | `README.md`、`TODO.md`、`docs/active/00_README.md` | 已完成。增加新文档入口，维持 P5 尚未冻结、P5-REAL 待授权的口径。 |

## 3. 采纳矩阵

| 外部意见 | 采纳方式 | 是否需要代码开发 |
| --- | --- | --- |
| 生成简历和背景资料审核页 | 使用合成候选人、合成目标 JD、资料清单、待确认问题和验收路径制作 HTML。 | 否 |
| 重新评估文档支撑度 | 以 PRD、目标架构、里程碑、验收门槛、追踪矩阵、drawio 和 P5 审计文档为输入完成复审。 | 否 |
| 列出剩余开发及验收计划 | 保留 P5-REAL、P5-Freeze、P6 provider opt-in、P7 产品化 Beta、P8+ 高风险能力的分层计划。 | 否 |
| 判断是否需要 ChatGPT 审计 | 建议做轻量外部审计，但不作为本地文档阶段阻塞项。 | 否 |

## 4. 当前文档支撑结论

结论：完成本轮修订后，当前文档可以完整支撑 P5 剩余自动化开发、真实资料验收准备和 P5 冻结审计，但不能替代真实资料授权与人工体验审查。

支撑充分的部分：

- PRD 已明确 P5 的目标体验：本地导入资料、导入 JD、事实确认、申请包生成、编辑后重新阻塞、确认后导出和连续追问。
- 目标架构已把前端页面、API、Domain Tools、Provider Runtime、本地 workspace、artifact、export、browser evidence 和 audit docs 串联到具体代码实体。
- 验收门槛已区分本地/mock 自动化候选、P5-REAL 真实授权资料验收和 P5-Freeze final closure audit。
- drawio 页数低于 8 页，覆盖目标架构与当前架构差异、开发计划、里程碑、验收门槛和出门条件。
- 合成资料审核页补齐了真实资料验收前的人类资料形态审查入口。

仍需人工或用户授权的部分：

- 用户尚未提供明确本地真实资料路径。
- 真实资料报告允许展示字段、脱敏范围和截图可见内容仍需用户确认。
- 真实外部 provider 仍属于 P6 opt-in，不是 P5 默认出门条件。

## 5. 剩余开发及验收大纲

### P5-REAL：真实授权资料本地闭环

目标体验：

1. 用户提供明确本地资料路径和允许展示字段。
2. 系统在本地导入简历、项目说明、背景材料和目标 JD。
3. 前端展示资料解析、source refs、blocking/warning/optional 待确认项。
4. 用户补充或确认事实后生成申请包。
5. 编辑申请包后重新阻塞导出，确认后允许 Markdown/DOCX 导出。
6. 用户围绕当前资料、JD 和申请包继续多轮追问。
7. 生成脱敏 HTML 验收报告，报告中不得包含未授权字段。

验收标准：

- 使用用户明确授权的本地资料路径。
- 不调用真实外部 provider。
- 不写入 workspace 外目录。
- 阻塞项未确认时不得导出。
- 报告必须包含真实界面截图、PRD 规格检视、未验证范围和隐私边界。

### P5-Freeze：阶段冻结

目标体验：

1. P5-REAL 通过后执行最终回归。
2. 完成人工体验审查记录。
3. 更新 final closure audit。
4. 明确 P5 出门结论和 P6/P7/P8+ 剩余计划。

验收标准：

- `python3 -m pytest` 通过。
- `npm --prefix apps/chatbox run build` 通过。
- drawio XML parse 通过，页数不超过 8。
- README、TODO、active docs、drawio、报告口径一致。
- 不声称真实外部 provider 默认路径通过。

### P6：真实外部 provider opt-in

目标体验：

1. 用户显式选择 MiniMax、DeepSeek 或其他 OpenAI-compatible provider。
2. 本地配置 API Key，不进入仓库、报告、日志或聊天记录。
3. provider-backed 自由智能聊天在受控次数和脱敏资料下验收。
4. 失败时可降级到本地/mock 或展示明确错误。

验收标准：

- 每次真实外呼前获得用户确认。
- provider invocation、timeout、retry、redaction、schema validation 有证据。
- 不把 provider-backed 结果混同为 P5 默认路径。

## 6. 风险与备选路线

| 风险 | 当前控制 | 备选路线 | 取舍 |
| --- | --- | --- | --- |
| 真实资料路径未提供，P5-REAL 无法执行 | 明确列为阻塞项 | 继续使用合成资料和脱敏 fixture 做预演 | 可降低开发风险，但不能冻结 P5 |
| 报告泄露个人信息 | 默认脱敏，需用户确认允许展示字段 | 报告只展示局部截图和结构化摘要 | 隐私更安全，但可读性降低 |
| 外部 provider 被误当作默认能力 | P5 文档明确 provider 属于 P6 opt-in | P5 全程禁用真实 provider | 最安全，但无法验证真实模型体验 |
| 申请包夸大经历 | questions_to_confirm 和 source refs 阻塞导出 | 增加人工事实审查清单 | 更严谨，但验收成本更高 |

## 7. 是否需要 ChatGPT 审计

建议：可以进行轻量 ChatGPT 审计，但不是本地文档阶段的阻塞项。

理由：

- 当前文档已经能支撑 P5 剩余自动化开发和验收。
- 主要剩余风险来自真实资料授权、隐私展示范围和人工体验记录，这些需要用户确认而不是外部模型判断。
- 外部审计更适合检查“是否存在概念冲突、过度承诺、P5/P6 边界混淆、验收口径虚假”等问题。

建议审计问题：

1. 文档是否把 P5 本地/mock、P5-REAL、P6 provider opt-in 三类路径区分清楚？
2. 是否存在把自动化候选报告描述成 P5 冻结通过的过度承诺？
3. 目标架构中的代码实体和验收门槛是否能支撑 PRD 的核心体验？
4. 是否存在真实个人资料、API Key、外部调用的隐私或安全遗漏？

## 8. 建议提交给 ChatGPT 的文档路径

文档数：17，小于 20。

1. `README.md`
2. `TODO.md`
3. `docs/active/00_README.md`
4. `docs/active/01_STAGE_PRD.md`
5. `docs/active/02_TARGET_ARCHITECTURE.md`
6. `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
7. `docs/active/04_ACCEPTANCE_GATES.md`
8. `docs/active/06_TRACEABILITY_MATRIX.md`
9. `docs/active/jobpilot-stage-gap-and-acceptance.md`
10. `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
11. `docs/active/stage-reviews/P5_PRE_FREEZE_AUTOMATED_CANDIDATE_AUDIT.md`
12. `docs/active/stage-reviews/P5_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md`
13. `docs/active/stage-reviews/P5_FREEZE_EXIT_AUDIT_PLAN.md`
14. `docs/active/stage-reviews/P5_EXTERNAL_REVIEW_REVISION_AUDIT.md`
15. `docs/active/stage-reviews/P5_DOCUMENTATION_COVERAGE_REAUDIT.md`
16. `docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html`
17. `docs/reports/P5_SYNTHETIC_PROFILE_REVIEW.html`

## 9. 待验收审查结论

- 本轮文档开发完成后，P5 仍处于“自动化候选通过，真实资料授权验收和最终冻结待完成”。
- 合成资料审核页可以作为 P5-REAL 前置资料结构审查材料。
- 当前文档可指导后续自动化开发和验收，但不能绕过真实资料路径授权。
- 若用户未提供真实资料路径，下一步只能继续文档审查、合成资料演练或 P6/P7 规划，不能声称 P5 已最终通过。
