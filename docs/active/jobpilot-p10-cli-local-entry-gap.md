# JobPilot AI P10-CLI 本地命令入口架构图说明

本文档是 `jobpilot-p10-cli-local-entry-gap.drawio` 的文本镜像，便于代码审查和 diff。当前图示主线是 **P10-CLI 本地命令入口文档开发阶段**。

P10-CLI 只规划本地 CLI 命令入口，不代表 CLI 代码已经实现；也不代表 MCP server、真实 provider、真实个人资料、招聘平台抓取、真实市场 provider、ASR、会议平台、自动投递或 SaaS 已通过。

## 图示页结构

drawio 共 8 页，不超过 8 页：

1. P10-CLI 目标体验与阶段边界；
2. 当前架构与 P10-CLI 差距；
3. 目标架构与代码实体状态；
4. CLI 命令流与数据流；
5. 开发计划、里程碑和验收门槛；
6. 出门条件、false-green 边界和后续路线；
7. API 契约与适配缺口；
8. 工作流树、输出 envelope 和错误码。

颜色含义：

- 绿色：已实现复用，包括 FastAPI、Domain Tools、SQLite workspace、artifact、reports；
- 蓝色：P10-CLI 待新增，包括 `JobPilotCLI`、router、config、safety gate、client、renderer、exit code、audit log；
- 黄色：需适配或后续补充，包括 status/report/demo 汇总 route、CLI eval、HTML 报告；
- 红色：高风险或禁止默认实现，包括真实 provider、真实个人资料、招聘平台抓取、MCP、ASR、自动投递、不可逆 workspace 操作；
- 灰色：审计证据、边界说明或历史基线。

## 第 1 页 - P10-CLI 目标体验与阶段边界

目标体验：

```text
用户或本地 Agent 打开终端
→ jobpilot --help 了解命令和边界
→ jobpilot workspace status 查看本地服务、workspace、provider、report 状态
→ jobpilot demo run --example 运行本地 examples / fixture 路径
→ jobpilot jobs list 查看本地岗位和 source refs
→ jobpilot artifacts list/show 查看产物、版本、待确认项
→ jobpilot reports open 打开或列出中文验收报告
```

阶段边界：当前只做文档开发。不能声明 CLI 命令已实现，不能把 CLI 扩写成 MCP server、真实 provider 外呼、真实资料读取、招聘平台抓取、ASR、自动投递或 SaaS。

## 第 2 页 - 当前架构与 P10-CLI 差距

当前已实现复用：

- Chatbox UI；
- FastAPI Agent Service；
- Domain Tools；
- SQLite workspace；
- artifact、resume_version、job、candidate_profile、source refs、pending confirmations；
- HTML 报告和截图证据链；
- examples / fixture 自动化验收路径。

P10-CLI 差距：

- 缺少 `jobpilot` 命令入口；
- 缺少命令路由、配置解析、workspace 选择、安全门、API client、输出渲染、exit code 和命令审计；
- 缺少面向 Codex CLI / ClaudeCode CLI / 本地 Agent 的稳定 stdout/stderr 和 JSON 输出；
- 缺少 CLI 级别的 false-green 边界和验收报告。

## 第 3 页 - 目标架构与代码实体状态

```text
User / Local Agent
→ JobPilotCLI（待新增）
  → CLICommandRouter（待新增）
  → CLIConfigResolver（待新增）
  → WorkspaceSelector（待新增）
  → CommandSafetyGate（待新增）
  → ApiClient（待新增）
  → OutputRenderer（待新增）
  → ExitCodePolicy（待新增）
  → CommandAuditLog（待新增）
→ Existing FastAPI Agent Service（已实现复用）
→ Existing Domain Tools（已实现复用）
→ Existing SQLite Workspace / Artifact / Evidence（已实现复用）
```

状态说明：

