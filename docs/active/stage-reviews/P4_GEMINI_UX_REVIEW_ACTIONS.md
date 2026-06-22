# P4 Gemini UX 审查处理记录

日期：2026-06-16  
阶段：P4 UX 体验强化  
输入：Gemini 前端页面方案审查意见  
结论：有条件通过，需要在 P4-M1/M2/M3 中优先修正信息架构和交互状态。

## 1. 审查结论

Gemini 对当前 P4 前端方案给出“有条件通过”。整体方向成立，但仍存在较重工程控制台痕迹：

- 任务入口与对话区割裂；
- 状态栏表达生硬；
- 产物卡操作优先级不清；
- 缺少 loading / thinking 状态；
- 推进台空状态不足；
- 移动端简单堆叠会压缩 Chatbox；
- 错误态缺少恢复路径；
- segmented 控件缺少 ARIA 状态；
- 长内容缺少折叠；
- 待确认项文案偏程序校验，不够像求职辅导。

## 2. 采纳的 P4 必修项

| Gemini 问题 | P4 处理决定 | 落入阶段 | 文档修订 |
| --- | --- | --- | --- |
| 任务入口与对话区割裂 | Task Launcher 改为 Chatbox 空状态 Suggested Prompts；点击后填入 composer 或直接触发对话 | P4-M1 / P4-M2 | PRD、架构、里程碑、验收门槛、Gemini 包 |
| 状态栏 provider 语义生硬 | 使用“外部模型未调用（隐私安全）/ 外部调用需确认”等用户语言 | P4-M4 | PRD、架构、验收门槛、组件规格 |
| 产物卡按钮层级不清 | 区分 primary action 和 secondary action；阻塞项高亮“补充事实/去确认” | P4-M3 | PRD、组件规格、原型 |
| 缺少 loading/thinking | 增加 Agent thinking、执行步骤和防重复点击策略 | P4-M2 | 架构、验收门槛、原型 JS |
| 推进台空状态不足 | Workbench 初始状态显示“导入资料后产物将在此生成” | P4-M3 | 信息架构、组件规格 |
| 移动端压缩 Chatbox | 390px 下 Workbench 收为底部抽屉/折叠区域，Conversation 优先 | P4-M5 | 架构、验收门槛、原型 CSS |
| 错误态缺少恢复路径 | 错误气泡必须附带恢复 action，例如重新上传、查看格式、补充 JD | P4-M2 | 验收门槛、组件规格 |
| 可访问性状态缺失 | segmented 增加 `aria-pressed`，状态区 `role=status`，按钮具备名称 | P4-M5 | 可访问性清单、原型 |
| 长内容缺少折叠 | 长 JD、长 plan、长 summary 增加折叠规则；虚拟列表推迟到 P5 | P4-M2 / P4-M5 | 组件规格 |
| 待确认语气生硬 | 待确认项改成求职辅导语气，解释为什么需要补充证据 | P4-M3 | 产物卡规格、原型 |

## 3. 延后到 P5 的建议

- 长篇历史记录分页或虚拟列表；
- 复杂版本 diff；
- 多文档管理看板；
- SaaS 登录、多端同步；
- 自动投递接口；
- BI 数据分析面板。

## 4. P4 文档核查结论

核查后发现，原 P4 文档已经覆盖 UX 体验强化方向，但需要把“任务入口”从独立页面层级收敛为 Chatbox Empty State / Suggested Prompts，并把状态反馈、按钮层级、移动端抽屉和 ARIA 作为硬性验收项。

本轮已修订：

- `01_STAGE_PRD.md`
- `02_TARGET_ARCHITECTURE.md`
- `03_MILESTONES_AND_DELIVERY_PLAN.md`
- `04_ACCEPTANCE_GATES.md`
- `06_TRACEABILITY_MATRIX.md`
- `16_P4_UX_EXPERIENCE_HARDENING_PLAN.md`
- `docs/gemini-frontend-review-package/`
- `jobpilot-stage-gap-and-acceptance.drawio`
- `jobpilot-stage-gap-and-acceptance.md`

## 5. 审计意见

当前没有新增致命或重大规格偏差。Gemini 的意见强化了 P4 原本目标，不要求扩展 P5 能力。可以继续进入 P4-M1/P4-M2 实质前端 UX 实现，但必须把以下内容作为出门门槛：

- Suggested Prompts 和 composer 形成闭环；
- loading/thinking 和错误恢复可见；
- Workbench 移动端不压缩核心 Chatbox；
- provider 状态不误导外呼；
- 产物卡主次操作清楚；
- 静态原型、Gemini 审查和真实实现验收分开表述。
