# P10-CLI 本地命令入口计划与实现收口记录

状态：自动化候选已完成。本文档最初定义 P10-CLI 自动化开发的 PRD、目标架构、里程碑、验收门槛和风险边界；当前已由 `jobpilot` CLI、`services/cli/main.py`、P10 CLI eval、中文 HTML 验收报告和阶段审计接续实现。该结论只覆盖本地 CLI 命令入口，不代表 MCP server、真实 provider、真实个人资料、招聘平台抓取、真实市场 provider、ASR、会议平台、自动投递或 SaaS 已通过。

P9.1 已完成本地自动化候选：ECharts 行政区划下钻式市场地图、Market Provider 未配置状态、Socratic Intake、产物台联动和中文 HTML 验收报告均已落地。P9+ 剩余准入审计显示，真实 provider、真实资料、MCP、ASR、会议平台、自动投递和真实市场 provider 都不能在缺少专项文档时直接进入实现。P10-CLI 选择了其中最低风险入口：只把现有本地 API、fixture、workspace、artifact 和报告能力封装成可由用户、Codex CLI、ClaudeCode CLI 或其他本地 Agent 调用的命令入口。

外部审计修订口径：P10-CLI 文档体系足以支撑 **P10-CLI 自动化开发启动**，但不应表述为“完整支撑整个 JobPilot 下一阶段产品化开发”。P10-M0 到 M5 已完成后，仍不能顺带声明 MCP、真实 provider、招聘平台、ASR、自动投递或产品化 SaaS。

当前实现证据：

- `jobpilot`
- `services/cli/main.py`
- `tests/evals/test_p10_cli_eval.py`
- `tests/evals/test_p10_cli_acceptance_report_eval.py`
- `docs/active/stage-reviews/P10_CLI_M0_DEVELOPMENT_START_AUDIT.md`
- `docs/active/stage-reviews/P10_CLI_M1_TO_M5_DEVELOPMENT_AUDIT.md`
- `docs/reports/P10_CLI_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p10_cli/p10_cli_command_evidence.json`

## 1. 目标体验

P10-CLI 完成后，用户或本地 Agent 应能通过终端完成以下本地安全路径：

```text
jobpilot --help
→ 看懂当前 CLI 可做什么、不可做什么
→ jobpilot workspace status 查看本地 workspace、provider、market provider、report 状态
→ jobpilot demo run --example 执行 examples / fixture 演示路径
→ jobpilot jobs list 查看本地已导入或 fixture 岗位
→ jobpilot artifacts list / show 查看本地产物和 source refs
→ jobpilot reports open 打开最近中文验收报告或列出报告路径
```

用户不需要知道 FastAPI 路由、SQLite 表、artifact JSON 或前端调试脚本；CLI 负责把本地状态、命令结果、失败原因和下一步建议用中文清楚打印出来。

## 2. 当前问题

- 当前系统主要入口是 Chatbox 和 HTTP API；其他 Agent 想自动验收或复用能力时需要知道多个脚本、端口、报告路径和 API 细节。
- P9+ 剩余项中 CLI 只有 TODO 级条目，缺少命令契约、输出格式、安全边界、错误码和验收门槛。
- 如果没有专项文档，后续实现容易把 CLI 扩张成真实 provider 外呼、平台抓取、MCP server、ASR 或自动投递入口。

## 3. 本阶段范围

P10-CLI 只规划本地命令入口，不改变 P9.1 已有业务语义。

允许规划：

- 本地 help/status/demo/jobs/artifacts/reports 命令；
- 对现有 FastAPI service 的本地 API client；
- 对现有 examples、fixture、workspace、artifact、report 的只读或安全执行包装；
- 命令输出结构、exit code、错误提示、审计日志和验收脚本；
- 与 Codex CLI、ClaudeCode CLI 或其他本地 Agent 可读的 stdout/stderr 约定。

禁止规划为 P10-CLI 默认能力：

