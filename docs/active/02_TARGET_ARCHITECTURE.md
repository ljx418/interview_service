# JobPilot AI P11 / P10-CLI / P9.1 Chatbox-native 求职工作台目标架构

## -9. P11 真实市场数据 Provider Opt-in 目标架构

P11 当前处于 Level1 自动化候选收口阶段。它在不改变 P10-CLI、P9.1 Chatbox-native 工作台、行政区划地图、Socratic Intake、FastAPI、Domain Tool、SQLite workspace 或 HTML 报告既有业务语义的前提下，新增受控 market provider opt-in 边界的本地实现，让 fixture/recorded/manual/public 市场数据进入同一条 source refs 和 evidence 链路；真实 provider 外呼仍属于 Level2 待授权范围。

目标分层：

```text
User / Local Agent
→ UI Control Plane（Level1 已实现）
  → TopServiceCenter（Level1 已实现：展示 market provider 状态）
  → ConversationPlane / Chatbox（Level1 已实现：发起 market search run；真实 consent flow 属于 Level2）
  → MarketIntelligenceMap（Level1 已实现：读取 fallback snapshot）
  → ArtifactWorkbench（Level1 已实现：展示 Market Insight、source refs、low confidence）
→ Market Provider Boundary（Level1 已实现）
  → JobMarketProviderRegistry（Level1 已实现：fixture / manual / public / opt-in 候选）
  → MarketProviderPolicyGate（Level1 已实现：未授权真实调用拒绝）
  → MarketProviderClient（Level2 待授权：一次性真实调用；Level1 不联网）
  → MarketProviderInvocationLog（Level1 已实现：脱敏调用日志）
→ Market Normalization Domain（Level1 已实现）
  → JobSearchRunService（Level1 已实现：创建和读取查询运行）
  → MarketDataNormalizer（Level1 已实现：provider/manual/public/fixture 归一化）
  → SourceRefBinder（Level1 已实现：每个聚合指标绑定 source refs）
  → ConfidenceScorer（Level1 已实现：缺字段、低可信、fallback 标记）
→ Existing FastAPI / Domain / Workspace Boundary（已实现复用，部分需适配）
  → workspace / jobs / artifacts / reports / provider status
→ Evidence Layer（Level1 已实现）
  → P11 Chinese HTML report
  → command evidence / screenshot evidence / provider invocation evidence
```

P11 实体状态与职责：

| 层级 | 实体 | 状态 | 上游 / 下游 | P11 职责 |
| --- | --- | --- | --- | --- |
| UI | `TopServiceCenter` | Level1 已实现 | 上游 provider status；下游设置/说明 | 显示 market provider Level1 状态和不能声明真实市场的边界 |
| UI | `ConversationPlane` | Level1 已实现 | 上游用户 market query；下游 API | 通过 Chatbox 发起本地 `JobSearchRun`；真实授权确认属于 Level2 |
| UI | `MarketIntelligenceMap` | Level1 已实现 | 上游 `JobMarketSnapshot`；下游地图图层 | 把 fixture/manual/public/fallback source 映射为行政区划、薪资、技术栈和可信度 |
| UI | `ArtifactWorkbench` | Level1 已实现 | 上游 snapshot / source refs；下游用户审查 | 展示 market insight、source refs、低置信度和未验证范围 |
| API | `JobMarketProviderRegistry` | Level1 已实现 | 上游 config；下游 provider client | 管理 provider 候选、启用状态、许可说明、限额和能力范围 |
| API | `MarketProviderPolicyGate` | Level1 已实现 | 上游 query / consent；下游 provider client | 拦截未授权、超范围、平台抓取、长期任务和敏感数据外发 |
| API | `MarketProviderClient` | Level2 待授权 | 上游 policy gate；下游外部 opt-in API | 仅在后续用户授权和合法凭据下执行一次性真实 provider 调用 |
| API | `MarketProviderInvocationLog` | Level1 已实现 | 上游 provider client；下游 evidence | 记录 provider、query 摘要、状态、耗时、错误、redaction，不记录密钥和完整原文 |
| Domain | `JobSearchRunService` | Level1 已实现 | 上游 API；下游 normalizer/storage | 创建、读取、失败保留和边界说明 |
| Domain | `MarketDataNormalizer` | Level1 已实现 | 上游 provider/manual/public/fixture；下游 snapshot | 归一化为 `NormalizedJobPost`，不补造公司、薪资、城市、年限 |
| Domain | `SourceRefBinder` | Level1 已实现 | 上游 normalized posts；下游 snapshot/evidence | 将岗位数、薪资、技术栈、来源可信度绑定到 source refs |
| Domain | `ConfidenceScorer` | Level1 已实现 | 上游 normalized posts；下游 snapshot | 标记缺字段、低置信度、fallback 和待确认 |
| Data | `JobSearchRun` | Level1 已实现 | 上游 service；下游 snapshot/report | 记录 query、城市、薪资、技术栈、provider、授权和边界 |
| Data | `NormalizedJobPost` | Level1 已实现 | 上游 normalizer；下游 snapshot/jobs | 标准化职位标题、公司、城市、薪资、技术栈、来源和置信度 |
| Data | `JobMarketSnapshot` | Level1 已实现 | 上游 normalizer/source binder；下游 UI/report | 聚合城市岗位数、薪资分布、技术栈热度、来源可信度 |
| Evidence | `P11MarketAcceptanceReport` | Level1 已实现 | 上游 logs/snapshot/screenshots；下游 human audit | 证明调用边界、source refs、失败/fallback 和未验证范围 |

目标架构与当前架构差异：

| 当前实现 | P11 目标差异 | 状态 | 验收口径 |
| --- | --- | --- | --- |
| P9.1 地图使用 fixture/manual/public/opt-in 状态表达 | P11 已增加 Level1 provider boundary、fallback snapshot 和 source refs 证据 | Level1 已实现 | provider called 仍必须有授权、日志和 source refs |
| TopServiceCenter 展示 Market Provider not_configured | P11 已展示 Level1 market provider 状态 | Level1 已实现 | configured 不等于 called |
| Chatbox 可发起市场查询但不外呼 | P11 已通过 FastAPI 创建 Level1 `JobSearchRun`；真实调用前确认属于 Level2 | Level1 已实现 | 未确认时必须拒绝外呼 |
| MarketIntelligenceMap 可展示行政区划下钻 | P11 已增加 fallback snapshot 与 source trust 展示 | Level1 已实现 | fixture fallback 必须弱化且标明 |
| 现有 provider policy 主要服务 LLM | P11 已增加 MarketProviderPolicyGate，独立于 LLM provider | Level1 已实现 | 不把真实 LLM provider 作为市场数据 provider |
| HTML 报告已有 P9.1/P10 证据 | P11 已增加 provider invocation、snapshot 和真实界面截图证据 | Level1 已实现 | 不把报告生成等同于真实市场通过 |

P11 架构不变量：

- P11 不登录、不抓取、不绕过招聘平台风控；
- P11 不建设长期爬虫、队列或后台定时任务；
- provider configured 不等于 connected，不等于 consented，不等于 called；
- 每次 called 必须有用户授权、调用日志、source refs 和报告证据；
- provider 失败不得静默回退成 fixture 后声明真实市场；
- P11 不读取真实个人资料，不调用真实 LLM provider，不开启 ASR，不实现 MCP server 或自动投递；
- API Key 只允许由本地环境或用户明确配置读取，不得出现在文档、日志、报告、截图或 git diff 中。

P11 推荐命令流和数据流：

```text
Chatbox: "查询北京/上海 LLM 前端岗位真实市场"
→ ConversationPlane parses market intent
→ TopServiceCenter / API returns provider status
→ MarketProviderPolicyGate builds consent preview
→ User confirms one-shot query scope
→ JobSearchRunService creates run
→ MarketProviderClient calls opt-in provider
→ MarketDataNormalizer creates NormalizedJobPost[]
→ SourceRefBinder + ConfidenceScorer create JobMarketSnapshot
→ MarketIntelligenceMap renders real/fallback layers
→ ArtifactWorkbench shows Market Insight + source refs + low confidence
→ Evidence Layer records invocation/report
```

P11 API handoff：

| UI / CLI 调用者 | FastAPI 边界 | Domain / Adapter | 数据或证据输出 | 必须防止 |
| --- | --- | --- | --- | --- |
| `TopServiceCenter` / `jobpilot workspace status` | `GET /api/market/providers/status` | `JobMarketProviderRegistry`、`MarketProviderInvocationLog` | provider 状态、上次检查、called/failed/fallback 摘要 | 输出 API Key、把 configured 写成 called |
| `ConversationPlane` provider check | `POST /api/market/providers/check` | `MarketProviderPolicyGate`、`MarketProviderClient` | minimal check 结果、脱敏 invocation log | 未确认外呼、调用招聘平台 |
| `ConversationPlane` market query | `POST /api/market/search-runs` | `JobSearchRunService`、`MarketProviderPolicyGate` | `run_id`、状态、边界说明 | 创建长期任务、跳过 consent |
| `MarketIntelligenceMap` | `GET /api/market/snapshots/{run_id}` | `MarketDataNormalizer`、`SourceRefBinder`、`ConfidenceScorer` | `JobMarketSnapshot`、source breakdown、低置信度 | 没有 source refs 的聚合指标 |
| `ArtifactWorkbench` | `GET /api/market/search-runs/{run_id}`、`GET /api/market/source-refs/{id}` | Workspace / Evidence adapter | Market Insight、source refs、pending confirmations | 返回 raw provider response 或敏感数据 |
| `P11MarketAcceptanceReport` | report generator 读取 API/log/screenshot evidence | Evidence Layer | 中文 HTML 报告和截图 | 用 fixture/fallback 声明真实市场 |

P11 存储 handoff：

| 聚合 / 表达实体 | 推荐持久化实体 | 上游 | 下游 | 约束 |
| --- | --- | --- | --- | --- |
| provider 状态 | `job_market_providers` | 本地配置摘要 | status API / TopServiceCenter / CLI | 只保存状态和许可说明，不保存 secret |
| 查询运行 | `job_search_runs` | Chatbox query + consent | run API / report | `source_policy`、`consent_id`、`boundary_note` 必填 |
| 标准化岗位 | `normalized_job_posts` | provider/manual/public/fixture | snapshot / job list | 缺公司、城市、薪资、年限不得补造 |
| 区域来源 | `region_source_refs` | normalized posts | map tooltip / report | 每个指标绑定 source refs |
| 市场快照 | `job_market_snapshots` | normalizer + scorer | map / Chatbox / workbench | 必须包含 `source_breakdown` 和 `low_confidence_notes` |
| 调用日志 | `market_provider_invocation_logs` | provider client | evidence report | `redacted=true`，不得含 API Key/raw response |

P11 验收分级不变量：

- Level 1：本地实现通过，只能证明 policy gate、normalization、snapshot、UI 联动和报告可用；
- Level 2：至少一个用户授权的真实 market provider 调用成功，并有脱敏 invocation log、source refs、snapshot 和报告证据；
- 没有真实 provider 凭据或合法公开调用路径时，不得声明 Level 2；
- 任何招聘平台抓取、绕验证码、自动投递、ASR、MCP、SaaS 需求都必须脱离 P11 重新立项。

P11 不新增独立招聘平台系统。若后续实现发现必须接入招聘平台账号、绕验证码、长期抓取、自动沟通、自动投递、真实 ASR 或 MCP server，必须打回文档阶段重新立项。

## -8. P10-CLI 本地命令入口目标架构

P10-CLI 本地命令入口自动化候选已完成。它不修改 P9.1 已完成的 Chatbox、市场地图、Socratic Intake、FastAPI、Domain Tool、SQLite workspace 或 HTML 报告业务语义；目标是提供一个本地 CLI 命令入口，供人类、Codex CLI、ClaudeCode CLI 或其他本地 Agent 以稳定命令复用现有本地能力。P10 结论不代表 MCP、真实 provider、真实资料、招聘平台抓取、真实市场 provider、ASR、会议平台、自动投递或 SaaS 已通过。

目标分层：

```text
User / Local Agent
→ JobPilotCLI（P10 已实现：本地命令入口）
  → CLICommandRouter（P10 已实现：help/status/demo/jobs/artifacts/reports）
  → CLIConfigResolver（P10 已实现：API URL、workspace 参数、本地 env 状态；不打印 API Key）
  → WorkspaceSelector（P10 已实现：默认 workspace 或用户显式路径；不扫描个人目录）
  → CommandSafetyGate（P10 已实现：拒绝真实外呼、平台抓取、ASR、自动投递、不可逆操作）
  → ApiClient（P10 已实现：调用 127.0.0.1 FastAPI；服务未启动时给启动建议）
  → OutputRenderer（P10 已实现：中文表格、摘要、可选 JSON）
  → ExitCodePolicy（P10 已实现：成功、输入错误、服务不可用、安全拒绝、内部错误）
  → CommandAuditLog（P10 已实现：本地脱敏命令审计）
→ Existing FastAPI Agent Service（已实现复用）
  → health / provider status / workspace / jobs / artifacts / reports / demo routes
→ Existing Domain Tools（已实现复用）
→ Existing SQLite Workspace / Artifact / Evidence（已实现复用）
```

