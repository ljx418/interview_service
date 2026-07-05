# P9 Chatbox-native 文档覆盖度复审

状态：文档开发阶段复审。本文档不代表 P9 UI、全网 JD 搜索、ASR、真实 provider、MCP/Skill、招聘平台自动接入或自动投递已经实现。

## 1. 复审问题

本轮复审回答四个问题：

1. 当前文档是否完整解决用户提出的前端体验和产品方向问题？
2. P9 目标是否已经落盘到相关 Markdown 文档和 drawio 文件？
3. 当前文档是否足以支撑 P9 本阶段后续自动化开发？
4. P9 完成后是否能顺利完成出门验收，或者是否存在必须先让用户选择技术路线的高风险阻塞？

## 2. 用户问题覆盖结论

| 用户诉求 | 文档覆盖位置 | 覆盖结论 |
| --- | --- | --- |
| 不要大量向导卡片，Chatbox 成为第一交互路径 | `01_STAGE_PRD.md`, `02_TARGET_ARCHITECTURE.md`, `04_ACCEPTANCE_GATES.md`, drawio 第 1/3/5 页 | 已覆盖 |
| 自动搜索全网各信息源 JD | `01_STAGE_PRD.md`, `23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`, `17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md` | 已规划，但明确第一阶段只允许合规公开源、用户粘贴源或 fixture；平台自动接入需独立授权 |
| 通过 Chatbox 汇总 JD、薪资、城市招聘信息 | `01_STAGE_PRD.md`, `03_MILESTONES_AND_DELIVERY_PLAN.md`, `06_TRACEABILITY_MATRIX.md` | 已覆盖 |
| 通过 Chatbox 或 ASR 引导补全简历、项目故事和用户信息 | `01_STAGE_PRD.md`, `02_TARGET_ARCHITECTURE.md`, `23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md` | 已覆盖；ASR 真实路径被标记为高风险 opt-in |
| 生成不同 JD 的简历、面试故事和申请包草稿 | `01_STAGE_PRD.md`, `04_ACCEPTANCE_GATES.md`, `06_TRACEABILITY_MATRIX.md` | 已覆盖 |
| 通过 Chatbox 调整申请包、项目事实和中间产物 | `01_STAGE_PRD.md`, `03_MILESTONES_AND_DELIVERY_PLAN.md`, `23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md` | 已覆盖 |
| 右侧产物台持续展示简历、事实摘要和结果产物 | `02_TARGET_ARCHITECTURE.md`, drawio 第 1/3/5 页 | 已覆盖 |
| Chatbox 上方展示用户历程状态 | `01_STAGE_PRD.md`, `02_TARGET_ARCHITECTURE.md`, `06_TRACEABILITY_MATRIX.md` | 已覆盖 |
| 顶部导航展示配置和服务状态 | `02_TARGET_ARCHITECTURE.md`, `04_ACCEPTANCE_GATES.md`, drawio 第 1/3/7 页 | 已覆盖 |
| 左侧展示求职态势图、地图/图钉、流程状态，并可通过 Chatbox 更新 | `23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`, `09_LEFT_INTELLIGENCE_PANEL_DETAIL.md`, `10_OPEN_SOURCE_MAP_VISUALIZATION_RESEARCH.md`, drawio 第 4/5 页 | 已覆盖 |

结论：用户提出的问题已经被完整落入 P9 文档主线。当前文档不再只是抽象说“优化 UI”，而是明确了顶部服务中心、左侧态势图、中央 Chatbox、右侧产物台四个区域及其交互边界。

## 3. 落盘完整性

P9 已落盘到以下主线文件：

