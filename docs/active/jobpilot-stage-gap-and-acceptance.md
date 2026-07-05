# JobPilot AI P9 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。当前图示主线是 **P9 Chatbox-native 求职情报与申请包工作台自动化候选阶段收口审计**。

P8.1 Chatbox-first、P8-JD Intake、P5.5 Candidate Profile、P6/P7 本地 Beta 自动化候选均作为 P9 基线保留。P9 本轮只允许声明本地 UI 信息架构、求职态势可视化层、Chatbox 本地命令路由、现有能力重新组织和多视口自动化截图证据已经形成自动化候选；不得声明全网 JD 搜索、ASR、真实 provider、MCP/Skill、招聘平台自动接入或自动投递已经通过。

## 图示页结构

drawio 共 8 页，不超过 8 页：

1. P9 目标体验总览；
2. 当前与目标差异；
3. 代码实体与分层；
4. 左侧态势图设计；
5. 用户体验路线；
6. 开发及验收计划；
7. 里程碑门槛出门；
8. 安全边界与证据。

颜色含义：

- 绿色：已实现或已完成自动化候选；
- 蓝色：现有实体已修改或复用实现；
- 黄色：后续可选增强、需人工体验复核或单独规划；
- 红色：未实现高风险能力、禁止默认实现或虚假验收打回项；
- 灰色：边界说明节点。

## 第 1 页 - P9 目标体验总览

P9 目标体验固定为四块：

- 顶部服务中心 `TopServiceCenter`：provider、JD 信息源、ASR、MCP/Skill、workspace、安全边界状态可见；
- 左侧求职态势 `LeftIntelligencePanel`：岗位市场地图、机会匹配、投递流程三页签，可缩放、拖动和重置；
- 中央 `ConversationPlane` / Chatbox：第一交互路径，用户通过对话发起 JD 汇总、资料补全、申请包生成和流程更新；
- 右侧 Workbench / `P9ArtifactOverview`：展示 search run、故事草稿、流程摘要、岗位、画像、简历、source refs 和 pending confirmations。

本页同时用红色标出 P9 未通过范围：真实全网 JD 搜索、BOSS/猎聘/拉勾登录抓取、真实 ASR、真实 provider 质量、MCP/Skill 平台连通、自动沟通/自动投递和 SaaS。

## 第 2 页 - 当前与目标差异

开发前基线是 P8.1 Chatbox-first 框架、P8 资料准备/JD 导入/多 JD/JD 定制简历、P5.5 画像和 P6/P7 本地 Beta 自动化候选。

P9 本轮已经完成以下自动化候选差距收口：

- 去除“向导卡片主导”体验；
- 顶部服务状态常驻；
- 左侧求职态势三板块；
- 中央 Chatbox 发起关键动作；
- 右侧产物台持续可见；
- 多视口截图和中文 HTML 报告。

保留红色未实现边界：真实平台搜索、自动抓取、自动沟通、真实 ASR 采集、真实 provider 质量验收、真实个人资料路径、MCP/Skill 实际连通和 SaaS 多租户。

## 第 3 页 - 代码实体与分层

该页明确 P9 本轮涉及的具体代码实体、状态和上下游关系：

```text
User
→ UI Layer
  → apps/chatbox/src/main.tsx
  → apps/chatbox/src/styles.css
  → TopServiceCenter
  → LeftIntelligencePanel
  → MarketMapView
  → OpportunityMatchPanel
  → ApplicationPipelineView
  → ConversationPlane / Composer
  → handleP9Command
  → Workbench / P9ArtifactOverview
→ API Boundary
  → services/api/main.py
  → services/api/schemas.py
  → /api/jobs
  → /api/resume/generate
  → /api/profile/candidate
→ Domain Tools
  → services/tools/jobpilot.py
  → services/profile/candidate.py
  → services/chat/core.py
→ SQLite Workspace / Artifact / Evidence
  → job / match_report / candidate_profile / resume_version / artifact
  → docs/reports/
  → scripts/generate_p9_chatbox_native_acceptance.py
  → scripts/generate_p9_stage_closure_acceptance.py
  → tests/evals/test_p9_*
```

禁止关系保持不变：UI 不直写 SQLite，Chatbox 不保存 API Key，不直连真实 provider，不登录或抓取招聘平台，不默认采集麦克风。

## 第 4 页 - 左侧态势图设计

左侧栏必须包含三大板块：

- 岗位市场态势 `MarketMapView`：城市、薪资、JD 来源图钉；离线地图形态；支持放大、缩小、重置和拖动；显示“本地可审计来源”；
- 目标机会与匹配 `OpportunityMatchPanel`：展示目标岗位、匹配分、薪资、城市、技能缺口和下一步建议；
- 投递流程态势 `ApplicationPipelineView`：按 JD 展示 interested、applied、interview、offer、rejected、archived，并允许 Chatbox 更新本地状态。

