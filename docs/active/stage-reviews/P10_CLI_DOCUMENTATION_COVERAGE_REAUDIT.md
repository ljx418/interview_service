# P10-CLI 文档覆盖度复审

状态：通过，限文档开发阶段。本文档判断当前 P10-CLI 文档是否足以支撑后续 P10-CLI-M0 到 M5 自动化开发；不代表 CLI 已经实现。

## 1. 复审结论

```text
P10-CLI PRD：通过
P10-CLI 目标架构：通过
P10-CLI 命令契约：通过
P10-CLI 里程碑：通过
P10-CLI 验收门槛：通过
P10-CLI 追踪矩阵：通过
P10-CLI drawio / 文本镜像：通过
是否可以进入代码开发：不能直接进入，必须先执行 P10-CLI-M0 开发前启动审计
是否允许声明 CLI 已实现：不允许
```

当前文档已经能支撑 **P10-CLI 自动化开发启动** 和 P10-CLI-M0 到 M5 的阶段化实现，但不能表述为“完整支撑整个 JobPilot 下一阶段产品化开发”。文档覆盖度通过之后，只能进入 P10-CLI-M0 开发前启动审计；M0 通过后才允许进入 P10-CLI-M1 实质实现。

## 2. PRD 覆盖

PRD 已明确 P10-CLI 目标体验：

```text
jobpilot --help
→ workspace status
→ demo run --example
→ jobs list
→ artifacts list/show
→ reports open
```

PRD 覆盖了人类、本地 Agent、Codex CLI、ClaudeCode CLI 等目标用户，说明 CLI 只包装现有本地 API、examples/fixture、workspace、artifact 和 report 能力。PRD 同时列出非目标，防止 CLI 误扩张为 MCP server、真实 provider、真实资料读取、招聘平台抓取、真实市场 provider、ASR、会议平台、自动投递或 SaaS。

判断：PRD 足以指导 P10-CLI-M0 到 M5。

## 3. 目标架构覆盖

目标架构使用具体代码实体：

```text
JobPilotCLI
CLICommandRouter
CLIConfigResolver
WorkspaceSelector
CommandSafetyGate
ApiClient
OutputRenderer
ExitCodePolicy
CommandAuditLog
Existing FastAPI Agent Service
Existing Domain Tools
Existing SQLite Workspace / Artifact / Evidence
```

每个实体都写明状态、职责、上游和下游。架构明确 CLI 不直接写 SQLite、不直连真实 provider、不绕过 Provider Policy Gate、不扫描个人目录、不抓取招聘平台、不执行不可逆 workspace 操作。

本轮按 Software Architect / Backend Architect / Workflow Architect 口径补齐了更细粒度的工程契约：

- 端口与适配器分层：CLI Presentation、CLI Application、CLI Adapter、Existing Boundary；
- API 映射：`workspace status`、`demo run --example`、`jobs list`、`artifacts list/show`、`reports open --no-browser` 到当前 FastAPI / 本地报告目录的映射；
- 输出 envelope：统一 success / failure JSON 结构；
- exit code：0、1、2、3、4、5、10 的稳定语义；
- 工作流树：`workspace status`、`demo run --example`、`artifacts show <id>`；
- handoff contract：router、handler、safety gate、API client、renderer、audit log 之间的输入输出和失败处理。
- 外部审计意见要求 M0 冻结的三项工程边界：FastAPI 不自动启动、`reports open` 不生成报告、workspace 解析优先级固定为 `--workspace` > `JOBPILOT_WORKSPACE` > 当前目录 `.jobpilot_workspace` > 失败。

判断：目标架构已经从“实体清单”升级为“可实现契约”，足以支撑工程实现，不需要继续扩写主架构文档。

## 4. 里程碑和验收覆盖

文档已拆分：

- P10-CLI-DOC-M0 到 M3：文档开发、drawio、审计和 false-green 扫描；
- P10-CLI-M0：开发前启动审计；
- P10-CLI-M1：CLI 框架和 help；
- P10-CLI-M2：workspace status 和 safety gate；
- P10-CLI-M3：demo/jobs/artifacts/reports；
- P10-CLI-M4：Agent-friendly 输出和错误码；
- P10-CLI-M5：中文验收报告和回归。

验收命令也已明确：

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

判断：后续开发和验收颗粒度足够，不需要继续文档拆分。

## 5. drawio 覆盖

drawio 为 8 页，不超过 8 页：

1. P10-CLI 目标体验与阶段边界；
2. 当前架构与 P10-CLI 差距；
3. 目标架构与代码实体状态；
4. CLI 命令流与数据流；
5. 开发计划、里程碑和验收门槛；
6. 出门条件、false-green 边界和后续路线；
7. API 契约与适配缺口；
8. 工作流树、输出 envelope 和错误码。

图中使用状态颜色：

- 绿色：已实现复用；
- 蓝色：P10-CLI 待新增；
- 黄色：需适配或后续补充；
- 红色：高风险或禁止默认实现；
- 灰色：审计证据或边界说明。

判断：drawio 可以让人类快速理解目标体验、目标架构、代码实体状态、命令到接口映射、工作流树、输出契约、开发计划和出门条件。

## 6. 主要风险和闭环

