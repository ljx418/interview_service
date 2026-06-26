# JobPilot AI P4 UX 目标架构深度设计

## 0. P4 当前阶段架构增补

P4 在 P0/P1/P2/P3 基线上增加“真实用户体验强化平面”。目标不是改变后端 Agent Tool-first 架构，而是把既有能力重新组织成清晰、低认知负担、可截图和可人工审查的前端体验架构。

P4 架构主线：

```text
用户任务意图
→ Experience Shell
→ Conversation Plane
  → Empty State Suggested Prompts
  → Composer and Upload Dock
  → Free Local Dialogue / Multi-turn Follow-up
  → Chat Intent Router
  → Loading / Error Recovery
→ Full-size Desktop Workbench Controller
→ Workbench Plane
→ Artifact Review Plane
→ Export / Confirmation Plane
→ Evidence and Review Plane
```

## 0.1 P4 目标 UX 架构模块

```text
User
  → Chatbox Experience Shell
    → Workspace / Mode / Provider Strip
    → Conversation Plane
      → Empty State Suggested Prompts
      → Free Local Dialogue
      → Clarification / Status / Next-step Replies
      → Loading / Thinking Steps
      → Error Recovery Actions
    → Composer and Upload Dock
    → Full-size Desktop Workbench Controller
    → Workbench Plane / Mobile Drawer
    → Artifact Review Cards
    → Confirmation and Export Bar
    → Responsive Layout Controller
  → FastAPI Agent Service
    → Chat Routes
    → Workflow Routes
    → Artifact Routes
    → Export Routes
    → Provider Routes
  → ChatCore and Flow Orchestration
    → KeywordChatCore
    → PiAgentChatCore
    → Chat Intent Router
    → Context Snapshot
    → Real User Flow Controller
  → Domain Tool Layer
    → Profile / Project / Job / Application / Interview / Realtime / Review Tools
  → Artifact and Storage Layer
    → ArtifactVersion
    → Confirmation Model
    → Export Service
    → SQLite Workspace
  → Evidence Layer
    → Chrome Screenshots
    → HTML UX Report
    → Gemini Review Package
    → PRD Spec Review
```

## 0.2 P4 模块职责、输入输出和禁止职责

| 模块 | 核心职责 | 输入 | 输出 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Experience Shell | 建立产品语境和整体布局，承载 mode/provider/workspace 状态 | workspace、provider status、viewport | 页面骨架、当前模式、隐私提示 | 不做营销首页；不隐藏外部调用状态 |
| Empty State Suggested Prompts | 在 Chatbox 空状态内把求职任务变成可点击建议 | 用户意图、examples 状态、资料状态 | 填入 composer 或直接触发对话 | 不作为割裂的独立任务区；不伪造已完成任务 |
| Conversation Plane | 展示用户消息、自由追问、系统计划、loading、结果、失败和下一步 | chat messages、tool summaries、errors、execution state、context snapshot | 人类可读对话流 | 不把裸 JSON 作为唯一反馈；不展示内部堆栈；不静默失败；不把普通聊天误触发为工具写入 |
| Chat Intent Router | 区分自由对话、状态查询、下一步、澄清和明确工具意图 | message、session history、workspace snapshot | free dialogue reply、clarification、tool intent | 不默认外呼 provider；不在未确认时写 artifact；不把“还没准备好 JD”误判为解析 JD |
| Context Snapshot | 为连续对话提供当前 workspace 摘要 | latest job、latest package、artifact count、pending confirmations | 状态摘要、下一步提示上下文 | 不暴露敏感原文；不替代 artifact/source refs |
| Composer and Upload Dock | 支持输入、上传和快捷任务触发 | 文本、文件、快捷动作 | chat/workflow request | 不直接解析简历/JD；不直连 provider |
| Loading / Error Recovery | 告诉用户 Agent 正在执行什么，失败后如何恢复 | running step、error code、missing input | thinking steps、retry/upload/fill action | 不用 spinner 替代解释；不让用户重复点击 |
| Full-size Desktop Workbench Controller | 管理 1200/1440/1600/1920 桌面宽度的信息密度、列宽、空白、快捷任务和推进台关系 | viewport、workflow state、artifact count、conversation state | 桌面工作台布局、状态指标、快捷任务带、推进台摘要 | 不把窄屏布局简单放大；不留下布局错误造成的大面积空白；不污染人工浏览器 viewport |
| Workbench Plane / Mobile Drawer | 管理当前任务状态、阶段、下一步、产物和导出；移动端折叠为抽屉或次级面板 | workflow state、artifact summaries、viewport | 状态摘要、行动列表、产物导航 | 不承担聊天输入；不复制业务生成逻辑；不在 390px 下压缩对话 |
| Artifact Review Cards | 以求职语义展示产物摘要、待确认项、版本和主次操作 | artifact/version/source refs | 可读卡片、primary action、secondary actions | 不隐藏待确认项；不暴露内部 id 作为主标题；不让所有按钮同等权重 |
| Confirmation and Export Bar | 在导出前展示 blocking/warning/optional 确认边界 | current artifact version、questions_to_confirm | 导出 preflight 结果、文件入口 | 不绕过 blocking confirmation |
| Responsive Layout Controller | 管理 1200/1440/1600/1920/720/390 多档布局、滚动和输入区 | viewport、content density | 可用且顺手的布局 | 不让关键操作被遮挡或截断；不把单一宽度截图当作全尺寸验收 |
| Gemini Review Package | 给外部模型和人类独立审查前端方案 | UX brief、prototype、checklist | 审查意见和风险清单 | 不声称代码已实现；不替代真实截图验收 |