P10-CLI 实体状态与职责：

| 层级 | 实体 | 状态 | 上游 / 下游 | P10-CLI 职责 |
| --- | --- | --- | --- | --- |
| CLI | `JobPilotCLI` | P10 已实现 | 上游为用户或本地 Agent；下游为 router | 注册命令、全局参数、帮助入口和版本信息 |
| CLI | `CLICommandRouter` | P10 已实现 | 上游 CLI args；下游 command handlers | 分发 `--help`、`workspace status`、`demo run`、`jobs list`、`artifacts list/show`、`reports open` |
| CLI | `CLIConfigResolver` | P10 已实现 | 上游环境变量和参数；下游 ApiClient / WorkspaceSelector | 解析 API URL、workspace、输出模式；不得输出 API Key 明文 |
| CLI | `WorkspaceSelector` | P10 已实现 | 上游 config；下游 API / workspace route | 只选择默认 workspace 或用户显式路径；不得扫描个人目录 |
| CLI | `CommandSafetyGate` | P10 已实现 | 上游 command intent；下游 router / handlers | 拒绝真实 provider 默认调用、真实资料读取、招聘平台抓取、ASR、自动投递和不可逆操作 |
| CLI | `ApiClient` | P10 已实现 | 上游 handlers；下游 FastAPI | 调用本地 `127.0.0.1` API；服务不可用时输出启动建议 |
| CLI | `OutputRenderer` | P10 已实现 | 上游 response / errors；下游 stdout/stderr | 输出中文表格、摘要、路径、可选 JSON；默认不打印敏感全文 |
| CLI | `ExitCodePolicy` | P10 已实现 | 上游 command result；下游 shell / Agent | 稳定定义成功、参数错误、服务不可用、安全拒绝和内部错误退出码 |
| CLI | `CommandAuditLog` | P10 已实现 | 上游 command result；下游本地日志 | 记录命令、时间、脱敏结果；不得记录 API Key 或真实资料全文 |
| API | FastAPI Agent Service | 已实现复用，部分 route 需后续适配 | 上游 ApiClient；下游 Domain Tools | 提供 health、workspace、jobs、artifacts、reports 和 demo 能力 |
| Domain | Domain Tools | 已实现复用 | 上游 API；下游 workspace/artifact | 执行现有资料、JD、画像、申请包、报告逻辑 |
| Storage | SQLite Workspace / Artifact | 已实现复用 | 上游 Domain / API；下游 CLI 输出 | 存储 job、artifact、resume_version、source refs 和 pending confirmations |
| Evidence | HTML reports / screenshots | 已实现复用 | 上游 report scripts；下游 reports command | 提供可打开或列出的验收证据 |

目标架构与当前架构差异：

| 当前实现 | P10-CLI 目标差异 | 状态 | 验收口径 |
| --- | --- | --- | --- |
| Chatbox / HTTP API / scripts 是主要入口 | 新增本地 CLI 作为稳定命令入口 | P10 已实现 | `jobpilot --help` 和命令输出可被人类 / Agent 理解 |
| P9.1 报告和截图由脚本生成 | CLI 能列出或打开报告路径 | P10 已实现 | `jobpilot reports open --no-browser` 可输出路径 |
| FastAPI health / routes 已存在 | CLI 用 ApiClient 检查服务，服务未启动时给启动建议 | P10 已适配 | 错误提示和 exit code 稳定 |
| workspace / artifact / job 已有数据结构 | CLI 提供只读摘要和 source refs 可见输出 | P10 已实现 | 不泄露敏感全文，pending confirmations 可见 |
| provider / market provider 状态在 UI 可见 | CLI status 输出同样区分 configured / consented / called / fallback | P10 已实现 | configured 不等于 called |
| 高风险能力在文档中禁用 | CLI safety gate 在命令层拒绝默认执行 | P10 已实现 | 高风险命令默认不存在或返回安全拒绝 |

P10-CLI 架构不变量：

- CLI 不直连真实 provider，不保存或打印 API Key，不绕过 Provider Policy Gate；
- CLI 不直接写 SQLite；后续实现应通过 API / Domain 边界完成安全操作；
- CLI 不扫描用户个人目录，不默认读取真实个人资料；
- CLI 不读取 `source_url` 网页，不登录或抓取招聘平台；
- CLI 不执行 workspace 删除、cleanup apply、migration apply；
- CLI 不把 MCP、ASR、会议平台、自动投递作为默认命令；
- CLI 输出必须让人类判断数据来自 examples、fixture、本地 workspace、mock/fake provider 还是未验证能力。

P10-CLI 推荐命令流：

```text
jobpilot workspace status
→ CLICommandRouter
→ CLIConfigResolver
→ CommandSafetyGate
→ ApiClient GET /api/health + provider/workspace/report summary
→ OutputRenderer prints Chinese table / optional JSON
→ ExitCodePolicy returns 0 or service unavailable code

jobpilot demo run --example
→ CLICommandRouter
→ CommandSafetyGate confirms local examples only
→ ApiClient or local script adapter triggers existing demo path
→ OutputRenderer prints stage summary, artifact ids, report paths
→ CommandAuditLog writes redacted local command audit
```

P10-CLI 不新增独立业务服务。若后续实现发现必须新增长期任务、外部数据源、MCP server、真实 provider adapter、ASR adapter 或平台 connector，必须打回文档阶段重新立项。

### P10-CLI M0 必须冻结的工程决策

外部审计意见确认当前文档足以支撑 **P10-CLI 自动化开发启动**，但不能上升为“完整支撑整个 JobPilot 下一阶段产品化开发”。因此 P10-CLI-M0 开发前启动审计必须先冻结以下三项，不允许在 M1 实现时临时扩大范围：

| 冻结项 | P10-CLI v1 结论 | 不采用的路线 | 原因与取舍 |
| --- | --- | --- | --- |
| FastAPI 生命周期 | CLI 不自动启动 FastAPI；只执行 health check，服务不可用时返回 `SERVICE_UNAVAILABLE` / exit 2 和启动建议 | CLI 自动拉起后台服务 | 自动启动会引入端口管理、后台进程生命周期、Windows/WSL 差异和清理责任，超出 P10-CLI v1 |
| `reports open` 范围 | 只做 `LocalReportLocator` + `BrowserOpenAdapter`；`--no-browser` 只打印路径 | 自动生成、重写或补充最新报告 | 生成报告属于验收脚本 / evidence pipeline，不属于 CLI v1 的报告打开命令 |
| workspace 解析优先级 | `--workspace` 参数 > `JOBPILOT_WORKSPACE` 环境变量 > 当前目录 `.jobpilot_workspace` > 失败 exit 3 | 扫描用户目录、隐式寻找历史 workspace、默认读取真实资料目录 | 防止隐式状态、误读真实资料和 Agent 自动调用时结果不稳定 |

M0 如果发现上述三项无法按表格执行，必须打回文档阶段；不得用“实现方便”替代安全边界。

### P10-CLI 架构决策

| 决策 | 选项 | 结论 | 取舍 |
| --- | --- | --- | --- |
| CLI 与业务逻辑关系 | 直接调用 Python Domain Tools / 调用本地 FastAPI / 新建独立服务 | 默认调用本地 FastAPI，必要时只允许包装现有只读脚本 | 保持与 Chatbox/API 同一业务边界；代价是服务未启动时需给清晰恢复路径；P10-CLI v1 不自动启动 FastAPI |
| CLI 状态存储 | 写 SQLite / 本地审计日志 / 不存储 | 业务数据不由 CLI 直写 SQLite；仅允许脱敏 `CommandAuditLog` | 降低数据破坏风险；代价是审计日志要单独定义路径和脱敏规则 |
| 命令输出 | 纯人类文本 / 纯 JSON / 双模式 | 默认中文文本，`--json` 输出稳定 envelope | 兼顾人类和 Agent；代价是每个命令都要定义字段 |
| 错误处理 | 直接抛异常 / 统一错误 envelope | 统一 `CliResult` / `CliError` / `ExitCodePolicy` | 便于自动化验收；代价是实现时要封装错误映射 |
| 高风险能力 | 通过参数开启 / 完全不暴露 / 独立阶段 | P10-CLI 默认完全不暴露，后续单独阶段立项 | 防止误外呼和虚假验收；代价是 CLI v1 能力较保守 |

### P10-CLI 端口与适配器分层

P10-CLI 后续实现应采用“薄 CLI + 本地 API adapter”的结构，而不是把业务逻辑搬进 CLI。

```text
CLI Presentation Layer
  JobPilotCLI
  CLICommandRouter
  OutputRenderer
  ExitCodePolicy

CLI Application Layer
  CommandHandlers
    HelpCommand
    WorkspaceStatusCommand
    DemoRunCommand
    JobsListCommand
    ArtifactsListCommand
    ArtifactShowCommand
    ReportsOpenCommand
  CommandSafetyGate
  CommandAuditLog

CLI Adapter Layer
  CLIConfigResolver
  WorkspaceSelector
  ApiClient
  LocalReportLocator
  BrowserOpenAdapter
  JsonEnvelopeAdapter

Existing JobPilot Boundary
  FastAPI Agent Service
  Domain Tools
  SQLite Workspace / Artifact
  docs/reports Evidence
```

分层约束：

- Presentation Layer 只处理命令解析、输出和 exit code，不包含业务判断；
- Application Layer 只组合安全门、API 调用和输出模型，不直接访问 SQLite；
- Adapter Layer 负责本地 API、文件路径和浏览器打开适配，必须可替换、可 mock；不得承担报告生成、FastAPI 自动启动或 workspace 扫描；
- Existing JobPilot Boundary 是业务事实来源，CLI 不复制 `jobpilot.py` 中的业务逻辑。

### P10-CLI 现有 API 映射与适配缺口

基于当前 `services/api/main.py` discovery pass，P10-CLI 可复用和需适配的入口如下：

| CLI 命令 | 现有入口 | 适配状态 | 目标 handoff |
| --- | --- | --- | --- |
| `workspace status` | `GET /api/health`, `GET /api/workspace/status`, `GET /api/provider/status`, `GET /api/provider/runtime-config` | 部分已实现，需 CLI 聚合 | `ApiClient.status()` 聚合 health、workspace、provider、market/report 状态；服务未启动只提示，不自动启动 |
| `demo run --example` | `POST /api/workflows/p2-demo/run` | 已实现本地 examples flow | `DemoRunCommand` 只允许 `data_mode=example`，禁止真实资料 |
| `jobs list` | `GET /api/jobs?workspace_id=` | 已实现 | `JobsListCommand` 输出岗位摘要、source 类型、当前目标 |
| `artifacts list` | `GET /api/artifacts?workspace_id=` | 已实现 | `ArtifactsListCommand` 默认只输出摘要、状态、版本、待确认数量 |
| `artifacts show <id>` | `GET /api/artifacts/{artifact_id}/versions`, `GET /api/artifacts/{artifact_id}/versions/{version_id}` | 已实现版本读取，需 CLI 摘要策略 | `ArtifactShowCommand` 展示 source refs、pending confirmations、content 摘要 |
| `reports open` | `docs/reports/` 文件系统 | 需新增 `LocalReportLocator`，不需要新业务服务 | `ReportsOpenCommand` 列出或打开报告路径，`--no-browser` 只打印路径；不得生成或改写报告 |
| `--json` | 无统一 CLI envelope | 待新增 | `JsonEnvelopeAdapter` 输出 `ok/data/error/meta` |
| command audit | 无 CLI 审计 | 待新增 | `CommandAuditLog` 写入本地脱敏日志，不进入仓库 |

### P10-CLI 输出 envelope

后续实现必须让所有命令都能映射到同一个结果模型，便于人类阅读和 Agent 自动判断：

```json
{
  "ok": true,
  "command": "workspace status",
  "workspace_id": "ws_xxx",
  "data_source": "local_api|fixture|examples|local_report",
  "provider_state": {
    "configured": false,
    "consented": false,
    "called": false,
    "fallback": "mock"
  },
  "data": {},
  "warnings": [],
  "next_actions": [],
  "meta": {
    "api_url": "http://127.0.0.1:8000",
    "workspace_root_display": ".jobpilot_workspace",
    "redacted": true
  }
}
```

