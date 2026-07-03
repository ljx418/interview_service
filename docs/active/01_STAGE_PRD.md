# JobPilot AI P8-JD Intake 与简历生成体验强化阶段 PRD

## -5. 当前文档阶段：P8.1 Chatbox-first 工作台信息架构修正

当前最新文档阶段为 P8.1 Chatbox-first 工作台信息架构修正。P8-JD Intake 与简历生成体验强化已经完成本地/mock + 受控真实感数据自动化候选；P8.1 不推翻 P8 的资料准备、JD 导入、岗位选择和 JD 定制简历能力，而是修正当前界面的主次关系。

P8.1 要解决的问题：

```text
P8 已经具备资料准备、JD 导入和简历生成能力
但中央对话区首屏被较重的 workflow strip 抢占
用户感知从“和求职 Agent 对话”变成“先填多个表单”
这违背 Chatbox 作为默认入口和主路径的产品定位
```

P8.1 目标体验：

```text
用户打开本地 Chatbox
→ 首屏清楚看到三栏结构：用户指导 - Chatbox - 工作台
→ 中央 Chatbox 第一优先展示聊天时间线、Agent 状态和输入框
→ 上传资料、粘贴 JD、选择目标岗位、生成简历入口紧贴输入框或进入左右辅助面板
→ Agent 通过对话解释缺少哪些资料、为什么需要、下一步做什么
→ 右侧工作台展示岗位、画像、简历草稿、source refs、pending confirmations 和 export preflight
→ 用户可以连续多轮对话、补资料、确认事实和导出
```

P8.1 必须产出的用户结果：

- 稳定三栏：左侧用户指导、中央 Chatbox、右侧工作台；
- Chatbox-first：中央首屏不能被资料/JD/简历生成大表单压住；
- 紧贴输入框的资料和 JD 快捷入口；
- Agent 状态机：等待资料、解析 JD、生成简历、待确认、可导出、失败恢复；
- 工作台产物区：岗位列表、当前目标 JD、CandidateProfile、简历草稿、source refs、待确认项和导出前检查；
- 多视口可用：1200px、1440px、1920px、720px、390px 无按钮错位、文字重叠或核心入口不可达；
- 中文 HTML 验收报告使用真实界面截图，明确未验证范围。

P8.1 完成后的人类可感知结果必须是：

```text
用户不需要先理解 workspace / artifact / job / resume_version
→ 先看到可以直接对话的 Chatbox
→ 再通过输入框上方工具补资料、粘贴 JD、选岗位和生成简历
→ 右侧只在产物生成或需要确认时承担工作台职责
→ 任一视口下都能判断“我现在该说什么 / 补什么 / 确认什么”
```

P8.1 对已有 P8 能力的处理原则：

- `MaterialIntakeWizard`、`JDIntakeCenter`、`JobTargetList`、`ResumeGenerationPlane` 是保留能力，不删除、不降级业务语义；
- 这些能力的入口必须从中央大块 workflow 区迁移为输入框附近工具、轻弹层、抽屉或左右辅助面板；
- `Conversation Plane` 是首屏主路径，不能被任何资料、JD 或简历表单挤出首屏；
- `Workbench` 是产物和确认路径，不能要求用户先理解内部 artifact 结构才能开始对话。

P8.1 非目标：

- 不登录 BOSS、猎聘、拉勾等招聘平台；
- 不抓取招聘平台页面、不绕风控、不自动沟通或自动投递；
- 不默认调用真实 MiniMax、DeepSeek 或 OpenAI-compatible provider；
- 不读取未授权真实个人资料；
- 不执行 workspace 删除、迁移 apply 或不可逆操作；
- 不实现 SaaS、多租户、Billing、ASR、会议平台、MCP/CLI。

P8.1 文档阶段出门标准：

- PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、drawio 和文本镜像均明确 P8.1 为 Chatbox-first 信息架构修正；
- 文档不把 P8.1 写成已实现或已人工验收；
- 文档不把招聘平台接入、真实 provider、真实个人资料或自动投递写成已通过；
- drawio 第 4 页必须能看出具体代码实体之间的层级、上游/下游和状态颜色；
- 后续实现计划能直接指导 P8.1-M0 到 P8.1-M5 自动化开发和验收。

## -4. 当前自动化候选阶段：P8-JD Intake 与简历生成体验强化

当前最新阶段已完成 P8-JD Intake 自动化候选。P4 本地/mock Chatbox 体验已冻结，P5 本地/mock + 脱敏 fixture 自动化候选已完成，P5.5 Candidate Profile 自动化候选已完成，P6/P7 本地 Beta 自动化候选和 P6-REAL / P7-post 审计报告已完成。P8 针对用户反馈“上传资料按钮太抽象、用户不知道需要提供什么资料、希望系统更主动帮助导入 JD 并增强简历生成”，已落地资料准备向导、JD 手动导入中心、多 JD 当前目标岗位、JD 定制简历、专项 eval 和中文 HTML 截图验收报告。

本阶段要解决的问题：

```text
JobPilot 已能解析资料和 JD
但用户不知道应该提供哪些资料、为什么需要这些资料、缺少资料会影响什么结果
用户也没有清晰的 JD 获取与导入路径
如果直接要求“上传资料”或“粘贴 JD”，真实用户会停在第一步
因此 P8 已先完成资料准备向导、JD 手动导入中心和 JD 定制简历的本地/mock 自动化候选
```

