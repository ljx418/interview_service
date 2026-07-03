# P9 开源地图与可视化方案调研

状态：Draft / 文档审查阶段
调研方式：使用 GitHub CLI 搜索开源项目，不引入生产依赖。

## 1. GitHub CLI 命令

```bash
gh search repos leaflet map visualization --limit 5 --json fullName,description,stargazersCount,license,url,updatedAt
gh search repos apache echarts map visualization --limit 5 --json fullName,description,stargazersCount,license,url,updatedAt
gh search repos maplibre gl js map --limit 5 --json fullName,description,stargazersCount,license,url,updatedAt
```

## 2. 候选方案

| 方案 | GitHub 结果 | 适合点 | 风险 / 约束 | P9 建议 |
| --- | --- | --- | --- | --- |
| MapLibre GL JS | `maplibre/maplibre-gl-js`，约 10k+ stars | 浏览器交互地图、缩放、拖动、图层、矢量瓦片能力成熟 | 需要地图样式、瓦片源、license/部署策略审查 | 生产候选，适合 P9-M3/M4 后续真实地图实现 |
| Leaflet + ECharts | `wandergis/leaflet-echarts3`, `gnijuohz/echarts-leaflet` | 轻量地图底图 + 统计可视化组合，适合城市薪资、热力、迁移线 | 插件维护度和 ECharts 版本兼容需验证 | 生产候选，适合先做城市图钉、薪资柱、流向线 |
| Apache ECharts Geo | 搜索结果显示不少业务 demo | 统计图强，柱状图、雷达图、热力图、关系图成熟 | 地图 geoJSON 来源和许可需单独处理 | 适合非地图底图的聚合可视化 |
| 内联 SVG + 原生 JS | 本轮审查页采用 | 离线可打开、可控、无依赖、便于审查交互意图 | 不是生产地图引擎，无法代表真实地图瓦片能力 | 当前文档原型使用，后续开发再替换为 MapLibre/Leaflet/ECharts |

## 3. 本轮选择

本轮 HTML 审查页选择 **内联 SVG + 原生 JS**：

- 支持放大、缩小、重置、拖动。
- 支持图钉选择和详情联动。
- 支持岗位市场、目标机会、投递流程三个视角切换。
- 不依赖外网 CDN，不下载第三方库，不改变前后端业务代码。

这只是 P9 文档原型，不代表 MapLibre、Leaflet、ECharts 或任何外部地图服务已经接入。

## 4. 后续生产建议

若进入 P9 代码开发：

1. P9-M3/M4 先用 ECharts 或 SVG 实现离线聚合图，降低地图瓦片依赖。
2. 需要真实地图底图时，再评估 MapLibre GL JS 或 Leaflet。
3. 地图数据源、瓦片源、geoJSON、招聘数据来源必须分别做 license 和隐私审计。
4. 地图图钉只展示聚合岗位和用户主动维护的流程状态，不展示未经授权个人位置。