- 真实 LLM provider 默认外呼；
- 真实个人资料目录扫描或默认读取；
- BOSS、猎聘、拉勾、LinkedIn 等招聘平台登录、抓取、绕风控；
- 真实市场 provider 调用；
- MCP server wrapper；
- ASR、麦克风采集、会议平台；
- 自动投递、自动沟通或对外发送消息；
- workspace 删除、cleanup apply、migration apply 或不可逆迁移。

## 4. 命令契约草案

| 命令 | 目标用户 | 目标行为 | 输出要求 | 默认安全边界 |
| --- | --- | --- | --- | --- |
| `jobpilot --help` | 人类 / Agent | 列出可用命令、示例、非目标 | 中文帮助 + 机器可读摘要提示 | 不触发服务写入 |
| `jobpilot workspace status` | 人类 / Agent | 查看本地 API、workspace、provider、market provider、reports 状态 | 表格或 JSON 可选；必须区分 configured / consented / called | 不读取真实资料，不外呼 |
| `jobpilot demo run --example` | 人类 / Agent | 运行 examples / fixture 演示路径 | 打印执行阶段、artifact id、报告路径 | 默认 mock/fake provider；不使用真实 API Key |
| `jobpilot jobs list` | 人类 / Agent | 列出本地岗位和当前目标岗位 | 岗位标题、城市、来源类型、匹配摘要、source refs 数量 | 不抓取 source_url |
| `jobpilot artifacts list` | 人类 / Agent | 列出本地产物 | artifact type、版本、确认状态、更新时间 | 不展示敏感全文，默认摘要 |
| `jobpilot artifacts show <id>` | 人类 / Agent | 展示单个产物摘要和 source refs | 人类可读摘要，可选 `--json` | blocking pending confirmations 必须可见 |
| `jobpilot reports open` | 人类 / Agent | 打开或列出最近验收报告 | Windows/WSL 路径友好；失败时打印路径 | 不生成虚假报告 |

后续实现可以在不扩大风险边界的前提下增加 `--json`、`--workspace`、`--api-url`、`--no-browser` 等参数；所有参数必须在实现前进入 acceptance gate。

## 5. 目标架构

```text
User / Local Agent
→ JobPilotCLI（待新增）
  → CLICommandRouter（待新增：解析 help/status/demo/jobs/artifacts/reports）
  → CLIConfigResolver（待新增：读取本地 env、默认 API URL、workspace 参数；不读取 API Key 明文）
  → WorkspaceSelector（待新增：选择本地 workspace，只允许用户显式路径或默认 workspace）
  → CommandSafetyGate（待新增：拦截真实 provider、真实资料、平台抓取、不可逆操作）
  → ApiClient（待新增：调用 127.0.0.1 FastAPI；服务未启动时给启动建议）
  → OutputRenderer（待新增：中文表格、摘要、JSON 输出）
  → ExitCodePolicy（待新增：统一 0/1/2/3 等退出码）
  → CommandAuditLog（待新增：记录命令、时间、结果和脱敏状态）
→ Existing FastAPI Agent Service（已实现）
  → health / provider status / jobs / artifacts / reports / demo routes（部分已实现，部分需后续适配）
→ Existing Domain Tools（已实现）
→ Existing SQLite Workspace / Artifact / Evidence（已实现）
```

架构决策：

| 决策点 | 方案 | 采用结论 | 原因 |
| --- | --- | --- | --- |
| CLI 与业务层关系 | CLI 直连 Domain / CLI 调 FastAPI / CLI 直写 SQLite | CLI 调本地 FastAPI | 复用现有 API、Provider Policy、workspace 边界和测试链路，避免重复业务逻辑 |
| 输出模型 | 仅人类可读 / 仅 JSON / 双格式 | 中文摘要 + `--json` envelope | 同时服务人类、本地 Agent、Codex CLI、ClaudeCode CLI |
| 审计记录 | 不记录 / 原文记录 / 脱敏记录 | 本地脱敏审计 | 能复盘命令，不泄露 API Key、真实资料全文或 provider 响应全文 |
| 高风险能力 | 默认暴露 / 参数开启 / 独立立项 | 默认不暴露，独立立项 | 防止 P10-CLI 被误实现为 MCP、ASR、真实 provider 或招聘平台入口 |

