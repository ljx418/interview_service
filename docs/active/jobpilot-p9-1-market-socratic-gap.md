# JobPilot AI P9.1 市场地图、真实数据与 Socratic Intake 架构图说明

本文档是 `jobpilot-p9-1-market-socratic-gap.drawio` 的文本镜像，便于代码审查和 diff。当前图示主线是 **P9.1 本地自动化候选完成**。

P9 已完成本地自动化候选。P9.1 本地自动化候选也已完成；不代表真实市场 provider、招聘平台抓取、真实 ASR、真实 provider、自动投递或 MCP/Skill 连通性已经实现。

## 图示页结构

drawio 共 7 页，不超过 8 页：

1. P9.1 目标体验与阶段边界；
2. 当前 P9 基线与 P9.1 差距；
3. 目标架构与当前架构差异；
4. 代码实体与分层交互关系；
5. 行政区划下钻市场地图原型与真实数据边界；
6. Socratic Intake 用户路线与产物台联动；
7. 开发计划、里程碑、验收门槛与出门条件。

颜色含义：

- 绿色：P9 已实现或已完成自动化候选；
- 蓝色：P9.1 本地自动化候选已实现；
- 黄色：后续 opt-in provider 或需人工确认能力；
- 红色：高风险或禁止默认实现；
- 灰色：边界说明、审计证据或非目标。

## 第 1 页 - P9.1 目标体验与阶段边界

目标体验：

```text
用户打开 Chatbox-native 工作台
→ 左侧市场地图呈现行政区划下钻招聘情报视图
→ 顶部和地图显示数据来源状态
→ Chatbox 发起市场查询或资料补全
→ Socratic Intake 一次只问一个问题
→ 右侧产物台形成事实摘要、故事草稿、source refs 和 pending confirmations
```

边界：P9.1 只是本地/fixture 自动化候选，不声明真实市场 API、平台抓取、ASR、自动投递或真实 provider 已通过。

## 第 2 页 - 当前 P9 基线与 P9.1 差距

P9 基线：

- `TopServiceCenter` 已展示服务状态；
- `LeftIntelligencePanel` 已包含市场、匹配、流程三页签；
- `MarketMapView` 已支持图钉、缩放、拖动、重置；
- `ConversationPlane` 和 `handleP9Command` 已支持本地命令路由；
- `Workbench / P9ArtifactOverview` 已展示 search run、故事草稿和待确认项。

P9.1 差距：

- 地图视觉仍是低保真示意图，缺少行政区划下钻、真实边界、breadcrumb 和 hover/click 反馈；
- 数据仍以 fixture、用户粘贴和已导入 JD 为主；
- Chatbox 还缺少 Socratic Intake 的一问一答事实采集策略；
- 当前产物台还没有稳定展示 `CandidateFactSummary`、`ProjectStoryDraft`、`JDKeywordMapping` 和 `DoNotClaimList`。

## 第 3 页 - 目标架构与当前架构差异

| 当前 P9 | P9.1 目标 | 状态 |
| --- | --- | --- |
| `MarketMapView` | `MarketIntelligenceMap`、`AdministrativeRegionNode`、`RegionDrilldownController`、`AdministrativeRegionLayer`、`MarketSourceLegend`、`MarketInsightDrilldown` | P9.1 已实现候选 |
| 本地 search run / fixture | `Market Provider: not_configured`、`JobSearchRun`、`AdministrativeRegionNode`、`RegionJobDistributionSnapshot`、`RegionSourceRef` | P9.1 本地自动化候选已实现；真实 provider 后续 opt-in |
| `handleP9Command` 命令式资料补全 | `SocraticIntakeSession`、`SocraticQuestionPlanner`、`PendingConfirmations` | P9.1 已实现候选 |
| `P9ArtifactOverview` 故事草稿 | `CandidateFactSummary`、`ProjectStoryDraft`、`DoNotClaimList` | P9.1 已实现候选 |
| `TopServiceCenter` 服务状态 | 市场 provider configured / connected / called / failed / fallback 状态 | P9.1 需修改展示 |

架构不变量：

- UI 不直接抓取招聘平台；
- `source_url` 不自动读取网页；
- provider configured 不等于 connected 或 called；
- Socratic Intake 不编造事实；
- HTML 原型和目标图不能替代真实实现截图。

## 第 4 页 - 代码实体与分层交互关系