失败 envelope：

```json
{
  "ok": false,
  "command": "workspace status",
  "error": {
    "code": "SERVICE_UNAVAILABLE|WORKSPACE_NOT_FOUND|INVALID_ARGUMENT|SAFETY_BLOCKED|NOT_IMPLEMENTED|INTERNAL_ERROR",
    "message": "中文错误说明",
    "retryable": true,
    "recovery": "启动 FastAPI 服务或传入 --api-url"
  },
  "meta": {
    "redacted": true
  }
}
```

### P10-CLI exit code 策略

| Exit code | 含义 | 触发场景 | 是否可重试 |
| --- | --- | --- | --- |
| 0 | 成功 | 命令完成，输出 `ok=true` | 不需要 |
| 1 | 用户输入错误 | 未知命令、参数缺失、非法 workspace 参数 | 否，需修改命令 |
| 2 | 本地服务不可用 | FastAPI 未启动、连接超时、health 失败 | 是 |
| 3 | workspace 不存在或未初始化 | `workspace status` 找不到 workspace | 是，运行 init 或指定路径 |
| 4 | 安全门拒绝 | 真实外呼、真实资料扫描、平台抓取、不可逆操作 | 否，需重新立项或授权 |
| 5 | 数据为空但命令有效 | 无 jobs、无 artifacts、无 reports | 否，需先导入或生成数据 |
| 10 | 内部错误 | 未预期异常，已脱敏 | 视情况 |

### P10-CLI 工作流树

#### Workflow A：`workspace status`

```text
触发：jobpilot workspace status [--workspace <path>] [--api-url <url>] [--json]
前置：用户在本机执行命令；默认不要求真实 provider 或真实资料。

1. ParseCommand
   成功：得到 command=workspace status、api_url、workspace_ref、output_mode
   失败：INVALID_ARGUMENT → exit 1
2. ResolveConfig
   成功：只读取允许的本地配置摘要；workspace 解析顺序为 --workspace > JOBPILOT_WORKSPACE > 当前目录 .jobpilot_workspace > 失败；API Key 只判断存在性，不输出值
   失败：CONFIG_ERROR → exit 1
3. SafetyGate
   成功：确认命令只读、无真实外呼、无平台抓取、无不可逆操作
   失败：SAFETY_BLOCKED → exit 4
4. ApiHealthCheck
   成功：GET /api/health
   超时/拒绝连接：SERVICE_UNAVAILABLE → exit 2，输出 uvicorn 启动建议；不得自动启动服务
5. WorkspaceStatusFetch
   成功：GET /api/workspace/status
   workspace 不存在：WORKSPACE_NOT_FOUND → exit 3，输出初始化建议
6. ProviderStatusFetch
   成功：GET /api/provider/status 和 runtime-config 摘要
   失败：降级为 warning，不触发真实 provider 检查
7. RenderOutput
   成功：中文表格或 JSON envelope
8. AuditLog
   成功：写入脱敏命令审计
```

#### Workflow B：`demo run --example`

```text
触发：jobpilot demo run --example [--workspace <path>] [--json]
前置：只允许 examples / fixture；禁止 my_data；默认 mock/fake provider。

1. ParseCommand
2. SafetyGate
   若出现真实资料路径、真实 provider 或外部平台参数 → SAFETY_BLOCKED exit 4
3. EnsureApiAvailable
   health 失败 → SERVICE_UNAVAILABLE exit 2
4. EnsureWorkspace
   无 workspace 时允许调用 /api/workspace/init 创建本地默认 workspace
5. RunDemo
   POST /api/workflows/p2-demo/run with data_mode=example
   失败：DEMO_FAILED exit 10，输出失败步骤和 recovery
6. SummarizeArtifacts
   从 response 中读取 artifact_refs、exports、summary，不读取敏感全文
7. RenderOutput
8. AuditLog
```

#### Workflow C：`artifacts show <id>`

```text
触发：jobpilot artifacts show <artifact_id> [--version <id>] [--json]
前置：workspace 已存在，artifact id 由用户显式提供。

1. ParseCommand
   artifact_id 缺失 → INVALID_ARGUMENT exit 1
2. SafetyGate
   只读命令通过；任何 export/apply/delete 参数拒绝
3. FetchArtifactVersions
   GET /api/artifacts/{artifact_id}/versions
   artifact 不存在 → NOT_FOUND exit 5
4. FetchSelectedVersion
   GET /api/artifacts/{artifact_id}/versions/{version_id}
5. RedactAndSummarize
   输出 artifact_type、status、version、source_refs、questions_to_confirm、content 摘要
   默认不打印完整 content_json；如后续允许全文必须单独验收
6. RenderOutput
7. AuditLog
```

### P10-CLI handoff contracts

#### CLICommandRouter -> CommandHandler

```json
{
  "command": "workspace status",
  "args": {
    "workspace": "string|null",
    "api_url": "string|null",
    "json": "boolean",
    "no_browser": "boolean"
  },
  "raw_argv": ["string"]
}
```

失败：

```json
{
  "ok": false,
  "code": "INVALID_ARGUMENT",
  "message": "未知命令或参数缺失",
  "retryable": false
}
```

#### CommandHandler -> CommandSafetyGate

```json
{
  "command": "demo run",
  "intent": "read|local_demo|open_report",
  "workspace_ref": "default|explicit_path",
  "requested_effects": ["read_workspace", "call_local_api"],
  "requested_high_risk": []
}
```

SafetyGate 必须拒绝：

```json
{
  "requested_high_risk": [
    "real_provider_call",
    "real_personal_data_scan",
    "platform_scrape",
    "asr_capture",
    "auto_apply",
    "workspace_delete_or_apply"
  ]
}
```

#### ApiClient -> FastAPI

| CLI handler | Method | Endpoint | Timeout | Failure mapping |
| --- | --- | --- | --- | --- |
| status | GET | `/api/health` | 3s | timeout/refused -> `SERVICE_UNAVAILABLE` |
| status | GET | `/api/workspace/status` | 5s | 400 not initialized -> `WORKSPACE_NOT_FOUND` |
| status | GET | `/api/provider/status` | 5s | failure -> warning only |
| demo | POST | `/api/workflows/p2-demo/run` | 60s | failure -> `DEMO_FAILED` |
| jobs | GET | `/api/jobs` | 10s | empty -> `EMPTY_RESULT` |
| artifacts list | GET | `/api/artifacts` | 10s | empty -> `EMPTY_RESULT` |
| artifact show | GET | `/api/artifacts/{artifact_id}/versions` | 10s | not found -> `NOT_FOUND` |

#### CommandHandler -> OutputRenderer

```json
{
  "ok": true,
  "command": "artifacts show",
  "display_mode": "table|json",
  "data": {},
  "warnings": [],
  "next_actions": [],
  "redaction": {
    "api_key_printed": false,
    "full_personal_data_printed": false,
    "source_url_fetched": false
  }
}
```

### P10-CLI workflow registry

| Workflow | Status | Trigger | Primary actor | Spec location |
| --- | --- | --- | --- | --- |
| CLI help | Planned | `jobpilot --help` | User / Local Agent | `25_P10_CLI_LOCAL_COMMAND_ENTRY_PLAN.md` |
| CLI workspace status | Planned | `jobpilot workspace status` | User / Local Agent | 本节 Workflow A |
| CLI demo run | Planned | `jobpilot demo run --example` | User / Local Agent | 本节 Workflow B |
| CLI jobs list | Planned | `jobpilot jobs list` | User / Local Agent | 命令契约 + API mapping |
| CLI artifacts list/show | Planned | `jobpilot artifacts list/show` | User / Local Agent | 本节 Workflow C |
| CLI reports open | Planned | `jobpilot reports open` | User / Local Agent | 命令契约 + report locator |
| MCP server wrapper | Missing / Future | 未立项 | External Agent | 后续 P10-MCP，非 P10-CLI |
| Real market provider | Missing / Future | 未授权 | User | 后续 P10-MARKET-OPTIN，非 P10-CLI |

### P10-CLI assumptions

| 假设 | 验证位置 | 如果错误的风险 |
| --- | --- | --- |
| 后续 CLI 可以调用本地 FastAPI 而不是直接调用 Domain Tools | 当前 API route discovery 已发现必要入口大多存在 | 如果服务不可用频繁，需增加启动提示或 local mode，但不能绕过安全门 |
| `reports open` 可通过文件系统定位 `docs/reports/*.html` | 当前报告目录存在 | 若报告命名不稳定，需要新增 report index，但不能生成虚假报告 |
| `artifacts show` 默认摘要足够，不需要全文 | 当前隐私边界要求不展示敏感全文 | 若用户需要全文，必须增加显式参数和验收门槛 |
| CLI 审计日志可存在 workspace 内或 `.tmp` | 尚未实现 | 路径选择错误可能污染仓库或泄露敏感信息，需在 M0 审计决定 |
| P10-CLI v1 不负责 FastAPI 生命周期管理 | M0 必须冻结 | 如果改为自动启动服务，会引入端口、后台进程和 Windows/WSL 清理风险，需重新立项 |
| `reports open` 只定位/打开报告，不生成报告 | M0 必须冻结 | 如果混入报告生成，会让 CLI 验收边界和 evidence pipeline 混淆 |
| workspace 解析优先级固定为 `--workspace` > `JOBPILOT_WORKSPACE` > 当前目录 `.jobpilot_workspace` > 失败 | M0 必须冻结 | 如果允许隐式扫描，会导致真实资料误读和 Agent 自动调用不稳定 |

## -7. P9.1 真实市场数据、行政区划下钻式地图原型与苏格拉底式资料补全目标架构

P9.1 当前本地自动化候选已完成。它在 P9 已完成的 `TopServiceCenter`、`LeftIntelligencePanel`、`MarketMapView`、`ConversationPlane`、`handleP9Command` 和 `Workbench / P9ArtifactOverview` 基线上，已实现 ECharts 行政区划下钻式市场地图、Market Provider 未配置状态、Socratic Intake、产物台联动和中文 HTML 验收报告；本节不代表真实市场 provider、招聘平台抓取、真实 ASR、真实 provider、自动投递或 MCP/Skill 连通性已经完成。

目标分层：

```text
User
→ Chatbox Experience Shell
  → TopServiceCenter（P9.1 已展示 Market Provider: not_configured）
  → LeftIntelligencePanel（P9.1 已升级市场页为行政区划下钻式市场地图）
    → MarketMapView / MarketIntelligenceMap（P9.1 已实现：ECharts 行政区划下钻情报板、visualMap、tooltip、toolbox、行政区划颜色深浅、城市气泡、选区详情、薪资直方图、来源可信度、面包屑返回）
      → RegionDrilldownController（P9.1 已实现为 React state：current region、breadcrumb、selected region、zoom 和 layer state）
      → AdministrativeRegionLayer（P9.1 已实现为 fixture-only GeoJSON + ECharts registerMap；真实 GeoJSON/provider 仍待单独授权）
    → MarketSourceLegend（P9.1 已实现：fixture / manual / public / opt-in API 状态）
    → MarketInsightDrilldown（P9.1 已实现：城市、薪资、技术栈、source refs 详情）
  → ConversationPlane
    → SocraticIntakeSession（P9.1 已实现：启发式一问一答事实采集）
    → SocraticQuestionPlanner（P9.1 已实现为本地阶段序列：选择下一个最高价值问题）
    → FactConfirmationStrip / PendingConfirmations（P9.1 已实现为右侧产物台摘要）
  → Workbench / P9ArtifactOverview
    → CandidateFactSummary（P9.1 已实现：事实摘要视图）
    → ProjectStoryDraft（P9.1 已实现：STAR/CAR 草稿）
    → JDKeywordMapping（P9.1 保留为后续增强；本轮以故事草稿和 source refs 为主）
    → PendingConfirmations / SourceRefs（P9/P8 已有概念，P9.1 强化展示）
→ API Boundary（P9.1 本轮只实现本地状态表达；不默认外呼真实市场 provider）
  → JobMarketProvider
  → JobSearchRun
  → NormalizedJobPost
  → JobMarketSnapshot
  → AdministrativeRegionNode
  → RegionJobDistributionSnapshot
  → MarketMapLayerState
  → MarketMapDrilldownState
  → RegionSourceRef
→ Domain Boundary（P9.1 本地候选；不新增默认外部平台接入）
  → MarketDataNormalizer
  → SocraticIntakePolicy
  → ProjectStoryEvidenceGuard
→ SQLite Workspace / Artifact / Evidence
```

P9.1 实体状态与职责：