验收要求：页签可切换、地图可缩放/拖动/重置、图钉可读、720px/390px 视口可折叠且入口可达、不依赖外部地图 token。

## 第 5 页 - 用户体验路线

P9 用户路线被定义为：

```text
打开本地 Chatbox-native 工作台
→ 顶部服务状态、左侧态势、中央 Chatbox、右侧产物台同时可见
→ 在 Chatbox 输入 JD / 城市 / 薪资汇总请求
→ 左侧市场态势与右侧 search run 更新
→ 在 Chatbox 继续补项目故事和能力证据
→ 生成面向目标 JD 的申请包草稿
→ 用 Chatbox 更新投递流程
→ 导出前仍需处理 source refs 和 pending confirmations
```

体验收口判断：P9 让用户通过中央 Chatbox 主路径驱动 JD 汇总、资料补全、申请包生成和流程更新；左侧负责“看态势”，右侧负责“看产物”，不再用大量向导卡片压住聊天。

## 第 6 页 - 开发及验收计划

P9-M0 到 P9-M9 本轮状态：

| 阶段 | 内容 | 当前状态 |
| --- | --- | --- |
| P9-M0 | 开发前启动审计 | 已完成自动化候选 |
| P9-M1 | Chatbox-native 信息架构，中央 Chatbox 主路径恢复 | 已完成自动化候选 |
| P9-M2 | 顶部服务中心，状态展示且不默认接入真实外部系统 | 已完成自动化候选 |
| P9-M3 | 左侧态势图，市场/匹配/流程三板块和地图交互 | 已完成自动化候选 |
| P9-M4 | 合规 JD source run，用户粘贴/fixture/本地示例，不抓取平台 | 已完成自动化候选 |
| P9-M5 | Chatbox 引导式资料故事补全，ASR 仅显示 opt-in 边界 | 已完成自动化候选 |
| P9-M6 | 多 JD 申请包草稿、source refs、pending confirmations | 已完成自动化候选 |
| P9-M7 | Chatbox 更新产物和投递流程，本地更新不对外沟通或投递 | 已完成自动化候选 |
| P9-M8 | 1920px、1440px、1200px、720px、390px 响应式截图 | 已完成自动化候选 |
| P9-M9 | 中文 HTML 验收报告、PRD/代码/文档审计 | 已完成自动化候选 |

## 第 7 页 - 里程碑门槛与出门条件

本轮出门门槛在本地自动化候选范围内全绿：

- 功能门槛：Chatbox 是第一交互路径；顶部服务状态可见；左侧态势三板块可见可操作；右侧产物台持续展示；Chatbox 可发起 JD 汇总、资料补全、申请包生成和流程更新；
- 工程门槛：`python3 -m pytest`、`npm --prefix apps/chatbox run build`、drawio XML parse、P9 eval、`git diff --check`、headless browser screenshots；
- 证据门槛：7 张真实界面截图、中文 HTML 报告、结构化命令证据、报告自检 JSON、drawio 和文本镜像同步、stage review 落盘。

人工出门建议：可以进入人工体验审查或下一轮产品规划。若人工体验认为地图精细度、移动端顺序、Chatbox 视觉权重仍不足，应打回 P9-M1/P9-M3/P9-M8。

## 第 8 页 - 安全边界与证据

允许声明：

- P9 本地 UI 信息架构、求职态势可视化层、Chatbox 本地命令路由、现有能力重新组织和多视口截图验收已经形成自动化候选。

禁止声明：

- 真实全网 JD 搜索已完成；
- BOSS、猎聘、拉勾、LinkedIn 自动接入；
- 真实 provider 质量通过；
- 真实个人资料路径通过；
- 真实 ASR 已实现；
- 自动投递已实现；
- SaaS、多租户、Billing 或会议平台已通过。

证据路径：

- `docs/reports/P9_CHATBOX_NATIVE_ACCEPTANCE_REPORT.html`
- `docs/reports/P9_STAGE_CLOSURE_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p9_chatbox_native/`
- `docs/reports/evidence/p9_stage_closure/`
- `docs/active/23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`
- `docs/active/stage-reviews/P9_M0_START_AUDIT.md`
- `docs/active/stage-reviews/P9_M1_TO_M8_IMPLEMENTATION_AUDIT.md`
- `docs/active/stage-reviews/P9_M9_AUTOMATED_ACCEPTANCE_AUDIT.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`

最终审计口径：本 drawio 已同步到 P9 阶段收口。目标架构、当前实现、开发内容和出门门槛在本地自动化候选范围内全绿；高风险外部能力保持未实现/未验收。
