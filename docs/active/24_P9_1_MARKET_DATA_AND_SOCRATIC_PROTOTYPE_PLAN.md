# P9.1 真实市场数据、行政区划下钻式地图原型与苏格拉底式资料补全计划

状态：P9.1 本地自动化候选已完成。本文档记录 P9.1 从文档与原型阶段进入本地实现后的目标、实现证据和剩余边界；不代表真实市场 provider 接入、招聘平台抓取、真实 ASR、真实 provider 质量、自动投递或 MCP/Skill 连通性已经完成。

## 1. 阶段定位

P9 已完成本地自动化候选：Chatbox-native 信息架构、顶部服务中心、左侧求职态势、中央 Chatbox 主路径和右侧产物台。P9.1 已在本地/fixture 范围内完成三个体验缺陷的自动化候选实现：

1. 市场模块从低保真 SVG 示意升级为 ECharts 行政区划下钻式招聘情报地图。
2. 数据来源以 `Market Provider: not_configured`、fixture/manual/public/opt-in source legend 和 source refs 明确边界，未授权不外呼。
3. Chatbox 增加 Socratic Intake 一问一答状态机，用于采集简历事实、项目故事和能力证据。

P9.1 当前已形成的本地自动化候选能力：

```text
行政区划下钻式市场地图实现候选
+ opt-in 真实市场数据 provider 边界
+ Socratic Intake 对话状态机
+ PRD / 架构 / 验收 / drawio / HTML 自动化验收报告
```

P9.1 自动化候选证据入口：

- `apps/chatbox/src/main.tsx`
- `apps/chatbox/src/styles.css`
- `tests/evals/test_p9_1_market_socratic_acceptance_eval.py`
- `scripts/generate_p9_1_market_socratic_acceptance.py`
- `docs/reports/P9_1_MARKET_SOCRATIC_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p9_1_market_socratic/`

## 2. 目标体验

用户打开 JobPilot 后，应能自然完成以下路径：

```text
打开 Chatbox-native 工作台
→ 左侧市场地图不再像示意图，而像可审计招聘情报视图
→ 顶部明确显示市场数据来源：fixture / 用户粘贴 / 公开源 / opt-in API
→ 用户通过 Chatbox 说“看北京和上海 LLM 前端岗位真实市场情况”
→ 系统说明当前是否已配置真实市场 provider，没有配置时不伪造真实数据
→ 用户通过 Chatbox 进入苏格拉底式资料补全
→ Agent 一次只问一个高价值问题，逐步补齐项目背景、本人职责、技术难点、量化结果、证据来源和不可编造边界
→ 右侧产物台展示事实摘要、项目故事草稿、source refs 和 pending confirmations
```

### 2.1 目标页面总体设计

P9.1 目标页面必须从“向导卡片工作台”转为“Chatbox-native 求职情报工作台”。页面结构固定为四区：

| 区域 | 设计目标 | 主要模块 | 验收关注 |
| --- | --- | --- | --- |
| 顶部服务中心 | 让用户快速知道当前服务边界和外部能力是否可用 | `TopServiceCenter`、provider chips、safety boundary | 不把配置状态写成真实连通或真实调用 |
| 左侧市场情报 | 将市场、匹配、流程做成可折叠的情报层 | `MarketIntelligenceMap`、source legend、drilldown、match、pipeline | 地图不再像装饰图，数字必须可追溯 |
| 中央 Chatbox | 始终作为第一交互路径，承接市场查询、资料补全、产物修改 | journey strip、timeline、Socratic question、tool rail、composer | 不再被大型任务卡或表单压住 |
| 右侧产物台 | 持续展示事实、故事、JD 映射、申请包和待确认项 | fact summary、story draft、keyword mapping、source refs、pending confirmations | 不展示无证据产物，不隐藏待确认项 |

页面首屏优先级：

```text
1. Chatbox 可读、可输入、可连续对话
2. 顶部服务状态说明当前是否可用真实 provider
3. 左侧地图提供可理解的市场上下文
4. 右侧产物台只在事实或草稿出现后承担审查职责
```

设计审查页和最终实现报告：

- `docs/p9_1_market_socratic_review/08_TARGET_PAGE_AND_MODULE_DESIGN.html`
- `docs/reports/P9_1_MARKET_SOCRATIC_ACCEPTANCE_REPORT.html`

