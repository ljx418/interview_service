# P11 真实市场数据 Provider Opt-in Level1 开发与验收计划

状态：Level1 自动化候选已实现并进入阶段性验收收口。本文档定义 P11 的 PRD、目标架构、实体状态、里程碑、验收门槛和风险边界；当前只允许声明本地/记录数据路径通过，不代表真实市场 provider Level2 已接入，不触发真实外呼。

P9.1 已完成本地自动化候选：ECharts 行政区划下钻式市场地图、Market Provider 未配置状态、Socratic Intake、产物台联动和中文 HTML 验收报告均已落地。P10-CLI 已完成本地命令入口自动化候选。P11 接续解决的缺口是：市场地图和求职情报仍主要使用 fixture / manual / public 状态表达，缺少可审计的真实市场 provider opt-in 数据链路。

## 1. 目标体验

P11 完成后，用户应能通过 Chatbox-native 工作台安全地发起一次真实市场数据查询：

```text
用户询问“帮我看北京和上海 LLM 前端岗位真实市场”
→ 顶部服务中心展示 Market Provider 状态
→ 系统说明 provider、查询条件、数据类别、调用次数、费用/隐私提示
→ 用户显式确认后创建一次 JobSearchRun
→ provider 返回结果被标准化为 NormalizedJobPost
→ 系统聚合为 JobMarketSnapshot
→ 左侧地图、中央 Chatbox、右侧产物台和验收报告展示 source refs、置信度和未验证范围
```

默认状态必须是安全的：

- 未配置 provider：显示 `not_configured`，不外呼；
- 已配置但未确认：显示 `configured`，不外呼；
- 已确认但未调用：显示 `consented`，不写成 called；
- 已调用：必须有调用日志、source refs 和报告证据；
- 调用失败：显示 `failed`，保留错误摘要；
- fallback：显示 `fallback`，不得写成真实市场。

## 2. 范围

允许规划：

- Adzuna、TheirStack、JSearch、Jooble 等公开职位 API 的 opt-in provider 边界；
- 公司官网公开 JD 和用户粘贴 JD 的 manual/public source 归一化；
- provider 状态 API、授权门、一次性 provider check、一次性 market search run；
- `NormalizedJobPost`、`JobMarketSnapshot`、`RegionSourceRef`、`MarketProviderInvocationLog`；
- Chatbox、市场地图、右侧产物台和报告中的 source refs / confidence / fallback 表达；
- P11 自动化验收脚本、中文 HTML 报告和 PRD 规格检视。

禁止作为 P11 默认能力：

- BOSS、猎聘、拉勾、LinkedIn 等招聘平台登录、抓取、绕验证码或绕风控；
- 长期运行爬虫、队列、定时任务、批量平台访问；
- 默认读取 API Key 并外呼；
- 默认调用真实 LLM provider；
- 扫描真实个人资料目录；
- ASR、麦克风、会议平台、MCP server；
- 自动投递、自动沟通或代表用户对外发送消息；
- SaaS、多租户、Billing。

## 3. 目标架构

P11 采用“受控 provider boundary + normalization domain + evidence first”的模块化架构，不新增招聘平台系统。

```text
UI Control Plane
  TopServiceCenter
  ConversationPlane
  MarketIntelligenceMap
  ArtifactWorkbench

Market Provider Boundary
  JobMarketProviderRegistry
  MarketProviderPolicyGate
  MarketProviderClient
  MarketProviderInvocationLog

Market Normalization Domain
  JobSearchRunService
  MarketDataNormalizer
  SourceRefBinder
  ConfidenceScorer

Existing Boundary
  FastAPI Agent Service
  SQLite Workspace
  Artifact / Reports

Evidence Layer
  P11MarketAcceptanceReport
  provider invocation evidence
  screenshots / command evidence
```

