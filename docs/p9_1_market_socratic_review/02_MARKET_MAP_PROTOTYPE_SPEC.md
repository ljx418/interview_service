# P9.1 行政区划下钻式市场地图原型规格

状态：文档原型规格，不代表生产代码实现。

## 1. 当前基线问题

当前 `MarketMapView` 已支持图钉、缩放、拖动和重置，但仍像低保真示意图，无法达到成熟互联网 App 常见的地图交互质感：

- 行政区划和城市群关系没有表达清楚；
- 岗位数量、薪资和来源可信度没有形成清晰层次；
- 图钉样式像装饰圆点，缺少招聘情报语义；
- 缺少城市薪资直方图、技术栈热度、来源可信度和趋势摘要；
- fixture 和真实数据边界不够醒目。
- 缺少地图工具栏、图层切换、选区详情抽屉、时间范围、hover/click 状态和 Chatbox 联动反馈。

结论：上一版“暗色控制中心”原型也应打回。它看起来像假大屏，不适合 JobPilot 左侧辅助面板。P9.1 下一版必须以 ECharts 行政区划下钻式情报板为主方案，强调产品化、可读性、真实区划边界、可下钻、hover/click 有反馈和 Chatbox 联动，不能用视觉质感冒充真实市场数据接入。

## 2. 新版视觉结构

```text
ECharts Job Market Intelligence Board
├─ MarketIntelligenceBoard：左侧完整求职情报板
├─ MarketExpandedView：展开态市场情报视图，不改变 Chatbox 主路径
├─ EChartsOptionBuilder：map / geo / scatter / visualMap / tooltip / toolbox
├─ AdministrativeDrilldownMap：全国 / 省 / 市 / 区县逐级下钻地图
├─ RegionDrilldownController：adcode / level / breadcrumb / hover / selected / fallback
├─ AdministrativeRegionLayer：合法 GeoJSON choropleth / registerMap / selected emphasis
├─ CityScatterLayer：重点城市气泡 + 岗位量 + 薪资层
├─ MarketLayerTabs：机会热度 / 薪资 / 技术栈 / 来源可信度
├─ RegionInsightPanel：选区详情、薪资直方图、技术栈热度、来源解释
├─ SourceTrustLegend：provider / public / manual / fixture 和置信度
└─ ChatboxPromptBridge：点击城市、薪资段、技术栈后生成追问草稿
```

## 2.1 页面级位置与优先级

市场地图位于目标页面左侧的 `JobMarketIntelligencePanel`。它是辅助情报层，不允许抢占中央 Chatbox 主路径。桌面端默认展开，平板和移动端必须降级为可打开的态势面板。

目标页面中的关系：

```text
TopServiceCenter 显示 Market Provider 状态
→ JobMarketIntelligencePanel 展示市场地图和 source legend
→ ConversationPlane 接收城市 / 技术栈 / 薪资追问
→ ArtifactWorkbench 保存 market insight、source refs 和待确认项
```

视觉优先级：

1. ECharts 图表层级必须一眼可读：标题、图层、visualMap、地图、tooltip、选区详情不能混在一起；
2. 行政区划色块、城市群和城市气泡必须具备明确数据语义；
3. source legend 必须固定可见，不能被筛选器隐藏；
4. 城市详情、薪资直方图和技术栈热度是 drilldown 信息，不应堆成大表格；
5. Chatbox 联动入口必须显式，但不能变成平台自动搜索承诺；
6. 不采用 dark-control-center 假大屏作为主视觉；左侧面板使用浅色、清晰、可扫读的产品化图表风格。

## 2.2 开源地图库调研与选型

已使用 GitHub CLI 对开源地图模块做过一轮搜索。重新评估后，P9.1 第一版不再优先采用真实瓦片地图，而是采用行政区划可视化：

