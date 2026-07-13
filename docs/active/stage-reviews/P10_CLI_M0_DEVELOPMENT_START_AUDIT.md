# P10-CLI-M0 开发前启动审计

状态：通过，允许进入 P10-CLI-M1 到 M5 自动化开发。本文档是 P10-CLI 实际开发前的启动审计，不代表 CLI 已完成验收。

## 审计结论

```text
P10-CLI 文档支撑自动化开发启动：通过
P10-CLI M0-M5 顺序开发支撑：通过
真实数据边界：本地真实状态
是否允许进入代码开发：允许，从 P10-CLI-M1 开始
是否允许实现 MCP / 真实 provider / 招聘平台 / ASR / 自动投递：不允许
```

## 本轮真实数据边界

本阶段验收使用当前仓库真实本地状态：

- 当前仓库 `.jobpilot_workspace`；
- 当前仓库 `docs/reports/*.html`；
- 当前 FastAPI 本地 API；
- examples / fixture 演示路径。

不得使用：

- 未授权真实个人资料目录；
- 真实 LLM provider 默认外呼；
- 招聘平台登录、抓取或读取 `source_url` 网页；
- 真实市场 provider；
- ASR、会议平台、自动投递或 MCP server。

## M0 冻结项

| 冻结项 | 结论 | 后续验收 |
| --- | --- | --- |
| FastAPI 生命周期 | CLI 不自动启动 FastAPI；服务不可用时返回 exit 2 和启动建议 | service unavailable CLI eval |
| `reports open` 范围 | 只定位/打开已有报告；`--no-browser` 只打印路径 | report locator CLI eval |
| workspace 解析优先级 | `--workspace` > `JOBPILOT_WORKSPACE` > 当前目录 `.jobpilot_workspace` > 失败 exit 3 | workspace resolver CLI eval |

## 后续开发顺序

```text
P10-CLI-M1 CLI skeleton and help
→ P10-CLI-M2 workspace status and safety gate
→ P10-CLI-M3 demo/jobs/artifacts/reports commands
→ P10-CLI-M4 JSON envelope, exit code, audit log
→ P10-CLI-M5 Chinese HTML acceptance report and regression
```

## 打回条件

任一情况出现时停止开发并回到计划阶段：

- CLI 自动启动 FastAPI 或管理后台进程；
- `reports open` 生成、修复或重写报告；
- workspace selector 扫描用户目录或隐式寻找历史 workspace；
- CLI 默认读取 API Key 并真实外呼；
- CLI 读取真实个人资料目录、招聘平台网页或 `source_url`；
- 报告把 CLI 文档开发写成 CLI 实现验收通过。
