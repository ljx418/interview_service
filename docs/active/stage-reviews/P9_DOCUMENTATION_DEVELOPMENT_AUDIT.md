# P9 Chatbox-native 求职情报与申请包工作台文档开发审计

状态：文档开发阶段审计。本文档不代表 P9 代码实现、全网 JD 搜索、ASR、真实 provider、招聘平台自动接入、自动投递或 SaaS 能力已经完成。

## 1. 审计背景

用户明确提出当前前端体验仍然很差，不希望继续存在大量向导卡片；期望产品能力重新围绕 Chatbox 展开，并补齐自动搜索 JD、招聘信息汇总、ASR/对话式资料补全、面向不同 JD 的申请包生成、右侧产物台、顶部服务状态和左侧求职态势可视化。

本轮文档开发的目标是把上述诉求纳入主线开发计划，并同步 PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap 和 drawio。当前仍不进入实际代码开发。

## 2. 已审计文档

- `docs/p9-chatbox-native-review/01_P9_PRD_DRAFT.md`
- `docs/p9-chatbox-native-review/02_CURRENT_IMPLEMENTATION_BASELINE.md`
- `docs/p9-chatbox-native-review/03_FRONTEND_EXPERIENCE_SPEC.md`
- `docs/p9-chatbox-native-review/04_USER_JOURNEY_AND_ACCEPTANCE.md`
- `docs/p9-chatbox-native-review/05_VISUAL_REVIEW_PAGE.html`
- `docs/p9-chatbox-native-review/09_LEFT_INTELLIGENCE_PANEL_DETAIL.md`
- `docs/p9-chatbox-native-review/10_OPEN_SOURCE_MAP_VISUALIZATION_RESEARCH.md`
- `docs/active/23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`

## 3. 规格一致性结论

P9 目标体验已经形成一致口径：

```text
顶部服务中心
→ 左侧求职态势图
→ 中央 Chatbox 主控台
→ 右侧产物台
```

核心约束已经清楚：

- Chatbox 是第一交互路径，不再让大型向导卡片压住聊天。
- 左侧态势图必须展示岗位市场、目标机会与匹配、投递流程三大板块。
- 左侧地图/图钉/聚合视图可以规划为 P9 目标，但外部地图服务和平台搜索不能写成已实现。
- 顶部服务中心只展示本地配置和连通性状态，不保存 API Key，不默认外呼。
- 右侧产物台展示候选人画像、简历、故事、申请包、source refs、pending confirmations 和流程节点。
- 用户可以通过 Chatbox 更新岗位目标、申请包草稿、项目事实和投递流程。

## 4. 架构可执行性结论

P9 架构已经落到可审查代码实体：

- `apps/chatbox/src/main.tsx`：Chatbox Experience Shell、ConversationPlane、Workbench / P9ArtifactOverview 的主要承载位置。
- `apps/chatbox/src/styles.css`：响应式、三栏比例、态势图和产物台可读性的主要承载位置。
- `TopServiceCenter`、`LeftIntelligencePanel`、`MarketMapView`、`OpportunityMatchPanel`、`ApplicationPipelineView`：P9 已落地的 UI 自动化候选实体。
- `handleP9Command`、本地 search run、local pipeline state、本地故事草稿：P9 已落地的前端编排边界；`JobSourceConnector`、`ApplicationPipelineService`、`StoryBank` 未新增为独立服务。
- `job`、`match_report`、`candidate_profile`、`resume_version`、`artifact`：P8/P5.5 已实现自动化候选实体，P9 复用并扩展体验组织。

当前文档没有要求重写全部业务层，也没有把平台自动化、真实 provider、ASR 或 SaaS 混入默认实现。

## 5. 风险与打回条件

后续如果出现以下情况，必须打回：

- 把 P9 文档写成 P9 UI 已实现。
- 把“全网搜索 JD”写成 BOSS/猎聘/拉勾/LinkedIn 已自动接入。
- 触发招聘平台登录、绕风控、自动沟通或自动投递。
- 默认调用真实 provider 或读取真实个人资料。
- ASR 在没有用户确认时采集麦克风或调用外部语音服务。
- 左侧态势图只剩静态说明，不能折叠、切换、放大、拖动或联动 Chatbox。
- 右侧产物台无法看到 source refs、pending confirmations 或版本边界。

## 6. 审计结论

通过。当前 P9 文档可以作为下一轮主线文档阶段的执行依据，并可以继续进入 P9 文档覆盖度复审或 P9-M0 开发前启动审计。

限定结论：

- 允许声明：P9 文档已经纳入主线，能指导后续自动化开发计划。
- 不允许声明：P9 前端已经实现。
- 不允许声明：真实 provider、ASR、全网 JD 搜索、招聘平台自动接入、自动投递、MCP/Skill 连通性已经通过。
