# JobPilot AI P6+P7 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。P4 已作为本地/mock Chatbox 体验冻结基线保留；P5 本地/mock + 脱敏 fixture 自动化候选证据保留为后续基线；P5-REAL/P5-Freeze 已冻结延期到 P7 完成后复验。当前图示主线是 P6 真实 provider opt-in、长程连续对话和 P7 产品化 Beta。

任何真实 API Key、真实个人资料、真实外部 provider 调用、workspace 删除、不可逆迁移、ASR/会议平台/自动投递/SaaS 操作都必须先获得用户确认。

## 图示页结构

drawio 保持 6 页，不超过 8 页：

1. P6+P7 目标体验与当前差距；
2. 当前架构与 P6+P7 目标架构；
3. 代码实体、分层结构与交互关系；
4. P6+P7 开发及验收计划；
5. 项目里程碑、验收门槛与出门条件；
6. 安全边界、证据、状态标记和 P7-post 复验。

颜色含义：

- 绿色：已实现并冻结或作为基线保留，包括 P0/P1/P2/P3/P4 本地/mock 基线、P5 自动化候选证据；
- 蓝色：当前 P6+P7 计划开发能力；
- 黄色：需修改或复验的既有能力；
- 橙色：需要用户确认的高风险流程，例如真实 provider、真实资料、workspace 删除、不可逆迁移；
- 灰色：P8+ 后续能力；
- 红色：禁止路径、打回条件或虚假验收风险。

## 第 1 页 - P6+P7 目标体验与当前差距

目标体验主链路：

```text
User
→ 本地 Chatbox
→ 默认 local/mock，不外呼
→ 模型设置和 provider opt-in
→ 调用前确认
→ provider-backed 自由聊天
→ Long Context Manager 维护 20-50 轮连续对话
→ provider 失败降级本地对话
→ P7 workspace 生命周期、诊断、发布/回滚和支持流程
→ P7-post P5-REAL/P5-Freeze 复验
```

当前差距：

- P4 已完成本地/mock Chatbox 体验冻结；
- P5 自动化候选已完成，但 P5-REAL/P5-Freeze 冻结延期复验；
- P6 仍缺 provider opt-in UX、真实 provider chat adapter、Long Context Manager、invocation log 脱敏和失败降级证据；
- P7 仍缺 workspace lifecycle、diagnostics、release/rollback、support runbook 和 Beta 验收报告；
- P8+ SaaS、ASR、会议平台、自动投递、MCP/CLI 不属于本阶段。

## 第 2 页 - 当前架构与 P6+P7 目标架构

当前已实现基线：

```text
React Chatbox
→ FastAPI Agent Service
→ ChatCore / PiAgent Adapter
→ Domain Tools
→ Artifact Versioning
→ Export Service
→ SQLite Workspace
→ P4/P5 Evidence
```

P6+P7 目标新增或改造：

```text
Model Settings / Provider Consent UI
→ Provider Status / Consent Routes
→ Provider Policy Gate
→ Provider-backed Dialogue Adapter
→ Long Context Manager
→ Local Fallback Dialogue
→ Provider Invocation Log
→ Workspace Lifecycle Service
→ Diagnostics Report Service
→ P6/P7 Visual Acceptance Reports
→ P7-post P5 Revalidation
```

架构关系：

- Chatbox 只做输入、展示、确认、编辑、导出和模型设置触发；
- FastAPI 负责请求边界、provider consent/status、workspace lifecycle 和 diagnostics 路由；
- ChatCore/Chat Orchestrator 负责自由聊天、澄清、状态查询、工具意图和 provider-backed 回复选择；
- Long Context Manager 负责 recent window、rolling summary、workspace snapshot 和相关 artifact/JD/profile 检索；
- Provider Policy Gate 负责默认拒绝未授权外呼；
- Artifact/Export/Storage 继续负责版本、确认项、导出和本地持久化；
- Diagnostics/Evidence 负责脱敏报告和验收证据。

## 第 3 页 - 代码实体、分层结构与交互关系

必须在图中出现的具体代码实体：

- `apps/chatbox/src/main.tsx`：Experience Shell、Conversation Plane、Workbench、Model Settings、Provider Consent、Workspace Lifecycle UI；
- `apps/chatbox/src/styles.css`：多视口布局、模型设置弹窗、长对话状态、生命周期入口、按钮对齐和移动端可达性；
- `services/api/main.py`：workspace、upload、chat、workflow、artifact、export、provider status/consent、diagnostics API 边界；
- `services/chat/core.py`：Intent Router、Local Fallback Dialogue、provider-backed reply selection、tool safety；
- `services/chat/context.py` 或等价模块：Long Context Manager，包含 recent window、rolling summary、workspace context snapshot、retrieved context blocks；
- `services/llm/`：OpenAI-compatible/MiniMax/DeepSeek provider adapter、timeout、retry、schema validation、redaction；
- provider runtime/policy 模块：Provider Policy Gate，检查 consent、API Key、脱敏、预算、失败降级；
- tool/provider invocation storage：Provider Invocation Log，只记录脱敏元数据；
- workspace storage/lifecycle 模块：backup、export、cleanup dry-run、migration dry-run；
- diagnostics/report 模块：脱敏诊断报告和安全扫描；
- `docs/reports/` 与截图脚本：P6/P7 HTML 验收报告、真实界面截图和 PRD 规格检视。