P8-JD Intake 目标体验：

```text
用户打开本地 Chatbox
→ 看到资料准备向导，而不是孤立的上传按钮
→ 按简历、项目经历、作品链接、目标 JD、求职偏好五类补充资料
→ 每类资料都看到示例、用途、可跳过条件和缺失影响
→ 用户从 BOSS / 猎聘 / 拉勾 / LinkedIn / 公司官网等平台手动粘贴 JD
→ 系统保存 JD 文本、来源链接、平台来源和用户备注
→ 用户可以在岗位列表中比较多个 JD 的匹配度和资料缺口
→ 选择一个目标 JD 后生成 JD 定制简历草稿
→ 简历草稿显示 source refs、岗位关键词覆盖、待确认项和导出入口
```

P8 必须产出的用户结果：

- 资料准备向导：简历、项目经历、作品链接、目标 JD、求职偏好五类资料的说明、示例、缺失影响和完成状态；
- JD 导入中心：粘贴 JD、保存来源 URL、平台来源、用户备注、解析状态和岗位列表；
- JD 对比与选择：多个 JD 的岗位标题、公司、技术栈、must-have、匹配状态和推荐下一步；
- JD 定制简历：基于目标 JD 的 Markdown 简历草稿、岗位关键词覆盖、经历取舍说明、source refs 和待确认项；
- 可视化验收报告：中文 HTML 报告展示资料向导、JD 导入、岗位列表、简历生成路径和未验证范围。

P8 非目标：

- 不登录 BOSS、猎聘、拉勾等招聘平台；
- 不绕过反爬、验证码、账号权限或平台风控；
- 不做平台列表抓取、批量岗位采集、自动开聊、自动沟通或自动投递；
- 不默认调用真实 MiniMax、DeepSeek 或 OpenAI-compatible provider；
- 不读取用户个人目录、聊天软件目录、浏览器缓存或下载目录；
- 不实现 SaaS、多租户、Billing、ASR、会议平台、自动投递、MCP/CLI。

招聘平台接入边界：

- 第一版只支持用户手动粘贴 JD 文本和保存来源链接；
- `source_url` 只作为 source refs 和回看依据，不触发网络抓取；
- 如果后续要接入 BOSS 或其他招聘平台，必须单独立项并通过合规审计，只允许官方 API、用户授权导出或用户明确打开页面后的浏览器辅助读取；
- 任何平台账号、自动沟通、自动投递、批量抓取或绕风控能力都属于高风险后续阶段，不得写成本阶段完成。

P8 自动化候选出门标准：

- 用户能在 Chatbox 中看到五类资料准备入口，并按 `document.kind` 入库；
- 用户能手动导入 JD，保存来源 URL、平台来源和备注，且 `source_url` 不触发抓取；
- 用户能查看岗位列表并切换当前目标 JD；
- 用户能基于当前目标 JD 生成简历草稿，看到 `resume_version_id`、source refs、pending confirmations 和 export preflight；
- 中文 HTML 报告包含目标架构、当前实现、真实界面截图、PRD 规格检视和未验证范围；
- 不把 BOSS/招聘平台接入、自动投递、真实 provider 或真实个人资料写成已通过。

## -3. 当前文档开发阶段：P6-REAL 与 P7-post P5-REAL 复验准备

当前最新阶段不是新增业务代码开发，而是把 P6-REAL 真实 provider 受控验收和 P7-post P5-REAL 真实资料复验准备成可执行规格。P5.5 Candidate Profile 已完成本地/mock + synthetic-style workspace 自动化候选；P6+P7 已完成本地 Beta 自动化候选；最新 P5.5 报告已包含多身份合成资料与 fake provider opt-in 的 20 轮连续对话证据。该证据只能证明 fake provider、长程对话边界、画像资料引用和报告展示成立，不能证明真实 LLM 回复质量、真实 provider 可用性或真实个人资料路径通过。

当前文档阶段要解决的问题：

```text
系统已经具备 P5.5 画像和 P6/P7 自动化候选
但真实 provider 与真实个人资料仍是未执行高风险路径
如果直接进入验收或产品化，容易把 fake provider、多身份合成资料或本地脱敏 fixture 误写成真实通过
因此必须先把授权表、数据边界、真实调用证据、脱敏报告和打回条件写成可执行规格
```

当前文档阶段目标体验：

```text
用户打开文档和 drawio
→ 能快速看清哪些能力已完成自动化候选，哪些仍待真实验收
→ 能看清 P6-REAL 真实 provider 调用前需要确认哪些 provider、模型、数据范围、次数、预算和报告展示字段
→ 能看清 P7-post P5-REAL 真实资料复验只读取用户指定路径，不扫描个人目录
→ 能看清 fake provider 多轮对话、synthetic personas 和真实 provider/真实资料之间的证据差异
→ 后续一旦用户授权，就能按文档直接执行受控验收并生成脱敏 HTML 报告
```

当前文档阶段必须产出的结果：