## 0.3 当前架构与 P4 目标差距

| 当前实现 | P4 目标 | 风险 | 验收证据 |
| --- | --- | --- | --- |
| 首屏以工程状态和分区为主 | Chatbox 空状态优先呈现 suggested prompts 和下一步 | 用户不知道从哪里开始，任务入口与对话割裂 | 初始页截图、5 秒理解审查、点击 suggested prompt 证据 |
| Chatbox 和推进台虽已分离但层级仍重 | 对话负责反馈，推进台负责状态和产物 | 用户误以为 chatbot 无响应 | 发送任务截图、错误态截图 |
| 缺少 thinking / executing 过渡 | 显示正在读取资料、对比 JD、生成草稿等步骤 | 用户重复点击或误判卡死 | loading 状态截图 |
| Chatbox 偏固定任务控制台 | 增加本地/mock 自由连续对话基线：普通追问、状态查询、下一步不会误触发工具 | 用户觉得对话被中断，或无意中写入 artifact | 自由追问两轮测试、浏览器截图、会话恢复证据 |
| 产物卡暴露 `job`、`match_report`、内部版本等术语 | 产物卡用“岗位解析 / 匹配报告 / 申请包草稿”等求职语义，并突出阻塞操作 | 用户读不懂产物价值或不知道先点哪个按钮 | 产物卡 before/after 截图 |
| Provider 标签可能被理解为正在外呼 | 明确“外部模型未调用（隐私安全）/ 外部调用需确认” | 隐私和费用误解 | provider 状态截图 |
| 1200px 以上桌面宽度仍可能像窄屏布局停靠在左侧 | 全尺寸桌面必须呈现完整工作台：对话区、状态指标、快捷任务、推进台摘要和下一步建议协同展示 | 大面积空白让用户误判页面未完成，人工体验审查不通过 | 1200/1440/1600/1920 Chrome 截图和人工体验审查记录 |
| 移动端可以运行但信息堆叠较重 | 390px 下 Conversation 优先，Workbench 收为底部抽屉或折叠面板 | 移动可用但不顺手 | 390px 关键路径截图 |
| 截图脚本可能遗留 Chrome viewport emulation | 截图脚本必须隔离或在 finally 清理 emulation/touch override | 人工审查者浏览器被污染，产生“窄屏布局占据大屏”的虚假体验证据 | 截图脚本清理逻辑、真实浏览器宽度检查、报告说明 |
| 验收报告有截图但缺少设计审查包 | 提供 Gemini 可独立审查的页面方案 | 外部审查上下文不足 | `docs/gemini-frontend-review-package/` |

## 0.4 P4 架构不变量

