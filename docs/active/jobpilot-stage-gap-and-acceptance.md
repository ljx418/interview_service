# JobPilot AI P6-REAL / P7-post 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。当前图示主线是 P6-REAL 真实 provider 受控验收准备与 P7-post P5-REAL 真实资料复验准备。P5.5 Candidate Profile、P6 fake provider 长程对话和 P7 本地 Beta 能力均作为自动化候选基线保留。

任何真实 API Key、真实个人资料、真实外部 provider 调用、workspace 删除、不可逆迁移、敏感属性分析、ASR/会议平台/自动投递/SaaS 操作都必须先获得用户确认。当前图示不代表这些高风险路径已经执行或通过。

## 图示页结构

drawio 保持 6 页，不超过 8 页：

1. 目标体验与当前差距；
2. 当前架构与目标架构；
3. 代码实体与交互关系；
4. 开发及验收计划；
5. 里程碑门槛与出门条件；
6. 安全边界证据与复验。

颜色含义：

- 绿色：已实现自动化候选，包括 P4/P5/P5.5/P6/P7 本地、mock、fake provider、synthetic-style workspace 或 dry-run 证据；
- 黄色：当前阶段待真实验收或文档准入项，包括 P6-REAL provider 调用和 P7-post P5-REAL 资料复验；
- 红色：高风险需用户确认或虚假验收打回项；
- 灰色：P8+ 后续独立阶段；
- 蓝色：目标体验、目标架构或用户可见结果。

## 第 1 页 - 目标体验与当前差距

目标体验主链路：

```text
User
→ 打开 Chatbox 和验收文档
→ 看清已完成自动化候选：P5.5 画像、P6 fake provider 多轮对话、P7 本地 Beta dry-run
→ 选择是否进入 P6-REAL 真实 provider 小样本验收
→ 明确 provider、model、调用次数、预算、数据类别和报告展示字段
→ 选择是否进入 P7-post P5-REAL 真实资料复验
→ 明确简历、项目资料、JD 路径和脱敏展示字段
→ 生成真实验收报告时明确区分 fake provider / synthetic personas / 真实 provider / 真实资料
```

当前差距：

- P5.5 Candidate Profile 已完成自动化候选，但不代表真实个人资料路径通过；
- P6 fake provider 长程对话已完成自动化候选，但不代表真实 LLM 质量通过；
- P7 workspace lifecycle、diagnostics 和 dry-run 已完成自动化候选，但不代表删除或迁移 apply 已执行；
- 真实 provider 和真实资料复验需要授权执行单、脱敏报告模板和打回条件；
- SaaS、ASR、会议平台、自动投递、MCP/CLI 属于 P8+ 或独立高风险阶段。

## 第 2 页 - 当前架构与目标架构

当前已实现自动化候选基线：

```text
React Chatbox
→ FastAPI Agent Service
→ ChatCore / Provider-backed fake adapter
→ Long Context Manager
→ Candidate Profile Aggregator
→ Domain Tools
→ Artifact Versioning / Export Guard
→ SQLite Workspace
→ Workspace lifecycle dry-run / Diagnostics
→ P5.5 / P6 / P7 Reports
```

P6-REAL / P7-post 目标补齐：

```text
P6-REAL Provider Acceptance
→ Provider Consent UI
→ Provider Policy Gate
→ Real provider runtime
→ Redacted Provider Invocation Log
→ Controlled real-provider HTML report

P7-post P5-REAL Revalidation
→ User-authorized source paths
→ Real-data acceptance runner
→ Profile / Project / Job / Match tools
→ Redacted source refs and screenshots
→ P5 closure audit
```

架构关系：

- Chatbox 只展示 provider 状态、确认边界、对话和 Workbench，不保存 API Key；
- FastAPI 负责 provider status、preferences、consent、chat 和 workspace 边界；
- Provider Policy Gate 负责未授权外呼、API Key、本地环境、数据类别、预算和失败降级检查；
- Long Context Manager 负责近期消息、rolling summary、workspace snapshot 和 source refs；
- Real-data acceptance runner 只读取用户指定路径；
- Evidence Layer 负责脱敏报告、截图、PRD 检视和虚假验收扫描。

## 第 3 页 - 代码实体与交互关系

必须在图中出现的具体代码实体：