实体状态：

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `TopServiceCenter` | Level1 已实现 | 展示 market provider Level1 状态机和边界 |
| `ConversationPlane` | Level1 已实现 | 通过 Chatbox 发起本地 market query；真实授权确认仍属 Level2 |
| `MarketIntelligenceMap` | Level1 已实现 | 展示 fallback snapshot、source trust 和未验证范围 |
| `ArtifactWorkbench` | Level1 已实现 | 展示 Market Insight、source refs、低置信度 |
| `JobMarketProviderRegistry` | Level1 已实现 | 管理 fixture/manual/public/opt-in provider 候选、启用状态、许可、限额 |
| `MarketProviderPolicyGate` | Level1 已实现 | 拦截未授权、超范围、平台抓取和敏感数据外发；真实调用仍关闭 |
| `MarketProviderClient` | Level2 待授权 | Level1 不执行真实 provider 网络调用，只保留 opt-in 边界 |
| `MarketProviderInvocationLog` | Level1 已实现 | 写入脱敏调用证据，不记录 API Key 或 raw response |
| `JobSearchRunService` | Level1 已实现 | 创建、读取、失败保留 market search run |
| `MarketDataNormalizer` | Level1 已实现 | 标准化 provider/manual/public/fixture 数据 |
| `SourceRefBinder` | Level1 已实现 | 将聚合指标绑定到 source refs |
| `ConfidenceScorer` | Level1 已实现 | 标记低置信度、缺字段和 fallback |
| `NormalizedJobPost` | Level1 已实现 | 统一职位标题、公司、城市、薪资、技术栈和来源 |
| `JobMarketSnapshot` | Level1 已实现 | 聚合岗位量、薪资、技术栈和来源可信度 |
| `P11MarketAcceptanceReport` | Level1 已实现 | 证明 provider 调用边界和未验证范围 |

## 4. 数据契约

`JobMarketProvider`：

- `provider_id`
- `provider_name`
- `provider_type=opt_in_api|public_source|manual_paste|fixture`
- `configured_state=not_configured|configured|connected|failed|disabled`
- `requires_key`
- `rate_limit`
- `license_note`
- `last_checked_at`

`JobSearchRun`：

- `run_id`
- `query`
- `city_filters`
- `salary_range`
- `tech_stack`
- `source_policy`
- `provider_ids`
- `consent_id`
- `started_at`
- `completed_at`
- `status=pending|running|succeeded|failed|fallback`
- `result_count`
- `source_refs`
- `boundary_note`

`NormalizedJobPost`：

- `job_id`
- `title`
- `company`
- `city`
- `salary_range`
- `seniority`
- `tech_stack`
- `source_url`
- `source_type`
- `fetched_at`
- `confidence`
- `source_ref_id`

`JobMarketSnapshot`：

- `run_id`
- `city_stats`
- `salary_histogram`
- `tech_heatmap`
- `source_breakdown`
- `remote_ratio`
- `competition_level`
- `trend_summary`
- `low_confidence_notes`

`MarketProviderInvocationLog`：

- `invocation_id`
- `provider_id`
- `run_id`
- `query_summary`
- `status`
- `duration_ms`
- `error_code`
- `redacted=true`
- `created_at`

约束：缺失薪资、公司、城市、年限时不得自动补事实，只能进入低置信度或待确认。

### 4.1 API 契约

P11 后续实现必须优先通过 FastAPI 边界暴露能力，不允许 UI 或 CLI 直接调用外部 provider，也不允许 UI 直接写 SQLite。

| API | 方法 | 输入 | 输出 | 安全约束 |
| --- | --- | --- | --- | --- |
| `/api/market/providers/status` | `GET` | `workspace_id` | provider 状态、配置摘要、上次检查时间、最近调用证据摘要 | 不返回 API Key、不返回完整 provider response |
| `/api/market/providers/check` | `POST` | `provider_id`、`workspace_id`、`consent_preview_id`、`confirm=true` | `connected/failed`、脱敏调用日志 id、错误摘要 | 未确认必须返回安全拒绝；只允许 minimal check |
| `/api/market/search-runs` | `POST` | query、城市、薪资、技术栈、provider_ids、consent_id | `run_id`、状态、边界说明 | 未授权不得创建 `running` run；不得触发长期任务 |
| `/api/market/search-runs/{run_id}` | `GET` | `workspace_id` | run 状态、统计、错误、source refs | 只返回脱敏摘要 |
| `/api/market/snapshots/{run_id}` | `GET` | `workspace_id` | `JobMarketSnapshot`、低置信度说明、source breakdown | 每个聚合指标必须可追溯 |
| `/api/market/source-refs/{source_ref_id}` | `GET` | `workspace_id` | source 摘要、来源类型、时间戳、可信度 | 不返回完整 raw response；不读取网页 |

