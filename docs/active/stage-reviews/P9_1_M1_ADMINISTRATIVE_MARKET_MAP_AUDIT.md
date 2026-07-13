# P9.1-M1 行政区划下钻式市场地图审计

状态：实现候选已落地；最终通过状态以 P9.1-M5 全量自动化报告、截图和 eval 为准。

## 开发内容

- 在 Chatbox 左侧求职态势市场页中引入 ECharts map/geo 表达；
- 使用本地行政区划 fixture 组织全国、省、市、区县四级节点；
- 支持点击区域下钻、面包屑返回、图层切换、source legend、tooltip、区域详情、薪资直方图和技术栈热度；
- 保留 JobSearchRun 卡片，让用户能从地图追问城市、岗位、薪资或技术栈。

## PRD 规格检视

| PRD 要求 | 实现候选 |
| --- | --- |
| 不再使用低保真装饰图或静态 SVG | 改为 ECharts map/geo 与行政区划节点 |
| 行政区划颜色深浅表达岗位数量 | jobs 图层使用 visualMap |
| 支持点击区域下钻 | 点击 map 区域或区域快捷列表进入下一层 |
| 地图反馈不冒充真实市场数据 | source legend 与 region detail 标记 fixture/manual/public/opt-in |

## 验收证据要求

- 1920px、1440px、1200px、720px、390px 真实界面截图；
- 初始全国视图、北京下钻视图、薪资图层视图；
- 报告必须说明当前数据为本地 fixture / manual / public 样例，不是招聘平台抓取。

## 打回条件

- 地图退化为普通图片、静态 SVG 或无下钻能力；
- 图中没有 source legend 或数据可信度提示；
- 报告宣称真实市场 provider、招聘平台抓取或全网 JD 搜索通过。