前者保留为 P9.1 前端开发前的目标设计基线；后者是当前本地自动化候选的真实界面截图和验收报告。不得用设计审查页替代最终报告，也不得把最终报告写成真实市场 provider、招聘平台、真实 ASR 或自动投递通过。

## 3. 市场地图原型设计

P9.1 地图实现候选采用“ECharts 行政区划求职情报板”而不是普通地理地图、低保真示意图或暗色假大屏。它可以具备互联网 App 常见的地图交互质感，但所有数字、图层和数据来源必须可解释、可追溯、可验收。核心设计：

- 底图：当前实现使用 fixture-only 行政区划 GeoJSON + ECharts map/geo；真实行政区划数据、真实市场 provider 或真实瓦片地图不作为默认能力。
- 下钻：必须支持全国 → 省/直辖市 → 城市 → 区县的逐级行政区划下钻；每次点击区域都要更新 `current_adcode`、`current_level`、breadcrumb、selected region、tooltip 和详情面板。
- 大地图感：默认左侧面板保持产品化二维行政区划图；展开态可以借鉴 `globe.gl` 的 raised polygons、轻微倾斜投影、区域抬升和 transition 来制造“大地图/地球仪感”，但不得牺牲行政区划可读性或把 3D 视觉写成真实数据能力。
- 情报板结构：必须包含 ECharts `visualMap`、`tooltip`、`toolbox`、图层切换、城市气泡、选区详情和 source legend，而不是单张静态地图。
- 城市图钉：大小表示岗位数量，颜色表示薪资中位数，描边表示数据可信度。
- 城市聚合：北京、上海、杭州、深圳、成都等重点城市可聚合为区域机会。
- 直方图叠层：图钉点击后展示薪资分布、年限分布和远程比例。
- 技术栈热度：React、TypeScript、Python、LLM、Data、Backend 等以 chip cloud 或小柱图展示。
- 来源可信度：区分 opt-in API、公开源、用户粘贴、fixture；fixture 必须使用弱化视觉标签。
- 交互：缩放、拖动、重置、hover tooltip、区域 selected、行政区划下钻、breadcrumb 返回、城市点击、技术栈筛选、source refs 展开、Chatbox 追问。

视觉要求：

- 不使用大面积单一绿色；主色保持 JobPilot 的克制商务感，加入数据蓝、琥珀、紫灰和中性色。
- 地图面板需要高密度但不拥挤，关键数字可扫读。
- 卡片半径不超过 8px，除地图容器和浮层外不使用过度圆角。
- 所有文字在 390px、720px、1200px、1440px、1920px 下可读，不遮挡。

可视化选型：

- 首选：Apache ECharts map/geo + GeoJSON。理由：最适合行政区划色块、城市气泡、区域 drilldown、薪资/技术栈叠层，能表达求职态势而不是导航地图。
- 备选：D3 + GeoJSON / TopoJSON。适合更自由的变形地图和复杂交互，但首版开发成本更高。
- 不作为主方案：Leaflet / MapLibre / OpenLayers。它们更适合真实地理地图、瓦片和 GIS，不适合作为当前求职态势主界面。
- 约束：行政区划数据必须来自合法 GeoJSON；外部地图或行政数据不等于真实招聘市场数据；GeoJSON 加载失败必须显示 fallback，不得空白验收。

### 3.1 市场地图模块详细设计

`MarketIntelligenceMap` 必须拆成可审查的前端子结构：

```text
MarketIntelligenceMap
├─ MarketIntelligenceBoard（左侧完整求职情报板）
├─ EChartsOptionBuilder（map / geo / visualMap / scatter / tooltip / toolbox）
├─ MarketLayerTabs（机会热度 / 薪资 / 技术栈 / 来源可信度）
├─ SourceStatusBar（当前数据：fixture / manual / public / opt-in API）
├─ AdministrativeDrilldownMap（全国 / 省 / 市 / 区县多级下钻）
├─ RegionDrilldownController（adcode / level / breadcrumb / hover / selected / fallback）
├─ AdministrativeRegionLayer（合法 GeoJSON choropleth / registerMap / selected emphasis）
├─ CityScatterLayer（重点城市气泡 / 岗位量 / 薪资层）
├─ RegionInsightPanel（全国 / 城市群 / 城市三级下钻与选区详情）
├─ SalaryHistogram（城市或岗位族薪资分布）
├─ TechHeatPanel（must-have / nice-to-have 技术栈热度）
├─ ChatboxPromptBridge（生成可编辑市场追问草稿）
└─ SourceRefsPanel（来源、置信度、抓取或粘贴边界）
```

