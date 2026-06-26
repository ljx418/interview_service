# P5 冻结出门审计计划

日期：2026-06-26
阶段：P5 真实资料本地闭环
状态：计划已就绪，等待 P5-REAL 真实授权资料复核和人工体验审查完成后执行。

## 1. 审计结论口径

本计划用于指导 P5 最终冻结审计。当前项目只能声明“P5 自动化候选通过”，不得声明 P5 已冻结。

P5 final closure audit 只有在以下事项全部完成后才能写成“通过”：

- 用户明确提供本地脱敏真实资料路径和允许展示字段；
- P5-REAL 只读取用户指定路径，不擅自搜索个人目录；
- 真实资料/JD 截图和报告完成脱敏复核；
- P5 人工体验审查清单完成并允许冻结；
- `.venv/bin/python -m pytest`、`npm --prefix apps/chatbox run build`、drawio XML parse 均通过；
- P5 报告、README/TODO/active docs/drawio 口径一致；
- 审计未发现 P6/P7/P8+ 能力被写成 P5 已完成。

## 2. 必须复验的 PRD 出门路径

最终审计必须以 PRD 的目标体验链路为主线，不得只用测试通过替代体验判断：

```text
打开本地 Chatbox
→ 导入或粘贴真实授权资料
→ 查看资料摘要、source refs、待确认项
→ 导入或粘贴目标 JD
→ 查看岗位要求、风险、缺口和下一步
→ 确认 blocking/warning/optional 事实项
→ 生成申请包草稿
→ 编辑或重新生成并保留版本
→ 导出 Markdown/DOCX
→ 围绕当前资料和 JD 继续多轮追问
```

每一步必须在 final closure audit 中记录结论、证据位置和是否存在隐私风险。

## 3. 必须复验的工程证据

| 证据 | 最低要求 | 不得声称 |
| --- | --- | --- |
| 全量回归 | `.venv/bin/python -m pytest` 通过 | 不代表人工体验通过 |
| 前端构建 | `npm --prefix apps/chatbox run build` 通过 | 不代表真实资料通过 |
| drawio | XML parse 通过，页数不超过 8 | 不代表功能已冻结 |
| P5 自动化报告 | HTML 可读，截图真实可见，未验证范围明确 | 不代表真实外部 provider 通过 |
| P5-REAL 复核 | 使用用户指定真实/脱敏资料路径 | 不代表可以读取任意个人目录 |
| 人工体验清单 | 所有项目明确通过或打回 | 不代表最终产品化发布 |

## 4. 必须复验的文档一致性

P5 final closure audit 前必须检查以下文档口径：

- `README.md`；
- `TODO.md`；
- `docs/active/00_README.md`；
- `docs/active/01_STAGE_PRD.md`；
- `docs/active/02_TARGET_ARCHITECTURE.md`；
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`；
- `docs/active/04_ACCEPTANCE_GATES.md`；
- `docs/active/06_TRACEABILITY_MATRIX.md`；
- `docs/active/jobpilot-stage-gap-and-acceptance.md`；
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`；
- `docs/active/stage-reviews/P5_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md`。

检查重点：

- 仍明确 P5 默认不调用真实外部 provider；
- 未把 provider-backed 自由智能聊天、SaaS、ASR、会议平台、自动投递、MCP/CLI、最终产品化发布写成 P5 已完成；
- 未把 examples 或脱敏 fixture 写成真实个人资料验收；
- 未把自动化报告写成人工体验认可；
- drawio 页数不超过 8，颜色语义和 active docs 一致。

## 5. 必须打回的情况

出现以下任一情况，P5 不得冻结，必须打回对应阶段：

- 用户未提供真实授权资料路径，却声明真实资料路径通过；
- 报告、截图、日志或 fixture 暴露联系方式、账号、API Key、私密链接或未授权长原文；
- 默认触发真实外部 provider；
- 普通追问误触发 artifact 写入、解析、生成或导出；
- blocking confirmation 未处理仍能导出正式申请材料；
- 用户无法判断资料、JD、确认项、版本或导出状态；
- 多视口截图显示按钮重叠、文字溢出、关键操作不可达；
- final closure audit 把 P6/P7/P8+ 能力写成 P5 已完成。

## 6. 备选路线和风险判断

| 路线 | 适用条件 | 优点 | 风险 | 当前结论 |
| --- | --- | --- | --- | --- |
| A：继续本地/mock + 用户授权资料复核 | 用户提供脱敏真实资料路径，P5 默认不外呼 | 风险最低，最符合 P5 PRD 和隐私边界 | 文本智能质量不代表真实 provider 水平 | 采用 |
| B：转 P6 provider opt-in | 用户明确要求真实外部模型质量验收 | 可验证 provider-backed 生成质量 | API Key、费用、隐私、失败降级风险上升 | 不纳入 P5，单独确认 |
| C：打回 UX/架构文档 | 人工体验发现状态不可理解或版本/导出链路不清 | 可避免带缺陷冻结 | 延后 P5 冻结 | 仅在审查失败时采用 |

## 7. 审计输出模板

P5 final closure audit 应至少包含：

- 审计日期、资料路径授权记录和脱敏范围；
- PRD 出门路径逐项结论；
- 工程证据命令和结果；
- 截图/报告/导出文件证据路径；
- 文档一致性检查结果；
- 隐私和 provider 边界检查；
- 打回项或残余风险；
- 最终结论：允许 P5 冻结 / 不允许 P5 冻结。
