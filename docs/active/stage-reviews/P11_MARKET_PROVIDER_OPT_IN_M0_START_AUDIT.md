# P11-M0 开发前启动审计

状态：通过。本文档是 P11 自动化开发前的风险冻结和执行准入记录，不代表 P11 已实现，也不代表真实市场 provider 已验收。

## 1. 本阶段允许实现

- FastAPI market provider 边界：provider status、provider check、search run、snapshot、source refs。
- SQLite workspace 内的 P11 市场数据表：provider registry、search run、normalized job posts、market snapshot、source refs、invocation log。
- Level 1 本地实现路径：fixture、manual、public sample、recorded data 的归一化、source refs、confidence、fallback 标识。
- CLI 和 Chatbox 展示 market provider 状态、search run、snapshot 和 source refs。
- P11 eval、中文 HTML 验收报告、PRD 规格检视和 false-green 边界说明。

## 2. 本阶段禁止实现或默认触发

- 不登录、不抓取、不绕过 BOSS、猎聘、拉勾、LinkedIn 等招聘平台。
- 不启动长期爬虫、队列、定时任务或批量平台访问。
- 不默认读取或调用真实市场 provider API Key。
- 不默认调用真实 LLM provider。
- 不读取用户未授权的真实个人资料目录。
- 不实现 ASR、麦克风、会议平台、MCP server、自动投递、自动沟通、SaaS、多租户或 Billing。
- 不存储 API Key、provider secret、完整 raw response、招聘平台 cookie/session/验证码/账号信息。

## 3. 验收分级冻结

- Level 1 可以通过：本地 fixture/manual/public/recorded provider 边界、归一化、snapshot、source refs、UI/CLI 联动和报告通过。
- Level 2 不能默认声明：只有用户明确提供合法 provider 凭据、确认真实外呼，且产生脱敏 invocation log 和 source refs 后，才能声明指定 provider opt-in 通过。
- 没有真实 provider 凭据时，P11-M5 只能声明 Level 1。

## 4. 开发前审计意见闭环

| 审计项 | 结论 | 处理 |
| --- | --- | --- |
| PRD 是否支持实现 | 通过 | 以 `26_P11_MARKET_PROVIDER_OPT_IN_PLAN.md` 为主规格 |
| 架构边界是否明确 | 通过 | UI/CLI 只能走 FastAPI，不能直连 provider 或 SQLite |
| 真实 provider 风险 | 已冻结 | 默认关闭真实外呼，只实现 opt-in 边界 |
| false-green 风险 | 已冻结 | 报告必须区分 Level 1 与 Level 2，不得把 fallback 写成真实市场 |
| 高风险操作 | 无需用户确认即可继续 Level 1 | 若触发真实 provider、平台、ASR、MCP、自动投递则必须暂停 |

## 5. 进入实现的出门条件

可以进入 P11-M1 到 P11-M5 自动化开发。开发停止时必须打印停止原因；若验收发现架构实现与 drawio/PRD 不一致、承诺内容未实现、测试阻塞、或 false-green 风险无法消除，必须拒绝声明 P11 自动化开发完成并打回开发阶段。