交互闭环：

```text
用户点击城市 / 技术栈 / 薪资段
→ RegionInsightPanel 展示可追溯数据
→ Chatbox 生成可编辑追问
→ ArtifactWorkbench 记录 market insight 和 source refs
```

ECharts 情报板验收重点：

- 不是只换深色背景或做假大屏，必须有 ECharts 风格的 `visualMap`、`tooltip`、`toolbox`、可操作图层、行政区划下钻、breadcrumb、选区详情和来源解释；
- 地图容器可以进入 focus mode，但不能改变 Chatbox 是主路径的产品定义；
- 未配置真实 provider 时，KPI 中必须明确显示真实 provider 调用次数为 0 或 not_configured；
- 视觉效果不得使用户误以为已经完成真实全网搜索、平台抓取或实时市场接入。

开源实现参考和边界：

| 参考 | 可借鉴 | 不可直接承诺 |
| --- | --- | --- |
| `TangSY/echarts-map-demo` | AMap DistrictSearch 获取行政区划、行政编码、下级边界加载、多级下钻思路 | 依赖 AMap 服务和数据授权；不得默认联网抓取或无许可打包边界数据 |
| `liupl/echarts-china-map-drill-down` | 点击区域后加载对应 GeoJSON、`echarts.registerMap`、重新 `setOption` 的最小下钻路径 | 示例规模较小，不能替代生产许可、性能和多视口验收 |
| `vasturiano/globe.gl` / `react-globe.gl` | polygon altitude、hover 抬升、transition、globe mode 的视觉反馈 | 不作为默认二维行政区划主图；中国省市区县下钻需额外数据和性能审查 |
| `echarts-maps/echarts-china-cities-js` | 城市级 GeoJSON 资产组织方式和 ECharts usage | README 明确有 AMap 内容许可风险；商业或公开分发前必须单独审查 |

## 4. 真实市场数据 provider 边界

P9.1 保留真实市场数据 opt-in 规划，但当前自动化候选默认不接入、不调用、不保存 API Key。

候选 provider 只作为后续 opt-in 选项：

| Provider | 适用 | 风险 |
| --- | --- | --- |
| Adzuna API | 海外岗位聚合、公开 API 文档 | 覆盖中国岗位有限，需要 Key 和调用限额 |
| TheirStack API | 技术岗位、公司技术栈和岗位聚合 | 付费/配额/字段许可需审查 |
| JSearch API | 聚合职位搜索，适合快速原型 | 数据来源和地域覆盖需验证 |
| Jooble API | 全球职位搜索 API | 需要 Key，字段和使用条款需复核 |
| 用户粘贴 / 公司官网公开 JD | 合规、可审计 | 自动化程度低 |

禁止默认实现：

- BOSS、猎聘、拉勾、LinkedIn 登录、抓取、绕验证码或绕风控；
- 长期运行爬虫、队列、定时抓取、批量平台访问；
- 把 source_url 变成自动网页读取；
- 把 provider configured 写成真实数据已调用；
- 把 fixture 图表写成真实市场结论。

## 5. 文档级数据契约

以下实体中，`AdministrativeRegionNode`、`RegionJobDistributionSnapshot`、`MarketMapLayerState`、`RegionSourceRef` 和本地 `JobSearchRun` 表达已作为 P9.1 本地候选实现；真实 `JobMarketProvider`、`NormalizedJobPost`、`JobMarketSnapshot` 仍属于后续 opt-in 能力：

```text
JobMarketProvider
→ JobSearchRun
→ NormalizedJobPost
→ JobMarketSnapshot
→ MarketInsightViewModel
→ AdministrativeRegionNode
→ RegionJobDistributionSnapshot
→ MarketMapLayerState
→ MarketMapDrilldownState
→ RegionSourceRef
```

### 5.1 JobMarketProvider

用途：封装真实职位数据来源或合规公开源。

字段：

- `provider_id`
- `provider_name`
- `provider_type=opt_in_api|public_source|manual_paste|fixture`
- `configured_state=not_configured|configured|connected|failed|disabled`
- `requires_key`
- `rate_limit`
- `license_note`
- `last_checked_at`

约束：未配置或未授权时只能显示状态，不能发起真实请求。

### 5.2 JobSearchRun

