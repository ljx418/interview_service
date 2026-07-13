# P10-CLI-M1 到 M5 自动化开发审计

状态：自动化候选通过。本文档记录 P10-CLI 实际开发阶段的子阶段计划、实现、验收和 PRD 规格检视。

## 数据边界

本轮使用本地真实状态验收：

- `.jobpilot_workspace` 中现有 SQLite workspace、exports、files；
- `docs/reports/*.html` 中现有 HTML 报告；
- 本地 FastAPI API；
- examples / fixture demo flow。

未使用、未声明通过：

- 真实个人资料目录；
- 真实 LLM provider；
- 招聘平台抓取；
- 真实市场 provider；
- MCP server；
- ASR、会议平台、自动投递、SaaS。

## 子阶段闭环

| 阶段 | 开发内容 | 验收结果 |
| --- | --- | --- |
| P10-CLI-M1 | 新增根命令 `./jobpilot` 和 `services/cli/main.py`；实现 `--help` | `./jobpilot --help` 通过 |
| P10-CLI-M2 | 实现 workspace resolver、ApiClient、service unavailable exit 2、安全门 | `test_p10_cli_eval.py` 覆盖 exit 2、exit 4、workspace env |
| P10-CLI-M3 | 实现 demo/jobs/artifacts/reports 命令 | `generate_p10_cli_acceptance.py` 真实调用本地 API 命令通过 |
| P10-CLI-M4 | 实现 JSON envelope、exit code、脱敏审计 | CLI eval 校验 JSON、exit code、redaction |
| P10-CLI-M5 | 生成中文 HTML 验收报告和报告 eval | `P10_CLI_ACCEPTANCE_REPORT.html` 生成；报告 eval 通过 |

## PRD 规格检视

| PRD 要求 | 当前结果 |
| --- | --- |
| `jobpilot --help` 可说明命令和边界 | 已实现 |
| `workspace status` 显示本地服务、workspace、provider、reports 状态 | 已实现 |
| `demo run --example` 只运行 examples / fixture | 已实现，报告中声明不代表真实资料或真实 provider |
| `jobs list` 列出本地岗位摘要 | 已实现 |
| `artifacts list/show` 列出产物与 source refs / pending confirmations 摘要 | 已实现 |
| `reports open --no-browser` 列出已有报告路径 | 已实现，不生成报告 |
| 不自动启动 FastAPI | 已实现，服务不可用返回 exit 2 |
| workspace 解析优先级固定 | 已实现：`--workspace` > `JOBPILOT_WORKSPACE` > `.jobpilot_workspace` > exit 3 |
| 不混入 MCP / 真实 provider / 平台抓取 / ASR / 自动投递 | 已由安全门和报告边界覆盖 |

## 自动化证据

```bash
python3 -m pytest tests/evals/test_p10_cli_eval.py tests/evals/test_p10_cli_acceptance_report_eval.py
python3 scripts/generate_p10_cli_acceptance.py
```

生成文件：

- `docs/reports/P10_CLI_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p10_cli/p10_cli_command_evidence.json`

## 审计结论

P10-CLI 已完成文档支撑范围内的自动化开发候选。该结论只覆盖本地 CLI 命令入口，不覆盖真实 provider、真实个人资料、招聘平台抓取、真实市场 provider、ASR、会议平台、自动投递、MCP server 或 SaaS。