| 实体 | 状态 | 说明 |
| --- | --- | --- |
| `JobPilotCLI` | 待新增 | 本地命令入口 |
| `CLICommandRouter` | 待新增 | 分发 help/status/demo/jobs/artifacts/reports |
| `CLIConfigResolver` | 待新增 | 解析 API URL、workspace、输出模式，不打印 API Key |
| `WorkspaceSelector` | 待新增 | 只选默认 workspace 或用户显式路径 |
| `CommandSafetyGate` | 待新增 | 拒绝真实外呼、平台抓取、ASR、自动投递和不可逆操作 |
| `ApiClient` | 待新增 | 调用本地 FastAPI，服务未启动时给启动建议 |
| `OutputRenderer` | 待新增 | 中文表格、摘要、报告路径、可选 JSON |
| `ExitCodePolicy` | 待新增 | 稳定 exit code |
| `CommandAuditLog` | 待新增 | 本地脱敏命令审计 |
| FastAPI / Domain / Workspace / Evidence | 已实现复用 | P10-CLI 不重写业务语义 |

端口与适配器分层：

```text
CLI Presentation
  JobPilotCLI / CLICommandRouter / OutputRenderer / ExitCodePolicy
→ CLI Application
  HelpCommand / WorkspaceStatusCommand / DemoRunCommand / JobsListCommand
  ArtifactsListCommand / ArtifactShowCommand / ReportsOpenCommand
  CommandSafetyGate / CommandAuditLog
→ CLI Adapter
  CLIConfigResolver / WorkspaceSelector / ApiClient
  LocalReportLocator / BrowserOpenAdapter / JsonEnvelopeAdapter
→ Existing Boundary
  FastAPI Agent Service / Domain Tools / SQLite Workspace / Evidence
```

设计约束：CLI 只做 presentation、command orchestration 和 adapter，不把业务逻辑、provider policy、artifact 版本语义或 workspace 写入逻辑搬进 CLI。

## 第 4 页 - CLI 命令流与数据流

命令流：

```text
jobpilot workspace status
→ CLICommandRouter
→ CLIConfigResolver
→ CommandSafetyGate
→ ApiClient GET /api/health and status summaries
→ OutputRenderer
→ ExitCodePolicy

jobpilot demo run --example
→ CLICommandRouter
→ CommandSafetyGate confirms local examples only
→ ApiClient or script adapter invokes existing local demo path
→ OutputRenderer prints stages, artifact ids, report paths
→ CommandAuditLog writes redacted audit record
```

数据边界：

- CLI 输出只来自本地 API、examples、fixture、workspace、artifact 和 reports；
- CLI 不读取 `source_url` 网页；
- CLI 不读取真实个人资料目录；
- CLI 不直连真实 provider；
- CLI 不执行不可逆 workspace 操作；
- CLI 不对外发送招聘消息或投递。

## 第 5 页 - 开发计划、里程碑和验收门槛

文档阶段：

| 阶段 | 目标 | 出门条件 |
| --- | --- | --- |
| P10-CLI-DOC-M0 | 阶段口径和范围锁定 | 不把 CLI 写成已实现 |
| P10-CLI-DOC-M1 | PRD、架构、命令契约、实体状态 | 具体实体和命令清楚 |
| P10-CLI-DOC-M2 | active docs、roadmap、drawio 同步 | drawio 不超过 8 页 |
| P10-CLI-DOC-M3 | 覆盖度复审和 false-green 扫描 | 无重大规格偏差 |

后续实现阶段：

| 阶段 | 目标 | 验收证据 |
| --- | --- | --- |
| P10-CLI-M0 | 开发前启动审计 | stage review |
| P10-CLI-M1 | CLI 框架和 help | `jobpilot --help` |
| P10-CLI-M2 | status 和 safety gate | `jobpilot workspace status` |
| P10-CLI-M3 | demo/jobs/artifacts/reports | 本地命令验收 |
| P10-CLI-M4 | Agent-friendly 输出 | `--json`、stdout/stderr、exit code |
| P10-CLI-M5 | 中文验收报告 | pytest、build、CLI eval、HTML report |

## 第 6 页 - 出门条件、false-green 边界和后续路线

P10-CLI 文档阶段出门条件：

- active PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、专项计划、drawio 和文本镜像一致；
- drawio XML 可解析且不超过 8 页；
- P10-CLI 实体状态、命令清单、上游下游和验收命令清楚；
- 审计文档明确当前不进入代码实现。

P10-CLI-M0 进入 M1 前必须冻结：