| 层级 | 实体 | 状态 | P9.1 职责 |
| --- | --- | --- | --- |
| UI | `TopServiceCenter` | P9 已实现自动化候选，P9.1 需修改展示 | 增加市场数据 provider 的 not_configured / configured / connected / failed / fixture fallback 状态，但不保存 API Key |
| UI | `LeftIntelligencePanel` | P9 已实现自动化候选，P9.1 需修改 | 保持三页签结构，市场页升级为行政区划下钻式招聘情报地图，匹配和流程页不得抢占 Chatbox 主路径 |
| UI | `MarketIntelligenceMap` | 文档规划 | 替代低保真示意地图，表达行政区划机会、薪资、技术栈和来源可信度；由 `MarketIntelligenceBoard`、`MarketExpandedView`、`AdministrativeDrilldownMap`、`RegionDrilldownController`、`EChartsOptionBuilder`、`AdministrativeRegionLayer`、`CityScatterLayer`、`MarketLayerTabs`、`RegionInsightPanel`、`SourceTrustLegend`、`ChatboxPromptBridge` 组成 |
| UI | `AdministrativeDrilldownMap` | 文档规划 | 负责全国/省/市/区县逐级下钻、地图面包屑、选区放大、hover/click 反馈和 fallback；不得退化为静态 SVG 或普通瓦片地图 |
| UI/State | `RegionDrilldownController` | 文档规划 | 管理 `current_adcode`、`current_level`、`breadcrumb`、`hover_region`、`selected_region`、`zoom`、`pan`、`layer_state`；向 `ChatboxPromptBridge` 输出可追问上下文 |
| UI/Data | `AdministrativeRegionLayer` | 文档规划 | 将合法 GeoJSON 注册到 ECharts map/geo，按 `RegionJobDistributionSnapshot` 映射颜色深浅、tooltip、emphasis 和 selected 状态 |
| UI | `MarketSourceLegend` | 文档规划 | 明确区分 fixture、用户粘贴、公开源、opt-in API，避免把样例数据写成真实市场 |
| UI | `MarketInsightDrilldown` | 文档规划 | 城市点击后展示岗位数、薪资直方图、技术栈热度、remote ratio、source refs 和 Chatbox 追问入口 |
| UI | `ConversationPlane` | P9 已实现自动化候选，P9.1 需修改 | 保持中央主路径，承载市场查询、Socratic Intake 和状态摘要 |
| UI | `SocraticIntakeSession` | 文档规划 | 用一问一答采集简历事实、项目故事、指标和边界 |
| UI/Domain | `SocraticQuestionPlanner` | 文档规划 | 选择下一轮最高价值问题，不做一次性表单 |
| UI | `FactConfirmationStrip` | 文档规划 | 每 3-5 轮展示已确认、待确认和不可声明事实，不阻塞普通聊天 |
| UI | `Workbench / P9ArtifactOverview` | P9 已实现自动化候选，P9.1 需修改 | 展示市场洞察、事实摘要、故事草稿、JD 映射、source refs、pending confirmations |
| API | `JobMarketProvider` | 文档规划，后续 opt-in | 封装 Adzuna、TheirStack、JSearch、Jooble 或公开源，未配置不调用 |
| API | `JobSearchRun` | 文档规划 | 记录 query、城市、薪资、技术栈、provider、结果数、source refs 和边界 |
| Data | `NormalizedJobPost` | 文档规划 | 标准化职位标题、公司、城市、薪资、技术栈、来源和置信度 |
| Data | `JobMarketSnapshot` | 文档规划 | 聚合城市、薪资、技能、来源和趋势，所有数字需可追溯 |
| Data | `AdministrativeRegionNode` | 文档规划 | 描述行政区划树：`adcode`、`name`、`level`、`parent_adcode`、`children_adcodes`、`geojson_ref`、`license_note` |
| Data | `RegionJobDistributionSnapshot` | 文档规划 | 描述某区划的岗位量、薪资中位数、技术栈热度、来源构成、置信度和 `source_refs` |
| UI/Data | `MarketMapLayerState` | 文档规划 | 描述当前图层：机会热度、薪资、技术栈、来源可信度、匹配度；驱动 ECharts visualMap、tooltip 和详情面板 |
| UI/Data | `MarketMapDrilldownState` | 文档规划 | 描述地图当前位置、层级、面包屑、缩放、拖动、选中区域和 fallback 状态 |
| Evidence | `RegionSourceRef` | 文档规划 | 将每个地图数字绑定到 fixture/manual/public/opt-in API 来源，避免无证据市场结论 |
| Domain | `MarketDataNormalizer` | 文档规划 | 将 provider/manual/public/fixture 数据归一化为可审计市场快照，不补造缺失薪资或公司 |
| Domain | `ProjectStoryEvidenceGuard` | 文档规划 | 阻止 Socratic Intake 将未证实贡献、指标、学历或年限写入正式产物 |
| Evidence | P9.1 HTML 原型页 / drawio / 自动化报告 | 已实现候选证据 | 原型页供人类审查目标体验；自动化报告提供真实实现截图 |

P9.1 目标架构与当前 P9 架构差异：

| 当前 P9 实现 | P9.1 目标差异 | 是否新增代码实体 | 验收口径 |
| --- | --- | --- | --- |
| `MarketMapView` 已支持图钉、缩放、拖动和重置 | 升级为 `MarketIntelligenceMap` / `AdministrativeDrilldownMap`，增加行政区划下钻、颜色深浅、面包屑、tooltip、selected feedback、薪资直方图、技术栈热度和来源可信度 | 是，后续开发新增或重构 UI 实体 | 多视口截图证明可读、可下钻、可拖动、可追溯 |
| P9 search run 使用本地/fixture/手动样例 | 增加 `JobMarketProvider` 与 `JobSearchRun` 状态模型，但默认不外呼 | 是，先做 opt-in 状态与契约 | 未配置时显示 not_configured，不伪造真实市场 |
| `handleP9Command` 支持命令式资料补全 | 增加 `SocraticIntakeSession` 和 `SocraticQuestionPlanner` | 是，后续开发新增对话状态 | 10 轮以上一问一答样例，不退化为表单 |
| 右侧已有故事草稿和 pending confirmations | 强化为 `CandidateFactSummary`、`ProjectStoryDraft`、`JDKeywordMapping` 和 `DoNotClaimList` | 部分新增展示模型 | 所有草稿有 source refs 和待确认项 |
| 顶部服务中心展示 provider/ASR/MCP/Skill/search 状态 | 增加真实市场 provider 的 configured/connected/called/failed/fallback 区分 | 修改现有实体 | 状态展示不等于真实连通验收 |

P9.1 架构不变量：

- P9.1 不默认新增真实数据源系统、招聘平台抓取、长期任务或独立业务服务；
- `source_url` 仍不得自动读取网页；
- provider configured 不等于 connected，不等于 called；
- Socratic Intake 不编造事实，不确定内容进入 pending confirmations；
- HTML 原型和目标图样不得替代后续真实界面验收。

P9.1 目标页面总体设计必须按以下前端模块关系落地，后续实现不得再只给抽象功能清单：

```text
ChatboxExperienceShell
├─ TopServiceCenter
│  ├─ ProviderStatusChip（LLM / Market / ASR / MCP / Skill / Workspace）
│  └─ SafetyBoundaryPopover（未授权不外呼、不抓取、不自动投递）
├─ JobMarketIntelligencePanel
│  ├─ MarketIntelligenceMap（ECharts 行政区划情报板 / visualMap / tooltip / toolbox）
│  │  ├─ MarketIntelligenceBoard（左侧完整求职情报板容器）
│  │  ├─ MarketExpandedView（查询 / 图层 / 地图 / 详情 / 证据栏）
│  │  ├─ AdministrativeDrilldownMap（全国 / 省 / 市 / 区县下钻主视图）
│  │  ├─ RegionDrilldownController（adcode / level / breadcrumb / selected / hover / fallback）
│  │  ├─ EChartsOptionBuilder（map / geo / scatter / visualMap / tooltip / toolbox）
│  │  ├─ AdministrativeRegionLayer（合法 GeoJSON choropleth / registerMap / selected emphasis）
│  │  ├─ CityScatterLayer（城市气泡 / 岗位量 / 薪资层）
│  │  ├─ MarketLayerTabs（机会热度 / 薪资 / 技术栈 / 来源可信度）
│  │  ├─ RegionInsightPanel（选区详情 / 薪资直方图 / 技术栈）
│  │  ├─ SourceTrustLegend（fixture / manual / public / opt-in API）
│  │  └─ ChatboxPromptBridge（生成可编辑追问草稿）
│  ├─ MarketSourceLegend（fixture / manual / public / opt-in API）
│  ├─ MarketInsightDrilldown（城市详情 / 薪资直方图 / 技术栈热度 / source refs）
│  ├─ OpportunityMatchPanel（目标 JD / 匹配 / 短板 / 证据覆盖）
│  └─ ApplicationPipelineView（流程状态 / 下一步 / 备注 / Chatbox 更新）
├─ ConversationPlane
│  ├─ JourneyStateStrip（探索市场 / 补故事 / 选 JD / 生成申请包 / 确认事实）
│  ├─ MessageTimeline（连续对话，首屏优先）
│  ├─ SocraticChatbox（一次一个问题，事实采集状态机）
│  ├─ ComposerToolRail（查市场 / 粘贴 JD / 补故事 / 生成申请包）
│  └─ Composer（用户输入与发送）
└─ ArtifactWorkbench
   ├─ CandidateFactSummary
   ├─ ProjectStoryDraft
   ├─ JDKeywordMapping
   ├─ SourceRefs
   ├─ PendingConfirmations
   └─ ExportPreflight
```

模块状态约束：

| 模块 | P9 当前状态 | P9.1 目标状态 | 验收证据 |
| --- | --- | --- | --- |
| `TopServiceCenter` | 已实现自动化候选 | 增加 Market Provider 明确状态和安全解释 | 顶部状态截图，未配置时不显示 connected/called |
| `MarketMapView` | 已实现但低保真 | 升级为 `MarketIntelligenceMap`，具备情报地图语义 | 多视口地图截图、缩放/拖动/点击证据 |
| `ConversationPlane` | 已是中央路径但仍有任务卡负担 | Chatbox 主体优先，状态条紧凑，工具入口靠近输入框 | 首屏截图证明 Chatbox 优先 |
| `SocraticChatbox` | 文档规划 | 一问一答采集事实，状态机可见 | 多轮对话日志和右侧产物截图 |
| `ArtifactWorkbench` | 已实现自动化候选 | 强化事实摘要、故事、JD 映射、source refs、pending confirmations | 产物台同步更新截图 |

响应式结构必须保持 Chatbox-first：

- 1920px / 1440px：四区同时可见，中央 Chatbox 宽度最大；
- 1200px：三栏保留但左/右压缩，输入框、发送和工具入口不得被挤压；
- 720px：Chatbox 为默认主视图，市场和产物作为辅助面板；
- 390px：默认只展示 Chatbox，地图和产物台通过全屏抽屉或页签打开。

## -6. P9 Chatbox-native 求职情报与申请包工作台目标架构

P9 当前已完成第一轮自动化候选实现。目标是在 P8.1 自动化候选基线上，把产品从“向导卡片工作台”调整为 Chatbox-native 求职情报与申请包工作台；当前实现仅覆盖本地 UI 信息架构、求职态势可视化层和现有能力重新组织。

目标分层：

```text
User
→ Chatbox Experience Shell (`apps/chatbox/src/main.tsx`)
  → TopServiceCenter（顶部服务中心，已实现自动化候选）
  → LeftIntelligencePanel（左侧求职态势图，已实现自动化候选）
    → MarketMapView（地图 / 图钉 / 缩放 / 拖动 / 重置，已实现自动化候选）
    → OpportunityMatchPanel（目标机会与匹配，已实现自动化候选）
    → ApplicationPipelineView（投递流程态势，已实现自动化候选）
  → ConversationPlane（中央 Chatbox，已修改为主路径）
    → Agent State / workflow strip（用户历程状态，已改造）
    → MessageTimeline（已实现基线，必须首屏优先）
    → Composer tool actions（输入框工具入口，已修改）
    → handleP9Command（对话意图路由，已实现自动化候选）
  → Workbench / P9ArtifactOverview（右侧产物台，已修改）
    → CandidateProfileSummary（已实现候选）
    → JobTargetList / ResumeGenerationPlane（已实现候选，已重排到产物台语义）
    → story draft / application package summary（本地自动化候选，真实 story service 待后续）
→ FastAPI Agent Service (`services/api/main.py`, `services/api/schemas.py`)
  → Provider / Service Health（已有基础，P9 通过 UI 状态展示）
  → Job Source / Search Runs（P9 使用用户粘贴、fixture、已导入 JD 和本地 search run 状态）
  → Profile / Resume / Application Package routes（复用已实现能力）
→ Domain Tools
  → JobSourceConnector boundary（未落成独立外部平台服务；P9 仅保留合规边界）
  → CandidateFactGraph / StoryBank boundary（P9 使用本地故事草稿和现有 profile/resume/artifact 能力）
  → ResumePackageGenerator / resume routes（复用已有基础并通过 Chatbox 触发）
  → ApplicationPipeline local state（P9 使用 localStorage 和 UI 状态，不对外沟通或投递）
→ SQLite Workspace / Artifact / Evidence
```

