# JobPilot P11 真实市场数据 Provider Opt-in Gap 图文本镜像

状态：P11 Level1 自动化候选已实现并进入阶段性验收收口。对应 drawio 文件：`docs/active/jobpilot-p11-market-provider-optin-gap.drawio`。

颜色约定：

- 绿色：P11 Level1 已实现
- 黄色：需人工复核 / 需修改
- 蓝色：Level2 待授权 / 待新增
- 红色：高风险禁止默认实现
- 灰色：审计 / evidence / 边界

## 1 P11目标体验与边界

展示 P11 的目标体验：用户通过 Chatbox 发起市场查询，系统先展示 provider 状态、费用/隐私提示、查询范围和调用次数；Level1 已支持本地/fixture/recorded/manual/public `JobSearchRun`，Level2 才允许在用户提供合法凭据并确认外呼后调用指定真实 provider。图中同时标注 P11 不代表招聘平台抓取、ASR、MCP、自动投递或 SaaS。

本页同时给出架构决策：P11 采用“opt-in API provider boundary + normalization anti-corruption layer + evidence first”，不采用招聘平台 connector、长期爬虫或 UI 直连 provider。Level1 先证明本地链路完整；Level2 再证明指定真实 provider 外呼可授权、可记录、可回滚。

## 2 当前架构与P11差距

左侧展示当前 P9.1/P10 基线：`TopServiceCenter`、`MarketIntelligenceMap`、`ConversationPlane`、`ArtifactWorkbench`、`jobpilot CLI`、FastAPI、workspace、reports。右侧展示 P11 Level1 已补齐的实体：market provider boundary、normalization domain、source refs、snapshot、CLI 状态和 invocation evidence；Level2 真实外部 `MarketProviderClient` 仍待授权。

本页增加三类风险判断：

| 风险 | 当前缺口 | P11 设计约束 | 出门判断 |
| --- | --- | --- | --- |
| 架构风险 | UI/CLI 可能绕过后端直接调用 provider | 只能通过 FastAPI + `MarketProviderPolicyGate` | 当前 Level1 实现已走 `/api/market/*`，不得直写 SQLite 或直调 provider |
| PRD 偏移风险 | P11 可能滑向招聘平台抓取或全网搜索 | P11 只做 opt-in provider boundary，不做平台登录/绕风控 | 文档和报告不得出现平台已接入或全网搜索已通过 |
| 验收风险 | fixture/fallback 可能冒充真实市场 | Level 1/Level 2 分级，source refs 必须可见 | 当前只能声明 Level1；无凭据不得声明 Level2 |

## 3 目标架构与实体状态

展示五层架构：

```text
UI Control Plane
→ Market Provider Boundary
→ Market Normalization Domain
→ Existing FastAPI / Workspace Boundary
→ Evidence Layer
```

每个实体都标明状态：Level1 已实现、需人工复核/需修改、Level2 待授权/待新增或高风险禁止。

本页必须让审计者看清具体实体的强关联：

```text
TopServiceCenter / ConversationPlane / MarketIntelligenceMap / ArtifactWorkbench
→ /api/market/* routes
→ MarketProviderPolicyGate
→ MarketProviderClient（Level2 待授权）
→ MarketDataNormalizer
→ SourceRefBinder / ConfidenceScorer
→ JobMarketSnapshot
→ UI / CLI / HTML report
```

当前 Level1 已实现实体：

- `services/market/provider.py`：provider registry、policy gate、local search run、snapshot、source refs；
- `services/api/main.py`：`/api/market/providers/status`、`/api/market/providers/check`、`/api/market/search-runs`、`/api/market/snapshots/{run_id}`、`/api/market/source-refs/{source_ref_id}`；
- `services/storage/db.py`：`job_market_providers`、`job_search_runs`、`normalized_job_posts`、`job_market_snapshots`、`region_source_refs`、`market_provider_invocation_logs`；
- `services/cli/main.py`：`workspace status` 的 market provider 状态输出；
- `apps/chatbox/src/main.tsx`：Chatbox 市场查询触发、地图/产物台 Level1 source refs 展示；
- `tests/evals/test_p11_market_provider_optin_eval.py` 与 `scripts/generate_p11_market_provider_acceptance.py`：专项 eval 与中文报告。

禁止出现只有“真实市场数据”“Provider 层”这类抽象词、但看不到实体上下游的架构图。

## 4 命令流与数据流

展示三条主路径：

1. provider status：读取配置摘要和调用证据；
2. provider check：用户确认后一次性检查；
3. market search run：Level1 本地授权边界、归一化、聚合、地图/Chatbox/产物台联动；Level2 才包含一次性真实 provider call。

图中同步标注 FastAPI handoff：`GET /api/market/providers/status`、`POST /api/market/providers/check`、`POST /api/market/search-runs`、`GET /api/market/search-runs/{run_id}`、`GET /api/market/snapshots/{run_id}`、`GET /api/market/source-refs/{source_ref_id}`。任何 UI/CLI 都不得绕过这些边界直接调用 provider 或写 SQLite。

