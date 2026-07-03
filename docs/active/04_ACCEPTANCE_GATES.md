# JobPilot AI P8-JD Intake 与简历生成体验强化验收门槛

## 当前阶段文档门槛 - P8.1 Chatbox-first 工作台信息架构

这些门槛只验收文档和架构方向是否足以支撑后续 P8.1 自动化开发，不代表 Chatbox-first UI 已经实现，不代表真实 provider、真实个人资料、招聘平台接入或自动投递已通过。

### P8.1 文档门槛 A - Chatbox 第一优先

通过条件：

- 文档明确三栏结构为“用户指导 - Chatbox - 工作台”；
- 中央 Chatbox 是第一优先展示和第一交互路径；
- 聊天时间线、Agent 状态和输入框不得被大型 workflow strip 或表单挤出首屏；
- 资料准备、JD 导入和简历生成入口必须围绕 Chatbox 组织。

不通过条件：

- 文档继续把中央大型资料/JD/简历表单作为首屏主路径；
- 用户必须先理解 workspace、artifact、job、resume_version 等内部概念才能开始聊天；
- 将 P8.1 写成只做视觉美化而不是信息架构修正。

### P8.1 文档门槛 B - 三栏职责稳定

通过条件：

- 左侧用户指导只承载资料清单、缺失影响、示例路径和下一步建议；
- 中央 Chatbox 承载连续对话、Agent 状态、时间线、输入框和紧邻输入框的工具入口；
- 右侧工作台承载岗位列表、当前目标 JD、画像、简历草稿、source refs、pending confirmations 和 export preflight；
- 文档列出 `DesktopContextPanel`、`Conversation Plane`、`p8-workflow-strip`、`MaterialIntakeWizard`、`JDIntakeCenter`、`JobTargetList`、`ResumeGenerationPlane`、`Workbench` 和 `styles.css` 的调整职责。

不通过条件：

- 左、中、右栏目职责互相重复或冲突；
- 资料/JD/简历生成入口没有明确迁移路径；
- 工作台空态、待确认、可导出和失败恢复没有验收要求。

### P8.1 文档门槛 C - 多视口体验可验收

通过条件：

- 1200px、1440px、1920px 桌面视口下，中央 Chatbox 首屏优先可见；
- 720px 平板视口下，Chatbox 是默认主视图，指导和工作台可作为次级区域；
- 390px 移动视口下，输入框、发送、上传资料、粘贴 JD 或等价入口可达；
- 验收报告必须使用真实界面截图证明无按钮错位、文字重叠、核心入口不可达。

不通过条件：

- 只用设计稿或合成图替代真实界面截图；
- 只验收桌面，不验收窄屏；
- 窄屏默认进入资料表单而不是 Chatbox。

### P8.1 文档门槛 D - 边界不虚假

通过条件：

- 文档明确 P8.1 不登录、不抓取、不自动沟通、不自动投递招聘平台；
- 不默认调用真实 MiniMax、DeepSeek 或 OpenAI-compatible provider；
- 不读取未授权真实个人资料；
- 不执行 workspace 删除、迁移 apply 或不可逆操作；
- 不把 P8.1 文档开发写成代码实现通过。

P8.1 后续自动化验收最低证据：

```bash
.venv/bin/python -m pytest
npm --prefix apps/chatbox run build
drawio XML parse
P8.1 browser acceptance screenshots: 1200px, 1440px, 1920px, 720px, 390px
P8.1 Chinese HTML acceptance report
```

P8.1 后续自动化验收报告必须逐项说明：

- 当前截图是否证明 Chatbox 首屏优先；
- 输入框工具入口是否紧贴输入框或处于清晰辅助面板；
- 左侧用户指导、中央 Chatbox、右侧工作台是否职责稳定；
- Agent 状态机、岗位、画像、简历草稿、source refs、pending confirmations、export preflight 是否在正确区域可见；
- 任何目标概念图、设计图或 AI 图像不得替代真实实现截图。

## 当前阶段文档门槛 - P8-JD Intake 与简历生成体验强化

这些门槛只验收文档和架构方向是否足以支撑后续 P8 自动化开发，不代表 BOSS/招聘平台接入、自动投递、真实 provider、真实个人资料或最终产品化已通过。

### P8 文档门槛 A - 资料准备向导完整

通过条件：

- 文档将资料输入拆成简历、项目经历、作品链接、目标 JD、求职偏好五类；
- 每类资料都有用户可见说明、可接受输入、示例、可跳过条件和缺失影响；
- 文档说明资料向导应该紧贴输入框或首屏任务入口，不能只保留单个“上传资料”按钮；
- 文档明确缺少资料时系统应显示影响和下一步，而不是直接失败或要求用户阅读开发文档。

不通过条件：

- 仍只写“上传资料”而不说明资料类型；
- 没有解释缺少项目经历、作品链接或目标 JD 的影响；
- 要求用户先理解内部表、artifact 或 workspace 概念。

### P8 文档门槛 B - JD 导入中心边界清晰

通过条件：

- 第一版只规划用户粘贴 JD 文本、保存来源 URL、平台标签和用户备注；
- `source_url` 只作为归档和 source refs，不触发网络抓取；
- 文档明确支持 BOSS / 猎聘 / 拉勾 / LinkedIn / 公司官网等来源的手动导入，但不声明平台自动接入；
- 多个 JD 可以进入岗位列表，并能选择当前目标岗位；
- JD 缺少公司、地点、薪资或技术栈时进入待确认，不自动补全。

不通过条件：

- 文档规划绕登录、反爬、验证码、账号权限或平台风控；
- 文档把“保存链接”写成“已接入 BOSS”；
- 文档包含自动沟通、自动投递或批量岗位抓取作为本阶段能力。

### P8 文档门槛 C - JD 定制简历可追溯

通过条件：

- 简历生成第一版以单个目标 JD 为中心，通用简历只能作为次要模式；
- 每个核心经历、技能亮点或项目描述必须来自 document、career_fact、skill_evidence、tech_project、job、match_report、candidate_profile 或 artifact source refs；
- 缺证据内容进入 `pending_confirmations`，不得写成事实；
- blocking 待确认项未处理时不得正式导出；
- 普通聊天不得静默覆盖 `resume_version`。