- `README.md`
- `TODO.md`
- `docs/active/00_README.md`
- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`
- `docs/active/stage-reviews/P9_DOCUMENTATION_DEVELOPMENT_AUDIT.md`
- `docs/active/stage-reviews/P9_DOCUMENTATION_COVERAGE_REAUDIT.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`

P9 审查材料保留在：

- `docs/p9-chatbox-native-review/`

结论：P9 目标已经完整落盘到相关 Markdown 和 drawio 文件。

## 4. 开发支撑能力评估

当前文档能支撑后续自动化开发，原因如下：

- PRD 明确了用户目标、目标体验、必须产出的用户结果和非目标；
- 目标架构明确了具体代码实体、状态、上游/下游和禁止关系；
- 里程碑拆分为 P9-DOC、P9-M0、P9-M1 到 P9-M9；
- 验收门槛覆盖 Chatbox 主路径、左侧态势图、顶部服务中心、申请包事实安全和多视口证据；
- 追踪矩阵把目标、实体、文件、当前证据和验收门槛连起来；
- drawio 共 8 页，覆盖目标架构与当前差异、代码实体分层、左侧态势图、用户路线、开发计划、出门条件和安全边界。

开发前仍需在 P9-M0 做启动审计，但这属于正常流程，不是文档缺口。

## 5. 出门验收可达性

P9 完成后可以顺利进入出门验收，前提是后续开发严格遵守以下门槛：

- 每个实现阶段都产出真实界面截图，不用概念图替代；
- JD 搜索只能在合规公开源、用户粘贴源或 fixture 下验收；
- ASR、真实 provider、招聘平台自动化、MCP/Skill 连通性必须独立授权；
- 申请包生成必须保留 source refs、pending confirmations 和版本边界；
- 1920px、1440px、1200px、720px、390px 多视口必须可读、无重叠、核心入口可达；
- 中文 HTML 验收报告必须列出目标架构、当前实现、用户路径、截图证据和未验证范围。

## 6. 风险与技术路线

当前没有必须暂停让用户选择技术路线的高风险阻塞。主要风险已经被文档约束：

| 风险 | 当前处理 |
| --- | --- |
| 全网 JD 搜索范围过大 | P9-M4 第一阶段限定为用户粘贴、fixture 或合规公开源；招聘平台自动接入独立立项 |
| 地图可视化依赖外部服务 | P9-M3 可先用 SVG/ECharts/离线地图形态实现，再评估 MapLibre/Leaflet |
| ASR 涉及麦克风和外部服务 | 仅作为 opt-in 路线，真实采集前必须单独授权 |
| 真实 provider 质量不可控 | 顶部服务中心只展示状态，真实外呼仍走 P6 opt-in 边界 |
| 自动投递/自动沟通合规风险 | 明确为非目标，不进入 P9 默认实现 |
| P9 扩张成平台系统 | 增加实施范围锁：不新增真实数据源系统、外部平台接入、长期任务系统或独立业务服务，只做 UI/信息结构/可视化层和现有能力重组 |

## 7. 复审结论

通过。当前文档已经完整支撑 P9 本阶段后续自动化开发，可以进入 P9-M0 开发前启动审计。

限定结论：

- 可以声明：P9 文档主线已完整落盘。
- 可以声明：当前文档足以支撑 P9-M0 到 P9-M9 后续开发和验收。
- 不可以声明：P9 UI 已实现。
- 不可以声明：全网 JD 搜索、ASR、真实 provider、MCP/Skill、招聘平台自动接入、自动投递或真实个人资料路径已通过。

## 8. 多轮独立审计记录

### 8.1 第一轮：PRD 体验路径审计

审计问题：P9 PRD 是否完整覆盖用户提出的 10 项体验诉求？

结论：通过。

理由：

- PRD 明确四区结构：顶部服务中心、左侧求职态势图、中央 Chatbox、右侧产物台；
- PRD 明确 Chatbox 发起 JD/薪资/城市招聘信息汇总；
- PRD 明确 Chatbox/ASR 引导式资料补全；
- PRD 明确不同 JD 的简历、面试故事、求职信和申请包草稿；
- PRD 明确 Chatbox 驱动产物和投递流程更新；
- PRD 明确 P9 非目标和高风险边界。

剩余注意事项：开发阶段不得把“自动搜索全网 JD”的远期目标实现为默认登录招聘平台或绕风控抓取。

### 8.2 第二轮：目标架构审计

审计问题：目标架构是否落到具体代码实体和分层关系？

结论：通过。

理由：

- `02_TARGET_ARCHITECTURE.md` 已列出 `TopServiceCenter`、`LeftIntelligencePanel`、`MarketMapView`、`OpportunityMatchPanel`、`ApplicationPipelineView`、`ConversationPlane`、`Agent State / workflow strip`、`Workbench / P9ArtifactOverview` 等 UI 实体；
- 已列出 `JobSourceConnector`、`StoryBank`、`ApplicationPipelineService`、`ResumePackageGenerator` 等 Domain/API 实体；
- 已明确 `job`、`match_report`、`candidate_profile`、`resume_version`、`artifact` 等已实现自动化候选数据实体；
- 已明确 UI 不直写 SQLite、Chatbox 不保存 API Key、不直连真实 provider。

剩余注意事项：P9-M0 启动审计应再次确认现有代码命名与文档实体命名的落地映射，允许实现时采用等价组件名，但必须保留职责边界。

### 8.3 第三轮：开发计划与验收门槛审计

审计问题：P9-M0 到 P9-M9 是否足够指导自动化开发和阶段验收？

结论：通过。

理由：

- `P9_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` 已逐阶段定义开发范围、验收标准、证据和打回条件；
- `04_ACCEPTANCE_GATES.md` 已覆盖 Chatbox 主路径、左侧态势图、顶部服务中心、事实安全与申请包；
- `03_MILESTONES_AND_DELIVERY_PLAN.md` 已定义 P9-DOC、P9-M0 到 P9-M9 的顺序；
- `06_TRACEABILITY_MATRIX.md` 已把目标、实体、文件、证据和验收门槛连接起来。

剩余注意事项：P9-M4 JD search run 和 P9-M5 ASR 相关能力必须使用 mock/fixture/opt-in 边界，不能在没有用户确认的情况下触发真实外部服务。

### 8.4 第四轮：drawio 与人工审查可读性审计

审计问题：drawio 是否能让人快速理解目标体验、目标架构、当前差距、开发计划和验收门槛？

结论：通过。

理由：

- drawio 共 8 页，满足“不超过 8 页”；
- 页结构覆盖目标体验、当前差异、代码实体分层、左侧态势图、用户路线、开发计划、出门门槛和安全边界；
- 第 3 页明确代码实体与分层交互关系；
- 第 4 页详细展示左侧求职态势图的三大板块和地图式交互；
- 第 8 页集中呈现 false green 风险。

剩余注意事项：后续 P9-M9 报告必须使用真实界面截图；drawio 只能作为设计方向和验收标准，不可替代实现证据。

### 8.5 第五轮：是否需要 ChatGPT 外部审计

审计问题：当前是否必须交给 ChatGPT 外部审计后才能进入 P9-M0？

结论：不强制。

理由：

- PRD、目标架构、里程碑、验收门槛、追踪矩阵、详细开发计划和 drawio 已闭合；
- 当前高风险点均已有非目标、授权门、验收边界和打回条件；
- 没有发现必须由用户选择技术路线的未消减高风险阻塞。

建议：如果用户希望降低后续自动化开发偏航风险，可以把本文件列出的文档包交给 ChatGPT 做外部审计；但从当前文档完备性看，不是进入 P9-M0 的强制前置。

### 8.6 第六轮：外部审计意见采纳复核

审计问题：ChatGPT 外部意见提出的“P9 必须限定为 Chatbox-first UI 重构 + 求职情报可视化层”是否已落盘？

结论：通过。

已落盘约束：

- P9 不新增真实数据源系统；
- P9 不新增外部平台接入；
- P9 不新增长期运行任务系统；
- P9 不新增独立业务服务；
- P9 只允许 UI 重排、现有 API 组合、Artifact 展示增强和 Chatbox 交互增强。

修订位置：

- `01_STAGE_PRD.md`
- `02_TARGET_ARCHITECTURE.md`
- `03_MILESTONES_AND_DELIVERY_PLAN.md`
- `04_ACCEPTANCE_GATES.md`
- `06_TRACEABILITY_MATRIX.md`
- `23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`
- `P9_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `P9_EXTERNAL_REVIEW_REVISION_AUDIT.md`
- `jobpilot-stage-gap-and-acceptance.md`
- `jobpilot-stage-gap-and-acceptance.drawio`
