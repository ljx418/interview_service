# P10-CLI 文档开发审计

状态：通过，限文档开发阶段。本文档不代表 CLI 代码已经实现。

## 1. 审计背景

P9.1 本地自动化候选已完成，P9+ 剩余准入审计列出真实 provider、真实资料、MCP、CLI、ASR、会议平台、自动投递、真实市场 provider 等未完成项。当前没有任何剩余项能在缺少专项文档时直接进入自动化实现。

本轮用户批准的是文档开发：将当前认可的开发目标制定为 PRD、目标架构、里程碑、验收门槛、drawio gap 和出门条件。根据 P9+ 审计建议，本轮选择最低风险的 **P10-CLI 本地命令入口** 作为当前阶段目标。

## 2. 已落盘文档

| 文档 | 作用 | 状态 |
| --- | --- | --- |
| `README.md` | 当前阶段入口和边界 | 已更新为 P10-CLI 文档开发阶段 |
| `TODO.md` | 当前 TODO 与后续 P10-CLI-M0 到 M5 | 已更新 |
| `docs/active/00_README.md` | active 阅读顺序和当前目标 | 已更新 |
| `docs/active/01_STAGE_PRD.md` | P10-CLI PRD、命令体验和非目标 | 已更新 |
| `docs/active/02_TARGET_ARCHITECTURE.md` | CLI 目标架构、实体状态和调用关系 | 已更新 |
| `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md` | 文档阶段和后续实现阶段计划 | 已更新 |
| `docs/active/04_ACCEPTANCE_GATES.md` | 文档门槛、实现门槛和打回条件 | 已更新 |
| `docs/active/06_TRACEABILITY_MATRIX.md` | 目标、实体、证据和门槛追踪 | 已更新 |
| `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md` | 产品化路线和 P10-CLI 位置 | 已更新 |
| `docs/active/25_P10_CLI_LOCAL_COMMAND_ENTRY_PLAN.md` | P10-CLI 专项计划 | 已新增 |
| `docs/active/jobpilot-p10-cli-local-entry-gap.md` | drawio 文本镜像 | 已新增 |
| `docs/active/jobpilot-p10-cli-local-entry-gap.drawio` | P10-CLI gap 图 | 已更新为 8 页，不超过 8 页；新增 API 契约与工作流树 |

## 3. 文档开发结论

P10-CLI 当前阶段目标清楚：

```text
本地命令入口
→ 包装现有 FastAPI / examples / fixture / workspace / artifact / report 能力
→ 输出中文、可选 JSON、稳定 exit code
→ 默认不外呼、不抓取、不读取真实资料、不做不可逆操作
```

P10-CLI 不允许在本阶段默认覆盖：

- MCP server wrapper；
- 真实 MiniMax / DeepSeek / OpenAI-compatible provider；
- 真实市场 provider；
- 真实个人资料路径；
- BOSS、猎聘、拉勾、LinkedIn 等招聘平台；
- ASR、麦克风、会议平台；
- 自动投递、自动沟通；
- workspace 删除、cleanup apply、migration apply；
- SaaS、多租户、Billing。

## 4. 架构审计

目标架构使用具体代码实体，而不是抽象功能词：

```text
JobPilotCLI
→ CLICommandRouter
→ CLIConfigResolver
→ WorkspaceSelector
→ CommandSafetyGate
→ ApiClient
→ OutputRenderer
→ ExitCodePolicy
→ CommandAuditLog
→ Existing FastAPI Agent Service
→ Existing Domain Tools
→ Existing SQLite Workspace / Artifact / Evidence
```

实体状态：

- 已实现复用：FastAPI Agent Service、Domain Tools、SQLite Workspace、Artifact、reports；
- 待新增：CLI 入口、router、config resolver、workspace selector、safety gate、API client、renderer、exit code、audit log；
- 需适配：部分 status/report/demo API 汇总能力；
- 高风险禁止：真实 provider、真实资料、平台抓取、ASR、自动投递、不可逆 workspace 操作。

## 5. 验收审计

当前文档已要求后续 P10-CLI 实现阶段至少覆盖：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
drawio XML parse for docs/active/jobpilot-p10-cli-local-entry-gap.drawio
jobpilot --help
jobpilot workspace status
jobpilot demo run --example
jobpilot jobs list
jobpilot artifacts list
jobpilot reports open --no-browser
P10-CLI Chinese HTML acceptance report
```

报告必须说明：

- 哪些 CLI 命令真实可运行；
- 哪些结果来自 examples / fixture / local workspace；
- 是否调用真实 provider，默认必须为否；
- 是否读取真实个人资料，默认必须为否；
- 是否接入招聘平台、ASR、MCP、自动投递，默认必须为否。

## 6. 待完成项

本轮文档开发完成后，下一步不能直接跳到 P10-CLI-M1。必须先执行：

```text
P10-CLI-M0：开发前启动审计
```

M0 需要复核 PRD、目标架构、drawio、验收门槛和 false-green 边界，确认没有把 MCP、真实 provider、真实资料、平台接入、ASR 或自动投递混入默认路径。

## 7. 审计结论

结论：P10-CLI 文档开发方向通过。当前已补齐 drawio、文本镜像和覆盖度复审；后续如进入实际开发，必须先执行 P10-CLI-M0 开发前启动审计。

不得声明：

- CLI 命令已经实现；
- MCP server 已实现；
- 真实 provider 或真实市场 provider 已通过；
- 真实个人资料路径已通过；
- 招聘平台抓取、ASR、会议平台、自动投递或 SaaS 已通过。