字段：

- `run_id`
- `query`
- `city_filters`
- `salary_range`
- `tech_stack`
- `source_policy`
- `provider_ids`
- `started_at`
- `completed_at`
- `result_count`
- `source_refs`
- `boundary_note`

约束：必须记录数据来源和边界；失败时要保留原因，不得静默回退成 fixture 后宣称真实结果。

### 5.3 NormalizedJobPost

字段：

- `job_id`
- `title`
- `company`
- `city`
- `salary_range`
- `seniority`
- `tech_stack`
- `source_url`
- `source_type`
- `fetched_at`
- `confidence`

约束：缺失薪资、公司、城市、年限时不得自动补事实，只能进入待确认或低置信度。

### 5.4 JobMarketSnapshot

字段：

- `city_stats`
- `salary_histogram`
- `tech_heatmap`
- `source_breakdown`
- `remote_ratio`
- `competition_level`
- `trend_summary`

约束：每个聚合指标必须能追溯到 `NormalizedJobPost` 或 source refs。

### 5.5 行政区划地图状态契约

以下契约服务于 P9.1 行政区划下钻地图，不代表生产 schema 已实现。

`AdministrativeRegionNode` 字段：

- `adcode`
- `name`
- `level=country|province|city|district`
- `parent_adcode`
- `children_adcodes`
- `geojson_ref`
- `license_note`

`RegionJobDistributionSnapshot` 字段：

- `adcode`
- `job_count`
- `salary_median`
- `salary_histogram`
- `tech_heat`
- `source_breakdown`
- `confidence`
- `source_refs`

`MarketMapLayerState` 字段：

- `active_layer=opportunity|salary|tech_stack|source_trust|match`
- `selected_tech_stack`
- `source_filter`
- `visual_map_range`
- `legend_state`

`MarketMapDrilldownState` 字段：

- `current_adcode`
- `current_level`
- `breadcrumb`
- `hover_region`
- `selected_region`
- `zoom`
- `pan`
- `fallback_state`

`RegionSourceRef` 字段：

- `source_type=fixture|manual|public|opt_in_api`
- `source_id`
- `source_url`
- `provider_id`
- `confidence`
- `boundary_note`

约束：

- GeoJSON 数据必须有来源和许可说明；许可不清时只能作为原型参考，不能默认打包进产品。
- 区域颜色、tooltip 和详情面板不得展示没有 `source_refs` 或 fixture 标签的数字。
- `fallback_state` 必须能解释 GeoJSON 加载失败、provider 未配置、无结果和低置信度四类状态。

## 6. Socratic Intake 对话策略

P9.1 的 Chatbox 资料补全不应再像表单，也不应一次抛出多个问题。目标是“启发式事实采集”：

```text
用户给出模糊经历
→ Agent 判断缺失事实
→ 一次只问一个最关键问题
→ 用户回答后更新事实摘要
→ Agent 继续追问本人职责、技术难点、指标、证据、边界
→ 形成项目故事草稿和 pending confirmations
```

### 6.1 追问顺序

1. 目标角色：你想用这段经历支持哪个岗位或能力？
2. 项目背景：项目解决了什么业务问题？
3. 本人职责：你本人具体负责哪些模块或决策？
4. 技术难点：最难的问题是什么，为什么难？
5. 行动过程：你采取了哪些具体动作？
6. 量化结果：有没有性能、转化、成本、效率、稳定性指标？
7. 证据来源：这些事实来自哪里，是否可展示？
8. 风险边界：哪些内容不能写，哪些只是团队贡献？
9. JD 映射：这段经历适合哪个 JD 的哪些关键词？
10. 故事成稿：生成 STAR/CAR 草稿，并标注待确认项。

### 6.2 提问原则

- 一次只问一个问题；
- 优先问能改变简历事实质量的问题；
- 不替用户编造公司、年限、指标、项目贡献；
- 对不确定内容使用“待确认”而不是写成事实；
- 每 3-5 轮总结一次已知事实和缺口；
- 任何导出前必须展示 source refs 和 pending confirmations。

### 6.3 参考调研

GitHub 调研显示可参考但不可直接承诺复用的项目：

- `SankaiAI/ats-optimized-resume-agent-skill`：强调 master resume + JD + company，按阶段生成定制简历，不发明事实。
- `Azure-Samples/interview-coach-agent-framework`：展示面试 coach、会话状态和多 agent 编排，但偏模拟面试。
- `dungnotnull/mock-interview-coach-agent-skill`：使用 STAR/CAR、评分和改写，适合后续面试训练阶段。