禁止关系：

- Chatbox 直接保存 API Key 或直连 provider；
- provider configured 被写成 provider called；
- 未确认真实外呼；
- provider raw response 未校验直接写 artifact；
- 普通聊天写 artifact；
- Export Service 绕过 blocking confirmation；
- diagnostics/report 写入完整真实资料、API Key 或 provider raw response；
- workspace cleanup/migration apply 默认执行。

## 第 4 页 - P6+P7 开发及验收计划

执行顺序：

```text
P6P7-DOC-M0 文档 / drawio / 风险边界锁定
→ P6P7-DOC-M0-SPEC Provider Policy Gate / Long Context / Invocation Log / P7 lifecycle 执行细则
→ P6-M0 启动审计和详细开发计划
→ P6-M1 Provider opt-in UX 与模型设置
→ P6-M2 Provider-backed Chat Adapter
→ P6-M3 Long Context Manager
→ P6-M4 Tool Safety 与 Artifact/Export Guard 复验
→ P6-M5 Privacy / Redaction / Invocation Log
→ P6-M6 Visual Acceptance 与 P6-Freeze
→ P7-M0 Beta 启动审计
→ P7-M1 Workspace Lifecycle
→ P7-M2 Diagnostics / Release / Rollback
→ P7-M3 Beta Support / Privacy Audit / P7-Freeze
→ P7-post P5-REAL/P5-Freeze 复验
```

每个子阶段必须先写验收标准和开发计划，再进入实质开发；完成后必须有端到端验收、PRD 规格检视和打回条件检查。

2026-06-29 复审后，P6-M0/P7-M0 的开发前细则已集中补入 `19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md` 第 9 节，包括 provider 状态机、外呼确认 UX、long context 持久化模型、invocation log schema、P6 子阶段验收 checklist、P7 子阶段验收 checklist 和高风险打回条件。后续无需继续扩大主文档，但每个实质开发子阶段仍必须生成短启动审计。

## 第 5 页 - 项目里程碑、验收门槛与出门条件

P6 门槛：

1. P0-P5 本地基线不退化；
2. Provider opt-in 默认安全；
3. Provider-backed chat 可控且可降级；
4. 长程连续对话 20-50 轮成立；
5. Tool Safety 和产物边界不被 provider 绕过；
6. 隐私、日志和报告脱敏；
7. P6 可视化验收证据完整。

P7 门槛：

1. Workspace 生命周期可用；
2. 诊断、发布、部署和回滚可复现；
3. Beta 使用说明、支持流程和隐私审计完整；
4. P7 报告不声称 SaaS、ASR、会议平台、自动投递或真实个人资料默认路径通过。

P7-post P5 复验门槛：

- 用户明确提供真实/脱敏资料路径和允许展示字段；
- 只读取用户指定路径；
- 报告和截图默认脱敏；
- 不能用 synthetic personas、examples 或脱敏 fixture 替代。

最终出门体验：

```text
本地 Chatbox 可用
→ 真实 provider 仅 opt-in 调用
→ 长程连续对话可恢复、可降级、可解释上下文
→ provider-backed chat 不绕过产物确认和导出门槛
→ workspace 生命周期、诊断、发布/回滚和支持流程具备 Beta 证据
→ P7 完成后执行 P5-REAL/P5-Freeze 复验
```

## 第 6 页 - 安全边界、状态标记、证据和 P7-post 复验

证据包：

- P6/P7 中文 HTML 自动化验收报告；
- 1200/1440/1600/1920/720/390 多视口真实界面截图；
- 默认不外呼、模型设置、调用前确认、provider-backed 回复、长对话摘要、刷新恢复、失败降级、tool safety、workspace lifecycle、diagnostics、release/rollback 截图；
- pytest、frontend build、drawio XML parse；
- PRD 规格检视、隐私审计和虚假验收风险清单。

高风险边界：

- 真实 provider 必须 opt-in；
- API Key 不得进入仓库、报告、日志或截图；
- 真实个人资料必须用户授权；
- 自动化报告必须脱敏；
- workspace 删除和迁移 apply 默认不执行；
- ASR、会议平台、自动投递、SaaS、多租户、Billing、MCP/CLI 不是本阶段出门条件；
- 文档通过不等于实现通过，drawio 方向认可不等于功能验收通过。