不通过条件：

- 简历草稿缺少 source refs；
- 自动补全学历、工作年限、项目贡献或量化结果；
- 未确认事实直接进入正式导出。

### P8 文档门槛 D - drawio 和审计可读

通过条件：

- drawio 不超过 8 页；
- 图中条目是具体 UI 平面、路由、数据表、领域工具、artifact、报告或验收证据；
- 颜色语义明确：已实现基线、P8 计划新增、高风险需确认、后续独立阶段；
- 文本镜像与 drawio 页结构一致；
- 阶段审计说明本轮只做文档开发，未进入业务代码实现。

P8 后续自动化验收最低证据：

```bash
.venv/bin/python -m pytest
npm --prefix apps/chatbox run build
drawio XML parse
P8 browser acceptance screenshots: 1200px, 720px, 390px
P8 Chinese HTML acceptance report
```

## 当前阶段文档门槛 - P6-REAL / P7-post 准入

这些门槛只验收文档和架构方向是否足以支撑后续执行，不代表真实 provider、真实个人资料或最终产品化已通过。

### 文档门槛 A - 状态口径一致

通过条件：

- PRD、目标架构、里程碑、追踪矩阵、roadmap、P6 计划、drawio 和文本镜像都区分 `已实现自动化候选`、`待真实验收`、`后续独立阶段`；
- fake provider、多身份合成资料、examples、脱敏 fixture 和 dry-run 只作为自动化候选证据；
- 文档没有使用“真实 LLM 已通过”“真实 provider 质量已验收”“真实个人资料路径已通过”等未执行结论；
- P6/P7 旧的“待开发/待新增/待强化”描述已改为明确状态，不造成实现状态冲突。

### 文档门槛 B - P6-REAL 真实 provider 授权完整

通过条件：

- 真实 provider 执行前必须有用户确认的 provider、model、base_url preset、API Key 本地配置方式；
- 必须限制最大调用次数、最大预算或等价费用边界、timeout、retry、失败降级和报告展示字段；
- 必须明确本次发送给 provider 的数据类别：近期消息、rolling summary、workspace 摘要、JD 摘要、artifact/profile 摘要；
- 必须区分 configured、consented、called、failed、fallback；
- API Key、完整 prompt、完整真实资料、完整 provider raw response 不得进入仓库、日志、截图说明或报告。

不通过条件：

- 配置了 provider 就被写成已调用；
- fake provider transcript 被写成真实 LLM 质量证据；
- 未给出费用、次数、数据范围或报告展示边界；
- 文档允许默认真实外呼。

### 文档门槛 C - P7-post P5-REAL 真实资料授权完整

通过条件：

- 真实资料复验必须由用户提供明确路径，至少包括简历/背景资料、项目资料或作品说明、目标 JD；
- 只读取用户指定路径，不扫描用户个人目录、聊天软件目录、下载目录或全盘；
- 报告默认脱敏联系方式、账号、私密链接、完整长原文和任何密钥；
- 允许展示字段和禁止展示字段必须在执行前确认；
- 若用户不提供真实资料，P5-REAL 结论必须保持未执行，不能用 synthetic personas、examples 或脱敏 fixture 替代。

### 文档门槛 D - drawio 和审计可读

通过条件：

- drawio 不超过 8 页；
- 图中每个架构条目都是具体代码实体、数据表、路由、脚本、报告或验收证据；
- 颜色语义明确：已实现自动化候选、当前待真实验收、高风险需确认、后续独立阶段；
- 文本镜像与 drawio 页结构一致；
- 阶段审计说明本轮只做文档开发，未触发真实外呼、未读取真实资料、未进入代码实现。

当前自动化候选证据：

- 后端/API/边界 eval：`tests/evals/test_p5_5_candidate_profile_eval.py`、`test_p5_5_capability_matrix_eval.py`、`test_p5_5_project_credibility_eval.py`、`test_p5_5_gap_analysis_eval.py`、`test_p5_5_chat_boundary_eval.py`；
- 前端构建：`npm --prefix apps/chatbox run build`；
- 浏览器证据：`docs/reports/evidence/p5_5_candidate_profile/`；
- 中文可视化验收报告：`docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html`；
- 报告断言：`tests/evals/test_p5_5_acceptance_report_eval.py`。

这些证据只支持 P5.5 examples / synthetic-style workspace + mock provider 自动化候选，不支持 P5-REAL、真实 provider 质量、真实个人资料路径或人工体验冻结结论。

## P5.5 历史验收门槛 0 - 文档和边界完整

通过条件：

- PRD、目标架构、里程碑、验收门槛、追踪矩阵、drawio 和 TODO 当时均已同步为 P5.5 阶段；
- drawio 不超过 8 页，且包含目标体验、目标架构、代码实体、开发计划、出门门槛和安全边界；
- 文档明确 P5.5 不等于 P5-REAL、真实 provider 复验或 P8+；
- 文档明确禁止敏感属性分析、人格判断、背景调查和未授权真实资料验收。

## P5.5 历史验收门槛 1 - CandidateProfile 可追溯

通过条件：

- 专业背景画像只能基于 `career_fact`、`skill_evidence`、`tech_project`、`job`、`match_report` 或 artifact；
- `POST /api/profile/candidate/refresh` 必须更新或创建 `candidate_profile` 行，并写入 `artifact_type=candidate_profile` artifact/version；
- `GET /api/profile/candidate` 必须能返回可读空态或完整画像，不允许前端只能依赖裸 SQLite/内部 id；
- 每条画像判断都有 source refs、证据强度或待确认项；
- 缺少证据时显示 missing / weak / needs confirmation，不自动补全事实。

不通过条件：

- 画像结论没有来源；
- 将合成资料写成真实个人资料；
- 将推断写成事实。

## P5.5 历史验收门槛 2 - 能力矩阵可解释

通过条件：

- 能力矩阵至少包含技能、类别、证据类型、证据强度、岗位相关性、待确认状态；
- 证据强度必须使用 `strong`、`usable`、`weak`、`missing` 或等价等级，并在报告中解释含义；
- 能力等级解释为证据强弱和岗位匹配度，不评价人格或潜力；
- 用户能看到哪些能力可用于申请材料，哪些需要补证据。

## P5.5 历史验收门槛 3 - 项目可信度不夸大