| 候选 | 适配判断 | 结论 |
| --- | --- | --- |
| Apache ECharts map/geo + GeoJSON | 最适合行政区划 choropleth、城市气泡、区域 drilldown、薪资/技术栈叠层 | 推荐作为 P9.1 下一阶段主路线 |
| TangSY/echarts-map-demo | 支持省、市、区县、乡镇边界获取和多级下钻，可参考行政编码与边界加载流程 | 仅作为参考；AMap 服务和内容许可必须单独审查 |
| liupl/echarts-china-map-drill-down | 点击区域后加载 GeoJSON、`echarts.registerMap`、重新渲染，是最小可理解下钻实现 | 适合实现思路，不替代生产数据许可和性能验收 |
| globe.gl / react-globe.gl | raised polygons、hover 抬升、transition 可提供“大地图/地球仪感” | 只作为展开态视觉参考，不作为默认主图 |
| D3 + GeoJSON / TopoJSON | 自由度最高，适合变形地图和复杂交互，但开发成本更高 | 高级备选 |
| Leaflet / MapLibre / OpenLayers | 更适合真实地理地图、导航、瓦片和 GIS 场景 | 当前不作为主路线 |

当前统一 HTML 原型页 `08_TARGET_PAGE_AND_MODULE_DESIGN.html` 已把地图主视图改成行政区划求职态势图。该原型只证明目标设计方向，不代表产品代码已集成 ECharts，也不代表真实市场数据 provider 已接入。

## 2.3 子模块设计

| 子模块 | 目标设计 | 不允许出现的问题 |
| --- | --- | --- |
| `SourceStatusBar` | 顶部小条显示 fixture / manual / public / opt-in API 与 provider 状态 | 把 fixture 写成真实市场 |
| `MarketIntelligenceBoard` | 左侧完整求职情报板容器，控制标题、图层、地图、侧栏和 source legend | 退化成独立 BI 大屏，抢占 Chatbox 主路径 |
| `MarketExpandedView` | 用户点击展开后显示模块级地图视图，包含查询、图层、地图、详情、证据栏 | 只做左栏小图，无法审查真实交互 |
| `EChartsOptionBuilder` | 生成 ECharts option：map/geo、scatter、visualMap、tooltip、toolbox、emphasis | 手写 SVG 继续硬编码坐标 |
| `AdministrativeDrilldownMap` | 全国/省/市/区县逐级下钻，点击区域后放大并展示下一层行政区划 | 只能点击城市圆点，不能看到真实区划层级 |
| `RegionDrilldownController` | 管理 adcode、层级、breadcrumb、hover、selected、zoom、pan 和 fallback | 下钻状态散落在 UI 中，无法验收或复现 |
| `AdministrativeRegionLayer` | 基于合法 GeoJSON 和 ECharts `registerMap` 绘制真实区划边界、emphasis、selected | 用抽象色块或静态 SVG 冒充行政边界 |
| `MarketLayerTabs` | 切换机会热度、薪资、技术栈、来源可信度 | 图层切换后没有视觉变化或缺少 source refs |
| `RegionOpportunityMap` | 保留为兼容别名，后续应收敛到 `AdministrativeRegionLayer` | 新旧命名混用导致架构图不可读 |
| `CityScatterLayer` | 重点城市气泡，大小表达岗位量，颜色表达薪资/热度/匹配 | 气泡遮挡行政区划或文字 |
| `RegionInsightPanel` | 选中区域详情面板，含岗位数、薪资中位、远程比例、竞争强度、趋势说明 | 缺 source refs 或无边界说明 |
| `SalaryHistogram` | 用短柱图展示薪资段分布，颜色与薪资琥珀 token 一致 | 与地图颜色语义冲突 |
| `TechHeatPanel` | must-have / nice-to-have 技术栈以 chip 或小柱图展示 | 变成长列表导致左侧失焦 |
| `SourceTrustLegend` | 展示 provider、公开源、用户粘贴、fixture 与置信度 | 隐藏低置信度来源 |
| `ChatboxPromptBridge` | 生成“分析该城市 / 比较薪资 / 补项目故事”等可编辑追问草稿 | 点击地图直接执行外部搜索或自动投递 |

## 3. 设计 token

- 背景：`#f7faf8`, `#eef5f1`, `#ffffff`
- 主色：`#176b5b`
- 数据蓝：`#2563eb`
- 薪资琥珀：`#b7791f`
- 风险红：`#c2410c`
- 证据紫灰：`#6d5bd0`
- 边框：`#d8e4de`
- 文本：`#10201d`, `#61746e`
- 圆角：卡片 8px，地图容器 10px
- 字号：11px 到 18px，禁止 viewport width 缩放字体