```text
User
→ TopServiceCenter（P9 已实现，P9.1 修改 provider 状态展示）
→ LeftIntelligencePanel（P9 已实现，P9.1 强化市场页）
  → MarketIntelligenceMap（P9.1 已实现候选）
    → AdministrativeDrilldownMap（P9.1 已实现候选：全国/省/市/区县下钻）
    → RegionDrilldownController（P9.1 已实现候选：level/breadcrumb/selected/layer）
    → AdministrativeRegionLayer（P9.1 已实现候选：fixture GeoJSON + ECharts registerMap）
  → MarketSourceLegend（P9.1 已实现候选）
  → MarketInsightDrilldown（P9.1 已实现候选）
→ ConversationPlane（P9 已实现，P9.1 增加 Socratic 状态）
  → SocraticIntakeSession（P9.1 已实现候选）
  → SocraticQuestionPlanner（P9.1 已实现候选）
  → PendingConfirmations / DoNotClaimList（P9.1 已实现候选）
→ Workbench / P9ArtifactOverview（P9 已实现，P9.1 强化展示）
  → CandidateFactSummary / ProjectStoryDraft / JDKeywordMapping / DoNotClaimList
→ API Boundary
  → JobMarketProvider / JobSearchRun / NormalizedJobPost / JobMarketSnapshot
  → AdministrativeRegionNode / RegionJobDistributionSnapshot / MarketMapDrilldownState
→ Domain Boundary
  → MarketDataNormalizer / ProjectStoryEvidenceGuard
→ SQLite Workspace / Artifact / Evidence
```

## 第 5 页 - 行政区划下钻市场地图原型与真实数据边界

目标地图必须展示：

- 全国 → 省/直辖市 → 城市 → 区县的行政区划下钻；
- 行政区划颜色深浅，表达岗位数、薪资、匹配度或来源可信度；
- 城市图钉、聚合气泡或热力；
- hover tooltip、click selected、breadcrumb 返回、zoom/pan/reset；
- 薪资直方图；
- 技术栈热度；
- 来源可信度；
- provider / public / manual / fixture 状态；
- 选区详情、source refs 展开和 Chatbox 追问。

真实数据边界：

- `JobMarketProvider` 只允许 opt-in；
- 未配置或未授权时只能展示 not_configured / unavailable；
- fixture fallback 必须弱化标注；
- 所有市场数字必须有 source refs 或明确样例标签；
- 不默认登录或抓取 BOSS、猎聘、拉勾、LinkedIn。
- 合法 GeoJSON 和第三方地图边界数据必须有许可说明；AMap 来源数据不得无审查直接打包进产品。

## 第 6 页 - Socratic Intake 用户路线与产物台联动

路线：

```text
用户给出模糊经历
→ Agent 问目标岗位
→ Agent 问项目背景
→ Agent 问本人职责
→ Agent 问技术难点
→ Agent 问行动过程
→ Agent 问量化结果
→ Agent 问证据来源
→ Agent 问不可编造边界
→ Agent 映射 JD 关键词
→ 生成 STAR/CAR 草稿和待确认项
```

产物台联动：

- `CandidateFactSummary` 展示已确认事实；
- `ProjectStoryDraft` 展示 STAR/CAR 草稿；
- `JDKeywordMapping` 展示 JD 关键词对应证据；
- `PendingConfirmations` 展示缺证据或需确认内容；
- `DoNotClaimList` 展示禁止写入简历或故事的内容。

验收重点：一次只问一个问题，每 3-5 轮总结一次，不确定事实进入 pending confirmations。

## 第 7 页 - 开发计划、里程碑、验收门槛与出门条件

P9.1 本地自动化候选出门条件：

- active PRD、目标架构、里程碑、验收门槛、追踪矩阵和 P9.1 专项文档已同步；
- HTML 原型页能展示当前截图、目标地图、Socratic 路线和 false-green 边界；
- drawio 可解析且不超过 8 页；
- P9 既有 stage closure eval 仍通过；
- 不声明真实市场 provider、平台抓取、ASR、自动投递或真实 provider 通过。

后续开发阶段：

| 阶段 | 目标 | 出门条件 |
| --- | --- | --- |
| P9.1-M0 | 开发前启动审计 | 文档无高风险默认实现 |
| P9.1-M1 | 行政区划下钻式市场地图 UI | 多视口截图证明地图可读、可缩放、可拖动、可下钻、breadcrumb 可返回，source legend 可见 |
| P9.1-M2 | opt-in 市场数据 provider 状态 | configured / connected / called / failed / fallback 可区分 |
| P9.1-M3 | Socratic Intake Chatbox | 两类技术背景 10 轮以上一问一答样例 |
| P9.1-M4 | 地图、Chatbox、产物台联动 | 城市/技术栈追问和右侧产物同步 |
| P9.1-M5 | 中文自动化验收报告 | 报告区分真实截图、原型图、fixture 和未验证能力 |

最终审计口径：本 drawio 证明 P9.1 本地自动化候选方向和实现证据已落盘。它不证明真实市场数据、招聘平台接入、真实 ASR、真实 provider、自动投递或 MCP/Skill 连通性通过。