通过条件：

- 项目可信度展示本人贡献、技术难点、可验证材料、量化结果缺口和风险标签；
- 项目可信度必须使用 `verified`、`plausible`、`needs_evidence`、`risky` 或等价标签，并保留 source refs；
- 未确认本人贡献必须保持 blocking / warning；
- 项目可用于申请材料前必须保留 source refs 和待确认项。

## P5.5 历史验收门槛 4 - 岗位短板可行动

通过条件：

- 岗位短板对应 JD must-have / nice-to-have；
- 每个短板都有证据、影响说明和补强行动；
- 系统不输出羞辱性、不可行动或敏感属性相关评价。

## P5.5 历史验收门槛 5 - Chatbox / Workbench 体验成立

通过条件：

- 用户能在 Workbench 中看到画像概览、能力矩阵、项目可信度和岗位短板；
- 普通追问不写画像 artifact；
- 明确要求刷新画像、生成画像报告或重新评估才进入工具路径；
- 多视口截图证明桌面和移动端可读。

## P5.5 历史验收门槛 6 - 可视化验收报告完整

通过条件：

- 中文 HTML 报告列出目标架构、当前实现、用户路径、截图证据、测试结果、PRD 规格检视和未验证范围；
- 报告不得包含完整真实个人资料、API Key、provider raw response 或未授权长原文；
- 报告明确 P5.5 未验证真实资料路径、真实 provider 质量、SaaS、ASR、会议平台、自动投递、MCP/CLI。

## P6+P7 验收门槛 0 - P0-P5 本地基线不退化

以下 P6+P7 内容作为已完成自动化候选和后续复验边界保留。

通过条件：

- P0/P1/P2/P3/P4 本地 mock/examples 路径继续可运行；
- P5 本地/mock + 脱敏 fixture 自动化候选路径继续可运行；
- Chatbox 仍是薄入口，不生成求职内容、不直接写 SQLite、不保存 API Key、不直连 provider；
- Artifact version、edit、regenerate、Markdown/DOCX export 和 export preflight 不退化；
- P4/P5 本地连续对话和普通追问不写 artifact 的约束不退化。

最低证据：

```bash
.venv/bin/python -m pytest
npm --prefix apps/chatbox run build
```

## P6 验收门槛 1 - Provider opt-in 默认安全

通过条件：

- 默认进入 Chatbox 时不调用真实外部 provider；
- provider configured、consented、called、failed、fallback 状态可区分；
- 配置 provider 但未确认本次调用时仍不外呼；
- 用户能看到 provider、model、隐私/费用提示和本轮是否外呼；
- 用户取消或缺少确认时，系统回到本地/mock 连续对话。

不通过条件：

- 配置 `.env` 后自动外呼；
- 报告把 provider configured 写成 provider called；
- 前端展示或保存 API Key；
- 用户无法判断本轮是否调用外部模型。

## P6 验收门槛 2 - Provider-backed 聊天可控且可降级

通过条件：

- 用户确认后可以完成 provider-backed 普通求职方向聊天；
- provider 调用经过 timeout、retry、schema validation、redaction；
- provider 超时、429、结构错误、网络错误时有可理解失败反馈并降级到本地连续对话；
- provider invocation log 只记录脱敏元数据；
- provider raw response 不直接写 artifact、报告或日志。

不通过条件：

- 未授权请求发生真实外呼；
- provider 失败导致 Chatbox 卡死、丢 session 或无法继续本地对话；
- 日志出现 API Key、完整 prompt、完整真实资料或完整 raw response。

## P6 验收门槛 3 - 长程连续对话成立

通过条件：

- 连续 20-50 轮聊天后，UI 不明显卡死，上下文不完全丢失；
- Long Context Manager 维护 recent messages、rolling summary、workspace context snapshot 和相关 artifact/JD/profile 摘要；
- 刷新页面后能恢复消息、摘要、当前 workspace 状态和 pending confirmations；
- 报告明确这不是无限 token 或无限成本；
- 上下文构造不把完整历史、完整简历或完整 JD 无边界发送给 provider。

不通过条件：

- 把 20-50 轮验收写成真正无限聊天；
- 刷新后丢失关键上下文；
- 长对话普通追问误写 artifact；
- 上下文包含未授权完整个人资料。

## P6 验收门槛 4 - Tool Safety 和产物边界不被 provider 绕过

通过条件：

- 普通聊天不生成 artifact；
- 明确“解析 / 生成 / 重新生成 / 导出”才进入工具确认或 Domain Tools；
- provider-backed 回复不能绕过 `questions_to_confirm`；
- blocking confirmation 未处理时仍不得导出正式申请材料；
- source refs、artifact version、export path 和 preflight 状态可追踪。

不通过条件：

- provider 聊天直接覆盖 artifact；
- 用户说“先别生成”仍触发生成；
- export preflight 被绕过。

## P6 验收门槛 5 - 隐私、日志和报告脱敏

通过条件：

- API Key、完整真实资料、完整 provider raw response 不进入仓库、报告、日志、截图说明或 fixture；
- Provider Invocation Log 能区分 configured/called/failed/fallback；
- 自动化报告明确 mock/fake provider、受控真实 provider 和未验证范围；
- 真实个人资料发送给外部 provider 前必须单独确认数据范围；
- 敏感信息扫描通过。

## P6 验收门槛 6 - P6 可视化验收证据完整

通过条件：

- 中文 HTML 报告可读，列出目标架构、当前架构实现、用户路径、截图证据、测试结果、PRD 规格检视和未验证范围；
- 截图至少覆盖：默认不外呼、模型设置、调用前确认、provider-backed 回复、20-50 轮长对话摘要、刷新恢复、失败降级、普通聊天不写 artifact、blocking export 仍拦截；
- 多视口至少覆盖 1200px、1440px、1600px、1920px、720px、390px；
- 自动化截图、焦点抢占或弹窗前必须提前告知用户。

## P7 验收门槛 7 - Workspace 生命周期可用

通过条件：

- 用户可以创建、恢复、导出、备份 workspace；
- 清理和迁移默认先 dry-run，列出影响文件、风险标签和确认需求；
- 删除、迁移 apply、workspace 清空等不可逆操作必须高风险确认；
- workspace 操作不写允许目录外路径；
- 用户能理解本地数据在哪里、如何备份、如何清理。