M0 必须冻结的工程决策：

| 冻结项 | P10-CLI v1 决策 | 打回条件 |
| --- | --- | --- |
| FastAPI 生命周期 | CLI 不自动启动 FastAPI；服务不可用时只返回 exit 2 和启动建议 | 实现计划试图新增后台服务管理、端口占用处理或自动拉起进程 |
| reports open 范围 | `reports open` 只做报告定位和打开；`--no-browser` 只打印路径 | 实现计划把报告生成、截图采集或报告修复塞进 CLI 命令 |
| workspace 解析优先级 | `--workspace` > `JOBPILOT_WORKSPACE` > 当前目录 `.jobpilot_workspace` > 失败 exit 3 | 实现计划扫描用户目录、隐式寻找历史 workspace 或默认读取真实资料目录 |

端口与适配器分层：

| 层级 | 待新增 / 复用实体 | 上游 | 下游 | 约束 |
| --- | --- | --- | --- | --- |
| CLI Presentation | `JobPilotCLI`, `CLICommandRouter`, `OutputRenderer`, `ExitCodePolicy` | 人类 / 本地 Agent | command handlers | 只解析命令、渲染输出和退出码，不访问 DB |
| CLI Application | `HelpCommand`, `WorkspaceStatusCommand`, `DemoRunCommand`, `JobsListCommand`, `ArtifactsListCommand`, `ArtifactShowCommand`, `ReportsOpenCommand`, `CommandSafetyGate`, `CommandAuditLog` | router | adapters | 每个 command handler 必须先过安全门，写入脱敏审计 |
| CLI Adapter | `CLIConfigResolver`, `WorkspaceSelector`, `ApiClient`, `LocalReportLocator`, `BrowserOpenAdapter`, `JsonEnvelopeAdapter` | command handlers | FastAPI / local reports / browser open | 只连接 127.0.0.1 API 和本地报告目录；不自动启动 FastAPI，不生成报告，不扫描用户个人目录 |
| Existing Boundary | FastAPI Agent Service, Domain Tools, SQLite Workspace / Artifact / Evidence | adapters | 现有服务 | 业务语义复用，不由 CLI 重写 |

现有 API 映射与适配缺口：

| CLI 命令 | 可复用现有入口 | 当前状态 | P10-CLI 适配要求 |
| --- | --- | --- | --- |
| `jobpilot workspace status` | `GET /api/health`, `GET /api/workspace/status`, `GET /api/provider/status`, `GET /api/provider/runtime-config` | 入口已存在，P10 CLI 聚合已实现 | `ApiClient.status()` 聚合服务、workspace、provider、market provider、reports 状态；服务未启动只提示，不自动启动 |
| `jobpilot demo run --example` | `POST /api/workflows/p2-demo/run` | 本地 examples 路径已存在 | 只允许 `data_mode=example` 或等价 fixture；不得读取真实资料 |
| `jobpilot jobs list` | `GET /api/jobs?workspace_id=...` | 已存在 | 输出岗位标题、城市、来源类型、当前目标和 source refs 数量；不抓取 `source_url` |
| `jobpilot artifacts list` | `GET /api/artifacts?workspace_id=...` | 已存在 | 默认摘要，不打印敏感全文 |
| `jobpilot artifacts show <id>` | artifact/version 相关 API | 已存在，CLI 摘要待实现 | 输出摘要、版本、source refs、pending confirmations 和 blocking 状态 |
| `jobpilot reports open --no-browser` | `docs/reports/` 本地文件 | 报告目录已存在 | `LocalReportLocator` 选择最新中文验收报告；`--no-browser` 只打印路径；不生成报告 |

输出 envelope：