- P6-REAL 受控外呼执行单：provider、model、base_url preset、API Key 本地配置、最大调用次数、数据类别、预算、超时、失败处理、报告展示范围；
- P7-post P5-REAL 资料授权执行单：简历、项目资料、JD 的明确本地路径、允许展示字段、脱敏级别、禁止展示字段和失败打回条件；
- 文档状态分层：`已实现自动化候选`、`待真实验收`、`后续独立阶段`；
- drawio 图：不超过 8 页，用颜色表达已完成、当前待验收、高风险需确认和 P8+；
- 验收门槛：明确 fake provider transcript 不等于真实 provider 质量，synthetic personas 不等于真实个人资料；
- 审计记录：说明本轮只做文档开发，不触发真实外呼、不读取真实资料、不进入代码实现。

当前文档阶段非目标：

- 不调用 MiniMax、DeepSeek、OpenAI-compatible 或其他真实外部 provider；
- 不读取真实简历、真实项目资料、真实 JD 或用户个人目录；
- 不保存、展示、扫描或迁移 API Key；
- 不做前后端业务代码实现；
- 不执行 workspace 删除、cleanup apply、migration apply；
- 不实现 SaaS、ASR、会议平台、自动投递、MCP/CLI。

当前文档阶段出门标准：

- PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、P6 计划和 drawio 对 P6-REAL/P7-post 的状态口径一致；
- 所有“待开发/待新增/待强化”旧口径被替换为“自动化候选已实现但真实验收待执行”或明确 P8+ 后续；
- drawio XML 可解析且页数不超过 8；
- 文档没有把真实 provider、真实个人资料、最终产品化、SaaS/ASR/会议平台/自动投递写成已通过。

## -2. P5.5 历史阶段状态与决策

P4 本地/mock Chatbox 体验已冻结，P5 本地/mock + 脱敏 fixture 自动化候选已完成，P6+P7 本地 Beta 自动化候选已完成。用户已确认优先对 P5.5 进行细致开发，把“个人专业背景、项目背景、各项能力评估和画像绘制”作为本阶段目标；当前 P5.5 自动化开发候选已完成。

当前 P5.5 结论只覆盖 examples / synthetic-style workspace + mock provider 自动化路径。P5.5 不代表 P5-REAL 通过，不读取用户真实个人资料，不默认调用真实 provider，不实现 SaaS/ASR/会议平台/自动投递/MCP/CLI。

P5.5 要解决的问题：

```text
P5 已能导入资料、解析 JD、生成申请包
P6/P7 已具备 provider opt-in 和本地 Beta 自动化候选
但用户仍缺少一个可审查、可追溯、可行动的候选人画像
无法快速判断自己的专业背景是否可信、项目是否有证据、能力强弱在哪里、目标岗位短板是什么
如果直接继续生成申请材料，系统可能放大未经确认的经历、弱证据技能或岗位不匹配风险
```

P5.5 目标体验路径：

```text
用户打开本地 Chatbox
→ 导入或粘贴简历、项目说明、经历材料和目标 JD
→ 系统基于已有 career_facts / skill_evidence / tech_project / job / match_report 汇总 CandidateProfile
→ Workbench 展示专业背景画像、能力矩阵、项目可信度、岗位短板和补强建议
→ 用户能展开每个判断的 source refs、证据强度、待确认项和风险原因
→ 用户围绕画像继续追问“我适合什么岗位 / 哪些项目最可信 / 还缺什么证据 / 下一步补什么”
→ 普通追问不写 artifact；明确要求刷新画像或生成材料时才进入工具路径
```

P5.5 必须产出的用户结果：

- 专业背景画像：目标岗位、转型路径、当前层级、主要经历线索和可信边界；
- 能力矩阵：技能名称、类别、证据类型、证据强度、岗位相关性和待确认状态；
- 项目可信度：本人贡献、技术难点、可验证材料、量化结果缺口和风险标签；
- 岗位短板：must-have / nice-to-have 缺口、表达风险、补强行动和优先级；
- source refs 面板：每条画像判断都能追溯到资料、项目、JD、match_report 或 artifact；
- 可视化验收报告：中文 HTML 报告展示目标架构、当前实现、用户路径、截图证据、未验证范围和 PRD 检视。

P5.5 非目标：

- 真实个人资料默认读取或验收；
- 默认外呼真实 MiniMax、DeepSeek 或 OpenAI-compatible provider；
- 敏感属性、人格、年龄、性别、健康、政治、家庭、民族等分析；
- 背景调查、社交媒体画像、隐私画像或不可解释评分；
- workspace 删除、cleanup apply、migration apply 或外部同步；
- SaaS、多租户、Billing、ASR、会议平台、自动投递、MCP/CLI。

P5.5 规格约束：

- 画像结论必须来自 `career_fact`、`skill_evidence`、`tech_project`、`job`、`match_report` 或 artifact source refs；
- “能力强/弱”必须解释为证据强弱和岗位相关性，不得写成人格或潜力判断；
- 项目可信度必须区分“资料已证明”“用户待确认”“证据不足”；
- 岗位短板必须可行动，不能只输出否定性评价；
- 普通聊天不写画像 artifact，明确画像刷新/生成才允许写入；
- 报告不得包含完整真实个人资料、API Key、provider raw response 或未授权长原文。

## -1. 当前阶段状态与决策

以下 P6+P7 内容作为已完成自动化候选和后续复验边界保留。P4 已在 2026-06-25 完成本地/mock Chatbox 体验冻结。P5 本地/mock + 脱敏 fixture 自动化候选已完成，证据包括 P5 HTML 报告、多视口真实界面截图、三身份合成资料可视化验收、`.venv/bin/python -m pytest` 88 passed, 1 warning、前端 build 通过和 drawio XML parse 通过。

