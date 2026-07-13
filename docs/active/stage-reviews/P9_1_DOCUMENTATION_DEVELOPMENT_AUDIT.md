# P9.1 文档开发审计

状态：历史文档开发审计，已被 P9.1-M0 到 M5 本地自动化候选实现和验收接续。本文档不代表真实市场 provider 接入、招聘平台抓取、真实 ASR、真实 provider、自动投递或 MCP/Skill 连通性已经完成。

## 1. 审计背景

人工体验反馈指出 P9 已完成本地自动化候选后仍存在三类问题：

- 市场模块地图体验很差，当前样式粗糙；
- 当前仍有大量 mock/fixture 数据，没有真实市场数据路径；
- Chatbox 需要使用苏格拉底启发式提问补充简历、项目故事和能力证据。

## 2. 本轮落盘文件

- `docs/active/24_P9_1_MARKET_DATA_AND_SOCRATIC_PROTOTYPE_PLAN.md`
- `docs/p9_1_market_socratic_review/01_P9_1_PRD_EXTENSION.md`
- `docs/p9_1_market_socratic_review/02_MARKET_MAP_PROTOTYPE_SPEC.md`
- `docs/p9_1_market_socratic_review/03_REAL_MARKET_DATA_PROVIDER_RESEARCH.md`
- `docs/p9_1_market_socratic_review/04_SOCRATIC_INTAKE_SPEC.md`
- `docs/p9_1_market_socratic_review/08_TARGET_PAGE_AND_MODULE_DESIGN.html`
- `docs/p9_1_market_socratic_review/06_CHATGPT_AUDIT_PROMPT.md`
- `docs/active/jobpilot-p9-1-market-socratic-gap.md`
- `docs/active/jobpilot-p9-1-market-socratic-gap.drawio`

## 3. 规格一致性

P9.1 当时明确为 P9 后的文档扩展，不推翻 P9 自动化候选结论；后续已进入并完成本地自动化候选。主线规格演进为：

```text
P9 已实现候选
→ P9.1 文档扩展
→ 用户批准后进入 P9.1-M0
→ P9.1-M1 到 M5 本地自动化候选完成
```

新增目标包括：

- 行政区划下钻式市场地图原型；
- 行政区划下钻式地图方案：全国/省/市/区县 drilldown、合法 GeoJSON、ECharts `visualMap` / `tooltip` / `toolbox` / `registerMap`、breadcrumb、hover/click feedback；
- opt-in 真实市场数据 provider 边界；
- Socratic Intake 一问一答资料补全；
- HTML 原型审查页；
- P9.1 drawio 和文本镜像。

## 4. 风险与边界

仍必须禁止：

- 把 fixture 写成真实市场数据；
- 把 provider configured 写成 connected 或 called；
- 默认抓取 BOSS、猎聘、拉勾、LinkedIn；
- 默认启用真实 ASR 或真实 provider；
- 自动投递或代表用户对外沟通；
- 用 HTML 原型或目标图样替代真实实现截图。

## 4.1 本轮行政区划地图修订记录

人工反馈指出此前地图设计仍然抽象、低质，期望接近控制中心或互联网 App 中“按行政区划着色、点击区域下钻、hover/click 有反馈、大地图/地球仪感”的体验。本轮文档修订已落盘：

- 主方案从泛化“高保真地图”收敛为 `ECharts map/geo + 合法 GeoJSON + visualMap + scatter + drilldown`；
- 明确 `AdministrativeDrilldownMap`、`RegionDrilldownController`、`AdministrativeRegionLayer`、`AdministrativeRegionNode`、`RegionJobDistributionSnapshot` 和 `MarketMapDrilldownState`；
- 明确全国 → 省/直辖市 → 城市 → 区县下钻、breadcrumb 返回、hover tooltip、click selected、selected region 与 Chatbox 草稿联动；
- 记录 `TangSY/echarts-map-demo`、`liupl/echarts-china-map-drill-down`、`globe.gl`、`react-globe.gl` 和 `echarts-china-cities-js` 的参考价值与许可风险；
- 明确 `globe.gl` 只作为展开态“大地图/地球仪感”参考，不替代默认二维行政区划主图；
- 明确 AMap 或第三方来源 GeoJSON 不得无许可审查直接打包进产品。

## 5. 审计结论

历史结论：当时 P9.1 文档包可以用于人工审查和下一轮开发计划制定。当前追加结论：P9.1-M0 到 M5 已完成本地自动化候选，但仍不声明任何高风险外部能力通过。