```json
{
  "ok": true,
  "command": "workspace status",
  "workspace_id": "default",
  "data_source": ["local_api", "workspace", "reports"],
  "provider_state": {"configured": false, "consented": false, "called": false},
  "data": {},
  "warnings": [],
  "next_actions": [],
  "meta": {"api_url": "http://127.0.0.1:8000", "redacted": true}
}
```

失败 envelope：

```json
{
  "ok": false,
  "command": "workspace status",
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "本地 FastAPI 服务不可用。",
    "hint": "请先运行 uvicorn services.api.main:app --reload"
  },
  "exit_code": 2
}
```

exit code 策略：

| Exit code | 含义 | 典型场景 |
| --- | --- | --- |
| 0 | 成功 | 命令完成并输出结果 |
| 1 | 参数或用法错误 | 未知命令、缺少 artifact id、非法参数组合 |
| 2 | 本地服务不可用 | 127.0.0.1 FastAPI 未启动或健康检查失败 |
| 3 | workspace 不存在或不可访问 | 显式 workspace 参数找不到 |
| 4 | 安全门拒绝 | 尝试真实 provider、平台抓取、ASR、自动投递或不可逆操作 |
| 5 | 本地数据为空 | 无 jobs、无 artifacts、无 reports，但命令本身有效 |
| 10 | 未分类内部错误 | adapter 解析失败或未预期异常 |

核心工作流树：