用户已确认：

- P5-REAL 标记为冻结延期复验，不在当前阶段读取真实个人资料；
- P5-Freeze 标记为冻结延期复验，不把 P5 自动化候选写成最终通过；
- P5-REAL/P5-Freeze 在 P7 完成后作为 P7-post 复验重新执行；
- P6+P7 一体规划和自动化候选已完成并作为后续基线保留；P5-REAL/P5-Freeze 仍需真实资料授权后复验。

本 PRD 当前新增目标是 P6-REAL 与 P7-post P5-REAL 复验准备。P5.5 Candidate Profile 作为已完成自动化候选保留；以下 P6+P7 章节作为已完成自动化候选基线和后续真实验收边界保留；后续 P5 章节作为历史基线和 P7-post 复验依据保留。

## -0. P6+P7 自动化候选基线目标

P6 解决的问题：

```text
当前 Chatbox 已能在本地/mock 中连续对话和完成求职材料闭环
但用户仍无法在受控、安全、可恢复的前提下使用真实 provider 自由聊天
长对话也没有明确的上下文压缩、刷新恢复、provider 失败降级和外呼证据链
如果直接进入产品化，会放大 API Key 泄露、隐私外发、费用失控和虚假验收风险
```

P7 解决的问题：

```text
当前项目仍是本地工程原型和可验收工作台
缺少 Beta 用户持续使用所需的 workspace 生命周期、备份/迁移、诊断报告、发布/部署/回滚、安全隐私审计和支持流程
如果不补齐这些产品化基础，即使 P6 provider 聊天可用，也不能称为 Beta 体验
```

P6 目标体验路径：

```text
用户打开本地 Chatbox
→ 页面明确显示 provider 模式、模型、隐私边界和本轮是否会外呼
→ 默认仍走本地/mock，不因配置了 provider 就自动调用
→ 用户在模型设置中选择 MiniMax、DeepSeek 或 OpenAI-compatible provider
→ 用户在发送前或首次调用前确认本轮外呼和数据边界
→ 系统使用 Provider Policy Gate 检查授权、API Key、脱敏、预算和安全边界
→ 用户围绕求职方向、个人资料、JD、申请包和面试准备连续追问 20-50 轮
→ Long Context Manager 维护近期消息窗口、滚动摘要、workspace context snapshot 和相关 artifact/JD/profile 检索
→ 刷新页面后会话、摘要、关键上下文和当前 workspace 状态可恢复
→ provider 超时、429、结构错误或不可用时降级到本地连续对话基线
→ 普通聊天不写 artifact；明确要求解析、生成、重新生成或导出时才进入工具确认或工具执行
```

P7 目标体验路径：

```text
用户使用已具备 P6 provider opt-in 的本地 JobPilot
→ 可以创建、恢复、导出、清理和备份 workspace
→ 可以查看本地数据生命周期、隐私边界和诊断报告
→ 可以执行迁移 dry-run，并在不可逆迁移或删除前获得明确确认
→ 开发者可以按文档启动、部署、回滚和收集脱敏错误诊断
→ Beta 验收报告展示真实界面路径、测试结果、安全隐私审计和未验证范围
→ P7 通过后，再按 P7-post 计划执行 P5-REAL/P5-Freeze 复验
```

P6 必须产出的用户结果：

- 用户能明确判断“本轮是否调用真实外部 provider”；
- provider 默认不外呼，配置 provider 也不等于已调用；
- 真实 provider 调用前必须有确认和隐私/费用提示；
- API Key 不进入仓库、日志、报告、截图说明或测试 fixture；
- 长程连续对话支持 20-50 轮、刷新恢复、滚动摘要和上下文快照；
- provider 失败时不丢会话、不阻塞 UI，并能降级到本地连续对话；
- provider-backed 回复不能伪造不存在的履历事实，不能绕过 `questions_to_confirm`、artifact confirmation 或 export preflight；
- 自动化报告必须区分 mock/fake provider、受控真实 provider 和未验证范围。

P7 必须产出的用户结果：

- workspace 生命周期清楚：创建、恢复、导出、清理、备份、迁移 dry-run；
- 本地/远端数据边界、保留策略、删除确认和不可逆操作风险可读；
- 诊断报告、错误追踪和日志脱敏可用，不暴露 API Key 或完整个人资料；
- 发布、部署、启动、回滚和故障排查文档可复现；
- Beta 使用说明和支持流程可独立阅读；
- P7 final acceptance report 能列出目标架构、当前实现、真实界面路径、测试证据、隐私审计和未验证范围；
- P7 完成后有单独 P7-post P5-REAL/P5-Freeze 复验计划和打回条件。

P6+P7 非目标：

- 真正无限 token、无限上下文、无限成本的对话；
- 默认外呼真实 provider；
- 未经确认把真实个人资料发送给外部 provider；
- 自动读取用户个人目录；
- 把 synthetic personas、examples 或脱敏 fixture 写成真实个人资料验收；
- SaaS 登录、多租户、Billing；
- ASR、会议平台、自动投递；
- MCP Server、CLI 产品入口；
- 隐蔽式面试辅助、逐字代答或敏感属性分析；
- 不经用户确认的 workspace 删除、不可逆迁移或外部同步。

