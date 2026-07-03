# P9 Chatbox-native 求职情报与申请包工作台计划

状态：P9 自动化候选已完成第一轮实现。本文档不代表全网 JD 搜索、ASR、真实 provider、招聘平台登录、自动投递或 MCP/Skill 连通性已经实现或通过验收。

## 1. 阶段定位

P9 是对当前前端体验和产品 PRD 的重新收束。用户明确反馈当前页面仍像一组向导卡片，Chatbox 的主体感不足，左侧求职态势没有讲清楚，也缺少主动搜索 JD、招聘信息汇总、申请包生成和过程状态可视化。

P9 目标不是继续堆叠资料向导，而是形成一个以 Chatbox 为核心的求职智能工作台：

```text
顶部服务中心
→ 左侧求职态势图
→ 中央 Chatbox 主控台
→ 右侧产物台
```

其中中央 Chatbox 始终是第一交互路径。用户通过对话发起 JD 搜索、薪资城市分析、候选人资料补全、简历与面试故事生成、申请包调整和投递流程更新；左右两侧只承担可视化和产物承载，不再抢占对话主路径。

P9 的实施定位必须被严格限定为：

```text
Chatbox-first UI 与信息结构重构
+ 求职情报可视化层
+ 现有 JobPilot 能力重新组织
```

P9 不是：

- 真实 JD 搜索系统；
- 真实 ASR 系统；
- 真实 MCP / Skill 平台；
- 真实招聘自动化系统；
- BI 数据分析平台；
- 长期任务调度系统。

P9 自动化开发只允许 UI 重排、现有 API 组合、Artifact 展示增强和 Chatbox 交互增强。

## 2. 目标体验

P9 完成后，用户应能在本地 Chatbox 中完成以下体验闭环：

1. 打开页面后，顶部看到服务状态、provider/ASR/MCP/Skill 配置摘要和安全边界。
2. 左侧看到可折叠、可切换、可放大拖动的求职态势图，包括岗位市场态势、目标机会与匹配态势、投递流程态势。
3. 中央看到 Chatbox 时间线、当前 Agent 历程状态、输入框和紧贴输入框的工具入口。
4. 通过 Chatbox 发起 JD、薪资、城市、公司、技术栈等招聘信息汇总。
5. 通过 Chatbox 或用户明确开启的 ASR 引导式会话补全简历模板、项目故事、能力证据、作品链接和求职偏好。
6. 基于不同 JD 自动生成可追溯的简历、面试故事、求职信或申请包草稿。
7. 通过 Chatbox 调整申请包、事实摘要、项目故事、岗位目标和投递流程。
8. 右侧产物台持续展示简历草稿、事实性背景摘要、岗位匹配、source refs、pending confirmations、导出预检和申请包版本。

## 3. 左侧求职态势三大板块

左侧栏不是向导卡片区，也不是表单区。它是求职态势观察与流程导航区。

### 3.1 岗位市场态势

目标问题：我现在应该关注哪些城市、薪资段、技术栈和公司类型？

必须展示：

- 城市维度：岗位数量、薪资中位数、远程比例、竞争强度。
- 技术栈维度：React、Python、LLM、数据工程、后端、前端等关键词热度。
- 薪资维度：薪资区间分布、城市差异、岗位年限要求。
- 来源维度：BOSS、猎聘、拉勾、LinkedIn、公司官网、手动粘贴、公开 RSS/API 等来源标签。

交互要求：

- 支持地图或地图形态可视化，含城市图钉、热力、聚合气泡或变形地图。
- 支持放大、缩小、拖动、重置视图。
- 点击城市或图钉后，中央 Chatbox 能接续解释该城市的岗位机会和推荐动作。
- 在没有真实外部搜索授权时，只能展示示例/手动导入/合规公开数据，不得声称全网搜索已完成。

### 3.2 目标机会与匹配态势

目标问题：哪些岗位最值得我投，短板是什么，应该先补什么资料？

必须展示：

- 多个目标 JD 的匹配度、岗位标题、公司、城市、薪资、技术栈。
- 与候选人画像的匹配项、短板项、待确认项。
- 每个 JD 对应的简历版本、面试故事版本和申请包状态。
- 可折叠的岗位对比、技能差距、项目证据覆盖度。

交互要求：

- 选择某个 JD 后，中央 Chatbox 当前上下文切换到该岗位。
- 用户可通过对话要求“帮我比较这三个北京后端岗位”“把上海岗位优先级调低”。
- 右侧产物台同步显示该 JD 的申请包草稿和待确认事实。

### 3.3 投递流程态势

目标问题：我投了哪些公司，每家公司处于什么流程，下一步该做什么？

必须展示：

- 公司/岗位列表：待评估、待投递、已投递、HR 沟通、笔试、面试、Offer、拒绝、搁置。
- 流程节点颜色：灰色未开始、蓝色进行中、琥珀色需行动、绿色完成、红色风险或失败。
- 下一步动作：补资料、生成定制简历、准备面试故事、跟进 HR、复盘面试。
- 每个流程节点的 source refs 和用户备注。

交互要求：

- 用户可通过 Chatbox 更新流程，例如“把字节后端岗位改成一面通过，下周三二面”。
- 所有流程更新必须可回看，不得静默覆盖关键历史。
- 不得默认自动投递、自动沟通或代表用户对外发送消息。

## 4. 信息架构与代码实体目标

P9 目标架构必须映射到具体代码实体，不能只写抽象能力。