## P7 验收门槛 8 - 诊断、发布、部署和回滚可复现

通过条件：

- 有脱敏诊断报告，包含版本、配置摘要、错误摘要、provider 状态和 workspace 健康检查；
- 有可复现启动、部署、回滚和故障排查文档；
- 错误追踪和日志脱敏不泄露 API Key、完整个人资料或 raw response；
- release checklist 可执行；
- 失败状态有恢复建议。

## P7 验收门槛 9 - Beta 使用说明、支持流程和隐私审计完整

通过条件：

- Beta 使用说明能让用户完成最小体验路径；
- 支持流程和故障排查可独立阅读；
- 安全隐私审计覆盖 provider、workspace、diagnostics、report、export 和不可逆操作；
- P7 HTML 报告展示真实界面截图、测试证据和未验证范围；
- P7 不声称 SaaS、ASR、会议平台、自动投递或真实个人资料默认路径通过。

## P7-post P5-REAL / P5-Freeze 复验门槛

通过条件：

- 用户明确提供真实/脱敏资料路径和允许展示字段；
- 只读取用户指定路径，不擅自搜索个人目录；
- 真实资料报告和截图默认遮蔽联系方式、账号、私密链接、API Key 和未授权长原文；
- P5-REAL 复验完成后再执行 P5 人工体验记录和 final closure audit；
- 若用户不提供真实资料，结论只能保持“未执行”，不能用 synthetic personas、examples 或脱敏 fixture 替代。

## P6+P7 自动化验收矩阵

| 验收项 | 建议测试 / 报告 | 必须证明 | 不得声称 |
| --- | --- | --- | --- |
| 本地基线回归 | `.venv/bin/python -m pytest` | P0-P5 本地路径不退化 | 不代表 P6/P7 已通过 |
| 前端可构建 | `npm --prefix apps/chatbox run build` | P6/P7 UI 能成功构建 | 不代表人类体验通过 |
| Provider 默认安全 | provider policy eval | configured 不等于 called，未确认不外呼 | 不代表真实 provider 质量 |
| Provider-backed chat | fake provider 记录已具备；受控真实 provider 记录待用户授权后生成 | 授权后可调用，失败可降级 | 不代表默认外呼或真实 provider 质量已通过 |
| Long Context Manager | long conversation eval | 20-50 轮、滚动摘要、刷新恢复 | 不代表无限上下文 |
| Tool Safety | chat/artifact/export eval | 普通聊天不写 artifact，blocking 仍拦截导出 | 不代表自动投递或 SaaS |
| Privacy / Redaction | sensitive scan eval | API Key、完整资料、raw response 不泄露 | 不代表真实资料外发已授权 |
| Workspace lifecycle | lifecycle eval | backup/export/cleanup dry-run/migration dry-run | 不代表执行删除或迁移 apply |
| Diagnostics / Release | diagnostics and docs eval | 脱敏诊断、启动、部署、回滚可复现 | 不代表 SaaS 运行 |
| Visual acceptance | P6/P7 HTML 报告 eval | 中文报告、真实界面截图、未验证范围 | 不代表未执行路径通过 |
| Drawio/docs | XML parse + rg 口径检查 | 页数不超过 8，文档和图一致 | 不代表功能已实现 |

## P6+P7 最终出门条件

P6+P7 完成后，项目应达到：

```text
本地 Chatbox 可用
→ 真实 provider 仅 opt-in 调用
→ 长程连续对话 20-50 轮可恢复、可降级、可解释上下文
→ provider-backed chat 不绕过产物确认和导出门槛
→ workspace 生命周期、诊断报告、发布/部署/回滚和支持流程具备 Beta 验收证据
→ P7 完成后进入 P7-post P5-REAL/P5-Freeze 复验
```

P6+P7 完成不代表 SaaS、ASR、会议平台、自动投递、MCP/CLI 或真实个人资料默认路径通过。

## P5 验收门槛 0 - P0-P4 冻结基线不退化

通过条件：

- P0/P1/P2/P3/P4 本地 mock/examples 路径继续可运行；
- Chatbox 仍是薄入口，不生成求职内容、不直接写 SQLite、不直连 provider；
- Artifact version、edit、regenerate、Markdown/DOCX export 继续可用；
- P4 的自由连续对话、本地工作台、响应式布局和截图脚本隔离不退化；
- workspace 路径沙箱、tool log 脱敏、provider policy gate 不退化。

最低证据：

```bash
.venv/bin/python -m pytest
npm --prefix apps/chatbox run build
```

## P5 验收门槛 1 - 真实资料本地导入可理解

通过条件：

- 用户可以在 Chatbox 中上传或粘贴自己的资料；
- UI 明确说明默认本地处理、mock/local 默认、外部 provider 需确认；
- 导入后展示解析状态、资料摘要、source refs 和待确认项；
- 缺资料、格式不支持、解析失败时提供恢复路径；
- 未授权真实资料不得进入自动化报告、日志或 fixture。

不通过条件：

- 用户无法判断资料是否已导入；
- 导入失败被写成成功；
- 报告暴露完整真实简历、项目材料或隐私字段；
- 文案暗示默认会调用真实外部 provider。

## P5 验收门槛 2 - JD 解析与缺失信息恢复成立

通过条件：

- 用户可以粘贴或导入目标 JD；
- 系统返回岗位要求、关键词、硬性条件、隐含风险和缺失信息；
- “缺资料 / 缺 JD / 缺确认项 / 可生成申请包”状态可区分；
- 缺失信息进入 `questions_to_confirm` 或等价确认队列；
- JD 解析结果使用求职语义展示，不以裸 JSON 作为主要反馈。

## P5 验收门槛 3 - 事实确认闭环可执行

通过条件：

- blocking、warning、optional 确认项可见；
- 用户可以补充、确认、暂缓或编辑相关事实；
- blocking confirmation 未处理时不得导出正式申请材料；
- source refs、确认状态、artifact version 在 UI 和数据层可追溯；
- 待确认项文案能解释“为什么影响求职材料”。

## P5 验收门槛 4 - 申请包生成、编辑、再生成和导出可信

通过条件：