- Chatbox 仍是薄入口，只做输入、展示、确认、编辑和导出触发；
- 前端不得生成求职内容，不得直接写 SQLite，不得直连 provider；
- PiAgent / ChatCore 仍只负责意图和工具计划，业务写入仍由 Python Domain Tools 完成；
- 本地连续对话只作为 mock/offline 基线，不得被描述为完整 provider-backed 自由智能聊天；
- Chat Intent Router 只有在明确工具意图或用户确认后才允许触发 Domain Tools 写入 artifact；
- source refs、questions_to_confirm、artifact version、export preflight 不得因 UX 简化而丢失；
- mock provider 仍是默认验收基线，external provider 仍需用户确认；
- realtime 仍是 text-in / hint-out，不进入 ASR、会议平台或逐字代答；
- P4 不能用更好看的静态原型替代真实前端实现和 Chrome 截图验收。

## 0.5 P4 架构验收问题

每个 P4 实现 PR 或阶段验收必须回答：

- 用户是否能在首屏判断下一步？
- Suggested prompts 是否与 composer 形成闭环，而不是割裂任务区？
- Conversation Plane 是否对有效输入、缺资料和失败都有反馈？
- Conversation Plane 是否能承接普通自由追问、状态查询和下一步问题，而不误触发工具？
- Chat Intent Router 是否能区分“聊方向”与“解析 JD / 生成申请包”等明确工具意图？
- Conversation Plane 是否有 loading / thinking / executing 状态和错误恢复 action？
- Full-size Desktop Workbench Controller 是否覆盖 1200/1440/1600/1920，且没有布局错误造成的大面积空白？
- Workbench Plane 是否只展示状态、产物、确认项、版本和导出，且移动端不会压缩 Chatbox？
- Artifact Review Cards 是否保留 source refs 和 questions_to_confirm？
- Artifact Review Cards 是否区分 primary / secondary action？
- Provider 状态是否明确本次是否外呼，并使用用户语言？
- 390px 下输入、消息、当前任务和产物操作是否仍可达？
- Chrome 截图脚本是否隔离或清理 viewport emulation，避免污染人工审查者浏览器？
- mode toggle、状态区和按钮是否具备必要 ARIA 状态？
- Gemini 审查包和 HTML 报告是否明确“设计方案 / 已实现 / 未验证”的边界？

以下 P3 内容作为已完成基线和历史背景保留。

## 0.6 历史 P3 阶段架构增补

P3 在 P0/P1/P2 基线上增加“真实用户 Chatbox 体验平面”。目标不是新增底层入口，而是把已有 Agent Tool 能力变成用户能直接完成的求职工作台。

本阶段架构文档不再把阶段顺序作为主线。主线改为：

```text
模块职责
→ 模块输入 / 输出
→ 模块之间的调用关系
→ 数据所有权
→ 安全边界
→ 验收证据
```

## 0.1 目标架构模块总览

```text
User
  → Chatbox Client
    → Conversation View
    → Composer / Upload Entry
    → Workbench Panel
    → Artifact Cards
    → Mode / Provider Status
  → FastAPI Agent Service
    → Chat Routes
    → Workflow Routes
    → Artifact Routes
    → Export Routes
    → Provider Routes
  → ChatCore Facade
    → KeywordChatCore
    → PiAgentChatCore
  → Flow Orchestration
    → Intent Router
    → Real User Flow Controller
    → P2 Demo Workflow Orchestrator
  → Domain Tool Layer
    → Profile Tools
    → Project Tools
    → Job Tools
    → Application Tools
    → Interview Tools
    → Realtime Hint Tools
    → Review / Training Tools
  → Provider and Contract Layer
    → Provider Policy Gate
    → Mock / Fixture Provider
    → OpenAI-compatible Provider
    → Prompt Contract
    → Schema Validation
  → Artifact and Storage Layer
    → Artifact Service
    → Artifact Versioning
    → Confirmation Model
    → Export Service
    → SQLite Workspace
    → Local Files / Exports
  → Evidence Layer
    → Pytest Eval Gates
    → Chrome Screenshots
    → HTML Acceptance Reports
```

## 0.2 模块职责和禁止职责