## -0.1 P6+P7 规格约束

- P6/P7 默认仍以本地 workspace 为安全边界；
- 真实 provider 必须 opt-in，且每轮外呼有可审计确认或会话级明确授权；
- Provider Policy Gate 必须拦截未授权外呼、缺 API Key、未脱敏真实资料、超预算、provider 配置错误和不安全请求；
- Long Context Manager 不能把完整历史、完整简历、完整 JD 或完整 provider raw response 无边界塞入模型；
- Provider Invocation Log 只记录脱敏元数据、provider/model、耗时、状态、错误类型、token 估算和 redaction 摘要；
- Chatbox 仍是薄入口，不生成求职内容、不直接写 SQLite、不直接保存 API Key；
- Domain Tools、Artifact Service、Export Service、Storage 和 Provider Runtime 继续承担业务写入、版本、导出、持久化和外呼边界；
- P7 不引入 SaaS 多租户或远端账号体系，除非另行立项；
- P7-post P5-REAL 复验必须由用户明确提供资料路径和允许展示字段；若用户不提供，结论只能保持未执行。

## 0. P5 历史阶段目标与 P7-post 复验依据

本节作为历史基线和 P7-post 复验依据保留。P4 已在 2026-06-25 完成本地/mock Chatbox 体验冻结。P5 的目标不是引入 SaaS、ASR、会议平台、自动投递或默认真实外部 provider，而是在 P4 已冻结的 Chatbox 工作台上，把用户自己的求职资料和目标 JD 组织成一条可确认、可编辑、可导出的本地闭环。

P5 的核心问题：

```text
当前项目已经能用 examples 和 mock provider 跑通完整求职材料体验
但真实用户把自己的简历、项目说明和 JD 放进来时
仍缺少足够明确的导入、解析、事实确认、缺口补充、编辑再生成和导出闭环
如果直接进入 provider 或产品化，会放大隐私、虚假验收和体验断裂风险
```

P5 当前状态：

- 本地/mock + 脱敏 fixture 的自动化候选路径已通过，覆盖资料导入、JD 解析、事实确认、申请包生成、编辑后重新阻塞、确认后导出、本地多轮追问和多视口截图；
- 最新工程证据为 `.venv/bin/python -m pytest` 88 passed, 1 warning、前端 build 通过、drawio XML parse 通过、`docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html`，以及 `docs/reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html`；
- P5-REAL/P5-Freeze 已按用户确认冻结延期到 P7 后复验：真实授权资料路径、允许展示字段、人工体验审查清单和 P5 final closure audit 仍未完成，不得写成通过；
- 当前 PRD 后续只允许指导 P5-REAL 与 P5-Freeze 收口，不得把真实外部 provider、provider-backed 自由智能聊天或产品化发布写成 P5 已完成。

P5 目标体验路径：

```text
用户打开本地 Chatbox
→ 明确看到当前仍是本地优先、mock 默认、外部 provider 需确认
→ 上传或粘贴自己的简历、项目 README、经历说明或作品材料
→ 系统解析资料并生成可读摘要、事实来源和待确认项
→ 用户粘贴或导入目标 JD
→ 系统解析岗位要求、识别缺失信息，并给出可补充问题
→ 系统把用户资料与 JD 匹配，生成匹配说明和申请策略
→ 用户确认事实、补充缺口、编辑草稿或要求重新生成
→ 系统生成申请包草稿、cover letter/申请说明、面试准备或简历改写建议
→ 用户在 Workbench 中查看产物、版本、确认项、来源和导出 preflight
→ 用户导出 Markdown/DOCX，并能继续围绕当前资料和 JD 多轮追问
```

P5 必须产出的用户结果：

- 真实资料导入路径清楚，支持上传或粘贴，并明确本地处理边界；
- 资料解析结果有人类可读摘要，不以裸 JSON 或内部 id 作为主要反馈；
- JD 解析结果能说明岗位要求、关键词、硬性条件、隐含风险和缺失信息；
- `questions_to_confirm` 能形成清晰的事实确认和补充闭环；
- 匹配报告能说明“哪些经历可用、哪些证据不足、哪些表达需要谨慎”；
- 申请包草稿能被用户编辑、重新生成、查看版本并导出；
- 导出前必须显示 blocking/warning/optional 确认状态；
- 多轮追问必须基于当前 workspace 状态回答“进展如何 / 下一步做什么 / 这个经历能否用于该 JD”等问题；
- 自动化验收报告必须使用脱敏或用户明确授权的数据，不得把真实个人资料全文写入报告、日志或 fixture；
- P5 文档、drawio、验收门槛和 TODO 必须清楚区分“已实现 P4 基线”“P5 本阶段计划”“P6+ 后续能力”。

P5 验收标准：

> 一个转行程序员可以在本地 Chatbox 中使用自己的求职资料和目标 JD，完成导入、解析、确认、生成、编辑、导出和连续追问；系统始终说明事实来源、待确认项、隐私边界和下一步，不默认调用真实外部 provider。

P5 非目标：

- 默认启用真实外部 provider 或 provider-backed 自由智能聊天；
- 把未授权真实个人资料写入报告、日志、测试 fixture 或截图说明；
- ASR / Whisper、会议平台、系统音频、视频解析；
- 自动海投、岗位数据源聚合、Offer 分析；
- SaaS 登录、多租户、Billing；
- MCP Server、CLI 产品入口；
- 不经用户确认的不可逆迁移、workspace 删除或外部调用。

