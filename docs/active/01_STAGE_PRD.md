# JobPilot AI P4 UX 体验强化阶段 PRD

## 0. P4 当前阶段增补

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

P4 非目标：

- MCP Server、CLI；
- ASR / Whisper、会议平台、系统音频、视频解析；
- 自动海投、岗位数据源聚合、Offer 分析；
- SaaS 登录、多租户、Billing；
- 全量重写前端或引入复杂 Dashboard；
- 默认启用真实外部 provider；
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