P9 代码实体状态与职责：

| 层级 | 实体 | 状态 | 上游 / 下游 | P9 职责 |
| --- | --- | --- | --- | --- |
| UI | `TopServiceCenter` | 已实现自动化候选 | 上游读取本地 provider/JD/ASR/MCP/Skill/workspace 状态；下游打开设置 | 展示 provider、ASR、MCP、Skill、JD 信息源、workspace、安全边界状态 |
| UI | `LeftIntelligencePanel` | 已实现自动化候选 | 上游读取本地 job/search/pipeline 摘要；下游联动 Chatbox | 承载岗位市场、目标机会、投递流程三大页签 |
| UI | `MarketMapView` | 已实现自动化候选 | 上游读取本地城市样例与 search run；下游触发城市/技术栈追问 | 地图、图钉、缩放、拖动、重置 |
| UI | `OpportunityMatchPanel` | 已实现自动化候选 | 上游读取 `job`、`match_report`、`candidate_profile` 和本地样例；下游选择当前目标 | 展示多 JD 匹配、短板、证据覆盖和优先级 |
| UI | `ApplicationPipelineView` | 已实现自动化候选 | 上游读取本地 pipeline state；下游通过 Chatbox 更新 | 展示投递流程、颜色状态、下一步动作和备注 |
| UI | `ConversationPlane` | 已修改为 P9 主路径 | 上游接收用户输入；下游触发 `handleP9Command` / 现有 API | 保持中央主路径，承载时间线、状态、输入框和工具入口 |
| UI | `Agent State / workflow strip` | 已改造 | 上游读取 workflow state；下游解释当前行动 | 展示探索市场、补资料、选 JD、生成申请包、确认事实等状态 |
| UI | `Workbench / P9ArtifactOverview` | 已实现自动化候选 | 上游读取 artifact / profile / resume / local P9 state；下游确认和导出 | 展示事实摘要、简历、故事、申请包、source refs 和 pending confirmations |
| API | `JobSourceConnector` routes | 未新增独立服务；P9 复用现有边界 | 上游 Chatbox/search run；下游现有 job/domain 能力 | P9 只归档本地 search run 表达，不登录平台、不抓取平台 |
| Domain | `StoryBank` | 未新增独立服务；P9 以本地故事草稿覆盖自动化候选 | 上游用户资料/Chatbox；下游申请包展示 | 管理项目故事草稿和待确认事实；真实 story service 后续单独规划 |
| Domain | `ApplicationPipelineService` | 未新增独立服务；P9 以 localStorage/UI 状态覆盖自动化候选 | 上游 Chatbox 更新；下游 pipeline UI | 管理本地投递流程状态，不对外发送消息 |
| Storage | `job`, `match_report`, `candidate_profile`, `resume_version`, `artifact` | 已实现自动化候选 | 上游 P8/P5.5；下游 P9 UI | 复用既有事实、岗位、画像、简历和产物数据 |
| Evidence | `docs/reports/`, browser screenshots | 已完成 P9 阶段收口报告 | 上游自动化验收；下游人工审查 | 证明多视口真实界面和 P9 目标路径 |

P9 架构不变量：

- Chatbox 是第一交互路径，左侧态势图和右侧产物台不能抢占中央对话。
- 顶部服务中心只展示配置/连通/安全状态，不保存 API Key，不默认外呼。
- JD 搜索默认只允许用户粘贴、fixture 或合规公开源；招聘平台登录、绕风控和自动投递必须独立立项。
- ASR 只能作为用户明确开启的资料补全入口，不得默认采集麦克风。
- 所有申请包草稿必须有 source refs、pending confirmations 和版本边界。
- Chatbox 不直接写 SQLite、不直连真实 provider；必须通过 API / Domain 边界。
- 验收报告必须使用真实界面截图，不能以概念图、AI 目标图或原型图替代实现证据。

P9 架构范围锁：

- `TopServiceCenter` 是 control-plane visibility，不是 provider、ASR、MCP 或 Skill 执行平台；
- `LeftIntelligencePanel` 是求职情报可视化层，不是 BI 分析引擎或长期数据任务系统；
- `JobSourceConnector` 在 P9 只允许作为现有 API/Domain 内的轻量边界或接口命名，不得落成独立平台接入服务；
- `MarketMapView` 在 P9 只展示用户粘贴、fixture、已有本地示例或合规公开样例数据，不负责真实全网搜索；
- `VoiceIntakeSession` 或 ASR 相关实体若后续出现，只能作为 opt-in 状态和文本引导边界，不得默认采集麦克风或调用外部语音服务；
- `ApplicationPipelineService` 只更新本地 workspace/artifact 状态，不对外发送消息、不自动沟通、不自动投递；
- P9 不新增独立业务服务，不新增长期运行调度任务，不新增真实外部数据源系统。

## -5. P8.1 Chatbox-first 工作台信息架构目标

P8.1 当前只做文档开发，不新增代码实现。目标是在 P8 已完成能力基础上修正前端信息架构，让 `apps/chatbox/src/main.tsx` 中的三栏工作台恢复为 Chatbox-first：

```text
User
→ Chatbox Experience Shell (`apps/chatbox/src/main.tsx`)
  → DesktopContextPanel / User Guidance（左侧，辅助）
  → Conversation Plane / Chatbox（中央，主路径）
    → Agent State Machine（紧凑状态）
    → Message Timeline（首屏可见）
    → Composer（始终可达）
    → Composer Tool Rail（上传资料 / 粘贴 JD / 选择岗位 / 生成简历）
  → Workbench（右侧，产物和确认）
    → Job Target List
    → Candidate Profile Summary
    → Resume Draft / Resume Version
    → Source refs / Pending confirmations / Export preflight
→ FastAPI Agent Service (`services/api/main.py`, `services/api/schemas.py`)
→ Domain Tools (`services/tools/jobpilot.py`, `services/profile/candidate.py`)
→ SQLite Workspace / Artifact / Evidence
```

P8.1 不改变 API、Domain Tool、SQLite 或 Artifact 的业务语义。它只规定 UI 平面的职责和首屏优先级：

| UI / 代码实体 | 当前 P8 风险 | P8.1 目标职责 | 状态 |
| --- | --- | --- | --- |
| `DesktopContextPanel` | 左侧指导弱，用户仍依赖中央表单理解资料需求 | 展示资料清单、缺失影响、示例路径和下一步建议 | 待 P8.1 实现 |
| `Conversation Plane` | `p8-workflow-strip` 位于 timeline 前，抢占中央首屏 | 作为中央主路径，优先展示 Agent 状态、聊天时间线和输入框 | 待 P8.1 修改 |
| `p8-workflow-strip` | 把资料/JD/简历生成入口做成中央大块任务区 | 降级为输入框附近工具条、弹层、抽屉或左右辅助面板入口 | 待 P8.1 修改 |
| `MaterialIntakeWizard` | 可见但过重，容易让用户先填表而不是聊天 | 提供资料说明和补充入口，优先由左侧指导或轻弹层承载 | 待 P8.1 调整 |
| `JDIntakeCenter` | 可见但与聊天主路径竞争 | 通过输入框工具入口触发，结果进入右侧岗位列表 | 待 P8.1 调整 |
| `JobTargetList` | 与资料/JD/简历入口混在中央任务区 | 右侧工作台展示多个 JD、当前目标和匹配摘要 | 待 P8.1 调整 |
| `ResumeGenerationPlane` | 作为表单入口抢占对话区 | 由对话意图或输入框工具触发，结果进入右侧简历草稿 | 待 P8.1 调整 |
| `Workbench` | 空态和产物职责需要更稳定 | 展示岗位、画像、简历、source refs、待确认项和导出前检查 | 待 P8.1 强化 |
| `styles.css` responsive rules | 不同屏幕下容易出现优先级混乱或按钮错位 | 桌面三栏、平板/移动 Chatbox 默认优先，辅助面板可抽屉化 | 待 P8.1 强化 |

P8.1 代码实体与分层关系必须按以下方向表达，后续 drawio 和开发计划不得改写为抽象能力清单：

```text
User action
→ DesktopContextPanel（辅助说明，不写业务数据）
→ Conversation Plane（主路径：状态机、timeline、composer、tool rail）
→ P8 UI tools（Material/JD/Job/Resume 只作为轻入口）
→ FastAPI Boundary（现有 P8 API，不由 P8.1 重写语义）
→ Domain Tools（jobpilot / candidate profile / export guard）
→ SQLite Workspace + Artifact（document/job/match_report/resume_version）
→ Workbench（右侧读取产物和确认项）
→ Evidence（真实截图、HTML 报告、PRD 检视）
```

实体状态定义：

- `已实现自动化候选`：P8 或更早阶段已经有本地/mock、fake provider、synthetic-style workspace、dry-run 或截图证据；
- `P8.1 待修改`：本阶段后续自动化开发需要调整布局、状态展示或响应式行为的现有实体；
- `P8 能力保留但重排`：业务能力已存在，但入口位置和视觉优先级必须调整；
- `禁止/高风险`：不得在 P8.1 默认实现，包含平台抓取、真实 provider 默认外呼、真实资料默认读取和自动投递。

P8.1 架构不变量：

- Chatbox 是默认入口和中央主路径；
- 资料准备、JD 导入和简历生成能力必须保留，但不得把聊天挤出首屏；
- 普通聊天不静默写 artifact，明确生成/刷新/导出才进入工具路径；
- `source_url` 仍只归档，不触发平台抓取；
- Chatbox 不直接写 SQLite、不保存 API Key、不直连真实 provider；
- 报告必须用真实界面截图验证多视口，不得用设计稿替代。

## -4. P8-JD Intake 与简历生成体验强化目标架构

当前文档阶段的目标是把“用户不知道该提供什么资料”“没有清晰 JD 导入路径”“简历生成不够围绕目标岗位”三个体验问题转化为可执行架构规格。本阶段只做文档开发，不新增代码实体。

P8 目标架构链路：

```text
User
→ Chatbox Experience Shell (`apps/chatbox/src/main.tsx`)
  → Material Intake Wizard
  → JD Intake Center
  → Job Target List
  → Resume Generation Plane
  → Workbench / Artifact Review Plane
→ FastAPI Agent Service (`services/api/main.py`, `services/api/schemas.py`)
  → document upload / ingest boundary
  → job intake / parse boundary
  → job list boundary
  → resume generation boundary
→ Domain Tools (`services/tools/jobpilot.py`, `services/profile/candidate.py`)
  → document / career_fact / skill_evidence
  → job / match_report
  → candidate_profile / source refs
  → resume_version / application_package
→ Storage / Evidence
  → SQLite workspace
  → artifact / artifact_version
  → HTML acceptance report and screenshots
```

P8 v1 必须复用现有核心实体，避免为了体验入口过早重写业务层：

| 目标能力 | 当前可复用实体 | P8 计划职责 | 禁止职责 |
| --- | --- | --- | --- |
| 资料准备向导 | `document.kind`, upload / ingest routes | 将资料分为简历、项目经历、作品链接、目标 JD、求职偏好，并解释用途和缺失影响 | 不扫描用户个人目录；不读取未授权路径 |
| JD 导入中心 | `job`, `job.source_url`, JD parse tools | 保存用户粘贴 JD、来源 URL、平台来源和备注，生成可读岗位列表 | 不因 URL 自动抓取网页；不登录招聘平台 |
| 岗位列表与目标选择 | `job`, `match_report`, artifact refs | 展示多个 JD 的解析状态、匹配摘要和当前目标岗位 | 不把缺失公司/地点/薪资自动补成事实 |
| JD 定制简历 | `resume_version`, `application_package`, `artifact_version` | 基于目标 JD 生成 Markdown 简历草稿、source refs、待确认项和导出 preflight | 不编造未证实经历；普通聊天不静默覆盖简历 |
| 证据和报告 | `docs/reports/`, browser evidence scripts | 生成中文 HTML 报告、截图、PRD 检视和未验证范围 | 不声明 BOSS/平台自动接入或真实 provider 通过 |

### P8 代码实体状态与分层关系

后续实现必须按分层依赖推进，不能把 UI、API、Domain Tool、SQLite 和验收证据混成一个不可审查的大改动。

状态定义：