## 0.1 P5 规格约束

- P5 默认数据边界仍是本地 workspace；真实外部 provider 只属于 P6 opt-in；
- P5 可以使用用户明确授权的真实资料做人工验收，但自动化报告必须脱敏；
- 如果没有用户授权的真实资料，自动化验收只能使用真实感示例数据，并明确标注不是个人真实资料；
- Chatbox 仍是薄入口，不能在前端生成求职内容或直接写 SQLite；
- Domain Tools、Artifact Service、Export Service 和 Provider Policy Gate 必须继续承担业务写入、版本、导出和外呼边界；
- P5 完成不代表最终产品化发布，只代表真实资料本地闭环达到可验收状态。

以下 P4 内容作为已冻结基线和历史背景保留。

## 1. 历史 P4 UX 体验强化阶段基线

P0 已冻结，P1 已完成工程闭环，P2 已完成 examples-guided 端到端体验，P3 已完成本地自动化验收和 Chrome 截图报告。P4 的目标不是增加新入口或新后端能力，而是把当前 Chatbox 工作台从“能演示、能验收”推进到“真实用户愿意使用、能快速理解、能顺手完成求职材料任务”的体验状态。

P4 的核心问题：

```text
当前页面已经能跑通求职路径
但首屏任务入口、对话反馈、推进台层级、产物卡语言、模式/Provider 状态和移动端操作仍不够自然
导致用户需要理解工程概念，才能知道下一步该做什么
```

P4B 全尺寸桌面体验修正：

```text
当前 P4A 已解决窄屏可达性和基础 Chatbox 交互
但 1200px / 1440px / 1600px / 1920px 桌面宽度仍可能出现大面积空白、信息密度不足、工作台感不强
因此 P4B 将“全尺寸桌面工作台体验”列为本阶段 hard gate
```

P4 目标体验路径：

```text
用户打开本地 Chatbox
→ Chatbox 空状态中直接看到“导入资料 / 粘贴 JD / 生成申请包 / 准备面试”建议任务
→ 选择示例模式或真实资料模式，并理解是否会调用外部 provider
→ 在对话区上传资料、粘贴 JD 或输入自然语言任务
→ 建议任务点击后填入输入框或直接触发对话
→ Chatbox 返回可理解的反馈、计划、处理中状态、错误原因或下一步
→ 推进台只呈现当前任务、阶段、产物、确认项、版本和导出
→ 产物卡使用求职语义表达摘要、待确认风险和主次分明的可执行操作
→ 用户完成“导入资料 → 分析岗位 → 生成申请包 → 确认/编辑 → 导出”
→ 1200px / 1440px / 1600px / 1920px 桌面、720px 窄屏、390px 移动宽度均通过截图和人工体验审查
```

P4 必须产出的用户结果：

- 更清晰的 Chatbox 空状态任务启动区，而不是工程状态堆叠；
- 更自然的 Chatbox 对话反馈，包括缺资料、失败、处理中和完成态；
- 更分离的推进台，只管理状态、产物、确认项、版本和导出；
- 更可读的产物卡，减少裸 JSON、artifact id、内部 version id 对用户的干扰，并区分 primary / secondary 操作；
- 更明确的示例模式 / 我的资料 / mock provider / external provider 表达，例如“外部模型未调用（隐私安全）”；
- 更顺手的 1200px、1440px、1600px、1920px、720px、390px 布局和滚动体验；
- 桌面大屏必须呈现完整工作台，而不是把窄屏布局放大后留下大面积空白；
- 桌面工作台应包含清晰的对话任务区、状态指标、快捷任务、推进台摘要和下一步建议；
- 390px 下 Workbench 可以收为底部抽屉或折叠面板，避免压缩 Chatbox；
- 给 Gemini 和人类审查者独立阅读的前端页面方案与静态原型；
- P4 UX before/after HTML 报告、截图证据和 PRD 规格检视。

P4 验收标准：

> 一个转行程序员不读开发文档，也能在本地页面理解从哪里开始、系统正在做什么、哪些内容待确认、哪些材料可导出，并能在桌面和窄屏完成关键求职路径。

P4B 全尺寸桌面体验验收标准：

> 用户在 1200px、1440px、1600px 和 1920px 桌面宽度下，不应看到由布局错误造成的大面积空白；页面应像一个完整求职材料工作台，而不是窄屏 Chatbox 停靠在左侧。

P4C-FC 自由连续对话补充目标：

```text
用户不应只能点击任务卡或触发固定工具流
→ 用户可以先自由描述求职方向、偏好、疑问和下一步
→ 普通连续追问不得误触发 artifact 写入
→ 系统应能基于当前 workspace 状态回答“现在进展如何 / 下一步做什么”
→ 只有明确要求“整理资料 / 解析 JD / 生成申请包 / 准备面试”时才执行对应工具
→ 当前阶段仍是本地/mock 连续对话基线，不声称完整 provider-backed 自由智能聊天
```

P4C-FC 必须产出的用户结果：