```text
User
→ Chatbox Experience Shell (`apps/chatbox/src/main.tsx`)
  → TopServiceBar（顶部服务中心，待新增）
  → LeftIntelligencePanel（左侧求职态势图，待新增）
    → MarketMapView（地图/图钉/热力，待新增）
    → OpportunityMatchPanel（岗位机会与匹配，待新增）
    → ApplicationPipelineView（投递流程态势，待新增）
  → ConversationPlane（中央 Chatbox，需修改）
    → JourneyStateHeader（当前历程状态，待新增或改造）
    → MessageTimeline（已实现基线，需保留优先级）
    → ComposerToolRail（输入框工具入口，需修改）
    → ChatboxCommandRouter（对话意图路由，待新增）
  → RightArtifactBench（右侧产物台，需修改）
    → CandidateProfileSummary（已实现候选）
    → JobTargetList / ResumeGenerationPlane（已实现候选，需重排）
    → StoryBank / ApplicationPackageVersion（待新增或强化）
→ FastAPI Agent Service (`services/api/main.py`, `services/api/schemas.py`)
  → Provider Health / Service Health（已有基础，需扩展展示）
  → Job Source / Search Runs（待新增，需合规边界）
  → Profile / Resume / Application Package routes（部分已实现）
→ Domain Tools
  → JobSourceConnector（待新增；默认只用合规公开/用户粘贴/fixture）
  → CandidateFactGraph / StoryBank（待新增或强化）
  → ResumePackageGenerator（已有基础，需围绕多 JD 强化）
  → ApplicationPipelineService（待新增）
→ SQLite Workspace / Artifact / Evidence
```

状态颜色：

- 绿色：已实现或已完成自动化候选。
- 蓝色：现有实体需修改。
- 黄色：待新增实体。
- 红色：高风险能力，必须独立确认。
- 灰色：非目标或禁止默认实现。

## 5. 开发计划

P9 已完成文档设计和第一轮自动化候选实现。后续若进入真实平台、真实 provider、真实个人资料、ASR 或自动投递，必须单独立项和授权。

| 阶段 | 目标 | 出门条件 |
| --- | --- | --- |
| P9-DOC-M0 | 新版 PRD、前端审查页、左侧态势细化和开源地图方案调研 | 文档能解释目标体验、基线差距、概念图和用户路线 |
| P9-DOC-M1 | 主线文档、roadmap、追踪矩阵、drawio 同步 | README/TODO/active/drawio 均进入 P9 文档阶段口径 |
| P9-DOC-M2 | 文档审计收口 | 无新增致命或重大规格偏差；不把目标写成已实现 |
| P9-M0 | 开发前启动审计 | 审计确认 P9 文档足以进入实质开发 |
| P9-M1 | Chatbox-native 信息架构重构 | 中央 Chatbox 首屏优先，无向导卡片压住聊天 |
| P9-M2 | 顶部服务中心 | provider/ASR/MCP/Skill/安全边界状态可见，未配置不写成连通 |
| P9-M3 | 左侧求职态势图 | 三大板块可切换，地图/图钉/聚合视图可放大拖动 |
| P9-M4 | JD 信息源与搜索运行 | 只支持用户粘贴、fixture、已有本地示例或合规公开样例数据的 search run 表达；不建设真实搜索系统 |
| P9-M5 | Chatbox 引导式资料与故事补全 | 通过对话补简历、项目故事、能力证据；ASR 只保留 opt-in 状态，真实采集延期 |
| P9-M6 | 多 JD 申请包生成 | 每个 JD 生成可追溯简历、面试故事和申请包版本 |
| P9-M7 | Chatbox 驱动产物与流程更新 | 用户通过对话调整事实、申请包和投递流程 |
| P9-M8 | 响应式与视觉质量验收 | 1920/1440/1200/720/390 多视口无重叠、可读、核心入口可达 |
| P9-M9 | 中文自动化验收报告 | 真实截图、PRD 规格检视、证据边界和未验证范围完整 |

## 6. 验收门槛

P9 出门验收必须覆盖：

- Chatbox 主路径：中央时间线、状态栏和输入框首屏可见。
- 顶部服务中心：能看出 provider、ASR、MCP、Skill、外部搜索等服务是否配置、是否启用、是否受限。
- 左侧态势图：三大板块、地图/图钉或等价地图可视化、缩放、拖动、折叠和 Chatbox 联动路径可验收。
- JD 搜索/汇总：只在合规源、公开源、用户粘贴或 fixture 下验收；不得虚假声明 BOSS 等平台自动接入。
- 用户信息补全：通过 Chatbox 引导补资料，缺证据进入 pending confirmations。
- 申请包生成：简历、面试故事、求职信或申请包草稿必须有 source refs 和版本边界。
- 流程更新：用户通过 Chatbox 更新投递流程，但系统不默认对外投递或沟通。
- 多视口体验：1920px、1440px、1200px、720px、390px 均需真实截图。

最低自动化证据：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
drawio XML parse
P9 browser acceptance screenshots
P9 Chinese HTML acceptance report
```

## 7. 非目标和高风险边界

P9 文档设计允许规划下列能力，但不得把它们写成本阶段已实现：

- 全网 JD 搜索；
- BOSS、猎聘、拉勾、LinkedIn 等平台登录、抓取、自动沟通或自动投递；
- 真实 MiniMax、DeepSeek、OpenAI-compatible provider 默认外呼；
- ASR 真实麦克风采集和外部语音服务；
- MCP / Skill 真实连通性；
- SaaS、多租户、Billing；
- workspace 删除、迁移 apply 或不可逆操作。
- 真实数据源系统、长期运行任务系统或独立业务服务。

上述能力进入代码开发或验收时，必须有独立授权、数据范围、调用次数、日志脱敏、失败降级和退出条件。