| 模块 | 核心职责 | 输入 | 输出 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox Client | 呈现对话、上传、状态、产物和导出入口 | 用户消息、文件、按钮操作、API 响应 | UI 状态、API 请求、截图证据 | 不生成求职内容；不绕过后端确认；不保存 API Key |
| Conversation View | 展示消息、计划、执行结果和错误 | chat messages、tool result summary | 用户可读消息流 | 不展示不可解释的裸 JSON 作为唯一结果 |
| Composer / Upload Entry | 输入文本、上传资料、触发发送 | 文本、文件、快捷动作 | chat/workflow 请求 | 不直接解析简历或 JD |
| Workbench Panel | 展示阶段、下一步、产物、确认项、版本和导出 | artifact summary、workflow state | 可操作工作台 | 不承担聊天输入；不复制业务逻辑 |
| Artifact Cards | 管理单个产物的摘要、source refs、确认项和版本 | artifact、artifact_version | edit/regenerate/export 操作 | 不隐藏待确认项；不把 warning 变成 confirmed |
| FastAPI Agent Service | 提供 HTTP API、认证前边界、请求校验 | HTTP 请求、workspace id | 结构化响应、错误码 | 不把 provider 原始敏感内容写入日志 |
| Chat Routes | 接收对话请求并调用 ChatCore | session id、message、attachments | assistant message、tool/action refs | 不直接执行复杂业务工具 |
| Workflow Routes | 执行示例或真实用户流程 | workflow request、mode | steps、artifacts、exports、summary | 不伪造完成步骤 |
| Artifact Routes | 读取、确认、编辑、版本切换、regenerate | artifact id、version id、patch | artifact state | 不覆盖旧版本 |
| Export Routes | 预检并导出当前版本 | artifact version、format | export file path/download token | 不写 workspace 外路径 |
| Provider Routes | 显示 provider 状态和测试连接 | env config、provider preset | provider status | 不回传 API Key |
| ChatCore Facade | 隔离前端对具体编排器的依赖 | message context | intent/tool plan | 不写业务数据 |
| KeywordChatCore | 离线可验收 fallback 编排 | message text | deterministic plan | 不替代真实 provider-backed 产物 |
| PiAgentChatCore | 接入 Pi Agent Core 做意图和工具计划 | message、tool catalog | planned tool invocations | 不直接写 SQLite；不绕过 Python tools |
| Real User Flow Controller | 把自然语言任务转成可执行工具序列 | intent、workspace state | tool execution plan | 不越过确认/安全边界 |
| Domain Tools | 执行业务能力和写入领域数据 | typed tool input | typed tool output、artifact refs | 不访问 workspace 外文件 |
| Provider Policy Gate | 决定是否允许 provider 调用 | provider mode、consent、data class | allow/deny、redacted input | 不默认外部调用 |
| Provider Runtime | 调用 mock/fixture/external provider | prompt contract input | provider output | 不返回未校验内容给业务层 |
| Prompt Contract / Schema Validation | 约束 LLM 输入输出结构 | schema、raw output | validated output or error | 不把 malformed output 写库 |
| Artifact Service | 统一 artifact 元数据和版本 | domain object、version content | current version、history | 不丢 source refs / questions_to_confirm |
| Export Service | 生成 Markdown/DOCX 等文件 | current/selected version | local export file | 不绕过 blocking confirmation |
| SQLite Workspace | 本地持久化业务状态 | validated writes | query results | 不保存 API Key、完整敏感 raw response |
| Evidence Layer | 证明实现与 PRD 一致 | tests、screenshots、reports | acceptance evidence | 不做未执行声明 |

## 0.3 组件关系和依赖方向

依赖方向必须保持单向：

```text
Chatbox Client
→ FastAPI Routes
→ ChatCore / Flow Controller
→ Domain Tools
→ Provider / Artifact / Export / Storage
```

允许的反向关系只有“状态读取”和“事件结果返回”：

```text
Storage / Artifact
→ API response
→ Workbench rendering
```

禁止关系：

- Chatbox 直接调用 Provider；
- Chatbox 直接写 SQLite；
- PiAgent 直接写 SQLite；
- Provider Runtime 直接写 artifact；
- Export Service 从未校验 provider raw output 导出；
- Workflow 在失败后伪造后续步骤完成；
- 任何模块把完整 API Key、完整简历、完整 JD、完整 transcript 或完整 raw response 写入日志。

## 0.4 关键端到端控制流

### 0.4.1 用户发起求职任务

```text
Composer
→ Chat Route
→ ChatCore Facade
→ PiAgentChatCore 或 KeywordChatCore
→ Real User Flow Controller
→ Domain Tool Executor
→ Artifact Service
→ Conversation View + Workbench Panel
```

验收关注：

- 用户发送后必须有可见响应；
- 缺少资料时返回下一步，而不是静默失败；
- 执行计划和产物引用必须可追踪。

### 0.4.2 资料导入和事实抽取