- Chatbox 可以承接至少两轮自由追问而不中断；
- “我还没有 JD，先聊聊求职方向”不会被误判为解析 JD；
- “继续，我应该先补 React 还是项目经历”会得到下一步建议，而不是写入 artifact；
- “当前进展如何 / 有哪些产物”可以得到 workspace 摘要；
- 明确工具意图仍能稳定生成对应产物；
- 会话恢复后能看到自由对话历史；
- UI 文案明确默认仍不调用真实外部 provider。

P4 非目标：

- MCP Server、CLI；
- ASR / Whisper、会议平台、系统音频、视频解析；
- 自动海投、岗位数据源聚合、Offer 分析；
- SaaS 登录、多租户、Billing；
- 全量重写前端或引入复杂 Dashboard；
- 默认启用真实外部 provider；
- 把本地/mock 连续对话写成完整 provider-backed 自由智能聊天；
- 把未人工体验通过的 UI 写成已通过。

## 0.1 Gemini 审查后 P4 必修修正

Gemini 对 P4 前端页面方案给出“有条件通过”。以下意见被采纳为 P4 hard gate：

- Task Launcher 必须并入 Chatbox empty state / suggested prompts，不能作为割裂的独立任务卡区域；
- Suggested prompt 点击后必须填入 composer 或直接触发对话；
- provider 状态必须使用用户语言，避免 `External configured` 一类工程表达；
- 对话必须有 loading / thinking / executing 状态，避免用户误以为系统卡死；
- 错误气泡必须包含恢复动作，例如重新上传、补充 JD、查看支持格式；
- 产物卡必须区分 primary action 和 secondary action，阻塞项优先显示“补充事实 / 去确认”；
- Workbench 初始状态必须说明“导入资料后，求职产物将在此生成”；
- 390px 下 Workbench 不得挤压 Chatbox，应折叠为底部抽屉或次级区域；
- segmented mode toggle 必须包含 `aria-pressed` 或等价状态；
- 长 JD、长计划和长摘要必须有折叠策略，虚拟列表可延后到 P5；
- 待确认项文案必须偏求职辅导，不得只像程序校验。
- 1200px / 1440px / 1600px / 1920px 必须作为桌面 hard gate，不能只用 390px / 720px 证明响应式体验；
- 截图脚本必须隔离或清理 Chrome viewport emulation，不能污染人工审查者正在使用的浏览器标签页；
- P4 HTML 报告必须明确标出全尺寸桌面截图、窄屏截图和移动端截图，且不能把自动截图替代人工体验认可。

以下 P3 内容作为已完成基线和历史背景保留。

## 0.1 历史 P3 阶段增补

P0 已冻结，P1 已完成工程闭环，P2 已完成 examples-guided Chatbox 端到端体验和可截图 HTML 验收报告。P3 的目标不是扩展 MCP、CLI、ASR 或会议平台，而是把当前产品推进到真实用户可用的 Chatbox 工作台：

```text
用户打开本地 Chatbox
→ 明确知道当前是示例模式还是真实资料模式
→ 在聊天区上传资料、粘贴 JD 或输入自然语言任务
→ Chatbox 必须有可见响应、计划、执行状态和失败原因
→ 推进台只展示状态、产物、确认项、版本和导出
→ 用户完成申请包、面试准备、实时文本提示、复盘和训练任务
→ 桌面、窄屏和移动宽度下都能完成截图验收
```

P3 的验收标准是：

> 真实用户是否能不读开发文档，只通过 Chatbox 和推进台完成一条可信、可确认、可导出的求职材料体验。

P3 不得把 P2 examples 一键演示包装成真实用户完整体验；不得把未执行的外部 provider 调用、未人工确认的真实个人资料或未截图验证的 UI 状态写成已验收。

P3 必须产出的用户结果：

- 清晰的 Chatbox 首屏：用户知道可以上传、粘贴 JD、生成申请包或准备面试；
- 清晰的模式边界：示例模式、真实资料模式、mock provider、外部 provider 状态可见；
- 可响应的聊天：发送有效任务后必须返回可理解的消息、下一步或错误；
- 分离的推进台：状态、阶段、产物、导出和确认项与对话区分开；
- 可用的响应式布局：桌面、窄屏、移动宽度下无严重截断、横向空洞或输入区遮挡；
- 真实感数据验收：默认使用 examples 真实感数据；真实个人资料和真实外部调用仍需人工确认。

P3 非目标：

- MCP Server、CLI；
- ASR / Whisper、会议平台、系统音频、视频解析；
- 自动海投、岗位数据源聚合、Offer 分析；
- SaaS 登录、多租户、Billing；
- 复杂 Dashboard 或营销首页；
- 默认启用真实外部 provider。

以下 P2 内容作为已完成基线和历史背景保留。

## 1. 产品定位

JobPilot AI 是面向转行程序员的本地优先、免费开源 AI 求职 Agent 服务。默认入口仍是极简 Chatbox，核心能力仍沉在后端 Agent Tool Service 和 Pi Agent Core 编排层。

P0 已冻结，P1 已完成本地工程闭环。P2 的目标不是扩展更多底层入口，而是把已有能力组织成一条完整、可点击、可截图验收的端到端用户体验路径。

P2 的验收标准仍是：

> 用户是否能在本地 Chatbox 中拿到可信、可确认、可导出的求职结果。

页面复杂度、模型炫技、MCP/CLI/ASR/会议平台都不是 P2 出门标准。

## 2. P0/P1 基线

P0 已完成：

