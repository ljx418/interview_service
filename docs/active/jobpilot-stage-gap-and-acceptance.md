# JobPilot AI P3 架构模块与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。

本轮图示弱化阶段关系，主线改为架构模块、功能角色、调用关系、数据所有权和验收边界。

## 图示页结构

P3 drawio 保持 5 页：

1. 系统上下文与目标模块图；
2. Chatbox 前端组件职责；
3. 后端编排与 Domain Tool 关系；
4. 数据、Artifact、Provider、Export 关系；
5. 安全边界、验收证据和状态标记。

颜色含义：

- 绿色：已完成 / P0+P1+P2 基线；
- 黄色：P3 正在完善；
- 灰色：P4+ 后续能力；
- 红色：高风险人工确认或禁止路径。

## 第 1 页 - 系统上下文与目标模块图

目标架构主链路：

```text
User
→ Chatbox Client
→ FastAPI Agent Service
→ ChatCore Facade
→ Flow Orchestration
→ Domain Tool Layer
→ Provider and Contract Layer
→ Artifact and Storage Layer
→ Evidence Layer
```

模块角色：

- Chatbox Client：只做输入、展示、确认、编辑和导出触发；
- FastAPI Agent Service：HTTP 边界、请求校验、错误码、workspace 边界；
- ChatCore Facade：隔离 KeywordChatCore / PiAgentChatCore；
- Flow Orchestration：把用户意图转成工具计划；
- Domain Tool Layer：执行求职业务能力；
- Provider and Contract Layer：外部调用、安全策略、prompt contract、schema validation；
- Artifact and Storage Layer：版本、确认项、导出、本地持久化；
- Evidence Layer：测试、截图、HTML 报告。

禁止路径：

- Chatbox 直接调用 Provider；
- Chatbox 直接写 SQLite；
- PiAgent 直接写 SQLite；
- Provider raw output 直接导出；
- Workflow 失败后伪造完成。

## 第 2 页 - Chatbox 前端组件职责

前端组件边界：

```text
Experience Shell
→ Mode / Provider Status
→ Conversation View
→ Composer / Upload Entry
→ Workbench Panel
→ Artifact Cards
→ Export Actions
```

职责：

- Experience Shell：展示 workspace、provider、示例/真实资料模式；
- Conversation View：展示消息、计划、结果、错误；
- Composer / Upload Entry：输入文本、上传资料、触发发送；
- Workbench Panel：展示阶段、下一步、产物、确认项、版本和导出；
- Artifact Cards：管理单个产物摘要、source refs、确认项、版本操作；
- Export Actions：只触发后端 export preflight。

P3 修正重点：

- Chatbox 与推进台职责分离；
- 有效输入必须有可见响应；
- 错误必须可理解；
- 720px / 390px 下不能截断关键操作。

## 第 3 页 - 后端编排与 Domain Tool 关系

后端调用链：

```text
Chat Routes / Workflow Routes
→ ChatCore Facade
→ KeywordChatCore or PiAgentChatCore
→ Real User Flow Controller
→ Domain Tool Executor
→ Domain Tools
```

Domain Tools：

- profile：extract_facts、skill evidence；
- project：create_card；
- job：parse_jd、match_profile；
- application：create_package；
- interview：prepare、story cards；
- realtime：generate_hint；
- review/training：review transcript、training tasks。

关键规则：

- ChatCore 只产出 intent / tool plan；
- Python Domain Tools 才能写业务数据；
- Workflow Orchestrator 只能编排工具，不复制工具逻辑；
- 每次工具调用需要 tool invocation 记录和脱敏摘要；
- 失败必须返回失败步骤和错误码，不得继续标绿。

## 第 4 页 - 数据、Artifact、Provider、Export 关系

数据所有权：

```text
Workspace
→ Chat Session / Message
→ Document
→ CareerFact / SkillEvidence / TechProject
→ Job / MatchReport
→ ApplicationPackage / InterviewPrep / Review
→ Artifact / ArtifactVersion
→ Export File
→ ProviderInvocation
```

关系：

- Document 是 source refs 的根；
- Domain Tools 生成领域对象；
- Artifact Service 包装可展示、可确认、可版本化的产物；
- ArtifactVersion 保存 content_json / content_path、source_refs、questions_to_confirm；
- Export Service 只读取 current 或显式选择版本；
- ProviderInvocation 只保存摘要、状态、延迟和错误，不保存敏感原文。

关键不变量：

- source refs 不得丢失；
- questions_to_confirm 不得静默删除；
- edit / regenerate 必须生成新版本；
- blocking confirmation 未解决不得导出；
- export 只写 workspace `exports/`；
- API Key、完整简历、完整 JD、完整 transcript、完整 raw response 不得入库或入日志。

## 第 5 页 - 安全边界、验收证据和状态标记

安全边界：

- Provider Policy Gate 是外部调用唯一出口；
- mock provider 是默认模式；
- external provider 必须 opt-in；
- 真实个人资料和真实外部调用必须人工确认；
- realtime 仍是 text-in / hint-out，不做 ASR 或会议平台。

验收证据：

- `python3 -m pytest`；
- `npm --prefix apps/chatbox run build`；
- Chrome 1280px / 720px / 390px 截图；
- P3 HTML 验收报告；
- PRD 规格检视；
- drawio XML parse；
- README/TODO/active docs 口径一致。

状态标记：

- 绿色：P0/P1/P2 已完成模块；
- 黄色：P3 正在完善的 Chatbox、模式边界、响应式 UX、截图验收；
- 灰色：MCP、CLI、ASR、会议平台、自动海投、SaaS、岗位数据源、Offer 分析；
- 红色：必须人工确认或禁止绕过的路径。