```text
Workflow A: jobpilot workspace status
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

```text
Workflow B: jobpilot demo run --example
ParseCommand
→ CommandSafetyGate confirms data_mode=example
→ EnsureApiAvailable
→ EnsureWorkspace
→ RunExistingDemo
→ SummarizeArtifactsAndReports
→ RenderOutput
→ CommandAuditLog
```

```text
Workflow C: jobpilot artifacts show <id>
ParseCommand
→ CommandSafetyGate
→ FetchArtifactVersions
→ FetchSelectedVersion
→ RedactAndSummarize
→ RenderOutput with source refs / pending confirmations
→ CommandAuditLog
```

handoff contracts：

| 交接点 | 输入 | 输出 | 失败处理 |
| --- | --- | --- | --- |
| `CLICommandRouter -> CommandHandler` | `argv`, env, cwd | `ParsedCommand` | unknown command -> exit 1 |
| `CommandHandler -> CommandSafetyGate` | command name, flags, workspace, requested data mode | allow / deny + reason | 高风险默认 exit 4 |
| `CommandHandler -> ApiClient` | method, path, query/body, timeout | typed response envelope | timeout / non-2xx 映射到稳定 error code |
| `CommandHandler -> OutputRenderer` | normalized result, warnings, next actions | stdout text or JSON | renderer failure -> exit 10 |
| `CommandHandler -> CommandAuditLog` | command summary, result code, redaction state | local redacted record | 审计失败不得打印敏感信息 |

实体状态：

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `JobPilotCLI` | 待新增 | CLI 入口进程，负责命令注册、帮助信息和全局参数 |
| `CLICommandRouter` | 待新增 | 将命令分发到 status/demo/jobs/artifacts/reports handler |
| `CLIConfigResolver` | 待新增 | 解析本地配置、API URL、workspace 参数；workspace 解析优先级为 `--workspace` > `JOBPILOT_WORKSPACE` > 当前目录 `.jobpilot_workspace` > 失败；不得把 API Key 打印到输出 |
| `WorkspaceSelector` | 待新增 | 选择 workspace；不得扫描用户个人目录，不隐式读取历史 workspace |
| `CommandSafetyGate` | 待新增 | 拒绝高风险命令、真实外呼、平台抓取和不可逆操作 |
| `ApiClient` | 待新增 | 只调用本地 FastAPI；服务未启动时输出启动命令，不自动拉起服务 |
| `OutputRenderer` | 待新增 | 生成人类可读中文输出和可选 JSON |
| `ExitCodePolicy` | 待新增 | 定义成功、用户输入错误、服务不可用、安全拒绝等退出码 |
| `CommandAuditLog` | 待新增 | 本地脱敏命令审计，不记录 API Key 或真实资料全文 |
| FastAPI / Domain / Workspace | 已实现 | P10-CLI 复用，不重写业务语义 |

## 6. 里程碑

| 阶段 | 工作内容 | 出门条件 |
| --- | --- | --- |
| P10-CLI-DOC-M0 | 当前文档、README、TODO、active docs、roadmap 同步 | 当前阶段明确为文档开发，不写成 CLI 已实现 |
| P10-CLI-DOC-M1 | PRD、目标架构、命令契约和实体状态落盘 | 命令范围、非目标、上游下游关系清楚 |
| P10-CLI-DOC-M2 | 验收门槛、追踪矩阵、drawio 和文本镜像落盘 | drawio 不超过 8 页，实体状态颜色明确 |
| P10-CLI-DOC-M3 | 文档覆盖度复审和 false-green 扫描 | 无新增致命或重大规格偏差 |
| P10-CLI-M0 | 后续开发前启动审计 | 确认不混入 MCP、真实 provider、真实资料、平台接入或 ASR；冻结 FastAPI 不自动启动、reports open 不生成报告、workspace 解析优先级 |
| P10-CLI-M1 | CLI 框架和帮助命令 | `jobpilot --help` 输出中文命令和边界 |
| P10-CLI-M2 | workspace status 和 safety gate | 能区分本地服务、workspace、provider 状态；高风险默认拒绝 |
| P10-CLI-M3 | demo/jobs/artifacts/reports 命令 | 可运行 examples / fixture 路径并列出本地结果 |
| P10-CLI-M4 | Agent-friendly 输出和错误码 | stdout/stderr、`--json`、exit code 可被自动化脚本稳定判断 |
| P10-CLI-M5 | 中文 HTML 验收报告和回归 | pytest、build、CLI eval、报告和 PRD 规格检视通过 |

## 7. 验收门槛

P10-CLI 文档阶段通过条件：

- README、TODO、active PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、drawio 和文本镜像口径一致；
- drawio 不超过 8 页，且能展示目标架构与当前架构差异、开发计划、里程碑、验收门槛和出门条件；
- 架构图包含具体代码实体、状态颜色、上下游关系和分层结构；
- 文档明确 CLI 是待实现能力，不把 TODO 写成已完成；
- 文档明确 P10-CLI 不覆盖 MCP、真实 provider、真实个人资料、ASR、招聘平台自动接入、自动投递或 SaaS。

P10-CLI 后续实现阶段最低验收证据：

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

后续实现报告必须说明：

- 哪些 CLI 命令真实可运行；
- 哪些输出来自 examples、fixture、本地 workspace 或已有 artifact；
- 是否调用真实 provider：默认必须为否；
- 是否读取真实个人资料：默认必须为否；
- 是否登录、抓取或联系招聘平台：必须为否；
- 是否实现 MCP、ASR、会议平台、自动投递：必须为否。

## 8. 打回条件

任一情况出现时，P10-CLI 文档或实现必须打回：

- CLI 文档把 MCP server、真实 provider、真实市场 provider、ASR、会议平台或自动投递写成本阶段默认能力；
- CLI 命令默认扫描用户目录或读取未授权真实个人资料；
- CLI 命令默认读取 `.env` 中的 API Key 并触发真实外呼；
- CLI 自动启动 FastAPI 或管理后台进程生命周期；
- `reports open` 生成、重写、补充或修复报告；
- workspace selector 扫描用户目录或隐式寻找历史 workspace；
- `source_url` 被 CLI 用于联网抓取；
- `reports open` 没有区分真实报告和原型/历史报告；
- drawio 页数超过 8 页，或代码实体关系仍是抽象功能清单；
- 后续验收报告无法让人类判断哪些命令真实可运行、哪些只是规划。

## 9. 可交给 ChatGPT 审计的文档路径

建议审计文件数：13，少于 20。

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
```