```text
创建 workspace
→ 导入简历和项目 README
→ 生成 CareerFact / SkillEvidence / TechProject
→ 粘贴 JD
→ 生成 JD 解析和 MatchReport
→ 生成 ApplicationPackage
→ 用户确认并导出 Markdown
→ 生成 Interview Prep 和 StoryCard
→ 输入实时问题并获得结构化提示
→ 输入 transcript 并生成复盘和 TrainingTask
```

P1 已完成：

- OpenAI-compatible provider opt-in 基础；
- provider timeout / retry / redaction / schema validation；
- 核心工具 provider-backed contract 路径；
- artifact edit / version / regenerate；
- Markdown + DOCX 导出；
- Chatbox provider mode、版本、编辑、重新生成和导出入口；
- P1 本地自动化验收和 Chrome 可见截图。

P2 不能破坏 P0/P1：无 API Key、无外部网络、mock provider 模式下，P0/P1 demo flow 和 eval gates 必须继续通过。

## 3. P2 目标用户

P2 仍聚焦：

- 正在转行申请 junior / entry-level 软件岗位的人；
- 有项目但不知道如何组织求职材料的人；
- 想在本地控制简历、JD、面试 transcript 和 API Key 的用户；
- 想看到 AI 产物来源、待确认项、导出文件和下一步行动的新贡献者或开发者。

P2 还服务人类体验审查者：他们应该能通过截图和 HTML 报告快速判断当前方向是否偏离“极简 Chatbox + 可用结果”。

## 4. P2 目标体验路径

P2 完成后，用户应能按以下路径完成一条完整求职 Agent 体验：

```text
启动本地项目
→ 打开 Chatbox
→ 创建或恢复 workspace
→ 看到 provider 状态和本地隐私边界
→ 选择 examples 一键体验，或上传自己的资料
→ 导入简历 / 项目 README
→ 生成职业事实、技能证据和项目卡
→ 粘贴或加载目标 JD
→ 生成 JD 解析和岗位匹配报告
→ 生成申请包
→ 用户确认 / 编辑 / regenerate
→ 导出 Markdown + DOCX
→ 生成面试准备和故事卡
→ 输入文本面试问题并获得结构提示
→ 输入 transcript 并生成复盘和训练任务
→ 看到本次求职推进摘要、产物列表和导出文件
```

## 5. P2 必须产出的用户结果

P2 必须让用户看到：

- 工作流步骤状态；
- 下一步动作；
- 导入资料结果；
- 职业事实和技能证据摘要；
- 技术项目卡摘要；
- JD 解析和岗位匹配结论；
- 申请包摘要；
- 待确认项；
- artifact 当前版本和历史版本；
- regenerate 后的新版本；
- Markdown 和 DOCX 导出文件；
- 面试准备问题和故事卡；
- realtime 文本结构提示；
- 面试复盘和训练任务；
- P2 HTML 验收报告和截图证据。

## 6. P2 范围

### 6.1 Guided Chatbox Flow

必须实现：

- Chatbox 顶部工作流面板；
- 一键体验 examples 完整路径；
- 步骤状态、当前结果、导出文件和失败恢复提示；
- 人类可读 artifact 摘要，不能只依赖 JSON；
- 本地可见验收入口，例如 `?autorun=1`。

### 6.2 Workflow Orchestrator

必须实现：

- 后端 workflow API；
- 串联现有 Domain Tools；
- 返回 `steps`、`artifacts`、`exports`、`summary`、`key_outputs`；
- workflow 只编排，不复制业务生成逻辑；
- 默认使用 examples 匿名真实感数据和 mock provider；
- 不触发真实外部 Provider。

### 6.3 Acceptance Evidence

必须实现：

- 后端 eval 覆盖 examples guided flow；
- 前端 build 通过；
- 全量 pytest 通过；
- Chrome 截图覆盖初始页、完成页、总结/导出页；
- P2 HTML 验收报告；
- PRD 规格检视；
- 已验证 / 未验证范围明确标注。

## 7. P2 非目标

P2 不做：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台接入；
- 屏幕解析或视频解析；
- 自动申请 / 自动投递；
- 隐蔽式面试浮窗；
- 自动 coding 代答；
- 面试官敏感属性分析；
- SaaS 登录、多租户或 Billing；
- 默认真实外部 Provider 调用；
- 使用真实个人资料做自动验收。

这些能力只能进入 P4+ 或独立阶段，并必须重新计划、审计和验收。

## 8. 成功标准

P2 完成的定义：

一个新贡献者能按 README 在本地启动 API 和 Chatbox；一个转行程序员能在 mock provider 下通过 Chatbox 一键或按引导跑通完整求职体验路径；用户能看到步骤、结果、待确认项、版本和导出文件；Chrome 截图和 HTML 报告能让人类快速理解当前项目已经实现什么、没有实现什么；测试、前端构建、PRD 检视和 P2 验收报告全部通过。

## 9. 高风险确认点

以下动作即使在 P2 中也必须暂停并找用户确认：

- 使用真实个人简历、真实私有 JD、真实 transcript；
- 配置或读取用户真实 API Key；
- 调用外部 LLM 网络服务；
- 删除 workspace 或执行不可逆数据迁移；
- 接入 ASR、系统音频、会议平台、屏幕解析或视频解析；
- 自动申请、自动投递或绕过面试规则。
