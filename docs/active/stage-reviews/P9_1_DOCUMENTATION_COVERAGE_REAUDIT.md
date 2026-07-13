# P9.1 文档覆盖度复审

状态：历史文档覆盖度复审，已被 P9.1-M0 到 M5 本地自动化候选实现和验收接续。本文档不代表真实市场 provider、招聘平台抓取、真实 ASR、真实 provider、自动投递或 MCP/Skill 连通性已经完成。

## 1. 复审范围

本轮复审覆盖以下文档和原型：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/24_P9_1_MARKET_DATA_AND_SOCRATIC_PROTOTYPE_PLAN.md`
- `docs/active/jobpilot-p9-1-market-socratic-gap.md`
- `docs/active/jobpilot-p9-1-market-socratic-gap.drawio`
- `docs/p9_1_market_socratic_review/08_TARGET_PAGE_AND_MODULE_DESIGN.html`

## 2. PRD 覆盖判断

P9.1 PRD 已覆盖用户提出的三个核心问题：

| 用户反馈 | 文档覆盖 | 结论 |
| --- | --- | --- |
| 市场模块地图体验很差 | PRD、地图原型规格、drawio 第 5 页均要求行政区划颜色深浅、全国/省/市/区县下钻、城市气泡、visualMap、tooltip、toolbox、breadcrumb、薪资直方图、技术栈热度、来源可信度、缩放拖动和 Chatbox 联动 | 通过 |
| 当前仍有很多 mock / fixture 数据 | PRD、provider 调研、验收门槛均要求 fixture/manual/public/opt-in API 区分，未配置 provider 不得伪造真实市场 | 通过 |
| Chatbox 需要苏格拉底启发式提问 | PRD、Socratic Intake 规格、drawio 第 6 页均要求一问一答、事实摘要、故事草稿、source refs、pending confirmations | 通过 |

## 3. 架构覆盖判断

目标架构已把 P9.1 拆成可实现的实体关系：

```text
TopServiceCenter
→ LeftIntelligencePanel
  → MarketIntelligenceMap
  → AdministrativeDrilldownMap
  → RegionDrilldownController
  → AdministrativeRegionLayer
  → MarketSourceLegend
  → MarketInsightDrilldown
→ ConversationPlane
  → SocraticIntakeSession
  → SocraticQuestionPlanner
  → FactConfirmationStrip
→ Workbench / P9ArtifactOverview
  → CandidateFactSummary
  → ProjectStoryDraft
  → JDKeywordMapping
  → PendingConfirmations
  → DoNotClaimList
