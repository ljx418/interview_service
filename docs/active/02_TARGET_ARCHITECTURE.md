# JobPilot AI P3 目标架构深度设计

## 0. P3 当前阶段架构增补

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