- `已实现自动化候选`：现有代码或报告已经有本地/mock、fake provider、synthetic-style workspace 或 dry-run 证据；
- `已实现自动化候选`：P8 已在本地/mock + 受控真实感数据下完成实现和自动化验收；
- `后续独立阶段`：真实 provider、真实个人资料、招聘平台自动化、自动投递、SaaS 等仍需单独授权；
- `禁止/高风险`：不能在 P8 默认实现，必须另行授权或独立立项。

| 分层 | 代码实体 | 当前状态 | P8 职责 | 上游 / 下游 |
| --- | --- | --- | --- | --- |
| Chatbox UI | `apps/chatbox/src/main.tsx` | 已实现自动化候选 | 承载资料准备向导、JD 导入中心、岗位列表、当前目标岗位、JD 定制简历入口 | 上游：用户动作；下游：FastAPI routes |
| Chatbox UI | `apps/chatbox/src/styles.css` | 已实现自动化候选 | 五类资料卡、JD 列表、响应式布局、状态标签和按钮对齐 | 上游：UI 状态；下游：多视口截图验收 |
| Chatbox UI | `MaterialIntakeWizard` / `JDIntakeCenter` / `JobTargetList` / `ResumeGenerationPlane` | 已实现自动化候选 | 把“上传资料”拆成可理解任务，把 JD 和简历生成变成可见流程 | 上游：Chatbox shell；下游：API Boundary |
| API Boundary | `services/api/main.py` | 已实现自动化候选 | 增加或扩展 job intake、jobs list、resume generate 路由 | 上游：Chatbox；下游：Domain Tools |
| API Boundary | `services/api/schemas.py` | 已实现自动化候选 | 定义 `JobIntakeRequest`、`JobSelectRequest`、`ResumeGenerateRequest` 等 schema | 上游：UI form state；下游：route validation |
| API Boundary | `POST /api/job/intake` | 已实现自动化候选 | 保存用户粘贴 JD、来源 URL、平台标签和备注；不抓取 URL | 上游：JD Intake Center；下游：`job` / `match_report` |
| API Boundary | `GET /api/jobs` | 已实现自动化候选 | 返回岗位列表、解析状态、匹配摘要、当前目标岗位 | 上游：Job Target List；下游：`job` / `match_report` |
| API Boundary | `POST /api/resume/generate` | 已实现自动化候选 | 基于 `job_id` 生成 JD 定制简历版本 | 上游：Resume Generation Plane；下游：`resume_version` / artifact |
| Domain Tools | `services/tools/jobpilot.py` | 已实现自动化候选 | 复用 ingest、parse_jd、match、application_package、export；扩展 JD 来源保存和目标 JD 简历生成 | 上游：API routes；下游：SQLite / Artifact |
| Domain Tools | `services/profile/candidate.py` | 已实现自动化候选 | 作为简历生成证据层，提供 CandidateProfile、能力矩阵、项目可信度、岗位短板 | 上游：career/project/job facts；下游：resume generation |
| Safety Guards | source refs / pending confirmations / export preflight | 已实现机制，P8 必须强制使用 | 缺证据内容进入待确认；blocking 项未确认不得正式导出 | 上游：Domain Tools；下游：Export / Evidence |
| Storage | `document` | 已实现自动化候选 | 规范 `kind=resume|project|portfolio|preference|jd`，承载五类资料输入 | 上游：upload/ingest；下游：facts/profile/resume |
| Storage | `job` / `match_report` | 已实现自动化候选 | 承载 JD 解析、`source_url`、`platform`、匹配摘要和当前目标岗位 | 上游：job intake；下游：job list/resume generation |
| Storage | `resume_version` | 已实现自动化候选 | 保存目标 JD 简历版本、状态、source refs 和待确认项 | 上游：resume generation；下游：Export / report |
| Storage | `application_package` / `artifact` / `artifact_version` | 已实现自动化候选 | 复用版本、source refs、确认项、导出机制 | 上游：Domain Tools；下游：Workbench / Evidence |
| Evidence | `docs/reports/` / `docs/reports/evidence/` | 已实现自动化候选 | 生成中文 HTML 报告、1200px/720px/390px 截图、PRD 检视和未验证范围 | 上游：E2E flow；下游：人工审查 |

禁止实体关系：

- Chatbox 不直接写 SQLite，不保存 API Key，不直连真实 provider；
- `source_url` 不触发自动网页抓取；
- `platform` 只作为用户标注和报告来源，不代表招聘平台已接入；
- P8 不新增招聘平台账号、密码、cookie、验证码或绕风控实体；
- 普通聊天不能静默覆盖 `resume_version`；
- 缺少 source refs 的简历内容只能进入 pending confirmations，不能写成事实。

P8 建议最小接口契约：

| 用户动作 | 建议接口 / 模块 | 输入 | 输出 | 约束 |
| --- | --- | --- | --- | --- |
| 上传分类资料 | 扩展 `POST /api/files/upload` | `workspace_id`, `file`, `kind=resume|project|portfolio|notes|jd` | document artifact | 兼容旧 `upload`；不读取 workspace 外路径 |
| 导入 JD | `POST /api/job/intake` | `workspace_id`, `jd_text`, `source_url?`, `platform?`, `import_method`, `user_notes?` | parsed job, match suggestion | 不抓取 URL，只保存来源 |
| 查看岗位列表 | `GET /api/jobs` | `workspace_id` | job list, parse status, match summary | 不返回完整敏感资料 |
| 生成定制简历 | `POST /api/resume/generate` | `workspace_id`, `job_id?`, `mode`, `language`, `style` | resume_version, source refs, pending confirmations | 不编造未证实经历 |

P8 架构不变量：

- Chatbox 仍是薄入口，不直接写 SQLite、不保存 API Key、不直连 provider；
- URL 字段只作为归档和 source refs，不触发平台抓取；
- JD 定制简历必须绑定 `job_id` 或明确为通用简历；
- 每个核心简历亮点必须有 source refs 或待确认项；
- blocking 待确认项未处理时不得正式导出；
- BOSS / 猎聘 / 拉勾等招聘平台接入必须单独合规立项；
- P8 完成不代表自动投递、平台沟通、真实 provider 或真实资料路径通过。

## -3. P6-REAL / P7-post 文档准备目标架构

当前文档阶段的目标是把已完成的自动化候选能力和仍待执行的真实验收路径分开。后续所有架构图、验收报告和开发计划必须使用三类状态：

- `已实现自动化候选`：本地/mock、fake provider、synthetic-style workspace、脱敏 fixture 或 dry-run 已有测试和截图证据；
- `待真实验收`：需要用户明确确认后才可执行的真实 provider、真实个人资料、真实 JD、真实资料导出或真实调用质量验证；
- `后续独立阶段`：SaaS、ASR、会议平台、自动投递、MCP/CLI、workspace 删除/迁移 apply 等 P8+ 或高风险能力。

P6-REAL 目标架构链路：

```text
User
→ Chatbox Experience Shell (`apps/chatbox/src/main.tsx`)
  → Model Settings / Provider Consent UI
  → Conversation Plane
  → Long-running Chat State View
→ FastAPI Agent Service (`services/api/main.py`, `services/api/schemas.py`)
  → Provider status / preferences / consent routes
  → Chat message route
→ Chat Orchestrator (`services/chat/core.py`)
  → Long Context Manager (`services/chat/context.py`)
  → Provider-backed Dialogue Adapter (`services/chat/provider_backed.py`)
  → Local Fallback Dialogue
→ Provider Runtime / Policy (`services/llm/`, provider policy modules)
  → Provider Policy Gate
  → Provider Invocation Log
→ Evidence Layer
  → P6-REAL controlled acceptance report
  → redaction scan
  → provider configured / consented / called / failed / fallback evidence
```

P7-post P5-REAL 目标架构链路：

```text
User explicit file authorization
→ Real-data acceptance runner (`scripts/generate_p5_real_data_acceptance.py`)
→ Workspace sandbox and source path validator
→ Profile / Project / Job / Match tools (`services/tools/`, `services/profile/candidate.py`)
→ Artifact / source refs / export preflight
→ Redacted P5-REAL report
→ P5 closure audit
```

本阶段不新增代码实体，只把上述实体的状态、边界、验收输入和出门条件写清。任何真实 provider 调用、真实个人资料读取、workspace 删除、迁移 apply 或 SaaS/ASR/会议平台/自动投递执行都必须在用户确认后另行进入执行阶段。

## -2. P5.5 历史阶段架构主线

P5.5 在 P5 本地资料闭环和 P6/P7 本地 Beta 自动化候选基线上推进。目标不是重写系统，也不是引入外部画像服务，而是在现有本地优先架构中增加一个可审查的 Candidate Profile 平面：

```text
User
→ Chatbox Experience Shell
  → Conversation Plane
  → Candidate Profile Workbench
  → Capability Matrix View
  → Project Credibility View
  → Job Gap View
→ FastAPI Agent Service
  → Profile Aggregation Routes
  → Artifact / Chat / Job / Workspace Routes
→ Profile Orchestrator
  → CandidateProfile Aggregator
  → Evidence Scorer
  → Project Credibility Evaluator
  → Job Gap Analyzer
  → Profile Refresh Guard
→ Domain Data Layer
  → candidate_profile
  → career_fact
  → skill_evidence
  → tech_project
  → job / match_report
  → artifact / artifact_version / source_refs
→ Evidence Layer
  → P5.5 Visual Acceptance Report
  → PRD Spec Review
  → Privacy and Fantasy-claim Audit
```

## -1. P5.5 代码实体与职责

| 层级 | 具体代码实体 | 当前状态 | P5.5 职责 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox UI | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 已实现自动化候选 | 展示画像概览、能力矩阵、项目可信度、岗位短板、source refs 和下一步建议 | 不直接推断敏感属性；不保存 API Key；不直连 provider |
| API 边界 | `services/api/main.py`, `services/api/schemas.py` | 已实现最小路由/Schema | 暴露 profile summary、capability matrix、project credibility、gap analysis 的读取/刷新入口 | 不返回完整未授权资料；不把缺证据写成已证实 |
| Profile Aggregator | `services/profile/candidate.py` | 已实现自动化候选 | 从 career_fact、skill_evidence、tech_project、job、match_report 聚合 CandidateProfile | 不引入复杂外部画像服务 |
| Evidence Scorer | `services/profile/candidate.py` | 已实现自动化候选 | 给技能和经历标注 strong / usable / weak / missing 或等价等级 | 不做人格、潜力或敏感属性评分 |
| Project Credibility Evaluator | `services/profile/candidate.py` | 已实现自动化候选 | 评估本人贡献、技术难点、可验证材料、量化结果缺口和风险标签 | 不把未确认贡献写成事实 |
| Job Gap Analyzer | `services/profile/candidate.py` | 已实现自动化候选 | 将能力矩阵与 JD must/nice requirements 对齐，输出短板和补强行动 | 不输出不可行动的否定性评价 |
| Storage | `candidate_profile`, `career_fact`, `skill_evidence`, `tech_project`, `job`, `match_report`, `artifact` | 基础表已存在 | 作为画像事实和证据来源；必要时写入 profile artifact/version | 不写 workspace 外路径；不丢 source refs |
| ChatCore | `services/chat/core.py` | 已复验自动化候选 | 支持画像状态查询和普通追问；明确画像刷新才触发工具 | 普通聊天不写画像 artifact |
| Evidence | `docs/reports/`, browser evidence scripts | 已生成 P5.5 报告 | 生成 P5.5 中文 HTML 报告、多视口截图、PRD 规格检视 | 不把合成资料写成真实个人资料通过 |

## -0.0.1 P5.5 最小接口和数据契约

P5.5 v1 采用最小可逆路线：新增 profile 读取/刷新 API，复用既有 SQLite 表和 artifact/version，不新增数据库表。

| 用户动作 | 默认接口 / 模块 | 输入 | 必须返回或产生 | 约束 |
| --- | --- | --- | --- | --- |
| 查看画像 | `GET /api/profile/candidate` | `workspace_id`, 可选 `job_id` | profile summary、capability matrix、project credibility、job gaps、source refs、artifact ref | 只读；无画像时返回空态和下一步 |
| 刷新画像 | `POST /api/profile/candidate/refresh` | `workspace_id`, 可选 `job_id`, `target_role` | 更新 `candidate_profile`，写入 `artifact_type=candidate_profile` artifact/version | 不访问 workspace 外路径；不调用真实 provider |
| 追问画像 | `POST /api/chat/message` | 普通自然语言问题 | 基于当前 profile/artifact 的解释性回复 | 普通追问不写画像 artifact |

`candidate_profile` 行保存摘要字段；完整能力矩阵、项目可信度、岗位短板和证据链保存为 `candidate_profile` artifact 的 `content_json`，并继承 artifact/version/source refs/confirmation 机制。