结论：P9.1 需要自定义 Socratic Intake，先服务“事实采集和故事成稿”，后续再规划模拟面试评分。

## 7. 验收与打回条件

P9.1 本地自动化候选通过条件：

- PRD 明确真实市场数据只是 opt-in provider 规划，不是已接入；
- HTML 自动化验收报告包含真实界面截图、目标架构、当前实现、Socratic 用户路线、数据边界和 false-green 自检；
- drawio 不超过 8 页，并以颜色标注 P9 已实现、P9.1 已实现候选、后续高风险；
- Socratic 对话样例至少覆盖两个技术背景；
- 每个样例都形成事实摘要、故事草稿、source refs 和 pending confirmations；
- 不出现把全网 JD 搜索、BOSS 自动接入或真实 ASR 写成已经通过的虚假结论。

打回条件：

- 地图仍只是低保真装饰，不能表达招聘市场数据；
- 文档把 fixture 当成真实市场数据；
- 规划默认抓取招聘平台或默认调用真实 provider；
- Socratic Chatbox 变成一次性表单问卷；
- 申请包故事缺少事实边界和待确认项；
- 原型图没有标注 AI/样例/真实数据边界。

## 8. 已完成自动化开发与验收记录

P9.1 已按子阶段推进。每个子阶段开始前单独落盘开发计划和审计意见；每个子阶段结束后做端到端验收、PRD 规格检视和 false-green 扫描。

| 阶段 | 开发目标 | 端到端验收 | 当前状态 |
| --- | --- | --- | --- |
| P9.1-M0 | 开发前启动审计 | 复核 PRD、目标架构、drawio、验收门槛和高风险边界 | 已完成：`P9_1_M0_START_AUDIT.md` |
| P9.1-M1 | 行政区划下钻式市场地图 UI | 多视口截图证明地图可缩放、拖动、重置、hover、click、breadcrumb 返回，行政区划颜色深浅、城市气泡、visualMap、tooltip、薪资、热度、来源可信度可读 | 已完成：P9.1 报告截图覆盖 1920/1440/1200/720/390 |
| P9.1-M2 | opt-in 市场数据 provider 状态 | 未配置 provider 显示 `Market Provider: not_configured`；fixture/manual/public/opt-in API 来源可区分 | 已完成：未授权不外呼 |
| P9.1-M3 | Socratic Intake Chatbox | 两个技术背景各 10 轮以上一问一答，生成事实摘要、故事草稿、待确认项 | 已完成：报告 transcript + 产物台截图 |
| P9.1-M4 | 地图、Chatbox、产物台联动 | 点击城市、薪资段、技术栈后 Chatbox 追问，右侧产物台更新市场洞察和故事素材 | 已完成：地图下钻、Chatbox Socratic、Workbench 联动截图 |
| P9.1-M5 | 中文自动化验收报告 | HTML 报告包含真实截图、目标架构、当前实现、用户路径、未验证能力和 PRD 检视 | 已完成：`P9_1_MARKET_SOCRATIC_ACCEPTANCE_REPORT.html` |

## 9. 需要给 ChatGPT 或人类审计的文档集

总文件数控制在 12 个以内：

1. `docs/active/00_README.md`
2. `docs/active/01_STAGE_PRD.md`
3. `docs/active/02_TARGET_ARCHITECTURE.md`
4. `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
5. `docs/active/04_ACCEPTANCE_GATES.md`
6. `docs/active/06_TRACEABILITY_MATRIX.md`
7. `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
8. `docs/active/24_P9_1_MARKET_DATA_AND_SOCRATIC_PROTOTYPE_PLAN.md`
9. `docs/active/jobpilot-p9-1-market-socratic-gap.md`
10. `docs/active/jobpilot-p9-1-market-socratic-gap.drawio`
11. `docs/p9_1_market_socratic_review/08_TARGET_PAGE_AND_MODULE_DESIGN.html`
12. `docs/p9_1_market_socratic_review/06_CHATGPT_AUDIT_PROMPT.md`

审计结论允许判断“P9.1 本地自动化候选已完成”。不得把该结论写成真实市场 provider、招聘平台抓取、真实 ASR、真实 provider、自动投递或 MCP/Skill 连通性通过。