- CLI 不自动启动 FastAPI；服务不可用时只返回 exit 2 和启动建议；
- `reports open` 只定位/打开已有报告，不生成、修复或重写验收报告；
- workspace 解析优先级固定为 `--workspace` > `JOBPILOT_WORKSPACE` > 当前目录 `.jobpilot_workspace` > 失败 exit 3。

不得声明：

- CLI 已实现；
- MCP server 已实现；
- 真实 provider 或真实市场 provider 通过；
- 真实个人资料路径通过；
- 招聘平台抓取、ASR、会议平台、自动投递或 SaaS 通过；
- examples/fixture/demo run 等于真实用户验收。

后续路线：

```text
P10-CLI 文档覆盖度复审
→ P10-CLI-M0 开发前启动审计
→ P10-CLI-M1 到 M5 自动化开发
→ P10-MCP 或 P10-MARKET-OPTIN 另行立项
```

## 第 7 页 - API 契约与适配缺口

本页把每个 CLI 命令落到当前仓库中已经存在或需要适配的入口，防止架构图只停留在功能词。

| CLI 命令 | 现有入口 | 当前状态 | 适配缺口 |
| --- | --- | --- | --- |
| `workspace status` | `GET /api/health`, `GET /api/workspace/status`, `GET /api/provider/status`, `GET /api/provider/runtime-config` | 已有 API | CLI 需要聚合服务、workspace、provider、market provider、reports 状态 |
| `demo run --example` | `POST /api/workflows/p2-demo/run` | 已有本地 examples 路径 | 只允许 example/fixture；不得读取真实资料或触发真实 provider |
| `jobs list` | `GET /api/jobs?workspace_id=...` | 已有 API | 输出摘要、当前目标、source refs 数量；不抓取 `source_url` |
| `artifacts list` | `GET /api/artifacts?workspace_id=...` | 已有 API | 默认只输出摘要、版本和确认状态 |
| `artifacts show <id>` | artifact/version API | 已有能力 | CLI 需要脱敏摘要、source refs、pending confirmations |
| `reports open --no-browser` | `docs/reports/` | 本地报告目录已有 | 需要 `LocalReportLocator`，失败时只打印路径和原因 |

本页还标出禁止默认实现的入口：真实 provider adapter、招聘平台 connector、ASR adapter、MCP server wrapper、workspace cleanup/migration apply、FastAPI 自动启动、报告生成器、workspace 扫描器。它们不是 P10-CLI 的可适配缺口，而是后续单独阶段。

## 第 8 页 - 工作流树、输出 envelope 和错误码

工作流树 A：`jobpilot workspace status`

```text
ParseCommand
→ ResolveConfig
→ CommandSafetyGate
→ ApiHealthCheck
→ WorkspaceStatusFetch
→ ProviderStatusFetch
→ ReportIndexFetch
→ RenderOutput
→ CommandAuditLog
```

工作流树 B：`jobpilot demo run --example`

```text
ParseCommand
→ CommandSafetyGate confirms data_mode=example
→ EnsureApiAvailable
→ EnsureWorkspace
→ RunExistingDemo
→ SummarizeArtifactsAndReports
→ RenderOutput
→ CommandAuditLog
```

工作流树 C：`jobpilot artifacts show <id>`

```text
ParseCommand
→ CommandSafetyGate
→ FetchArtifactVersions
→ FetchSelectedVersion
→ RedactAndSummarize
→ RenderOutput with source refs / pending confirmations
→ CommandAuditLog
```

JSON 输出 envelope 统一包含 `ok`、`command`、`workspace_id`、`data_source`、`provider_state`、`data`、`warnings`、`next_actions`、`meta`；失败时统一包含 `error.code`、`message`、`hint` 和 `exit_code`。

exit code：

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 1 | 参数或用法错误 |
| 2 | 本地服务不可用 |
| 3 | workspace 不存在或不可访问 |
| 4 | 安全门拒绝 |
| 5 | 本地数据为空 |
| 10 | 未分类内部错误 |

外部审计修订后的结论口径：本图支撑 P10-CLI 自动化开发启动和 M0-M5 实现，不支撑整个 JobPilot 产品化阶段一次性开工。