默认证据等级：

- `strong`：有 source refs 且用户确认或有明确项目/文档证据；
- `usable`：有来源但缺量化结果或本人贡献确认；
- `weak`：只有单一线索或表达模糊；
- `missing`：JD 要求中出现但 workspace 没有可追踪证据。

默认项目可信度：

- `verified`：本人贡献、技术难点、可验证材料均有来源；
- `plausible`：有项目来源但缺量化结果或验证材料；
- `needs_evidence`：缺本人贡献或技术细节；
- `risky`：存在未确认贡献、夸大风险或与 JD 表达冲突。

## -0.1 P5.5 自动化候选架构与目标差距

| 当前实现 | P5.5 目标 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| 已有 `candidate_profile` 表，P5.5 已形成用户可见画像闭环 | CandidateProfile 聚合并在 Workbench 可读展示 | 已完成自动化候选 | profile summary API/UI 截图 |
| `career_fact` 可保存事实和技能线索 | 专业背景画像和经历可信边界 | 已完成自动化候选 | source refs 和待确认项截图 |
| `skill_evidence` 可保存技能证据 | 能力矩阵、证据强度、岗位相关性 | 已完成自动化候选 | capability matrix eval |
| `tech_project` 可保存项目卡 | 项目可信度、本人贡献、技术难点、验证材料缺口 | 已完成自动化候选 | project credibility eval |
| `job` / `match_report` 已有岗位解析和匹配 | 岗位短板、补强建议和优先级 | 已完成自动化候选 | gap analysis eval |
| Artifact/Export 已保留版本和 source refs | 画像 artifact 可追溯、可刷新、可报告 | 已复验自动化候选 | artifact/source refs eval |
| P5/P6/P7 报告链路成熟 | P5.5 可视化验收报告 | 已完成自动化候选 | 中文 HTML 报告和真实界面截图 |

## -0.2 P5.5 架构不变量

- source refs 是画像判断的核心，不得隐藏；
- 缺少证据时必须输出 missing / weak / needs confirmation，而不是补全事实；
- 能力评估只评价证据强弱、岗位相关性和补强行动，不评价人格、身份或敏感属性；
- 普通连续聊天不得误写画像产物；
- 真实个人资料和真实 provider 仍需用户确认；
- P5.5 完成不代表 P5-REAL、SaaS、ASR、会议平台、自动投递或 MCP/CLI 已通过。

## -1. P6+P7 自动化候选基线架构主线

以下 P6+P7 内容作为已完成自动化候选和后续复验边界保留。P6+P7 在 P4 已冻结 Chatbox 工作台和 P5 自动化候选本地资料闭环基线上推进。P5-REAL/P5-Freeze 当前为冻结延期复验，不作为 P6/P7 开发前置；P7 完成后再执行 P7-post 真实资料复验。

该历史阶段的目标不是重写系统，也不是把外部 provider 变成默认路径，而是在现有本地优先架构中增加四个可审计平面。P6+P7 已作为自动化候选基线保留，不是当前 P5.5 的新增开发目标：

```text
User
→ Chatbox Experience Shell
  → Model Settings / Provider Consent UI
  → Conversation Plane
  → Long-running Chat State View
  → Workbench and Artifact Review Plane
→ FastAPI Agent Service
  → Chat Routes
  → Provider Status / Consent Routes
  → Workspace Lifecycle Routes
  → Diagnostics Routes
  → Artifact / Export Routes
→ Chat Orchestrator
  → Intent Router
  → Long Context Manager
  → Provider-backed Dialogue Adapter
  → Local Fallback Dialogue
  → Tool Intent Confirmation
→ Provider Policy Gate
  → Opt-in authorization
  → API Key availability check
  → Redaction boundary
  → Budget / timeout / retry policy
  → External-call denial by default
→ Domain Tool Layer
  → Profile / Project / Job / Match / Application / Interview Tools
→ Artifact / Export / Storage Layer
  → Artifact Service
  → Export Service
  → SQLite Workspace
  → Workspace Backup / Cleanup / Migration Dry-run
→ Evidence and Operations Layer
  → Provider Invocation Log
  → Diagnostics Report
  → Visual Acceptance Report
  → Privacy / Redaction Audit
```

## -0. P6+P7 代码实体与职责

| 层级 | 具体代码实体 | P6/P7 状态 | 当前阶段职责 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox UI | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 自动化候选已实现；真实 provider 验收待执行 | 展示模型设置、provider opt-in、外呼确认、长对话状态、上下文摘要、失败降级、workspace 生命周期入口 | 不保存 API Key；不直连 provider；不伪造 provider called |
| API 边界 | `services/api/main.py` | 自动化候选已实现；真实 provider/真实资料复验待执行 | 提供 provider consent/status、chat provider mode、workspace backup/cleanup/diagnostics 等最小路由 | 不回传密钥；不允许未确认外呼；不执行不可逆操作默认确认 |
| Chat Orchestrator | `services/chat/core.py` | 自动化候选已实现；真实 provider 质量待验收 | 统一自由聊天、状态查询、澄清、工具意图、provider-backed 回复和 local fallback | 普通聊天不写 artifact；不绕过 tool confirmation |
| Long Context Manager | `services/chat/context.py` 或等价模块 | 自动化候选已实现；真实 provider 上下文质量待验收 | 管理 recent message window、rolling summary、workspace context snapshot、artifact/JD/profile retrieval | 不把完整历史或完整个人资料无边界发送给 provider |
| Provider Adapter | `services/llm/` provider runtime 及 chat adapter | fake provider 自动化候选已实现；受控真实 provider 待用户确认 | 接入 OpenAI-compatible/MiniMax/DeepSeek 类 provider，支持 timeout/retry/schema validation | 不在缺 consent 时调用；不把 raw response 直接写入 artifact |
| Provider Policy Gate | provider policy/runtime 相关模块 | 自动化候选已强化；真实外呼门槛待复验 | 校验 opt-in、API Key、provider/model、脱敏、预算、外呼次数和失败降级策略 | 不把 provider configured 当作 provider called |
| Provider Invocation Log | tool invocation / provider log 相关存储 | 自动化候选已实现；真实调用日志待复验 | 记录脱敏元数据、耗时、状态、错误类型、token 估算和 redaction 摘要 | 不记录 API Key、完整 prompt、完整个人资料、完整 raw response |
| Local Fallback Dialogue | `services/chat/core.py` | 自动化候选已实现 | provider 不可用时保持本地连续对话、状态查询和下一步建议 | 不声称 provider-backed 质量 |
| Artifact/Export Guard | artifact/export 相关服务 | 自动化候选已复验；真实 provider 场景待复验 | 确保 provider-backed chat 不绕过 confirmation、source refs、version 和 export preflight | 不允许 blocking confirmation 未处理仍正式导出 |
| Workspace Lifecycle | SQLite workspace、本地文件目录、lifecycle service | dry-run/diagnostics 自动化候选已实现；删除/迁移 apply 未执行 | 支持恢复、导出、清理、备份、迁移 dry-run 和不可逆操作确认 | 不默认删除 workspace；不写 workspace 外路径 |
| Diagnostics | diagnostics/report service | 自动化候选已实现；真实资料脱敏诊断待复验 | 生成脱敏诊断包、错误摘要、版本信息和本地环境检查 | 不包含密钥、完整个人资料或 provider raw response |
| Evidence | `docs/reports/`, screenshot/test scripts | 自动化候选报告已实现；真实 provider/真实资料报告待执行 | 生成 P6/P7 中文 HTML 报告、真实界面截图、PRD 规格检视和未验证范围 | 不做虚假验收；不抢占焦点前静默截图 |

## -0.1 P6+P7 当前架构与目标差距

| 当前实现 | P6/P7 目标 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| P4/P5 本地 Chatbox 可用，mock/local 默认 | 支持 provider opt-in 且默认不外呼 | 自动化候选已实现；真实 provider 调用待验收 | 初始页、模型设置、调用前确认截图 |
| P1 已有 OpenAI-compatible provider 基础 | provider-backed 自由聊天 adapter，覆盖 MiniMax/DeepSeek/OpenAI-compatible 配置 | fake provider 自动化候选已实现；真实 provider 质量待验收 | fake provider eval、受控真实 provider 验收记录 |
| P4C/P5-FC 已有本地连续对话 | Long Context Manager 支持 20-50 轮、滚动摘要、刷新恢复 | 自动化候选已实现；真实 provider 上下文质量待验收 | 20-50 轮 eval、刷新恢复截图 |
| provider invocation/tool log 已有基础 | 脱敏 invocation log 明确 configured/called/failed/fallback | 自动化候选已强化；真实调用日志待复验 | 日志脱敏 eval、报告扫描 |
| Artifact/Export guard 已支撑 P5 | provider-backed chat 不绕过 confirmation/export preflight | 自动化候选已复验；真实 provider 场景待复验 | 普通聊天不写 artifact、blocking 仍拦截导出 |
| workspace 可初始化和恢复 | 生命周期管理、备份、导出、清理、迁移 dry-run | dry-run 自动化候选已实现；删除/迁移 apply 未执行 | workspace lifecycle eval、不可逆确认截图 |
| 报告和截图链路成熟 | P6/P7 可视化验收报告，覆盖 provider、长对话、生命周期、诊断 | 自动化候选报告已生成；P6-REAL/P7-post 报告待授权执行 | 中文 HTML 报告、真实截图证据 |
| P5-REAL/P5-Freeze 未真实执行 | P7 后按 P7-post 重新复验真实资料路径 | 冻结延期 | P7-post P5 复验计划和审计 |

## -0.2 P6+P7 架构不变量

- 默认路径永远是 local/mock，不得因 `.env` 中配置了 provider 就自动外呼；
- 真实外呼必须经过 Provider Policy Gate，并产生脱敏 Provider Invocation Log；
- API Key 只允许从本地环境读取，不进入前端 bundle、仓库、报告、截图说明、日志或 fixture；
- Long Context Manager 只发送必要上下文，必须优先使用摘要、source refs、artifact/JD/profile 摘要和近期消息窗口；
- provider-backed 回复不得绕过 `questions_to_confirm`、Artifact Service、Export Service 或 workspace 沙箱；
- Workspace cleanup、delete、migration apply 等不可逆操作必须显式确认；P7 默认只允许 dry-run 验收；
- Diagnostics report 必须先脱敏再落盘；
- 自动化截图、焦点抢占或弹窗必须提前告知用户；
- P7 完成不自动代表 P5-REAL 通过，P5 复验必须单独执行。

## -0.3 P6+P7 最小可执行接口契约

| 用户动作 | 默认接口 / 模块 | 输入 | 必须返回或产生 | 约束 |
| --- | --- | --- | --- | --- |
| 查看 provider 状态 | `GET /api/provider/status` 或现有 provider status 路由 | workspace_id | configured、selected_provider、selected_model、called_in_session、last_error | configured 不等于 called |
| 保存模型偏好 | `POST /api/provider/preferences` | provider、model、base_url preset、mode | preference saved，redacted display | 不保存 API Key；只保存非敏感偏好 |
| 确认本轮外呼 | `POST /api/provider/consent` | workspace_id、session_id、scope、ttl、allowed_data_classes | consent token / policy snapshot | scope 必须可审计，可撤销或过期 |
| 发送 provider-backed 聊天 | `POST /api/chat/message` | workspace_id、session_id、message、provider_mode | assistant message、context summary、invocation status、fallback status | 未授权时必须走 local/mock 或返回确认请求 |
| 获取长对话摘要 | `GET /api/chat/session/{id}/context` | workspace_id、session_id | recent_count、rolling_summary、context_snapshot、source refs | 不返回完整敏感原文 |
| 刷新恢复会话 | `GET /api/chat/session/{id}` | workspace_id、session_id | messages、summary、artifacts、pending confirmations | 恢复后不重复外呼 |
| 导出诊断报告 | `POST /api/diagnostics/report` | workspace_id、include options | redacted diagnostics zip/html/json | 不含密钥、完整简历、raw response |
| workspace 备份 | `POST /api/workspace/backup` | workspace_id、target | backup path、manifest、redaction status | 只写允许路径 |
| workspace 清理 dry-run | `POST /api/workspace/cleanup/plan` | workspace_id、rules | affected files、risk labels、confirmation required | 不删除文件 |
| workspace 迁移 dry-run | `POST /api/workspace/migrate/plan` | workspace_id、target_version | migration plan、rollback notes | apply 必须另行确认 |
| P7-post P5 复验 | stage review script/report | 用户明确资料路径和允许展示字段 | P5-REAL report、closure audit | 未提供资料则保持未执行 |

