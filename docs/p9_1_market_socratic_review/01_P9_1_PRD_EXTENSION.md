# JobPilot AI P9.1 PRD 扩展初稿

状态：文档开发与原型审查阶段。本文档用于扩展 P9，不进入代码实现。

## 1. 背景

P9 已把 JobPilot 从向导卡片式工作台推进到 Chatbox-native 工作台，但人工体验反馈仍有三个核心缺陷：

- 市场模块地图视觉粗糙，无法让用户相信它是求职市场情报工具。
- 当前数据仍以 fixture、用户粘贴和已导入 JD 为主，没有真实市场数据路径。
- Chatbox 还偏命令触发，缺少苏格拉底启发式提问来帮助用户补齐简历事实和项目故事。

## 2. P9.1 目标

P9.1 目标是先完成文档与原型设计：

```text
行政区划下钻式市场地图原型
→ 真实市场数据 provider 边界
→ Socratic Intake 对话策略
→ 可审查 HTML 原型页
→ active PRD / 架构 / 验收 / drawio 同步
```

P9.1 不声明任何真实 provider、真实招聘平台、真实 ASR、自动投递或真实个人资料路径已经通过。

## 3. 目标用户体验

用户应该能通过一个连续对话完成求职材料准备：

1. 打开工作台，看到左侧市场地图不是装饰图，而是行政区划下钻式招聘情报入口。
2. 系统清楚显示当前市场数据来源：fixture、用户粘贴、公开源或 opt-in API。
3. 用户问“北京和上海 LLM 前端岗位真实市场怎么样？”
4. 如果没有配置真实 provider，系统明确说明只能展示本地/样例数据。
5. 用户说“帮我把智能客服项目整理成简历故事。”
6. Agent 以苏格拉底方式逐步追问背景、本人职责、技术难点、行动、指标、证据和边界。
7. 右侧产物台形成项目故事草稿、source refs、pending confirmations 和 JD 映射。

## 4. 市场地图体验要求

地图模块必须回答：

- 哪些城市机会最多？
- 哪些城市薪资更匹配？
- 哪些技术栈热度高？
- 哪些数据来自真实 provider，哪些只是 fixture？
- 哪些岗位值得进一步生成申请包？

地图必须具备：

- 全国/省/市/区县行政区划下钻；
- 行政区划颜色深浅表达岗位数、薪资、匹配度或来源可信度；
- 城市图钉、聚合气泡或热力层；
- hover tooltip、click selected、breadcrumb 返回、缩放、拖动和重置；
- 薪资直方图；
- 技术栈热度；
- 来源可信度；
- 点击区域后放大展示下一层区划或选区详情，并联动 Chatbox；
- 390px、720px、1200px、1440px、1920px 响应式策略。

地图主方案：`Apache ECharts map/geo + 合法 GeoJSON + visualMap + scatter + drilldown`。`TangSY/echarts-map-demo`、`liupl/echarts-china-map-drill-down`、`globe.gl`、`react-globe.gl` 和 `echarts-china-cities-js` 只作为开源参考；涉及 AMap 或第三方边界数据时必须单独审查许可，不得直接写成产品依赖或真实数据接入。

## 5. 真实市场数据要求

P9.1 仅规划 opt-in provider：

- Adzuna；
- TheirStack；
- JSearch；
- Jooble；
- 用户粘贴和公司官网公开 JD。

默认不做：

- BOSS、猎聘、拉勾、LinkedIn 平台登录；
- 平台自动抓取；
- 绕验证码、反爬或权限；
- 自动沟通或自动投递；
- source_url 自动读取网页。

## 6. Socratic Intake 要求

Chatbox 必须用启发式追问替代大表单：

- 一次只问一个问题；
- 每个问题都服务于事实质量提升；
- 每 3-5 轮总结已知事实；
- 不确定内容进入 pending confirmations；
- 草稿必须区分“事实”“建议表达”“待确认”。

核心追问维度：

- 目标岗位；
- 项目背景；
- 本人职责；
- 技术难点；
- 具体行动；
- 量化结果；
- 证据来源；
- 不可编造边界；
- JD 关键词映射；
- STAR/CAR 故事草稿。

## 7. 非目标

P9.1 不实现：

- 真实全网 JD 搜索；
- 招聘平台账号登录或自动抓取；
- 真实 ASR 麦克风采集；
- 真实 provider 默认调用；
- MCP/Skill 真实连通；
- 自动投递、自动沟通、SaaS、多租户、Billing。
