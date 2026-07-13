# P11 阶段性收口审计与 PRD 规格检视

状态：P11 Level1 自动化候选通过阶段性收口审计；P11 Level2 真实 market provider opt-in 未执行。

## 审计范围

本轮审计覆盖：

- 原始 PRD 与 active PRD 的阶段口径；
- P11 目标架构、drawio、里程碑、验收门槛和追踪矩阵；
- 后端 market provider boundary、FastAPI API、SQLite schema、CLI 状态输出和 Chatbox 联动；
- P11 专项 eval、全量 pytest、前端 build、drawio XML parse 和中文 HTML 自动化验收报告。

本轮不覆盖：

- 指定真实 market provider 的外呼质量；
- BOSS、猎聘、拉勾、LinkedIn 等招聘平台自动接入；
- 全网 JD 搜索、长期爬虫、ASR、MCP、自动投递、SaaS 或真实个人资料路径。

## 代码检视结论

P11 Level1 的代码实体已落到可审计边界：

| 层级 | 当前实现 | 审计结论 |
| --- | --- | --- |
| Market Provider Boundary | `services/market/provider.py` | 通过。实现 provider registry、policy gate、本地 search run、snapshot、source refs；真实外部 client 仍为 Level2 待授权。 |
| FastAPI Boundary | `services/api/main.py`、`services/api/schemas.py` | 通过。已暴露 `/api/market/providers/status`、`/api/market/providers/check`、`/api/market/search-runs`、snapshot 和 source refs 查询。 |
| Storage Boundary | `services/storage/db.py` | 通过。已落盘 `job_market_providers`、`job_search_runs`、`normalized_job_posts`、`job_market_snapshots`、`region_source_refs`、`market_provider_invocation_logs`。 |
| CLI Boundary | `services/cli/main.py` | 通过。`workspace status` 输出 market provider 状态，不自动启动 FastAPI，不真实外呼。 |
| Chatbox UI | `apps/chatbox/src/main.tsx`、`apps/chatbox/src/styles.css` | 通过。Chatbox 市场查询走 `/api/market/search-runs`，地图和产物台展示 Level1 source refs 与 provider 状态。 |
| Evidence | `scripts/generate_p11_market_provider_acceptance.py`、`tests/evals/test_p11_*` | 通过。报告和 eval 能验证 Level1 证据链及未验证范围。 |

未发现本轮必须阻塞 Level1 收口的架构偏差。主要保留风险是 Level2 真实 provider 尚未授权执行，不能被写成已通过。

## 文档审计结论

P11 文档已经从“文档开发阶段”同步为“Level1 自动化候选收口”：

- README / TODO / active README 已说明 P11 Level1 已实现，Level2 待授权；
- PRD、目标架构、里程碑、验收门槛、追踪矩阵和 P11 专项计划均保留 Level1 / Level2 分级；
- drawio 文本镜像和 drawio 本体均标注 Level1 已实现、Level2 待授权、高风险禁止；
- 报告和文档均不得声明真实 provider、全网 JD 搜索、平台接入、ASR、MCP、自动投递或 SaaS 已通过。

## 功能检查结论

P11 Level1 可实现的用户路径：

1. 用户打开 Chatbox-native 工作台；
2. 顶部和左侧市场模块显示 Market Provider Level1 / local / fallback 状态；
3. 用户在 Chatbox 输入“汇总北京和上海 LLM 前端岗位薪资和城市机会”；
4. 前端调用 `/api/market/search-runs`；
5. 后端创建 `JobSearchRun`、`NormalizedJobPost`、`JobMarketSnapshot` 和 `RegionSourceRef`；
6. 左侧市场地图、中央 Chatbox、右侧产物台展示 source refs、confidence、low confidence notes 和未验证边界；
7. CLI `workspace status` 可看到 market provider 状态；
8. 中文 HTML 报告展示 API 证据、命令证据、截图证据、drawio parse 和未验证范围。

## PRD 规格检视

| PRD 要求 | 当前结果 | 结论 |
| --- | --- | --- |
| Provider 状态必须可见 | Chatbox、CLI、报告均显示 Level1/local/fallback 状态 | 通过 |
| 未确认不得真实外呼 | opt-in provider 未授权时被拒绝；默认 `JOBPILOT_ALLOW_MARKET_PROVIDER_CALL=0` | 通过 |
| Market search run 必须有 source refs | eval 和报告验证 source refs、snapshot、source breakdown | 通过 |
| UI/CLI/report 状态必须一致 | 报告汇总 API、CLI 和截图证据 | 通过 |
| 不得把 fallback 写成真实市场 | 报告明确 Level1，不声明 Level2 | 通过 |
| 指定真实 provider opt-in | 当前无用户授权和凭据 | 未执行，不能声明通过 |

## 阶段验收评价

P11 Level1 自动化候选可声明阶段性收口通过。该结论只覆盖本地/fixture/recorded/manual/public 路径和可审计 provider boundary，不覆盖 Level2 真实 provider 外呼。

出门前必须保留以下声明边界：

- 不能声明真实 market provider 已接入；
- 不能声明全网 JD 搜索已完成；
- 不能声明招聘平台抓取、自动投递、ASR、MCP、SaaS 或真实个人资料路径已通过；
- Level2 必须由用户提供合法 provider、凭据、调用范围和一次性外呼确认后单独验收。