## 0. P5 历史架构增补与 P7-post 复验依据

本节作为历史基线和 P7-post 复验依据保留。P5 在 P4 已冻结的 Chatbox 工作台、FastAPI、ChatCore、Domain Tools、Artifact/Export 和本地 workspace 基线上增加“真实资料本地闭环平面”。目标不是重写后端或默认启用外部 provider，而是让真实资料、真实 JD、事实确认、产物编辑、导出和多轮追问都沿同一条可审计链路闭合。

P5 架构主线：

```text
User
→ Chatbox Experience Shell
  → Composer / Upload Dock
  → Conversation Plane
  → Workbench Plane
  → Artifact Review / Edit / Export Plane
→ FastAPI Agent Service
  → Workspace Routes
  → File Upload Routes
  → Chat Routes
  → Workflow Routes
  → Artifact Routes
  → Export Routes
→ ChatCore and Intent Router
  → Context Snapshot
  → Real Data Intake Controller
  → Fact Confirmation Loop
  → Application Package Loop
→ Domain Tool Layer
  → Profile / Project / Job / Match / Application / Interview Tools
→ Artifact and Storage Layer
  → Artifact Service
  → ArtifactVersion
  → Confirmation Model
  → Export Service
  → SQLite Workspace / Local Files
→ Provider Policy Gate
  → Mock default
  → External provider denied unless P6 opt-in confirmation exists
→ Evidence Layer
  → P5 automation report
  → PRD spec review
  → privacy/redaction audit
```

## 0.1 P5 代码实体与职责

| 层级 | 当前代码实体 | P5 状态 | P5 职责 | 禁止职责 |
| --- | --- | --- | --- | --- |
| Chatbox UI | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 自动化候选通过，待人工体验冻结 | 呈现上传/粘贴入口、资料解析状态、事实确认、申请包产物、编辑/再生成/导出、多轮追问 | 不生成求职内容；不直接写 SQLite；不直连 provider |
| API 边界 | `services/api/main.py` | 自动化候选通过，待真实资料复核 | 暴露 workspace、upload、chat、workflow、artifact、export 的 P5 路由和错误语义 | 不回传 API Key；不把完整敏感原文写入日志 |
| ChatCore | `services/chat/core.py` | 自动化候选通过，待人工体验复核 | 区分自由追问、状态查询、资料导入、JD 解析、事实确认、生成/再生成等意图 | 不在普通聊天中写 artifact；不绕过确认 |
| Workflow Orchestrator | `services/workflows/p2_demo.py` 及 P5 本地闭环路径 | 自动化候选通过，待真实资料路径复核 | 从 examples flow 扩展为真实资料本地 flow，保留可回归基线 | 不伪造真实资料路径通过 |
| Domain Tools | `services/tools/` | 自动化候选通过，待真实资料质量复核 | 执行资料解析、项目抽取、JD 解析、匹配、申请包生成、面试准备 | 不访问 workspace 外路径；不绕过 source refs |
| Artifact Service | artifact/version 相关服务 | 自动化候选通过，待版本 UI 人工复核 | 保留 source refs、`questions_to_confirm`、版本、编辑、再生成历史 | 不覆盖旧版本；不隐藏 blocking confirmation |
| Export Service | export 相关服务 | 自动化候选通过，待真实资料导出脱敏复核 | 导出 Markdown/DOCX，并在导出前执行 preflight | 不写 workspace 外路径；不导出未确认 blocking 内容 |
| Storage | SQLite workspace、本地文件目录 | 自动化候选通过，持续作为冻结门槛 | 持久化资料、会话、产物、版本、导出记录 | 不保存 API Key；不写完整 raw provider response |
| Provider Policy Gate | provider runtime/policy | 已实现需约束 | P5 默认 mock/local；真实外部 provider 归入 P6 opt-in | 不默认外呼；不把已配置误写为已调用 |
| Evidence | `docs/reports/`, screenshot/test scripts | 自动化候选通过，待真实资料报告复核 | 生成脱敏 P5 验收报告、截图和 PRD 规格检视 | 不暴露真实个人资料全文；不做未执行声明 |

## 0.2 P5 当前架构与目标差距

| 当前实现 | P5 目标 | 状态 | 验收证据 |
| --- | --- | --- | --- |
| P4 Chatbox 已可用，默认 examples/mock 路径冻结 | 支持用户自己的资料和 JD 进入本地闭环 | 自动化候选通过，P5-REAL 待执行 | 上传/粘贴资料截图、脱敏解析结果、错误恢复截图 |
| 资料导入已有基础文件路径和示例数据 | 真实资料导入必须显示本地处理、支持格式、解析摘要、缺失项 | 脱敏 fixture 通过，真实资料路径待用户提供 | 资料导入 eval、隐私提示截图 |
| JD 解析已服务 examples 路径 | JD 粘贴/导入后给出岗位要求、风险、缺口和下一步 | 自动化候选通过，真实 JD 片段待复核 | JD 解析截图、缺失信息恢复测试 |
| Artifact 卡已可读 | 真实资料产物必须显示来源、待确认项、版本、编辑/再生成 | 自动化候选通过，人工体验待复核 | artifact card 截图、version/edit/regenerate 测试 |
| 自由连续对话已在本地/mock 基线通过 | 围绕当前资料/JD/申请包回答状态、建议和非执行型追问 | 自动化候选通过，不代表 provider-backed 聊天 | 多轮追问不误写 artifact 的 eval |
| Markdown/DOCX 导出已实现 | 导出前必须执行确认 preflight，并标明 warning/blocking | 自动化候选通过，真实资料导出待脱敏复核 | 导出 preflight、导出文件和截图 |
| Provider opt-in 基础存在 | P5 默认不外呼；P6 才验证真实 provider | 已实现需约束 | provider 状态截图、无外呼日志审计 |
| P4 报告和 drawio 已完成 | P5 报告必须脱敏并区分真实资料授权/示例数据 | P5 自动化报告已生成，真实资料报告复核待执行 | P5 HTML 报告、PRD 规格检视 |

## 0.3 P5 架构不变量

- 用户资料和 JD 进入系统后必须先落在本地 workspace 边界内；
- 前端只能发起请求、展示状态、触发确认、编辑和导出，不能承担业务生成；
- ChatCore 只能决定意图和下一步，业务写入仍由 Python Domain Tools 执行；
- artifact 必须保留 source refs、`questions_to_confirm`、版本和导出状态；
- blocking confirmation 未处理时不得导出正式申请材料；
- P5 默认 provider 是 mock/local；真实外部 provider、API Key 和 provider-backed 自由智能聊天属于 P6 opt-in；
- 自动化报告不得包含完整真实简历、真实 JD、API Key 或外部 provider raw response；
- 任何涉及真实个人资料、真实外部调用、workspace 删除或不可逆迁移的验收都必须先获得用户确认。

## 0.4 P5 架构验收问题

每个 P5 实现或阶段验收必须回答：

- 用户是否能清楚知道资料会留在本地，外部 provider 未默认调用？
- 上传或粘贴资料后，系统是否返回可读摘要、来源和待确认项？
- JD 解析是否能给出岗位要求、缺口和下一步，而不是只生成内部 JSON？
- 普通追问是否不会误触发生成、解析或 artifact 写入？
- 明确“生成申请包 / 重新生成 / 导出”时，是否走确认和版本链路？
- Workbench 是否能让用户看到当前资料、目标 JD、产物、确认项、版本和导出状态？
- 导出前是否执行 blocking/warning/optional preflight？
- 报告是否区分真实授权资料、脱敏资料和 examples 真实感数据？
- 文档、drawio、测试和报告是否都没有把 P6/P7/P8 能力写成 P5 已完成？

## 0.5 P5 最小可执行接口契约

P5 优先复用当前 API 和 Domain Tools，不以新增复杂后端入口作为默认方案。只有现有接口无法表达验收状态时，才允许增加最小新接口；新增接口必须同步 schema、测试、报告和 drawio。

| P5 用户动作 | 默认接口 / 模块 | 请求输入 | 必须返回或产生 | P5 约束 |
| --- | --- | --- | --- | --- |
| 创建或恢复 workspace | `POST /api/workspace/init`, `GET /api/workspace/status` | name、root_path、privacy_mode | workspace_id、root_path、privacy_mode、next_actions | 默认 `privacy_mode=local_first`，不得默认外呼 |
| 上传资料 | `POST /api/files/upload` | workspace_id、file | document_id、kind、path 或安全错误 | 文件必须落在 workspace 内；报告不得暴露全文 |
| 导入本地资料 | `POST /api/files/ingest-local` | workspace_id、source_path、kind | document_id、source metadata | 必须拒绝 workspace 外逃逸路径 |
| 解析资料 | `POST /api/profile/extract-facts` | workspace_id、document_ids、target_roles | career_facts、skill_evidence、artifact_ref、source_refs、questions_to_confirm | 没有 document_ids 时可使用 workspace 现有文档，但必须可追踪来源 |
| 生成项目卡 | `POST /api/project/create-card` | workspace_id、project_name、source_document_ids、target_role | tech_project、artifact_ref、source_refs | 不得臆造未在资料中出现的项目事实 |
| 解析 JD | `POST /api/job/parse-jd` 或明确 JD chat intent | workspace_id、jd_text、source_url | job_id、requirements、risks、artifact_ref | 缺少 JD 时返回恢复动作，不伪造成解析成功 |
| 匹配岗位 | `POST /api/job/match-profile` | workspace_id、job_id | match_report、strengths、gaps、questions_to_confirm | 必须说明证据不足的项 |
| 生成申请包 | `POST /api/application/create-package` 或明确 chat intent | workspace_id、job_id、style、language | package_id、artifact_ref、draft、questions_to_confirm | blocking confirmation 未处理时仍可生成草稿，但不得正式导出 |
| 编辑产物 | `PATCH /api/artifacts/{artifact_id}` | workspace_id、content_json | 新 artifact version | 不覆盖旧版本，不丢 source_refs |
| 重新生成 | `POST /api/artifacts/{artifact_id}/regenerate` | workspace_id | 新 artifact version | 保留旧版本和失败恢复信息 |
| 确认事实 | `POST /api/artifacts/{artifact_id}/confirm` | workspace_id | confirmed status 或剩余 blocking 项 | 不允许隐藏未处理 blocking 项 |
| 导出申请包 | `POST /api/application/export-package` | workspace_id、package_id、formats、artifact_version_id | exports、preflight、download path | 只能写 workspace `exports/`，blocking 未处理时不得导出正式材料 |
| 多轮追问 | `POST /api/chat/message` | workspace_id、session_id、message | assistant message、chat_mode、artifacts | 普通追问不写 artifact；明确工具意图才执行 |

P5 前端状态机必须至少表达以下状态：

```text
idle
→ profile_importing
→ profile_ready 或 profile_needs_recovery
→ jd_importing
→ jd_ready 或 jd_needs_recovery
→ facts_need_confirmation
→ package_draft_ready
→ package_editing / regenerating
→ export_preflight_blocked 或 export_ready
→ exported
```

P5 不要求一次性引入新全局状态管理库。若现有 `main.tsx` 状态已难以维护，可以在 P5-M1 后按组件边界拆分；拆分必须保持行为不变，并优先服务资料导入、JD 解析、事实确认、产物和导出状态可读。

## 0.6 P5 数据、脱敏和验收资料策略

P5 自动化开发默认使用 `examples/` 真实感数据和测试临时 workspace。真实个人资料只能用于用户明确授权的人工体验审查；任何自动化报告、截图标题、日志、fixture 和提交内容都不得包含完整真实资料。

| 数据类型 | P5 默认处理 | 可进入报告 | 禁止事项 |
| --- | --- | --- | --- |
| examples 简历/JD/项目 | 可用于自动化验收 | 可摘要展示，并标注为真实感示例数据 | 不得写成真实个人资料 |
| 用户真实简历/JD | 仅用户明确授权后用于人工体验 | 只能脱敏摘要、截图局部或人工结论 | 不得全文写入仓库、报告、日志、fixture |
| API Key / provider 配置 | P5 不默认使用 | 只能写“未调用 / 需 P6 opt-in” | 不得写入报告、截图、日志或提交 |
| provider raw response | P5 默认不存在 | 不适用 | 不得伪造或声称已通过 |
| 导出文件 | 写入 workspace `exports/` | 可展示路径和脱敏片段 | 不得越过 workspace 或包含未授权隐私 |

P5 自动化报告必须包含“未验证范围”段落，并明确列出：真实外部 provider、provider-backed 自由智能聊天、SaaS、ASR、会议平台、自动投递、MCP/CLI、最终产品化发布。

以下 P4 内容作为已冻结基线和历史背景保留。

## 1. 历史 P4 UX 体验强化架构基线

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
