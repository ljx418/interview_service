# P11-M1 到 P11-M5 自动化开发审计

状态：P11 Level 1 自动化开发与本地验收通过。本文档记录 P11 Level 1 自动化开发子阶段计划、验收标准、实现结果和 PRD 规格检视。

## M1：后端 Market Provider Boundary

开发目标：

- 新增 `services/market/provider.py`，实现 `JobMarketProviderRegistry`、policy gate、Level 1 search run、snapshot 和 source refs。
- 新增 FastAPI 路由：`/api/market/providers/status`、`/api/market/providers/check`、`/api/market/search-runs`、`/api/market/search-runs/{run_id}`、`/api/market/snapshots/{run_id}`、`/api/market/source-refs/{source_ref_id}`。
- 新增 SQLite 表：`job_market_providers`、`job_search_runs`、`normalized_job_posts`、`job_market_snapshots`、`region_source_refs`、`market_provider_invocation_logs`。

验收标准：

- 默认不外呼真实 provider。
- fixture/manual/public/recorded 路径可创建 search run 和 snapshot。
- 每个 snapshot 有 source refs、confidence、low confidence notes。
- opt-in provider 在未确认时返回稳定安全拒绝。

PRD 规格检视：通过。实现范围保持在 P11 Level 1，不声明真实市场 provider 通过。

## M2：CLI Agent-friendly 状态输出

开发目标：

- `workspace status` 输出 `market_provider_state`。
- `provider_state` 增加 `market_level`、`market_external_call_enabled`、`market_can_claim_real_market`。

验收标准：

- CLI 不自动启动 FastAPI。
- CLI 不生成报告、不真实外呼、不直连 provider。
- JSON envelope 对 Agent 可读。

PRD 规格检视：通过。CLI 仍是薄入口。

## M3：Chatbox 市场状态与 SearchRun 联动

开发目标：

- 顶部服务中心展示 Market Provider Level1 状态。
- 左侧市场地图显示后端 provider 状态、snapshot source breakdown、low confidence notes。
- 用户通过 Chatbox 发起岗位/薪资/城市汇总时，调用 `/api/market/search-runs`，而不是只在前端构造 mock。

验收标准：

- 页面保持 Chatbox-first 三栏结构。
- 市场汇总明确显示 fallback/Level1，不写成全网搜索。
- 失败时不生成假市场结论。

PRD 规格检视：通过。前端仍未触发真实 provider、平台抓取或 ASR。

## M4：自动化 Eval

开发目标：

- 新增 `tests/evals/test_p11_market_provider_optin_eval.py`。
- 覆盖 provider status、provider check、search run、snapshot、source refs、opt-in 拒绝、CLI 状态和前端接入静态证据。

验收标准：

- P11 eval 全绿。
- opt-in provider 未确认时不可被调用。
- source refs 不返回 raw provider response 或 API Key。

PRD 规格检视：通过。

## M5：中文可视化验收报告

开发目标：

- 新增 `scripts/generate_p11_market_provider_acceptance.py`。
- 生成 `docs/reports/P11_MARKET_PROVIDER_OPTIN_ACCEPTANCE_REPORT.html`。
- 报告包含目标架构、当前实现、API 证据、命令证据、drawio parse、未验证范围和可选 headless 截图。

验收标准：

- 报告可读性足以让人类审计本阶段 Level 1 开发。
- 截图若失败必须如实标注，不伪造证据。
- 报告不得声明真实 provider、全网 JD 搜索、招聘平台接入、ASR、MCP、自动投递或 SaaS 通过。

PRD 规格检视：通过。`scripts/generate_p11_market_provider_acceptance.py` 已生成中文 HTML 报告，并由 `tests/evals/test_p11_market_provider_acceptance_report_eval.py` 验证报告结构、截图、命令证据、API 证据和未验证边界。

## 剩余限制

- Level 2 真实 provider opt-in 未执行，因为当前没有用户明确提供的合法 provider 凭据和外呼确认。
- 当前 search run 使用本地 fixture/recorded/manual/public sample 路径，不能等同真实市场数据。
- P11 未实现招聘平台自动接入、长期爬虫、ASR、MCP、自动投递或 SaaS。
