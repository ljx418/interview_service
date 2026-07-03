# P9 前端体验规格

## 1. 设计原则

P9 前端的主控入口只有一个：中央 Chatbox。
其他区域只辅助观察、配置、确认和交付。

反模式：

- 大量向导卡片常驻中央。
- 用按钮堆叠替代对话引导。
- 把资料表单放到聊天时间线之前。
- 左右栏内容和中央 Chatbox 竞争注意力。
- 顶部导航只做装饰，不表达系统可用性。

## 2. 页面结构

```text
Top Service Bar
├─ Provider / MCP / Skill / ASR / Search Source / Workspace / Diagnostics

Main Workspace
├─ Left Intelligence Panel
│  ├─ A. 岗位市场态势
│  ├─ B. 目标机会与匹配态势
│  └─ C. 投递流程态势
├─ Center Chatbox Plane
│  ├─ User Journey State Machine
│  ├─ Message Timeline
│  ├─ Command Chips
│  └─ Composer
└─ Right Artifact Bench
   ├─ 当前目标 JD
   ├─ 候选人事实摘要
   ├─ 简历 / 项目故事 / 面试故事
   ├─ Source refs
   ├─ Pending confirmations
   └─ Export preflight
```

## 3. 顶部服务栏

职责：

- 展示当前 provider、MCP、Skill、ASR、搜索源、workspace 和诊断状态。
- 明确区分 configured、available、called、failed、fallback。
- 提供设置入口。

禁止：

- 展示 API Key。
- 把 configured 写成 called。
- 在未确认时触发真实外呼。

## 4. 左侧求职态势图

职责：

- 以页签或折叠面板展示岗位市场、目标机会和投递流程。
- 图表必须来自标准化 JD 或用户更新的流程状态。
- 可以隐藏或压缩，不能挤压 Chatbox。

三大板块：

### A. 岗位市场态势

回答“哪里有机会、薪资怎样、技术栈热度如何”。默认展示：

- 本轮岗位数、城市数、主薪资区间和来源数。
- 城市薪资直方图或区间图。
- 技术栈热度 chip cloud。
- 来源可信度分组：公司官网、搜索 API、用户粘贴、其他公开来源。
- 最近搜索时间和 source refs 入口。

### B. 目标机会与匹配态势

回答“哪些机会最值得我优先处理，缺什么证据”。默认展示：

- 重点目标岗位列表。
- 每个岗位的匹配摘要、薪资城市、关键差距和下一步。
- 颜色状态：高匹配、需补证据、暂缓。
- “设为重点”“补证据”“生成申请包”等轻操作入口，这些操作也必须能通过 Chatbox 发起。

### C. 投递流程态势

回答“每家公司到哪一步了，下一步做什么”。默认展示：

- 收藏 / 待评估 / 已生成申请包 / 已投递 / 筛选中 / 一面待约 / 面试中 / Offer / 关闭。
- 公司、岗位、城市、薪资、当前阶段、下一步行动和最近更新时间。
- 关联申请包版本和待确认项。
- Chatbox 更新记录，例如“把 B 公司改成一面待约”。

详细设计见 `09_LEFT_INTELLIGENCE_PANEL_DETAIL.md`。

## 5. 中央 Chatbox

职责：

- 首屏第一优先。
- 用户可直接输入求职目标。
- 状态机显示“正在搜索 / 等待补资料 / 生成中 / 待确认 / 可导出”。
- command chips 只作为快捷入口，不替代聊天。

示例输入：

- “帮我找上海 25k-40k React 岗位，按薪资和公司阶段汇总。”
- “把最适合我的 5 个岗位列出来。”
- “我来讲一下电商后台项目，你帮我整理成 STAR 故事。”
- “给 A 公司生成一版偏性能优化方向的简历。”
- “把 B 公司状态改成一面待约。”

## 6. 右侧产物台

职责：

- 展示所有可审查产物和中间产物。
- 对每个申请包展示版本、source refs、待确认项和导出状态。
- 支持通过 Chatbox 指令定位和编辑指定产物。

禁止：

- 只显示内部 JSON。
- 无产物时只显示空白。
- 没有 source refs 的内容直接可导出。

## 7. 响应式

- 1440px / 1920px：四区同时可见，中央 Chatbox 最大视觉权重。
- 1200px：左侧图表压缩，右侧保留关键产物。
- 720px：顶部保留，左侧和右侧折叠为页签，Chatbox 优先。
- 390px：默认只显示 Chatbox，态势图和产物台通过底部/顶部切换进入。

## 8. 地图类可视化与交互要求

P9 左侧态势图应支持地图类可视化，但第一版必须先保证离线可验收：

- 文档原型使用内联 SVG + 原生 JS，支持图钉、拖动、放大、缩小、重置和视角切换。
- 生产实现候选参考 `10_OPEN_SOURCE_MAP_VISUALIZATION_RESEARCH.md` 中的 MapLibre GL JS、Leaflet + ECharts、Apache ECharts Geo。
- 地图图钉至少支持三种语义：岗位数量 / 机会匹配状态 / 投递流程阶段。
- 图钉点击后必须联动右侧说明或产物台。
- 地图和图表数据必须来自标准化 JD、match_report、candidate_profile 或用户显式维护的流程状态。
- 地图不得暗示真实平台登录、自动抓取、自动投递或用户真实地理位置追踪。