- `apps/chatbox/src/main.tsx`：模型设置、provider consent、长程对话状态、Candidate Profile Workbench、workspace lifecycle 入口；
- `apps/chatbox/src/styles.css`：多视口布局、状态机、按钮对齐、证据面板和风险标签；
- `services/api/main.py`：provider status/preferences/consent、chat、profile、workspace lifecycle、diagnostics 路由；
- `services/api/schemas.py`：provider consent、chat response、profile、diagnostics 和 workspace lifecycle schema；
- `services/chat/core.py`：意图路由、本地 fallback、普通聊天不写 artifact、工具确认边界；
- `services/chat/context.py`：recent message window、rolling summary、workspace context snapshot、retrieved context block；
- `services/chat/provider_backed.py`：fake provider / real provider adapter、timeout、retry、schema validation、fallback；
- `services/llm/`：provider runtime、OpenAI-compatible/MiniMax/DeepSeek 类配置边界；
- `services/profile/candidate.py`：CandidateProfile、能力矩阵、项目可信度、岗位短板；
- `services/workspace_lifecycle.py` 或等价模块：backup/export/cleanup dry-run/migration dry-run；
- `scripts/generate_p5_real_data_acceptance.py`：P7-post P5-REAL 真实资料复验入口；
- `docs/reports/` 与 `docs/reports/evidence/`：中文 HTML 报告、截图、transcript 和审计证据。

禁止关系：

- 配置 provider 被写成已调用；
- fake provider transcript 被写成真实 LLM 质量证据；
- synthetic personas、examples 或脱敏 fixture 被写成真实个人资料验收；
- 未授权读取用户个人目录；
- API Key、完整 prompt、完整真实资料、完整 provider raw response 进入报告或日志；
- workspace 删除、cleanup apply、migration apply 默认执行；
- 普通聊天绕过 `questions_to_confirm`、artifact confirmation 或 export preflight。

## 第 4 页 - 开发及验收计划

当前文档阶段执行顺序：

```text
REAL-DOC-M0 文档口径修复
→ P6-REAL-M1 真实 provider 受控验收计划
→ P6-REAL-M2 真实 provider 小样本验收门槛和报告模板
→ P7POST-P5REAL-M1 真实资料授权和脱敏复验计划
→ FINAL-DOC-M1 drawio / 验收门槛 / 审计收口
```

后续执行阶段必须先获得用户确认：

```text
P6-REAL execution
→ 读取本地 `.env` 中用户配置的 provider API Key
→ 按最大调用次数执行小样本真实 provider 对话
→ 生成脱敏真实 provider 验收报告

P7-post P5-REAL execution
→ 读取用户明确提供的简历、项目资料和 JD 路径
→ 执行真实资料本地闭环复验
→ 生成脱敏 P5-REAL 报告和 closure audit
```

## 第 5 页 - 里程碑门槛与出门条件

当前文档阶段出门条件：

1. 文档状态口径一致：已实现自动化候选、待真实验收、后续独立阶段不混淆；
2. P6-REAL 外呼执行单完整：provider、model、API Key 本地配置、调用次数、预算、数据类别、timeout/retry/fallback 和报告展示字段齐全；
3. P7-post P5-REAL 执行单完整：真实资料路径、允许展示字段、禁止展示字段和脱敏策略齐全；
4. drawio 不超过 8 页，图中条目是具体代码实体、数据表、路由、脚本或报告；
5. 审计记录明确本轮只做文档开发，未真实外呼、未读取真实资料、未实现代码。

后续 P6-REAL 执行出门体验：

```text
用户知道当前是否外呼
→ 配置 provider 不等于调用 provider
→ 真实调用前确认数据范围和费用边界
→ 真实 provider 成功或失败都有脱敏 invocation log
→ 失败可降级到本地连续对话
```

后续 P7-post P5-REAL 执行出门体验：

```text
用户指定资料路径
→ 系统只读指定路径
→ 资料解析、画像、匹配、申请包和导出 preflight 可复验
→ 报告默认脱敏
→ 若未授权真实资料则保持未执行
```

## 第 6 页 - 安全边界证据与复验

当前证据包：

- P5.5 中文 HTML 自动化验收报告；
- 多身份合成资料与 20 轮 fake provider 连续对话 transcript；
- P6/P7 本地 Beta 自动化候选报告；
- 桌面、宽屏、移动端真实界面截图；
- pytest、frontend build、drawio XML parse；
- PRD 规格检视、隐私审计和虚假验收风险清单。

需要明确保留的未验证范围：

- 真实 MiniMax、DeepSeek、OpenAI-compatible 或其他 provider 质量；
- 真实 API Key 配置后的外呼路径；
- 用户真实个人资料路径；
- workspace 删除、cleanup apply、migration apply；
- SaaS、ASR、会议平台、自动投递、多租户、Billing、MCP/CLI。

高风险边界：

- 真实 provider 必须 opt-in；
- 真实个人资料必须用户授权；
- API Key 不得进入仓库、报告、日志或截图；
- 自动化截图、焦点抢占或弹窗前必须告知用户；
- 文档通过不等于实现通过，drawio 方向认可不等于功能验收通过。