## 4. 交互状态

- Hover 省份/城市群/城市：显示职位数、薪资中位数和来源构成。
- Click 省份/城市群/城市：若存在下级区划则进入下一层行政区划；若无下级区划则选中区域，右侧显示 region insight，Chatbox 生成“分析该区域机会”草稿。
- Breadcrumb：显示全国 / 省 / 市 / 区县路径，支持返回上一层和重置全国视角。
- Selected feedback：选中城市必须有明确视觉反馈，包括气泡高亮、区域强调、连接线或等价视觉指向，以及右侧洞察同步。
- Zoom：0.75x 到 1.8x。
- Pan：限制在地图容器内，避免行政区划或气泡拖出视野。
- Reset：回到默认全国/重点城市视角。
- Source filter：切换 provider/public/manual/fixture，不允许隐藏 source refs。
- Layer switch：切换热度、薪资、技术栈、来源可信度时，ECharts option、visualMap 和右侧选区详情同步变化。
- Toolbox：提供 zoom、restore、save-as-evidence 或等价工具；不得用不可点击的装饰图标冒充。
- Expanded view：展开态必须包含顶部查询、左侧图层、中央地图、右侧详情、底部证据栏，并提供“同步到 Chatbox”动作。
- Focus mode：只放大左侧情报面板，不得抢占中央 Chatbox 的主路径定义。

## 4.1 体验质感和反馈标准

地图模块不得停留在静态说明图。后续实现必须具备以下反馈：

- Hover feedback：区域或城市悬停时，tooltip 浮层在 150-250ms 内出现，且不遮挡关键城市气泡。
- Selected feedback：点击上海、杭州等城市或行政区后，城市气泡、行政区域、breadcrumb 和右侧洞察面板必须同时进入选中态。
- Drilldown feedback：从全国进入省级、从省级进入城市级时，需要有轻量 zoom/opacity 过渡，并保留可返回路径。
- Transition feedback：图层切换、城市选择、tooltip 出现、右侧洞察切换需要有轻量过渡，禁止突然闪烁。
- Prompt feedback：生成 Chatbox 草稿时，需要显示“已生成可编辑草稿”或等价状态，不得直接执行外部搜索。
- Evidence feedback：fixture/manual/provider 的来源状态必须常驻可见，不能只藏在 tooltip。
- Accessibility feedback：可点击控件触控目标不小于 44px，键盘 focus 态和 aria-label 必须可验收。

## 5. 响应式

| 视口 | 行为 |
| --- | --- |
| 1920 / 1440 | 行政区划图、区域详情、薪资直方图和技术栈热度同时可见 |
| 1200 | 行政区划图保留，直方图和热度压缩为两列 |
| 720 | 左侧变为可展开抽屉，行政区划图默认半高 |
| 390 | 默认只显示 Chatbox；态势图作为全屏面板打开 |

## 6. 验收标准

- 行政区划图不能被误读为真实平台抓取结果；
- 每个数字有 source refs 或明确 fixture 标签；
- 真实 provider 未配置时必须显示未配置；
- 行政区划、城市气泡、直方图、热度和来源状态不能互相遮挡；
- 点击省份、城市群或城市后 Chatbox 能产生可读追问；
- 视觉层次要明显优于当前 SVG 示意图。
- ECharts 情报板必须包含 visualMap、tooltip、toolbox、图层切换、选区详情、薪资直方图、source legend 和 Chatbox 联动证据；
- 行政区划下钻必须单独验收：截图或步骤需要证明全国、省、市、区县至少三级路径中的两级可切换，并且 breadcrumb、selected region、详情面板同步；
- 地图不能再采用暗色假大屏作为主视觉，必须像可落地的产品组件。
- 展开态必须单独验收：截图需要证明查询栏、图层面板、地图画布、区域详情、底部证据栏和 Chatbox 联动草稿同时可读。
- 交互反馈必须单独验收：截图或自动化步骤需要证明 hover、selected、prompt draft、source boundary 四类状态存在。