```text
Upload Entry
→ File / Workspace Route
→ Document Store
→ profile.extract_facts / project.create_card
→ Provider Policy Gate
→ Provider Runtime or Mock
→ Schema Validation
→ CareerFact / SkillEvidence / TechProject
→ Artifact Version
→ Workbench Panel
```

验收关注：

- source refs 必须指向资料来源；
- 不确定内容进入 questions_to_confirm；
- 未确认内容不得作为确定事实导出。

### 0.4.3 JD 分析和申请包生成

```text
Conversation or Workflow request
→ job.parse_jd
→ job.match_profile
→ application.create_package
→ Artifact Service
→ Export Preflight
→ Markdown / DOCX Export
```

验收关注：

- MatchReport 必须区分 strengths、gaps、next actions；
- ApplicationPackage 必须保留 source refs 和 pending confirmations；
- blocking confirmation 未解决不得导出。

### 0.4.4 Artifact 编辑、重新生成和导出

```text
Artifact Card action
→ Artifact Route
→ Artifact Service
→ create new artifact_version
→ update current_version_id
→ Export Route
→ Export Service
→ workspace/exports
```

验收关注：

- 编辑和 regenerate 必须产生新版本；
- 旧版本不可覆盖；
- 导出只读取 current 或用户显式选择版本；
- 导出只写 workspace `exports/`。

### 0.4.5 Realtime 文本提示

```text
Text question
→ realtime.generate_hint
→ Prompt Contract
→ Safety boundary
→ structured hint
```

验收关注：

- P3 realtime 仍是 text-in / hint-out；
- formal_assist 不返回逐字代答；
- 不接入 ASR、系统音频、会议平台或视频解析。

## 0.5 数据所有权

| 数据 | 所有者 | 主要读者 | 关键不变量 |
| --- | --- | --- | --- |
| Workspace | Workspace Service | 所有后端服务 | 所有文件和导出必须在 workspace 内 |
| Chat Session / Message | Chat Service | Chatbox、ChatCore | 消息可恢复，不含 API Key |
| Document | File / Document Service | Profile、Project、Job tools | source refs 可追踪 |
| CareerFact / SkillEvidence | Profile Tools | Match、Application、Interview | 低置信事实必须待确认 |
| TechProject | Project Tools | Match、StoryCard、Interview | 项目描述必须有来源 |
| Job / MatchReport | Job Tools | Application、Workbench | must-have / nice-to-have / gaps 可解释 |
| ApplicationPackage | Application Tools | Export、Workbench | 导出前执行 confirmation preflight |
| StoryCard / InterviewPrep | Interview Tools | Realtime、Review | 不编造不存在项目 |
| Artifact / ArtifactVersion | Artifact Service | Workbench、Export | version 不覆盖，current 指向有效版本 |
| Export File | Export Service | User download | 只写 workspace/exports |
| ProviderInvocation | Provider Runtime | Audit / Debug | 只存摘要和错误，不存敏感原文 |

## 0.6 质量属性和架构验收

- 可维护性：前端只做展示和触发，业务逻辑在 Domain Tools；
- 可替换性：ChatCore 可在 Keyword 和 PiAgent 之间切换；
- 安全性：Provider Policy Gate 是外部调用唯一出口；
- 可追溯性：所有用户可见产物必须保留 source refs 或 artifact refs；
- 可恢复性：chat session、artifact 和 export 均可从 workspace 恢复；
- 可验收性：每条关键体验必须有测试或 Chrome 截图证据；
- 可扩展性：MCP/CLI/ASR 未来只能通过 API/Tool 层接入，不改变 P3 Chatbox-first 核心。

P3 目标架构按 6 个平面验收：

```text
体验壳层
  → 顶部状态、workspace 状态、provider 状态、示例/真实资料模式

对话平面
  → 消息流
  → 上传入口
  → JD / 申请包 / 面试准备自然语言意图
  → 可见响应、计划、执行状态、错误说明

推进台平面
  → 当前阶段
  → 待办和下一步
  → artifact 摘要、确认项、版本、导出
  → 不承载业务生成逻辑

编排平面
  → ChatCore Facade
  → PiAgentChatCore / KeywordChatCore
  → Real User Flow Controller
  → P2 Workflow Orchestrator

业务能力平面
  → profile / project / job / application / interview / realtime / training tools
  → Provider Policy Gate
  → Provider Runtime
  → Prompt Contract / Schema Validation
  → Artifact Versioning / Export Service

本地数据与验收平面
  → SQLite workspace
  → local files / exports
  → tool/provider invocation redaction
  → pytest eval
  → Chrome screenshots at desktop / narrow / mobile
  → HTML acceptance reports
```

