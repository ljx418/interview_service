# P9.1-M0 开发前启动审计

状态：自动化开发启动审计已完成；后续结论仍以 P9.1-M5 全量自动化验收报告为准。

## 审计范围

P9.1 本阶段只允许实现以下内容：

- 行政区划下钻式市场地图 UI；
- Market Provider / JobSearchRun 的 opt-in 和未配置状态表达；
- Chatbox Socratic Intake 一问一答资料补全；
- 市场地图、Chatbox 和右侧产物台的本地联动；
- 中文 HTML 自动化验收报告和真实界面截图。

## 不进入的高风险范围

- 不登录、抓取或自动操作 BOSS、猎聘、拉勾、LinkedIn 等招聘平台；
- 不默认调用 MiniMax、DeepSeek、OpenAI-compatible 或其他真实外部 LLM provider；
- 不读取未授权真实个人资料；
- 不启用真实 ASR、会议平台、自动投递、SaaS、多租户或 MCP/Skill 连通性验收；
- 不把 fixture / manual / public 样例数据写成真实市场 provider 通过。

## 文档支撑结论

P9.1 PRD、目标架构、里程碑、验收门槛、追踪矩阵、drawio 和 P9.1 原型审查页已覆盖 M1 到 M5 的实现边界、代码实体、验收证据和打回条件。可以进入实现，但每个子阶段必须保留独立审计记录并在最终报告中复验。

## 出门条件

- 后续实现不得偏离 Chatbox-native 工作台主线；
- 行政区划地图必须有 source legend、breadcrumb、tooltip/hover/click feedback 和多图层表达；
- Socratic Intake 必须是一问一答，不得一次性表单化或编造事实；
- 最终必须使用真实浏览器界面截图而不是原型图替代验收。