- 申请包草稿基于当前资料和目标 JD 生成；
- 用户可以编辑草稿、保存新版本、重新生成并查看版本；
- Markdown/DOCX 导出前执行 preflight；
- 导出只写 workspace 允许路径；
- 申请包、匹配说明、面试准备等产物以人类可读摘要展示；
- 用户不展开 JSON 也能理解产物价值、风险和下一步。

不通过条件：

- 旧版本被覆盖；
- blocking confirmation 被绕过；
- 导出路径越过 workspace；
- 产物主要依赖内部 id、version id 或裸 JSON 才能理解。

## P5 验收门槛 5 - 本地多轮追问不误触发工具

通过条件：

- 用户可以围绕当前资料、JD、申请包连续追问；
- “当前进展如何 / 下一步做什么 / 我还缺什么 / 这个经历能否用于该 JD”返回上下文相关回复；
- 普通追问不写入 artifact；
- 明确“解析 / 生成 / 重新生成 / 导出”才触发工具；
- 会话恢复后能看到关键上下文和当前 workspace 摘要。

## P5 验收门槛 6 - 隐私、provider 和报告不误导

通过条件：

- P5 默认不调用真实外部 provider；
- provider 状态明确区分“未配置”“已配置但本次未调用”“外部调用需确认”“调用失败”；
- API Key、完整简历、完整 JD、完整 transcript、完整 provider raw response 不进入日志、报告或截图说明；
- 自动化报告必须标明使用的是用户授权脱敏资料还是 examples 真实感数据；
- 真实外部 provider、provider-backed 自由智能聊天、SaaS、ASR、会议平台、自动投递均列为 P6+ 或独立阶段。

## P5 验收门槛 7 - 多视口体验和证据完整

通过条件：

- 1200px、1440px、1600px、1920px 桌面宽度下，Conversation、Workbench、Artifact/Export 有清晰结构；
- 720px 窄屏和 390px 移动宽度下，上传/输入/确认/导出主要操作可达；
- 输入区、资料动作、确认按钮和产物卡文字不重叠、不溢出；
- 截图证据来自真实界面，不以静态原型替代实现；
- 截图脚本不污染人工审查者浏览器 viewport。

## P5 自动化验收矩阵

P5 完成前至少需要以下自动化证据。文件名为建议命名，允许实现时按仓库测试命名习惯微调，但覆盖内容不得减少。

| 验收项 | 建议测试 / 报告 | 必须证明 | 不得声称 |
| --- | --- | --- | --- |
| P0-P4 回归 | `.venv/bin/python -m pytest` | 历史 mock/examples 路径不退化 | 不代表 P5 已通过 |
| 前端可构建 | `npm --prefix apps/chatbox run build` | P5 UI 能成功构建 | 不代表人类体验通过 |
| 资料导入 | `tests/evals/test_p5_real_data_local_flow_eval.py` | 上传/粘贴资料、解析摘要、source refs、恢复路径 | 不代表未授权真实资料通过 |
| JD 解析 | `tests/evals/test_p5_jd_gap_recovery_eval.py` | JD 解析、缺资料/缺 JD/可生成状态区分 | 不代表岗位数据源接入 |
| 事实确认 | `tests/evals/test_p5_confirmation_gate_eval.py` | blocking/warning/optional 可见，blocking 影响导出 | 不代表事实已由真人确认 |
| 编辑和再生成 | `tests/evals/test_p5_application_package_loop_eval.py` | 申请包生成、编辑、版本、重新生成、旧版本保留 | 不代表文本质量达到外部 provider 水平 |
| 导出 preflight | `tests/evals/test_p5_export_preflight_eval.py` | workspace exports、blocking 拦截、Markdown/DOCX 路径 | 不代表 PDF 或 SaaS 下载能力 |
| 本地多轮追问 | `tests/evals/test_p5_local_dialogue_eval.py` | 普通追问不写 artifact，明确工具意图才执行 | 不代表 provider-backed 自由智能聊天 |
| 隐私和脱敏 | `tests/evals/test_p5_privacy_redaction_eval.py` | API Key、完整真实资料、provider raw response 不进报告/日志 | 不代表真实外部 provider 已验收 |
| 自动化报告 | `tests/evals/test_p5_acceptance_report_eval.py` | 中文 HTML 报告、真实界面截图、未验证范围、虚假验收风险 | 不代表人工体验认可 |
| drawio 一致性 | drawio XML parse + 文本镜像检查 | 页数不超过 8、颜色语义、模块状态和 active docs 一致 | 不代表功能已实现 |

P5 HTML 报告必须至少截图以下真实界面状态：

- 初始页：本地/mock 默认、资料导入入口、外部 provider 未默认调用；
- 资料导入后：资料摘要、source refs、待确认项；
- JD 解析后：岗位要求、缺口和下一步；
- 事实确认：blocking/warning/optional 项；
- 申请包草稿：摘要、版本、编辑/再生成入口；
- 导出 preflight：blocking 拦截或可导出状态；
- 导出完成：Markdown/DOCX 路径；
- 多轮追问：普通追问不生成 artifact，明确工具意图会执行；
- 多视口：1200px、1440px、1600px、1920px、720px、390px。

## P5 人工体验审查门槛

自动化验收通过后，仍必须进行人工体验审查。人工审查只能认可以下内容：

- 本地资料/JD/申请包闭环是否顺手；
- 用户是否能理解当前状态、下一步、确认项和导出风险；
- UI 是否存在明显重叠、按钮错位、文本溢出或主次不清；
- 报告是否没有虚假验收和隐私泄露。

P5-REAL 执行前置条件：

- 用户明确提供本地脱敏真实资料路径和允许展示字段；
- 只读取用户指定路径，不擅自搜索个人目录；
- 真实资料截图和报告默认遮蔽联系方式、账号、API Key、私密链接和未授权长原文；
- 如需真实外部 provider，必须转入 P6 opt-in 计划并单独确认，不能混入 P5 默认验收。

人工审查不得把以下内容写成通过：

- 未确认的真实个人资料路径；
- 未授权真实外部 provider；
- provider-backed 自由智能聊天；
- SaaS、ASR、会议平台、自动投递、MCP/CLI；
- 最终产品化发布。

## P5 最终出门条件

