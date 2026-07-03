# P8.1 Chatbox-first 工作台信息架构文档开发审计

## 1. 审计结论

本轮审计结论：P8.1 可以作为 P8 后续体验修正阶段进入主线，但当前仍是文档开发阶段，不代表前端代码已经完成修复。

P8 自动化候选能力仍然有效：资料准备向导、JD 手动导入中心、多 JD 目标岗位、JD 定制简历、source refs、pending confirmations、export preflight 和中文 HTML 报告已经具备本地/mock + 受控真实感数据证据。

P8.1 需要修正的是信息架构主次关系：

```text
当前风险：P8 workflow strip 在中央对话区首屏抢占 Chatbox 优先级
目标结构：用户指导 - Chatbox - 工作台
验收重点：Chatbox 始终是第一优先展示和第一交互路径
```

## 2. 输入材料

本轮审计参考以下材料：

- `README.md`
- `TODO.md`
- `docs/active/00_README.md`
- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`

## 3. 规格一致性审计

### 3.1 与 PRD 的关系

P8 PRD 解决的是“用户不知道提供什么资料、没有清晰 JD 导入路径、简历生成不够围绕目标岗位”。P8.1 不改变这些目标，而是补充一个更强的信息架构约束：这些能力必须围绕 Chatbox 主路径组织，不能让大型表单压住聊天。

结论：一致。

### 3.2 与目标架构的关系

P8 目标架构已经定义 Chatbox Experience Shell、Material Intake Wizard、JD Intake Center、Job Target List、Resume Generation Plane、Workbench 和 FastAPI/Domain/Storage/Evidence 分层。P8.1 只调整这些 UI 平面的摆放优先级和职责归属：

- `Conversation Plane` 必须成为中央主路径；
- `MaterialIntakeWizard` 和 `JDIntakeCenter` 应变为紧邻输入框的轻量入口、弹层、抽屉或辅助面板；
- `Workbench` 继续承载岗位、画像、简历、source refs、pending confirmations 和导出前检查；
- API、Domain Tools、SQLite 和 Evidence 层不因 P8.1 发生业务语义变化。

结论：一致。

### 3.3 与验收门槛的关系

P8.1 新增验收门槛聚焦真实用户体验：

- 首屏是否以 Chatbox 为主；
- 用户是否能识别“用户指导 - Chatbox - 工作台”；
- 工具入口是否紧贴输入框或在辅助面板内；
- 多视口是否无重叠、无错位、无核心入口不可达；
- 报告是否明确未验证招聘平台自动接入、真实 provider、真实个人资料、自动投递、SaaS、ASR 和会议平台。

结论：一致。

## 4. 文档缺口修正

本轮需要修正的文档缺口：

- P8 文档只说明资料/JD/简历生成能力，但没有明确 Chatbox-first 的首屏优先级；
- drawio 需要展示 P8.1 在三栏结构中的位置，以及它与 P8 已实现能力的关系；
- README/TODO/active 文档需要避免把 P8 当前 UI 体验写成已被人工认可；
- 验收门槛需要增加多视口 Chatbox 优先级和按钮/文字不重叠检查。

修正后应形成以下口径：

```text
P8 = JD Intake 与简历生成自动化候选已完成
P8.1 = Chatbox-first 信息架构修正文档阶段
P8.1 目标 = 保留 P8 能力，但把聊天框恢复为中央第一优先体验
```

## 5. 风险审计

| 风险 | 判断 | 处理 |
| --- | --- | --- |
| 把 P8.1 写成已实现 | 高风险 | 所有文档标注“文档阶段 / 未进入代码实现” |
| 把 P8.1 扩展成招聘平台自动接入 | 高风险 | 明确不登录、不抓取、不自动沟通、不自动投递 |
| 把真实 provider 写成已验收 | 高风险 | 保留 P6 opt-in 边界，P8.1 不触发真实外呼 |
| 把真实个人资料路径写成已通过 | 高风险 | 保留用户授权路径要求，不读取个人目录 |
| 仅做视觉美化不修正信息架构 | 中风险 | 验收门槛要求首屏 Chatbox 优先和三栏职责稳定 |

## 6. 开发准入建议

在用户认可 P8.1 drawio 和文档方向后，可以进入 P8.1-M0 开发前启动审计。启动审计必须先确认：

- 当前代码中的 Chatbox 仍存在，问题是优先级和布局，不是能力删除；
- 后续实现只重排 UI/IA，不重写业务层；
- 所有 P8 能力仍通过现有 API/Domain/Storage/Evidence 层实现；
- 自动化验收必须包含 1200px、1440px、1920px、720px、390px 截图；
- 报告必须使用真实界面截图，不得用设计稿或合成图替代。

## 7. 最终判断

当前 P8.1 文档开发可以支撑后续自动化开发计划，但本轮不能进入实际代码开发，也不能形成 P8.1 通过结论。

需要人工审核的重点：

- 三栏目标是否符合“用户指导 - Chatbox - 工作台”；
- 是否接受将资料/JD/简历生成入口从中央大表单调整为输入框附近工具和左右辅助面板；
- 是否接受 P8.1 作为 P8 后续体验修正阶段，而不是重新定义 P8 业务能力。

## 8. 二次文档修订记录 - 实体关系和 drawio 质量修复

本轮根据人工反馈继续修订 P8.1 文档与 drawio。修订目标不是扩写功能范围，而是提升后续自动化开发可执行性和人工审查可读性。

已修订内容：

- PRD 增加 P8.1 完成后的人类可感知结果，明确用户不需要理解 workspace、artifact、job 或 resume_version 才能开始对话；
- 目标架构增加 `User action → Chatbox UI → API Boundary → Domain / Orchestration → SQLite Workspace / Artifact → Evidence` 的实体流转；
- 里程碑和 TODO 统一 P8.1-M0 到 P8.1-M5，避免报告阶段与响应式阶段混在一个任务中；
- 验收门槛增加真实截图必须证明 Chatbox 首屏优先、输入框工具入口可达、三栏职责稳定和工作台产物可见；
- 追踪矩阵增加实体状态表，列出 `DesktopContextPanel`、`Conversation Plane`、`p8-workflow-strip`、P8 UI tools、Workbench、P8 API、Domain/Storage 和 Evidence 的状态与验收证据；
- drawio 保持 7 页，重新强化第 4 页“代码实体与分层交互关系”，用颜色区分已实现自动化候选、P8.1 待修改、P8 能力保留但重排和禁止关系；
- drawio 文本镜像同步重写，避免第 5/6 页继续停留在 P8 旧阶段口径。

二次审计结论：

```text
P8.1 文档质量修复通过。
当前文档能够指导后续 P8.1-M0 到 P8.1-M5 自动化开发。
当前仍不能写成 P8.1 UI 已实现、已人工验收或已冻结。
```

仍需在后续代码实现阶段打回的情况：

- 大型资料/JD/简历表单仍位于聊天时间线之前；
- 移动端默认展示资料表单而不是 Chatbox；
- 入口迁移后上传资料、粘贴 JD、选择岗位或生成简历不可达；
- 右侧工作台缺少岗位、画像、简历、source refs、待确认项或导出预检；
- 验收报告使用目标图或概念图替代真实实现截图；
- 打回：报告声称招聘平台接入、真实 provider、真实个人资料或自动投递已通过。

## 9. 外部审计意见采纳 - 文档收口与开发准入

本轮采纳 ChatGPT 外部审计意见。外部意见与本地多轮审计结论一致：

```text
P8.1 文档支撑自动化开发：通过
P8.1 PRD 体验路径：通过
P8.1 目标架构：通过
P8.1 工作包颗粒度：通过
P8.1 验收门槛：通过
P8.1 drawio / 文本镜像：通过
是否还需要扩写主设计文档：不建议
是否可以进入实质开发：可以，从 P8.1-M0 开始
```

采纳后的文档口径：

- 允许声明：P8.1 文档体系可支撑后续自动化开发；
- 允许声明：P8.1 可以进入 M0 开发前启动审计；
- 允许声明：P8.1 完成后应支撑“用户指导 - Chatbox - 工作台”的目标体验；
- 不允许声明：P8.1 UI 已修复；
- 不允许声明：Chatbox-first 真实界面已验收通过；
- 不允许声明：招聘平台接入、真实 provider、真实个人资料、自动投递、SaaS、ASR 或会议平台已通过。

最终收口结论：

```text
P8.1 文档开发可以收口。
下一步应进入 P8.1-M0 开发前启动审计。
除非 P8.1-M0 发现新增致命或重大规格偏差，否则不再扩写主设计文档。
```