本页增加失败分支：

- 未配置 provider：返回 `PROVIDER_NOT_CONFIGURED`，不外呼；
- 未确认授权：返回 `CONSENT_REQUIRED`，不创建 running run；
- provider 调用失败：返回 `PROVIDER_CALL_FAILED`，保留脱敏错误；当前 Level1 不触发真实 provider 外呼；
- 调用成功但无结果：返回 `NO_RESULTS`，不伪造数据；
- fallback-only：返回 `FALLBACK_ONLY`，报告只能声明 Level 1；
- 越界平台抓取或敏感外发：返回 `POLICY_REJECTED`。

## 5 数据契约与证据链

展示 `JobMarketProvider`、`JobSearchRun`、`NormalizedJobPost`、`JobMarketSnapshot`、`RegionSourceRef`、`MarketProviderInvocationLog` 的关系。强调每个聚合指标必须绑定 source refs。

图中同步标注推荐存储实体：`job_market_providers`、`job_search_runs`、`normalized_job_posts`、`job_market_snapshots`、`region_source_refs`、`market_provider_invocation_logs`。禁止保存 API Key、完整 raw response、平台 cookie/session 或未授权真实个人资料。

本页增加证据链判定：

```text
provider called
→ consent_id
→ market_provider_invocation_logs.redacted=true
→ normalized_job_posts.source_ref_id
→ region_source_refs.metric_name
→ job_market_snapshots.source_breakdown
→ report screenshot / command evidence
```

如果任一环缺失，不能声明真实 provider opt-in 通过。当前 Level1 报告只能证明本地链路、source refs 和截图证据完整，不能证明 Level2。

## 6 开发及验收计划

展示 P11-DOC-M0 到 DOC-M3，以及 P11-M0 到 M5。当前 P11-DOC 和 P11-M0 到 M5 的 Level1 自动化候选均已完成，正在执行阶段性审计、drawio 同步、中文报告和 Git 收口。

图中同步标注验收分级：Level 0 文档通过；Level 1 本地实现通过但不代表真实 provider；Level 2 指定真实 provider opt-in 调用通过；Level 3 多 provider/source 对比通过。当前只有 Level1 可验收；无真实 provider 凭据时不得声明 Level2。

本页增加每阶段打回条件：

| 阶段 | 必须证明 | 打回条件 |
| --- | --- | --- |
| M0 | 已证明高风险边界冻结 | 混入平台抓取/长期爬虫/ASR/MCP |
| M1 | 已证明 provider 状态可见且脱敏 | configured 被写成 called |
| M2 | 已证明未确认拒绝真实外呼 | 配置 Key 后自动调用 |
| M3 | 已证明 normalization 和 source refs 完整 | 聚合指标没有 source refs |
| M4 | 已证明 UI/CLI/report 状态一致 | 地图显示真实但报告为 fallback |
| M5 | 已证明中文报告可审计 | 无 Level 判定或无截图/命令证据 |

## 7 里程碑门槛出门

列出 P11 Level1 收口门槛 A-E、最低验收命令和出门条件。

出门条件增加：报告必须包含 provider 状态、consent preview、未确认拒绝外呼、脱敏 invocation log、`JobSearchRun`、`NormalizedJobPost`、`JobMarketSnapshot`、source refs、confidence 和 Level 1/Level 2 判定。当前 Level1 出门只能声明本地链路通过。

本页增加人类审核问题清单：

- 是否能从图中看出 Level1 已实现、需修改、Level2 待授权和禁止项？
- 是否能判断每个 PRD 承诺落到哪个代码实体或 API？
- 是否能判断没有真实 provider 凭据时不能 Level 2 出门？
- 是否能判断失败/fallback/no-results 时如何报告？
- 是否能判断 P11 没有承诺招聘平台接入、ASR、MCP、自动投递或 SaaS？

## 8 安全边界与后续路线

红色区域列出禁止默认实现：招聘平台抓取、长期爬虫、默认 API Key 外呼、真实 LLM provider、ASR、MCP、自动投递、SaaS。灰色区域列出后续路线：P11 Level1 阶段验收收口、P11 Level2 指定 provider opt-in 授权验收、P12 高风险专项规划。

本页增加备选技术路线对比：

| 路线 | 优点 | 缺点 | P11 结论 |
| --- | --- | --- | --- |
| Opt-in job API provider | 可授权、可记录、可验收 | 覆盖依赖 provider | 采用 |
| 用户粘贴/公司官网公开源 | 低风险、可追溯 | 自动化弱 | 作为 fallback/manual |
| 招聘平台自动抓取 | 覆盖近似真实平台 | 合规、账号、验证码、封禁风险高 | P11 禁止，后续单独立项 |
| 长期爬虫/队列 | 数据更新稳定 | 运维、成本、合规和误用风险高 | P11 禁止 |