一个转行程序员可以在本地 Chatbox 使用自己的求职资料和目标 JD，完成：

```text
导入资料 → 解析资料 → 导入 JD → 解析岗位 → 确认事实
→ 生成申请包 → 编辑/重新生成 → 导出 → 围绕当前资料继续追问
```

项目必须通过 P0-P4 回归、P5 自动化验收、PRD 规格检视、drawio XML parse、脱敏截图报告和人工体验审查。P5 完成不代表真实外部 provider 默认路径、SaaS、ASR、会议平台、自动投递或最终产品化发布已通过。

当前 P5 自动化候选证据只证明本地/mock + 脱敏 fixture 路径达到冻结候选状态。P5 最终出门必须额外补齐 P5-REAL 真实授权资料复核、人工体验审查清单和 P5 final closure audit。

## P5 不通过条件

出现以下任一情况，P5 不得验收通过：

- 真实资料未经确认被写入报告、日志或 fixture；
- 默认触发真实外部 provider；
- 用户无法判断资料、JD、确认项或申请包当前状态；
- 普通追问误触发生成、解析、导出或 artifact 写入；
- blocking confirmation 未处理仍能导出正式申请材料；
- 产物主要依赖 JSON 或内部 id 才能理解；
- 报告把 examples 写成真实个人资料验收；
- 报告把 P6/P7/P8 能力写成 P5 已完成；
- P0-P4 冻结基线退化。

以下 P4 内容作为已冻结基线和历史背景保留。

## P4 验收门槛 0 - P0/P1/P2/P3 回归不退化

通过条件：

- mock provider 默认路径仍可跑通历史 examples 体验；
- P1 provider runtime、artifact version、regenerate、DOCX export 继续可用；
- P2 workflow API、guided flow、HTML 报告和截图证据仍可追溯；
- P3 Chatbox 响应闭环、示例/真实资料模式边界、对话区/推进台分离和响应式截图不退化；
- Chatbox 仍是薄入口，不承载业务生成逻辑；
- workspace 路径沙箱、tool log 脱敏、formal_assist 边界不退化。

最低证据：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

## P4 验收门槛 1 - Chatbox 空状态任务入口清楚

通过条件：

- Chatbox 空状态明确提供导入资料、粘贴 JD、生成申请包、准备面试等 suggested prompts；
- 点击 suggested prompt 后能填入 composer 或直接触发对话；
- workspace、mode、provider 状态可见但不压过任务入口；
- 示例模式和我的资料模式的差异可理解；
- 空状态直接给出下一步。

不通过条件：

- 用户仍需要读 README 才知道从哪里开始；
- 首屏主要展示工程状态、内部 id 或过多阶段表；
- 任务入口像割裂的临时测试按钮，而不是 Chatbox 对话入口。

## P4 验收门槛 2 - 对话反馈和恢复路径可理解

通过条件：

- 有效输入后有可见响应、计划、处理中状态或结果；
- 普通自由追问、求职偏好补充、状态查询和下一步问题能连续对话，不误触发工具写入；
- “我还没有 JD，先聊聊求职方向”不得被误判为 JD 解析；
- “继续 / 下一步 / 当前进展如何”应基于当前 workspace 状态给出可理解回复；
- 只有明确“整理资料 / 解析 JD / 生成申请包 / 准备面试”等工具意图时才生成对应 artifact；
- 缺资料、无效任务、后端错误都有恢复路径；
- loading / thinking 状态必须展示执行步骤，例如读取资料、对比 JD、生成草稿；
- 错误气泡必须包含可执行恢复动作，例如重新上传、补充 JD、查看支持格式；
- 长 JD、长计划和长摘要必须具备折叠或收起策略；
- 发送、上传、快捷任务在桌面/窄屏/移动端可见；
- 错误不被静默吞掉，也不伪造成成功。

P4C-FC 最低证据：

```bash
.venv/bin/python -m pytest tests/evals/test_p3_chatbox_response_eval.py
npm --prefix apps/chatbox run build
```

截图或 HTML 报告至少覆盖：

- 自由聊两轮不生成 artifact；
- 明确工具意图后生成 artifact；
- 会话恢复后仍能看到自由对话历史。

## P4 验收门槛 3 - 推进台和产物卡可读

通过条件：

- 推进台只负责当前任务、下一步、产物、确认项、版本和导出；
- 产物卡以求职语义表达，例如“岗位解析”“匹配报告”“申请包草稿”“面试准备”；
- 用户不展开 JSON 也能理解产物价值、风险和下一步；
- source refs、questions_to_confirm、version 信息保留并可查看；
- 导出、确认、编辑、regenerate 操作层级清楚。
- 阻塞项必须有明确 primary action，例如“补充事实 / 去确认”；
- secondary action 不能与 primary action 同等视觉权重；
- Workbench 空状态必须说明产物将在导入资料后生成。

不通过条件：

- 裸 JSON 是唯一可读结果；
- 内部 artifact id/version id 成为主要视觉信息；
- 待确认项被隐藏或弱化成不可见；
- 所有按钮视觉权重一致，用户无法判断下一步。

## P4 验收门槛 4 - provider、隐私和外呼语义不误导

通过条件：

- provider 状态区分“mock 默认”“外部模型未调用（隐私安全）”“外部调用需确认”“外部调用失败”；
- 真实个人资料和真实外部调用仍需人工确认；
- API Key、完整简历、完整 JD、完整 transcript 不进入日志、报告或截图；
- examples 结果不得写成真实个人资料验收。

## P4 验收门槛 5 - 响应式和基础可访问性

通过条件：

- 1200px、1440px、1600px、1920px 下对话区、状态指标、快捷任务、推进台摘要和下一步建议有清晰结构；
- 1200px 以上桌面宽度不得出现由布局错误造成的大面积空白；
- 1440px、1600px、1920px 不得只是把窄屏布局放大后停靠在左侧；
- 1280px 下对话区和推进台有清晰主次；
- 720px 下布局合理堆叠，不出现半屏空洞或严重截断；
- 390px 下无严重横向滚动，输入区不遮挡消息，当前任务和主要产物操作可达；
- 390px 下 Workbench 不得挤压 Chatbox，必须折叠为底部抽屉、折叠面板或次级区域；
- 交互控件有可理解名称，键盘焦点可见；
- segmented mode toggle 具备 `aria-pressed` 或等价状态；
- 文本不溢出按钮、状态标签或卡片。
- Chrome 截图脚本必须隔离或在结束时清理 viewport emulation 和 touch emulation，不能污染人工审查者正在使用的浏览器标签页。