→ JobMarketProvider / JobSearchRun / NormalizedJobPost / JobMarketSnapshot
→ AdministrativeRegionNode / RegionJobDistributionSnapshot / MarketMapLayerState / MarketMapDrilldownState
→ MarketDataNormalizer / ProjectStoryEvidenceGuard
```

当前架构差异也已写清：P9 的 `MarketMapView`、`handleP9Command`、`P9ArtifactOverview` 是基线，P9.1 需要在这些基础上升级地图、数据来源状态、Socratic Intake 和产物台可追溯展示。

## 4. 开发计划覆盖判断

P9.1 后续开发已经拆为：

| 阶段 | 是否有目标 | 是否有验收 | 是否有打回条件 |
| --- | --- | --- | --- |
| P9.1-M0 开发前启动审计 | 有 | 有 | 有 |
| P9.1-M1 行政区划下钻式市场地图 UI | 有 | 有 | 有 |
| P9.1-M2 opt-in 市场数据 provider 状态 | 有 | 有 | 有 |
| P9.1-M3 Socratic Intake Chatbox 路径 | 有 | 有 | 有 |
| P9.1-M4 地图 / Chatbox / 产物台联动 | 有 | 有 | 有 |
| P9.1-M5 中文自动化验收报告 | 有 | 有 | 有 |

历史结论：当前颗粒度足以指导后续自动化开发，不需要继续扩写主设计文档。当前状态：P9.1-M0 到 M5 已完成本地自动化候选，证据为 `docs/reports/P9_1_MARKET_SOCRATIC_ACCEPTANCE_REPORT.html`、P9.1 专项 eval、前端 build 和全量 pytest。

## 5. 验收门槛覆盖判断

验收门槛已经覆盖：

- 行政区划下钻式市场地图原型；
- 合法 GeoJSON、ECharts drilldown、breadcrumb、hover/click feedback 和 fallback；
- 真实市场数据 provider 边界；
- Socratic Intake；
- 架构和实体状态一致；
- 后续自动化开发准入；
- false-green 防护。

特别注意：P9.1 已使用真实界面截图证明本地实现，不得用 HTML 原型图或 AI 目标图替代最终证据；后续真实 provider / 平台 / ASR 仍需单独报告。

## 6. 高风险边界

以下能力仍不属于 P9.1 默认实现：

- BOSS、猎聘、拉勾、LinkedIn 登录、抓取、绕验证码或绕风控；
- 长期运行爬虫、队列、定时抓取、批量平台访问；
- 默认真实 provider 外呼；
- 默认 ASR 麦克风采集；
- 自动沟通、自动投递或代表用户对外发送消息；
- MCP/Skill 连通性验收；
- 真实个人资料默认读取。

若后续开发必须触及这些能力，必须停止并重新进入计划和人工确认流程。

## 7. 复审结论

历史结论：当前 P9.1 文档体系已经能完整支撑后续自动化开发阶段的启动审计、实现、验收和打回。当前追加结论：P9.1 本地自动化候选已完成。允许声明：

- P9.1 文档开发目标已落盘；
- P9.1-M0 到 M5 本地自动化候选已完成；
- P9.1 真实界面截图报告、专项 eval、前端 build 和全量 pytest 已通过。

暂不允许声明：

- 不得声明：真实市场数据 provider 已接入；
- 不得声明：招聘平台自动抓取或全网 JD 搜索已完成；
- 不得声明：真实 ASR、真实 provider、自动投递或 MCP/Skill 连通性已通过。

## 8. 风险闭环复审 - 行政区划下钻地图

本轮根据人工反馈继续复审并修订了 P9.1 地图相关文档。此前残留风险是部分入口文档仍使用“高保真地图 / 地图原型”泛化口径，可能导致后续开发把目标理解成普通美化、静态 SVG、真实瓦片地图或暗色控制中心。本轮已完成以下闭环：

- PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、P9/P9.1 专项计划、drawio、文本镜像、HTML 原型页和审计文档均已统一到“行政区划下钻式市场地图”；
- drawio 第 3 页、第 4 页、第 5 页已显式展示 `AdministrativeDrilldownMap`、`RegionDrilldownController`、`AdministrativeRegionLayer`、`AdministrativeRegionNode`、`RegionJobDistributionSnapshot` 和 `MarketMapDrilldownState`；
- P9.1-M1 验收已从“地图可读、可拖动”提升为“行政区划颜色深浅、全国/省/市/区县下钻、breadcrumb、hover/click feedback、visualMap、tooltip、toolbox、source legend 和 Chatbox 联动可见”；
- 真实市场 provider、招聘平台抓取、真实 ASR、自动投递、MCP/Skill 连通性仍被排除在 P9.1 默认实现之外；
- GeoJSON 和第三方行政区划数据许可风险已作为 P9.1-M0/M1 的前置审计项，不允许无许可审查直接打包。

风险判断：

| 风险 | 当前状态 | 处理 |
| --- | --- | --- |
| 后续实现退化成静态 SVG 或普通地图 | 已通过 PRD、架构、验收门槛和 drawio 明确禁止 | P9.1-M1 截图和交互证据打回 |
| 行政区划数据许可不清 | 已记录为前置审计项 | M0/M1 必须选择合法 GeoJSON 或 fixture-only 原型 |
| 视觉大地图/地球仪感导致偏离主路径 | 已明确 `globe.gl` 仅作展开态参考 | 不进入默认主图实现 |
| fixture 被写成真实市场 | 已由 source refs、source legend、not_configured、false-green 扫描约束 | M2/M5 必须复验 |

最终判断：当前风险已闭环到文档层。剩余风险属于后续实现阶段的技术和证据执行风险，不是文档规格缺口；当前不需要用户在多条技术路线之间做选择。后续默认路线为 `Apache ECharts map/geo + 合法 GeoJSON + visualMap + scatter + drilldown`。

## 9. 外部意见修订复核

本轮在人工认可 drawio 开发方向后，重新按 PRD、目标架构、里程碑、验收门槛、追踪矩阵、drawio 文本镜像和 HTML 原型审查页进行多轮独立审计。结论如下：

| 审计轮次 | 检查重点 | 结论 |
| --- | --- | --- |
| 第一轮：PRD 体验闭环 | 是否覆盖行政区划下钻式市场地图、真实市场数据边界和 Socratic Intake | 通过。PRD 已明确 P9.1 不是代码实现阶段，目标体验和非目标边界完整 |
| 第二轮：目标架构闭环 | 是否有具体代码实体、状态、上下游关系和分层结构 | 通过。`MarketIntelligenceMap`、`AdministrativeDrilldownMap`、`RegionDrilldownController`、`JobMarketProvider`、`SocraticIntakeSession` 等实体均可追踪 |
| 第三轮：验收与打回闭环 | 是否能指导 M0-M5 自动化开发、端到端验收和 false-green 打回 | 通过。验收门槛覆盖多视口截图、真实界面证据、GeoJSON/fallback、provider 状态、Socratic 对话和中文报告 |
| 第四轮：外部审计必要性 | 是否仍存在需要 ChatGPT 先行选择技术路线或补充主设计文档的风险 | 不强制。当前风险已收敛为实现阶段证据风险，不是文档规格缺口 |

当时允许进入的下一步是 `P9.1-M0 开发前启动审计`；当前 P9.1-M0 到 M5 已完成。后续若要进入 P9+，必须重新复核：

- GeoJSON 来源和许可是否适合当前项目；
- 行政区划下钻地图是否仍坚持 ECharts map/geo 主路线；
- 未配置真实 provider 时是否保持 `not_configured` / fixture fallback；
- Socratic Intake 是否只采集和整理用户确认事实；
- 真实招聘平台、ASR、真实 provider、自动投递、MCP/Skill 连通性是否仍未被默认纳入。

可选 ChatGPT 审计文件集如下，文件数 14 个，小于 20。当前判断是不强制再交 ChatGPT 审计；如需要外部复核，应只审这些文件，避免扩大审计范围导致口径漂移：

1. `README.md`
2. `TODO.md`
3. `docs/active/00_README.md`
4. `docs/active/01_STAGE_PRD.md`
5. `docs/active/02_TARGET_ARCHITECTURE.md`
6. `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
7. `docs/active/04_ACCEPTANCE_GATES.md`
8. `docs/active/06_TRACEABILITY_MATRIX.md`
9. `docs/active/24_P9_1_MARKET_DATA_AND_SOCRATIC_PROTOTYPE_PLAN.md`
10. `docs/active/jobpilot-p9-1-market-socratic-gap.md`
11. `docs/active/jobpilot-p9-1-market-socratic-gap.drawio`
12. `docs/p9_1_market_socratic_review/01_P9_1_PRD_EXTENSION.md`
13. `docs/p9_1_market_socratic_review/02_MARKET_MAP_PROTOTYPE_SPEC.md`
14. `docs/p9_1_market_socratic_review/08_TARGET_PAGE_AND_MODULE_DESIGN.html`

最终外部意见修订结论：P9.1 文档开发已被本地自动化候选实现接续并完成。不得声明真实市场 provider、招聘平台抓取、真实 ASR、自动投递或 MCP/Skill 连通性已实现。