| 风险 | 当前闭环 |
| --- | --- |
| 把 CLI 文档写成 CLI 已实现 | README、TODO、PRD、审计均明确当前仅文档阶段 |
| CLI 扩张成 MCP server | 非目标和红色高风险边界明确禁止 |
| CLI 默认真实 provider 外呼 | `CommandSafetyGate` 和验收门槛要求默认不外呼 |
| CLI 读取真实资料 | `WorkspaceSelector` 只允许默认 workspace 或用户显式路径，不扫描个人目录 |
| CLI 抓取招聘平台 | 明确不读取 `source_url` 网页，不登录平台 |
| CLI 执行不可逆操作 | 明确禁止 workspace 删除、cleanup apply、migration apply |
| CLI 生命周期膨胀为后台服务管理 | M0 冻结 P10-CLI v1 不自动启动 FastAPI，只提示启动命令 |
| `reports open` 膨胀为报告生成 | M0 冻结该命令只定位/打开已有报告，不生成或修复报告 |
| workspace 隐式解析造成误读资料 | M0 冻结解析优先级，禁止扫描用户目录和历史 workspace |
| 验收报告虚假全绿 | P10-CLI-M5 要求逐项说明命令真实可运行范围和未验证能力 |

## 7. 可交给 ChatGPT 审计的文档路径

建议审计文件数：14，少于 20。

```text
README.md
TODO.md
docs/active/00_README.md
docs/active/01_STAGE_PRD.md
docs/active/02_TARGET_ARCHITECTURE.md
docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md
docs/active/04_ACCEPTANCE_GATES.md
docs/active/06_TRACEABILITY_MATRIX.md
docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md
docs/active/25_P10_CLI_LOCAL_COMMAND_ENTRY_PLAN.md
docs/active/jobpilot-p10-cli-local-entry-gap.md
docs/active/jobpilot-p10-cli-local-entry-gap.drawio
docs/active/stage-reviews/P10_CLI_DOCUMENTATION_DEVELOPMENT_AUDIT.md
docs/active/stage-reviews/P10_CLI_DOCUMENTATION_COVERAGE_REAUDIT.md
```

## 8. 最终复审意见

结论：当前文档已经支撑 P10-CLI 本阶段后续自动化开发启动和 M0-M5 顺序实现。可以在用户批准代码开发后进入 **P10-CLI-M0 开发前启动审计**。

但仍不允许声明：

- CLI 命令已实现；
- CLI 已完成自动化验收；
- 当前文档完整支撑整个 JobPilot 产品化阶段开发；
- MCP server 已实现；
- 真实 provider、真实市场 provider、真实个人资料、招聘平台抓取、ASR、会议平台、自动投递或 SaaS 已通过。

## 9. 风险闭环复核记录

复核日期：2026-07-09。

本轮风险闭环复核检查了：

```bash
drawio XML parse for docs/active/jobpilot-p10-cli-local-entry-gap.drawio
rg "P10-CLI|JobPilotCLI|CLICommandRouter|CommandSafetyGate|jobpilot --help|P10-CLI-M0|P10-CLI-DOC" ...
rg "CLI 已实现|CLI 命令已实现|MCP server 已实现|真实 provider 已通过|真实市场 provider 已通过|真实个人资料路径已通过|招聘平台.*已接入|ASR 已实现|自动投递已实现|SaaS.*已通过" ...
git diff --check
```

检查结论：

- `jobpilot-p10-cli-local-entry-gap.drawio` 可解析，共 8 页，满足不超过 8 页要求；
- README、TODO、active PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、专项计划、drawio 文本镜像和阶段审计均已落盘 P10-CLI；
- 架构实体不再是抽象功能清单，已经明确 `JobPilotCLI`、`CLICommandRouter`、`CLIConfigResolver`、`WorkspaceSelector`、`CommandSafetyGate`、`ApiClient`、`OutputRenderer`、`ExitCodePolicy`、`CommandAuditLog` 与 FastAPI / Domain / Workspace / Evidence 的关系；
- 已补齐 API 映射、adapter 缺口、工作流树、输出 envelope、exit code 和 handoff contract；
- 已采纳外部审计修订：降低结论层级为“支撑 P10-CLI 自动化开发启动”，并把 FastAPI 生命周期、reports open 范围、workspace 解析优先级作为 M0 冻结项；
- 虚假声明扫描命中的内容均处于“不得声明 / 不代表 / 后续阶段验收条件”语境，未发现把 CLI、MCP、真实 provider、真实资料、招聘平台抓取、ASR、自动投递或 SaaS 写成已实现的正向结论；
- `git diff --check` 通过。

风险判断：

| 风险 | 当前状态 | 是否需要备选路线 |
| --- | --- | --- |
| CLI 范围扩张为 MCP / 外部 Agent 平台 | 已通过非目标和红色边界约束 | 否 |
| CLI 默认触发真实 provider 或读取 API Key | 已通过 `CommandSafetyGate`、Provider Policy Gate 和验收门槛约束 | 否 |
| CLI 扫描真实个人资料 | 已通过 `WorkspaceSelector` 和非目标约束 | 否 |
| CLI 抓取招聘平台或读取 `source_url` 网页 | 已明确禁止 | 否 |
| CLI 绕过 API/Domain 直接写 SQLite | 已在目标架构中禁止 | 否 |
| 文档完成被误写成代码实现完成 | 已在 README、TODO、PRD、审计中声明当前仅文档阶段 | 否 |

最终风险闭环结论：

```text
P10-CLI 文档已支撑后续 P10-CLI-M0 到 M5 的自动化开发启动和阶段化实现。
当前没有无法消减的高风险阻塞点。
当前不需要让用户在替代技术路线之间选择。
下一步若用户批准代码开发，应先执行 P10-CLI-M0 开发前启动审计。
```