最低证据：

- Chrome 1200px 截图；
- Chrome 1280px 截图；
- Chrome 1440px 截图；
- Chrome 1600px 截图；
- Chrome 1920px 截图；
- Chrome 720px 截图；
- Chrome 390px 截图；
- 截图脚本清理 viewport emulation 的实现或运行记录；
- 前端 build 通过。

## P4 验收门槛 6 - Gemini 审查包、HTML 报告和 PRD 规格检视

通过条件：

- `docs/gemini-frontend-review-package/` 存在且文件数小于 20；
- 审查包包含产品/UX brief、页面信息架构、组件状态、视觉方向、交互/可访问性清单、静态原型和推荐 Gemini 提示词；
- P4 HTML 报告使用真实 Chrome 截图证据；
- 报告列出目标 UX 架构、当前实现、体验路径、自动化测试结果、未验证范围和虚假验收风险；
- 报告明确区分“设计方案”“已实现”“待人工审查”。

## P4 最终出门条件

一个转行程序员可以在本地打开 Chatbox，不读开发文档也能知道从哪里开始，能清楚区分示例模式和我的资料模式，能通过对话区完成资料/JD/申请包任务，能在推进台理解当前阶段、产物、确认项、版本和导出，并能在 1200px、1440px、1600px、1920px、720px、390px 下顺手完成关键路径。P4 必须通过回归测试、前端 build、Chrome 截图、PRD 规格检视、Gemini 审查包和人工体验审查记录。

若进入 P4C-FC，最终出门条件还必须增加：

- Chatbox 能承接自由、多轮、不中断的本地/mock 对话；
- 普通追问不会误触发工具或写入 artifact；
- 明确工具意图仍能稳定执行；
- 文档和报告明确 provider-backed 自由智能聊天仍是 P6 opt-in，不属于当前默认完成范围。

## P4 不通过条件

出现以下任一情况，P4 不得验收通过：

- 用户仍然不知道第一步该做什么；
- Chatbox 发送有效任务后仍表现为无响应；
- 普通自由聊天误触发 JD 解析、资料整理、申请包生成或 artifact 写入；
- 用户明确说“先别生成 / 先解释”时仍执行生成；
- 推进台与聊天区职责再次混淆；
- 产物卡主要依赖 JSON 或内部 id 才能理解；
- provider 状态让用户误以为默认外呼；
- 1200px 以上桌面宽度仍出现布局错误造成的大面积空白，或像窄屏 Chatbox 停靠在左侧；
- 390px 下核心操作不可达或输入区遮挡消息；
- 截图脚本污染人工审查者浏览器 viewport，导致截图或人工审查状态不可信；
- 报告把静态原型、Gemini 建议或未人工审查体验写成已实现/已通过；
- MCP、CLI、ASR、会议平台、自动投递或 SaaS 被误作为 P4 必交付。

以下 P3 验收门槛作为已完成基线和历史背景保留。

## P3 验收门槛 0 - P0/P1/P2 回归不退化

通过条件：

- mock provider 默认路径仍可跑通 P0/P1/P2 examples 体验；
- P1 provider runtime、artifact version、regenerate、DOCX export 继续可用；
- P2 workflow API、guided flow、HTML 报告和截图证据仍可追溯；
- Pi Agent Core 业务编排仍能生成 intent/tool plan；
- Chatbox 仍是薄入口，不承载业务生成逻辑；
- workspace 路径沙箱、tool log 脱敏、formal_assist 边界不退化。

最低证据：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

## P3 验收门槛 1 - Chatbox 可对话和可失败

通过条件：

- 用户发送支持任务后，Chatbox 必须显示可理解响应；
- 空输入、无效任务、缺少资料、API 失败都有明确错误或下一步；
- 上传入口、JD 输入和发送按钮在桌面/窄屏/移动宽度可见；
- Enter 发送、Shift+Enter 换行行为不破坏输入。

不通过条件：

- 点击发送没有任何可见变化；
- 错误被静默吞掉；
- 前端伪造完成结果。

## P3 验收门槛 2 - 示例模式 / 真实资料模式边界

通过条件：

- 示例模式可一键跑 examples 完整路径；
- 真实资料模式明确说明本地处理、provider 状态和外部调用确认边界；
- mock / external provider 标签清楚；
- MiniMax 或其他外部 provider 只能在用户明确授权后受控验收；
- 未使用真实个人资料时，报告只能写“真实感示例数据验收”。

不通过条件：

- 把 examples 结果写成用户真实资料结果；
- 默认触发外部 provider；
- 把 API Key、完整简历、完整 JD 或 transcript 写入日志。

## P3 验收门槛 3 - 对话区和推进台分离

通过条件：

- 对话区负责输入、消息、计划和错误反馈；
- 推进台负责阶段、下一步、artifact、版本、确认项和导出；
- 用户能在视觉上区分“我要说什么”和“系统已经产出了什么”；
- 空状态提供下一步，不出现大面积无意义空白；
- artifact source refs、questions_to_confirm、version 信息不丢失。

## P3 验收门槛 4 - 响应式 UX

通过条件：

- 桌面宽度可完整展示对话区和推进台；
- 720px 窄屏下布局单列或合理堆叠，不出现半屏空洞；
- 390px 移动宽度下无严重横向滚动，输入区不遮挡消息；
- 卡片、按钮、状态标签文字不溢出；
- 滚动区域清楚，分区不被硬截断。

最低证据：

- Chrome 1280px 截图；
- Chrome 720px 截图；
- Chrome 390px 截图；
- 前端 build 通过。

## P3 验收门槛 5 - 端到端真实感数据体验

通过条件：

- 使用 examples 真实感数据完成导入资料、分析 JD、生成申请包、导出、面试准备、实时文本提示、复盘；
- 若使用外部 provider，只能使用匿名 examples 数据和用户授权的 API Key；
- 导出文件只写 workspace `exports/`；
- blocking confirmation 不得绕过导出 preflight；
- warning/optional confirmation 不得静默删除。