当前完成状态：

- 绿色基线：P0/P1 工具链、Provider Runtime、Artifact Versioning、Export、PiAgent 编排、P2 Workflow Orchestrator、P2 HTML 报告；
- P3 正在完成：Chatbox 与推进台分离、真实用户输入响应、模式边界、响应式 UX、截图验收；
- P4+ 后续：MCP、CLI、ASR、会议平台、自动申请、SaaS。

P3 关键架构约束：

- Chatbox 前端不得复制业务生成逻辑，只能调用后端 chat/workflow/artifact/export API；
- 对话区负责输入和反馈，推进台负责状态和产物，二者必须视觉和职责分离；
- 真实资料模式默认仍使用本地 mock provider，外部 provider 必须显式 opt-in；
- provider 调用和个人资料处理必须经过安全边界，不能把 API Key、完整简历、完整 JD 或 transcript 写入日志；
- responsive layout 必须作为架构验收项，而不是事后美化；
- P3 自动验收可以使用 examples 真实感数据，真实个人资料只允许人工确认后进入验收。

P3 目标数据流：

```text
User action
→ Chatbox Conversation Plane
→ /api/chat/sessions/{id}/messages 或 /api/workflows/*
→ ChatCore Facade
→ PiAgent / Keyword intent plan
→ Real User Flow Controller
→ Domain Tools
→ Provider Policy Gate
→ Provider Runtime or Mock
→ Schema validation
→ Artifact Version / Export
→ Conversation response + Workbench state
→ Chrome screenshot evidence
```

以下 P2 架构内容作为已完成基线和历史背景保留。

## 1. 架构目标

P2 目标是在 P0/P1 已完成的本地优先、Chatbox-first、Agent Tool-first 架构上，新增 Experience Flow 层，把底层能力组合成完整端到端用户体验。

P2 架构必须满足：

- Chatbox 继续只负责输入、展示、确认、编辑、导出触发和体验流程展示；
- Experience Flow 只编排现有 Domain Tools，不复制业务生成逻辑；
- Pi Agent Core 继续负责 Chat Intent Router / Domain Tool Planner 层；
- Python JobPilot Domain Tools 继续负责真实业务执行、写库、artifact 和 workspace 边界；
- Provider 默认仍为 mock，本阶段不默认触发真实外部调用；
- OpenAI-compatible provider 仍是 opt-in；
- workflow 输出必须来自真实工具执行结果；
- artifact 编辑和 regenerate 仍版本化，不覆盖旧产物；
- 导出只读取 current/selected version，只写 workspace `exports/`；
- P2 不引入 MCP、CLI、ASR、会议平台或 SaaS。

## 2. 当前架构实现

P1 当前已实现：

```text
React Chatbox
  → FastAPI Agent Service
    → ChatCore Facade
      → KeywordChatCore fallback
      → PiAgentChatCore optional
        → Node Pi Agent Core
        → jobpilot_orchestrate AgentTool
    → Python Domain Tool Executor
    → Domain Tools
      → profile / project / job / application / interview / realtime / training
    → LLM Provider Runtime
      → MockProvider / FixtureProvider / OpenAI-compatible opt-in
    → Prompt Contract / Schema Validation
    → Artifact Versioning / Regenerate
    → Export Service
    → SQLite Workspace / files / exports
    → pytest eval gates / frontend build / Chrome screenshot evidence
```

P2 已开始实现：

- `services/workflows/p2_demo.py`；
- `POST /api/workflows/p2-demo/run`；
- Chatbox `端到端体验路径` 工作流面板；
- `?autorun=1` 本地可见验收入口；
- 人类可读 artifact 摘要；
- P2 guided demo flow eval。

当前差距：

- P2 HTML 最终验收报告尚未完成；
- 截图证据需要整理到最终报告；
- 用户上传真实资料的分步引导仍弱于 examples 一键路径；
- artifact 摘要仍是最小实现，后续可继续增强；
- drawio 需要从 P1 图切换到 P2 端到端体验架构图。

## 3. P2 目标架构总览

