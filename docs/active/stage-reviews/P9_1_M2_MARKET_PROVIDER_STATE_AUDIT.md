# P9.1-M2 Market Provider 状态审计

状态：实现候选已落地；最终通过状态以 P9.1-M5 全量自动化报告、截图和 eval 为准。

## 开发内容

- 顶部服务中心新增 `Market Provider` 状态；
- 未配置真实市场 provider 时显示 `not_configured`；
- 地图和报告统一说明本轮只使用 fixture/manual/public 样例；
- JobSearchRun 保留查询词、城市、薪资、来源模式、结果数和 source refs。

## PRD 规格检视

| PRD 要求 | 实现候选 |
| --- | --- |
| 真实市场数据必须 opt-in | 默认显示 Market Provider 未配置 |
| 未授权不得外呼真实请求 | 本轮没有新增平台登录、抓取或 provider 调用 |
| fixture 不得写成真实市场 | source legend、服务状态和报告均标记边界 |

## 验收证据要求

- 截图中能看到 `Market Provider: not_configured`；
- HTML 报告列出未验证范围；
- 静态 guard 检查不得出现“真实市场 provider 已接入”等 false-green 句式。

## 打回条件

- 未授权情况下触发真实网络抓取或招聘平台登录；
- 把保存 URL、fixture 或本地样例写成真实市场接入；
- 顶部服务状态无法让用户快速识别 provider 未配置。