失败语义必须稳定：

- `PROVIDER_NOT_CONFIGURED`：未配置，不能外呼；
- `CONSENT_REQUIRED`：已配置但未确认，不能外呼；
- `PROVIDER_CALL_FAILED`：已授权调用失败，保留错误摘要；
- `NO_RESULTS`：真实调用成功但无结果，不回退伪造成市场数据；
- `FALLBACK_ONLY`：仅 fixture/manual/public sample，不允许声明真实市场；
- `POLICY_REJECTED`：命中平台抓取、长期爬虫、敏感信息外发或越界 provider。

### 4.2 存储和证据实体

P11 后续实现可以复用当前 SQLite workspace，但必须把真实 provider 相关证据与普通 fixture/manual 数据区分清楚。

| 存储实体 | 建议职责 | 必填边界字段 |
| --- | --- | --- |
| `job_market_providers` | provider registry 和本地启用状态 | `provider_type`、`configured_state`、`license_note`、`last_checked_at` |
| `job_search_runs` | 一次查询运行 | `source_policy`、`consent_id`、`status`、`boundary_note` |
| `normalized_job_posts` | 标准化岗位 | `source_type`、`source_ref_id`、`confidence`、`fetched_at` |
| `job_market_snapshots` | 地图/Chatbox/产物台聚合视图 | `run_id`、`source_breakdown`、`low_confidence_notes` |
| `region_source_refs` | 区域指标来源 | `region_code`、`metric_name`、`source_ref_ids`、`confidence` |
| `market_provider_invocation_logs` | 脱敏调用日志 | `redacted=true`、`query_summary`、`status`、`error_code` |

禁止存储：

- API Key 或 provider secret；
- 完整 provider raw response；
- 未授权真实个人资料；
- 招聘平台 cookie、session、验证码、账号信息；
- 用户未确认的对外投递或沟通内容。

### 4.3 验收分级

P11 存在外部 provider 可用性和凭据风险，因此后续实现验收必须分级表达，不能用 fallback 替代真实 provider 通过。

| 验收级别 | 条件 | 允许声明 | 不允许声明 |
| --- | --- | --- | --- |
| Level 0 文档通过 | PRD、架构、drawio、门槛、审计完成 | P11 文档可支撑后续开发 | P11 已实现 |
| Level 1 本地实现通过 | provider status、policy gate、normalizer、snapshot、UI 联动通过 fixture/recorded/public/manual 验收 | P11 本地能力实现通过 | 真实市场 provider 已通过 |
| Level 2 真实 provider opt-in 通过 | 用户提供授权配置，至少一次真实 provider 调用成功，有脱敏 invocation log、source refs、snapshot 和报告证据 | 指定 provider 在本机 opt-in 路径通过 | 全网 JD 搜索、招聘平台接入、自动投递通过 |
| Level 3 多 provider 对比通过 | 两个及以上授权 provider 或公开源路径完成一致性对比 | 指定 provider/source 组合通过 | 未测试 provider 或平台通过 |

如果没有可用真实 provider 凭据，P11-M5 只能声明 Level 1，本阶段不能声明 Level 2。若用户要求“真实市场 provider 必须通过”但没有提供凭据或可合法调用的公开 provider，则必须暂停并回到风险决策。

## 5. 工作流

### Workflow A：provider status

```text
GET provider status
→ Load registry
→ Redact config
→ Count called/failed/fallback evidence
→ Render status to TopServiceCenter / CLI / report
```

### Workflow B：provider check

```text
User asks to check provider
→ MarketProviderPolicyGate builds consent preview
→ User confirms one-shot check
→ MarketProviderClient performs minimal call
→ MarketProviderInvocationLog records redacted result
→ UI displays connected/failed without exposing key
```

### Workflow C：market search run

```text
User asks market query
→ Parse query, city, salary, tech stack
→ Preview provider, cost, data classes, call count
→ User confirms
→ Create JobSearchRun
→ Call opt-in provider once
→ Normalize posts
→ Bind source refs and confidence
→ Build JobMarketSnapshot
→ Update map, Chatbox, workbench, report evidence
```

## 6. 里程碑

