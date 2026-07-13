# P11 真实市场数据 Provider Opt-in 文档开发审计

状态：文档开发阶段完成候选。本文档记录 P11 文档开发范围、架构审计、验收门槛和 false-green 边界。

## 1. 审计背景

P9.1 已完成本地/fixture 范围内的行政区划下钻市场地图和 Socratic Intake。P10-CLI 已完成本地命令入口自动化候选。当前未完成的核心体验缺口是：市场地图和求职情报仍缺少真实市场 provider opt-in 数据链路。

P11 选择低风险路径：

```text
真实市场 provider opt-in
≠ 招聘平台抓取
≠ 全网 JD 搜索系统
≠ 长期爬虫
≠ 自动投递
```

## 2. 架构审计

P11 架构采用五层：

| 层级 | 结论 |
| --- | --- |
| UI Control Plane | 复用 P9.1 的顶部服务中心、Chatbox、市场地图、产物台，后续只修改状态和数据来源表达 |
| Market Provider Boundary | 新增 registry、policy gate、client、invocation log，隔离真实外呼风险 |
| Market Normalization Domain | 新增 search run、normalizer、source ref binder、confidence scorer，避免 UI 直接消费 provider raw response |
| Existing Boundary | 复用 FastAPI、workspace、artifact、reports，不新建招聘平台系统 |
| Evidence Layer | 后续必须生成中文报告、调用日志、source refs 和截图证据 |

架构风险可控，因为 P11 不直接做平台自动化，不新增长期后台任务，不读取真实个人资料，不调用真实 LLM provider。

## 3. 文档覆盖度

已覆盖：

- P11 PRD 和目标体验；
- provider 状态机；
- 数据契约；
- FastAPI API handoff；
- SQLite 存储和证据实体；
- Level 0 / Level 1 / Level 2 / Level 3 验收分级；
- 代码实体状态；
- 命令流和数据流；
- 里程碑和后续开发计划；
- 验收门槛；
- drawio 和文本镜像；
- false-green 打回条件。

## 4. drawio 质量复核

本轮按 P10-CLI 和 P9.1 drawio 的历史基线复核 P11 drawio，发现早期 P11 图存在信息密度偏低风险：它能表达 P11 目标和边界，但不足以让人类独立判断架构风险、PRD 偏移风险和出门验收风险。

已修订 `docs/active/jobpilot-p11-market-provider-optin-gap.drawio` 和文本镜像，补齐：

- 第 1 页：架构决策和路线取舍，明确采用 opt-in API provider + normalization anti-corruption layer + evidence first；
- 第 2 页：架构风险、PRD 偏移风险、验收风险三类矩阵；
- 第 3 页：UI / API / PolicyGate / Client / Normalizer / Snapshot / Report 的强关联实体链；
- 第 4 页：provider 未配置、未授权、调用失败、无结果、fallback-only、policy rejected 的失败分支；
- 第 5 页：从 consent 到 invocation log、source refs、snapshot、report evidence 的证据链判定；
- 第 6 页：P11-M0 到 M5 的阶段打回条件；
- 第 7 页：人类审核问题清单；
- 第 8 页：opt-in provider、manual/public source、招聘平台抓取、长期爬虫的路线取舍。

复核结论：修订后的 P11 drawio 不低于 P10/P9.1 的审查强度；审计者可以基于该图判断当前架构风险、规格是否偏离 PRD、后续开发完成后能否出门验收，以及哪些场景必须打回。

## 5. 不允许声明

- 不允许声明真实市场 provider 已接入；
- 不允许声明全网 JD 搜索已完成；
- 不允许声明 BOSS/猎聘/拉勾/LinkedIn 已接入；
- 不允许声明 provider configured 等于 called；
- 不允许声明 fixture/manual/public sample 等于真实市场；
- 不允许声明 ASR、MCP、自动投递或 SaaS 已完成。

## 6. 剩余风险与闭环结论

风险 1：真实 provider 凭据和网络可用性不由代码仓库控制。

闭环方式：P11 文档已定义 Level 1 / Level 2 验收分级。没有真实 provider 凭据或合法公开调用源时，后续实现只能声明 Level 1 本地实现通过，不得声明 Level 2 真实 provider opt-in 通过。

风险 2：实现时可能为了快速展示地图效果而用 fixture/fallback 冒充真实市场。

闭环方式：P11 文档已要求 `JobMarketSnapshot.source_breakdown`、`RegionSourceRef`、`confidence` 和中文报告中的未验证范围。fixture/manual/public/fallback 必须可见，不得替代真实 provider evidence。

风险 3：真实市场 provider 容易滑向招聘平台抓取或长期爬虫。

闭环方式：P11-M0 必须冻结 provider 范围，只允许 opt-in API、manual paste、company public source 和 fixture/recorded source；招聘平台登录、绕验证码、长期抓取、自动沟通、自动投递必须单独立项。

## 7. 结论

P11 文档可以支撑后续 P11-M0 开发前启动审计。当前没有需要用户先选择技术路线的不可消减阻塞；但 P11 后续是否能声明 Level 2，取决于实现阶段是否具备用户授权的真实 provider 凭据或合法公开调用源。进入代码开发前仍必须再次确认高风险边界：不抓平台、不默认外呼、不长期爬虫、不伪造真实市场。
