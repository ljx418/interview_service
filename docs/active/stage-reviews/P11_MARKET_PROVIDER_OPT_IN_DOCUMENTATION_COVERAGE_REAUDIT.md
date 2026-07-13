# P11 真实市场数据 Provider Opt-in 文档覆盖度复审

状态：文档审查阶段完成候选。本文档只审查 P11 文档是否足以支撑后续自动化开发；不代表 P11 代码实现、真实 provider 调用、招聘平台接入、ASR、MCP、自动投递或 SaaS 已通过。

## 1. 复审输入

本轮复审读取并交叉检查以下文档：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/26_P11_MARKET_PROVIDER_OPT_IN_PLAN.md`
- `docs/active/jobpilot-p11-market-provider-optin-gap.md`
- `docs/active/jobpilot-p11-market-provider-optin-gap.drawio`
- `docs/active/stage-reviews/P11_MARKET_PROVIDER_OPT_IN_DOCUMENTATION_DEVELOPMENT_AUDIT.md`
- `README.md`
- `TODO.md`

## 2. 第一轮审计：PRD 与目标体验

结论：通过。

PRD 已清楚说明 P11 要解决的产品缺口：P9.1 市场地图具备本地/fixture 产品化交互，但缺少可审计的真实市场 provider opt-in 数据链路。目标体验覆盖：

```text
Chatbox 发起市场查询
→ 顶部服务中心展示 provider 状态
→ 授权预览展示 provider、查询条件、数据类别、调用次数、费用/隐私提示
→ 用户确认后创建一次 JobSearchRun
→ provider/manual/public/fixture 输入被标准化为 NormalizedJobPost
→ 聚合为 JobMarketSnapshot
→ 地图、Chatbox、产物台和报告展示 source refs、confidence、未验证范围
```

PRD 已明确非目标：招聘平台登录/抓取/绕风控、长期爬虫、真实 LLM provider、ASR、MCP、自动投递、SaaS、未授权真实资料读取均不属于 P11 默认能力。

## 3. 第二轮审计：目标架构与实体关系

结论：通过。

目标架构已经从抽象概念落到可开发实体：

```text
UI Control Plane
→ FastAPI /api/market/* boundary
→ MarketProviderPolicyGate
→ MarketProviderClient
→ MarketDataNormalizer
→ SourceRefBinder / ConfidenceScorer
→ JobMarketSnapshot
→ UI / CLI / HTML report
```

关键实体状态清楚：

- 已实现需修改：`TopServiceCenter`、`ConversationPlane`、`MarketIntelligenceMap`、`ArtifactWorkbench`；
- 待新增：`JobMarketProviderRegistry`、`MarketProviderPolicyGate`、`MarketProviderClient`、`MarketProviderInvocationLog`、`JobSearchRunService`、`MarketDataNormalizer`、`SourceRefBinder`、`ConfidenceScorer`、`NormalizedJobPost`、`JobMarketSnapshot`；
- 复用边界：FastAPI、SQLite workspace、artifact、reports、P10 CLI evidence；
- 禁止范围：招聘平台 connector、长期爬虫、真实 LLM provider、ASR、MCP、自动投递、SaaS。

架构可以支撑 P11 后续实现，不需要新增独立招聘平台系统。

## 4. 第三轮审计：API、存储和失败语义

结论：通过。

P11 已定义 FastAPI handoff：

- `GET /api/market/providers/status`
- `POST /api/market/providers/check`
- `POST /api/market/search-runs`
- `GET /api/market/search-runs/{run_id}`
- `GET /api/market/snapshots/{run_id}`
- `GET /api/market/source-refs/{source_ref_id}`

P11 已定义建议存储实体：

- `job_market_providers`
- `job_search_runs`
- `normalized_job_posts`
- `job_market_snapshots`
- `region_source_refs`
- `market_provider_invocation_logs`

P11 已定义失败语义：`PROVIDER_NOT_CONFIGURED`、`CONSENT_REQUIRED`、`PROVIDER_CALL_FAILED`、`NO_RESULTS`、`FALLBACK_ONLY`、`POLICY_REJECTED`。这些语义足以让后续实现和报告区分未配置、未授权、调用失败、无结果、fallback 和 policy 拒绝。

## 5. 第四轮审计：验收分级与出门风险

结论：通过。

P11 已建立 Level 0 到 Level 3 验收分级：

| 级别 | 允许声明 | 不允许声明 |
| --- | --- | --- |
| Level 0 | 文档可支撑后续开发 | P11 已实现 |
| Level 1 | 本地实现和 fixture/recorded/public/manual 路径通过 | 真实 provider 已通过 |
| Level 2 | 指定真实 provider opt-in 路径通过 | 全网 JD 搜索、招聘平台、自动投递通过 |
| Level 3 | 指定多 provider/source 对比通过 | 未测试 provider 或平台通过 |

该分级解决了 P11 最大 false-green 风险：没有真实 provider 凭据或合法公开调用源时，只能声明 Level 1，不能声明 Level 2。

## 6. 第五轮审计：drawio 与文本镜像

结论：通过。

P11 drawio 保持 8 页，不超过限制，并已补齐与 P10/P9.1 历史基线等价的审查信息：

1. 目标体验与架构决策；
2. 当前架构与 P11 差距、三类审计风险；
3. 目标架构与实体强关联链；
4. 命令流、数据流和失败分支；
5. 数据契约与证据链判定；
6. 开发计划、验收分级和阶段打回条件；
7. 里程碑门槛、出门条件和人类审核问题清单；
8. 安全边界、后续路线和备选技术路线取舍。

审计者可以基于 drawio 判断架构风险、规格偏移风险、开发计划完成后的出门验收风险。

## 7. 剩余开发计划大纲

P11 后续应按以下顺序进入自动化开发：

| 阶段 | 目标 | 开发前审计重点 | 出门验收 |
| --- | --- | --- | --- |
| P11-M0 | 开发前启动审计 | 冻结不抓平台、不默认外呼、不长期爬虫、不伪造真实市场 | stage review 无重大规格偏差 |
| P11-M1 | Provider 状态 API | 不泄露密钥，configured 不等于 called | status API、TopServiceCenter、CLI 状态输出 |
| P11-M2 | Provider check 授权门和调用日志 | 未确认拒绝外呼，确认后只做 minimal check | consent preview、拒绝证据、脱敏 invocation log |
| P11-M3 | Search run / normalization / snapshot | 不补造缺失事实，每个指标有 source refs | `JobSearchRun`、`NormalizedJobPost`、`JobMarketSnapshot` eval |
| P11-M4 | Chatbox / 地图 / 产物台联动 | UI、CLI、report 状态一致 | 多视口截图、source refs、confidence、fallback 可见 |
| P11-M5 | 中文自动化验收报告 | Level 1 / Level 2 判定清楚 | pytest、frontend build、P11 eval、HTML 报告、PRD 规格检视 |

## 8. 后续详细验收计划

后续 P11 实现完成后至少执行：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
python3 -m pytest tests/evals/test_p11_market_provider_optin_eval.py
drawio XML parse docs/active/jobpilot-p11-market-provider-optin-gap.drawio
P11 Chinese HTML acceptance report
```

中文 HTML 验收报告必须包含：

- provider 状态截图；
- consent preview 截图；
- 未确认拒绝外呼证据；
- 成功或失败的脱敏 invocation log；
- `JobSearchRun`、`NormalizedJobPost`、`JobMarketSnapshot` 示例；
- 地图、Chatbox、产物台展示 source refs 和 confidence 的截图；
- Level 1 / Level 2 判定；
- 未验证 provider、招聘平台、ASR、MCP、自动投递、SaaS 的声明。

## 9. 是否需要 ChatGPT 再审计

结论：不强制需要。

理由：P11 文档当前已经覆盖 PRD、目标架构、实体关系、API handoff、存储 handoff、失败语义、验收分级、drawio 风险矩阵、出门条件和 false-green 打回条件。当前未发现必须交给外部审计才能消减的致命或重大风险。

可选建议：如果用户希望增加外部审计信心，可以把第 10 节文档包交给 ChatGPT 审计，但这不是进入 P11-M0 的硬前置。

## 10. 可交给 ChatGPT 审计的文档路径

推荐审计文档少于 20 个：

1. `README.md`
2. `TODO.md`
3. `docs/active/00_README.md`
4. `docs/active/01_STAGE_PRD.md`
5. `docs/active/02_TARGET_ARCHITECTURE.md`
6. `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
7. `docs/active/04_ACCEPTANCE_GATES.md`
8. `docs/active/06_TRACEABILITY_MATRIX.md`
9. `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
10. `docs/active/26_P11_MARKET_PROVIDER_OPT_IN_PLAN.md`
11. `docs/active/jobpilot-p11-market-provider-optin-gap.md`
12. `docs/active/jobpilot-p11-market-provider-optin-gap.drawio`
13. `docs/active/stage-reviews/P11_MARKET_PROVIDER_OPT_IN_DOCUMENTATION_DEVELOPMENT_AUDIT.md`
14. `docs/active/stage-reviews/P11_MARKET_PROVIDER_OPT_IN_DOCUMENTATION_COVERAGE_REAUDIT.md`

## 11. 最终结论

通过。当前文档水平已经可以完整支撑 P11 本阶段后续自动化开发。P11 完成后可以支撑 PRD 中“Chatbox 发起真实市场查询、授权预览、一次性 JobSearchRun、NormalizedJobPost、JobMarketSnapshot、source refs、confidence、地图/Chatbox/产物台/报告联动”的目标体验，并达成目标架构中的受控 provider boundary、normalization domain 和 evidence-first 设计。

保留限定：

- 这不是 P11 代码实现通过；
- 这不是真实 provider 默认路径通过；
- 这不是招聘平台接入通过；
- 这不是全网 JD 搜索通过；
- 这不是 ASR、MCP、自动投递或 SaaS 通过；
- 是否能声明 Level 2 取决于后续是否具备用户授权的真实 provider 凭据或合法公开调用源。