| 阶段 | 目标 | 出门条件 |
| --- | --- | --- |
| P11-DOC-M0 | 阶段口径和范围锁定 | P11 是文档阶段；不做真实外呼 |
| P11-DOC-M1 | PRD、架构、实体状态、数据契约落盘 | provider boundary 和 normalizer 关系清楚 |
| P11-DOC-M2 | README、TODO、active docs、roadmap、drawio 同步 | drawio 不超过 8 页，文本镜像可审计 |
| P11-DOC-M3 | 文档覆盖度复审 | 无新增重大规格偏差或高风险混入 |
| P11-M0 | 开发前启动审计 | 冻结不抓平台、不默认外呼、不长期爬虫、不伪造真实市场 |
| P11-M1 | provider 状态 API | not_configured/configured/failed/fallback 可见 |
| P11-M2 | provider check 授权门 | 未确认拒绝；确认后有脱敏 log |
| P11-M3 | search run / normalization / snapshot | source refs 和 confidence 可验收 |
| P11-M4 | UI 联动 | Chatbox、地图、产物台状态一致 |
| P11-M5 | 中文验收报告 | provider 调用证据、失败/fallback、未验证范围清楚 |

### 6.1 P11-M0 必须冻结的工程决策

P11-M0 进入代码实现前必须单独落盘审计，确认以下决策没有漂移：

| 决策项 | P11 v1 结论 | 不采用路线 | 原因 |
| --- | --- | --- | --- |
| provider 范围 | 只允许 opt-in API、manual paste、company public source 和 fixture/recorded source | 招聘平台账号登录、抓取、绕验证码、长期爬虫 | 降低合规和虚假验收风险 |
| 外呼触发 | 默认不外呼；用户确认一次性 consent 后才调用 | 配置了 Key 就自动调用 | 防止误用 API Key、费用和隐私风险 |
| 真实验收 | 没有真实凭据时只能 Level 1；有凭据且调用成功才 Level 2 | 用 fixture/fallback 冒充真实市场 | 防止 false green |
| 数据保留 | 只保留标准化岗位、source refs、snapshot、脱敏日志 | 保存 raw response、secret、cookie 或完整隐私数据 | 降低泄露风险 |
| UI 表达 | 地图、Chatbox、产物台必须显示 source_type/confidence | 只展示漂亮图表不展示来源 | 防止用户误判数据真实性 |

## 7. 验收门槛

P11 文档与 Level1 实现最低检查：

```bash
drawio XML parse for docs/active/jobpilot-p11-market-provider-optin-gap.drawio
rg "P11|JobMarketProviderRegistry|MarketProviderPolicyGate|JobMarketSnapshot" docs/active README.md TODO.md
rg "真实市场 provider 已接入|招聘平台已接入|自动投递已实现|ASR 已实现|MCP 已实现" docs/active README.md TODO.md
```

P11 后续实现最低检查：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
tests/evals/test_p11_market_provider_optin_eval.py
P11 Chinese HTML acceptance report
```

P11 后续实现报告必须至少包含：

- provider 状态截图；
- consent preview 截图；
- 未确认时拒绝外呼的命令/API 证据；
- 成功或失败的脱敏 `MarketProviderInvocationLog`；
- `JobSearchRun`、`NormalizedJobPost`、`JobMarketSnapshot` 示例；
- 地图、Chatbox、产物台展示 source refs 和 confidence 的截图；
- Level 1 / Level 2 验收级别判定；
- 未验证 provider、招聘平台、ASR、MCP、自动投递、SaaS 的明确声明。

## 8. 打回条件

任一情况出现时，P11 文档或实现必须打回：

- 默认登录或抓取招聘平台；
- 默认外呼真实 provider；
- provider configured 被写成 called；
- fixture fallback 被写成真实市场；
- API Key、完整 provider response 或敏感路径出现在报告、日志或 git diff 中；
- 自动投递、ASR、MCP、SaaS 被写入 P11 默认能力；
- drawio 缺少具体代码实体、状态颜色、分层关系或出门条件。

## 9. 审计结论

当前 P11 Level1 自动化候选已完成，可进入阶段性审计、报告复核和 Git 收口。不能直接进入真实 provider 调用；不能声明真实市场 provider、全网 JD 搜索、招聘平台接入、真实 ASR、MCP、自动投递或 SaaS 已通过。