## P3 验收门槛 6 - 截图证据、HTML 报告和 PRD 规格检视

通过条件：

- P3 HTML 报告存在；
- 报告使用真实 Chrome 截图证据；
- 报告列出目标架构和当前架构实现；
- 报告列出当前可实现的用户场景体验路径；
- 报告列出自动化测试结果、未验证范围和虚假验收风险；
- 报告包含 PRD 规格检视和审计意见。

## P3 最终出门条件

一个用户可以在本地打开 Chatbox，明确选择示例模式或真实资料模式，通过聊天区上传/输入资料和 JD，看到系统响应、计划、错误或下一步；同时在分离的推进台中看到阶段、产物、确认项、版本和导出。项目必须在桌面、窄屏和移动宽度下完成截图验收，并通过 P0/P1/P2 回归测试和 P3 PRD 规格检视。

## P3 不通过条件

出现以下任一情况，P3 不得验收通过：

- Chatbox 对有效输入无可见响应；
- 真实资料模式默认触发外部 provider；
- examples 结果被写成真实个人资料验收；
- 窄屏或移动宽度出现严重截断、不可操作输入区或横向滚动；
- 推进台与聊天区职责混乱，用户无法理解下一步；
- P0/P1/P2 核心路径退化；
- 截图或报告把未执行事项写成已通过；
- MCP、CLI、ASR、会议平台、自动投递或 SaaS 被误作为 P3 必交付。

以下 P2 验收门槛作为已完成基线和历史背景保留。

## 验收门槛 0 - P0/P1 回归不退化

通过条件：

- mock provider 默认路径仍可跑通 P0 完整体验；
- P1 provider runtime、artifact version、regenerate、DOCX export 继续可用；
- Pi Agent Core 业务编排仍能生成 intent/tool plan；
- Chatbox 仍是薄入口；
- workspace 路径沙箱仍有效；
- realtime formal_assist 仍只输出结构提示。

必须通过：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

## 验收门槛 1 - Workflow Orchestrator

通过条件：

- `POST /api/workflows/p2-demo/run` 可执行；
- workflow 使用 examples 匿名真实感数据；
- workflow 串联现有 Domain Tools；
- 返回步骤、摘要、产物、导出文件和关键输出；
- 默认不触发真实外部 Provider；
- 失败时不得伪造完成步骤。

最低证据：

- `tests/evals/test_p2_guided_demo_flow_eval.py`；
- workflow 返回 9 个关键步骤；
- Markdown 和 DOCX 导出文件存在；
- training tasks 至少 3 个。

## 验收门槛 2 - Chatbox Guided Flow UX

通过条件：

- Chatbox 显示 P2 端到端体验路径面板；
- 用户可以点击一键体验完整路径；
- UI 显示步骤完成状态；
- UI 显示 provider 状态和 workspace 状态；
- UI 显示结果摘要和导出文件；
- UI 不变成复杂 dashboard。

最低证据：

- 前端 build 通过；
- Chrome 初始页截图；
- Chrome 完成页截图；
- Chrome 总结/导出截图。

## 验收门槛 3 - 产物可读性和确认边界

通过条件：

- 关键产物有可读摘要；
- JSON 可以作为详情保留，但不能是唯一表达；
- 待确认项必须可见；
- source refs 或 artifact refs 不丢失；
- version、edit、regenerate、export 入口仍可见；
- 未确认信息不能被包装为确定事实。

最低产出：

- ApplicationPackage 摘要；
- MatchReport 摘要；
- CareerFacts 摘要；
- InterviewPrep 摘要；
- 待确认项截图或测试证据。

## 验收门槛 4 - 导出和本地边界

通过条件：

- Markdown 继续可导出；
- DOCX 继续可导出；
- 导出文件只写 workspace `exports/`；
- workspace 外路径不能下载；
- blocking confirmation 规则不退化；
- warning/optional confirmation 不被静默删除。

最低产出：

- 一个 Markdown 文件；
- 一个 DOCX 文件；
- 一个导出路径截图或报告引用；
- 相关 eval 通过。

## 验收门槛 5 - 截图证据和 HTML 验收报告

通过条件：

- P2 HTML 报告存在；
- 报告使用截图证据；
- 报告列出目标架构；
- 报告列出当前架构实现；
- 报告列出当前可以实现的用户场景体验路径；
- 报告列出自动化测试结果；
- 报告明确已验证和未验证范围；
- 报告不做虚假验收。

最低产出：

- `docs/reports/P2_END_TO_END_ACCEPTANCE_REPORT.html`；
- `docs/reports/evidence/p2_initial_guided_flow.png`；
- `docs/reports/evidence/p2_completed_guided_flow.png`；
- `docs/reports/evidence/p2_summary_exports.png`；
- PRD 规格检视段落。

## 验收门槛 6 - 文档、drawio 和开源复现

通过条件：

- README 说明 P2 当时阶段目标和运行方式；
- TODO 与 active docs 不冲突；
- PRD、目标架构、里程碑、验收门槛和 drawio 口径一致；
- drawio 覆盖目标架构与当前架构差异、开发计划、里程碑、验收门槛和出门条件；
- active 文档数量保持可审计；
- 新贡献者能按 README 复现 API、Chatbox、tests、build 和 guided demo flow。

## P2 最终出门条件

一个用户可以在本地无 API Key 的 mock 模式下打开 Chatbox，看到端到端体验路径，点击一键体验 examples 完整求职流程，获得职业事实、项目卡、岗位匹配、申请包、导出文件、面试准备、实时文本提示、复盘和训练任务；人类可以通过 P2 HTML 报告和截图快速理解当前项目的目标架构、当前实现、体验路径、测试结果和未验证范围。

## P2 不通过条件

出现以下任一情况，P2 不得验收通过：

- P0/P1 回归测试失败；
- P2 workflow 需要真实 API Key 才能跑通；
- Chatbox 把业务生成逻辑写在前端；
- workflow 伪造已完成步骤；
- 导出写到 workspace 外；
- formal_assist 返回逐字代答；
- 截图或报告把未执行的真实外部调用写成已通过；
- docs/drawio 与实际范围不一致；
- MCP、CLI、ASR、会议平台被误作为 P2 必交付。