```text
Chatbox Client
  → Experience Flow Panel
    → step list
    → current state
    → next action
    → run examples demo flow
    → artifact summary
    → exports summary
  → Artifact Cards
    → human-readable summary
    → source refs
    → confirmations
    → versions
    → edit / regenerate / export

FastAPI Agent Service
  → Workspace / File / Chat routes
  → Provider routes
  → Artifact version routes
  → Application export routes
  → Workflow routes
    → POST /api/workflows/p2-demo/run

Workflow Orchestrator
  → load examples
  → save documents
  → extract facts
  → create project card
  → parse JD
  → match profile
  → create application package
  → export Markdown + DOCX
  → prepare interview
  → realtime text hint
  → review transcript
  → collect steps / artifacts / exports / summary

Domain Tool Executor
  → profile / project / job / application / interview / realtime / training
  → provider call boundary
  → schema validation boundary
  → artifact writer
  → tool_invocation logger

Provider Runtime
  → MockProvider default
  → FixtureProvider tests
  → OpenAI-compatible opt-in
  → redaction / input summary
  → timeout / retry / error mapping

Artifact / Export / Storage
  → artifact
  → artifact_version
  → regenerate lineage
  → export preflight
  → Markdown / DOCX
  → SQLite workspace
  → local files / exports

Eval / Evidence
  → pytest
  → frontend build
  → P2 guided flow eval
  → Chrome screenshots
  → P2 HTML acceptance report
```

## 4. 分层职责

| 层 | 职责 | 代码区域 |
| --- | --- | --- |
| Chatbox Client | 展示工作流、产物、版本、待确认项和导出入口 | `apps/chatbox/src/main.tsx`, `styles.css` |
| Experience Flow Panel | 展示步骤、下一步、执行结果、导出文件 | `apps/chatbox/src/main.tsx` |
| FastAPI Routes | 暴露 workflow、artifact、chat、export 等 HTTP API | `services/api/main.py`, `schemas.py` |
| Workflow Orchestrator | 串联 examples 和 Domain Tools，生成体验摘要 | `services/workflows/p2_demo.py` |
| ChatCore / Pi Agent Core | 自然语言 intent/tool plan 编排 | `services/chat/*`, `services/chat/pi_node_bridge.mjs` |
| Domain Tools | 执行真实求职业务、写库和产物 | `services/tools/jobpilot.py` |
| Provider Runtime | mock/fixture/openai-compatible 结构化生成边界 | `services/llm/provider.py`, `contracts.py` |
| Artifact Versioning | 记录 current version、edit、regenerate lineage | `services/storage/db.py`, `jobpilot.py` |
| Export Service | Markdown/DOCX 导出和 preflight | `services/tools/jobpilot.py` |
| Storage | SQLite workspace、本地 files/exports | `services/storage/*` |
| Evidence Gates | 测试、截图、HTML 报告和 PRD 检视 | `tests/evals`, `docs/reports` |

## 5. 控制流与数据流边界

```text
用户控制流：
Chatbox → Workflow Panel → FastAPI Workflow Route → Workflow Orchestrator

业务执行流：
Workflow Orchestrator → Domain Tools → Artifact / Business Tables → Export Service

模型生成流：
Domain Tools → Prompt Contract → Provider Runtime → schema validation → structured output

证据流：
Tests / Chrome screenshots → stage review → P2 HTML report → human review
```

关键边界：

- Chatbox 不拼业务 prompt；
- Workflow Orchestrator 不直接写数据库，只调用 Domain Tools；
- Provider Runtime 不直接写数据库；
- Domain Tools 是唯一业务写入边界；
- Export Service 只写 workspace `exports/`；
- screenshots 证明可见体验，不替代业务测试；
- examples 数据是匿名真实感数据，不等于真实个人资料验收。

## 6. 失败回滚边界

P2 workflow 失败时：

- 已完成步骤可以保留在 workspace 中；
- API 必须返回失败步骤和可理解错误；
- 不得删除用户已有 workspace；
- 不得覆盖旧 artifact version；
- 不得因为某一步失败而伪造后续完成状态；
- HTML 报告必须标注失败或未验收范围。

## 7. 后续扩展边界

以下进入 P4+ 或独立阶段：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台；
- 自动申请；
- SaaS 多租户；
- 默认真实外部 Provider；
- 岗位数据源抓取和 Offer 分析。
