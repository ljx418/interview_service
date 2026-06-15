# P2-M4/M5 Acceptance Evidence 与 Freeze Regression 阶段审计

生成日期：2026-06-13  
阶段范围：P2-M4 Acceptance Evidence、P2-M5 Freeze Regression  
阶段结论：P2 自动化冻结验收通过；当前可以进入人工体验复核。本报告生成时真实外部 Provider、真实 API Key、真实个人资料和用户上传资料完整手动路径未自动验收；P2-M6 已在用户授权后补充 MiniMax opt-in provider examples 受控验收。

## 1. 本阶段目标

完成 P2 剩余交付：

- P2 HTML 验收报告；
- 截图证据整理；
- 全量自动化回归；
- drawio/docs 一致性检查；
- PRD 规格检视；
- 目标架构检视；
- 虚假验收风险控制。

## 2. P2-M4 验收证据

新增报告：

```text
docs/reports/P2_END_TO_END_ACCEPTANCE_REPORT.html
```

引用截图：

```text
docs/reports/evidence/p2_initial_guided_flow.png
docs/reports/evidence/p2_completed_guided_flow.png
docs/reports/evidence/p2_summary_exports.png
docs/reports/evidence/p2_summary_exports_chrome_wide.png
docs/reports/evidence/p2_2026-06-13_autorun_completed.png
docs/reports/evidence/p2_2026-06-13_html_report_open.png
```

截图证据说明：

- 初始页证明 Chatbox 出现 P2 工作流面板和一键体验入口；
- 完成页证明 P2 workflow 进入完成状态；
- 总结/导出页证明步骤 6~9、本次结果和导出文件可见；
- 2026-06-13 autorun 截图证明当天重新打开 `?autorun=1` 后 workflow 请求返回 200；
- 2026-06-13 HTML report 截图证明验收报告已在 Chrome 中打开；
- 部分截图包含非产品区域，因此只作为可见验收证据，不单独证明业务正确性。

## 3. P2-M5 冻结复验结果

```bash
python3 -m pytest
```

结果：

```text
46 passed
```

```bash
npm --prefix apps/chatbox run build
```

结果：

```text
通过
```

```bash
python3 -m pytest tests/evals/test_schema_and_docs_hardening_eval.py
```

结果：

```text
3 passed
```

```bash
python3 -m pytest tests/evals/test_p2_guided_demo_flow_eval.py
```

结果：

```text
1 passed
```

drawio 检查：

```text
XML 可解析，5 页：
01 P2架构与差异
02 P2开发及验收计划
03 P2项目里程碑
04 P2验收门槛与出门条件
05 P2实现追踪矩阵
```

active 文档数量：

```text
17，小于 20
```

## 4. PRD 规格检视

通过：

- P2 仍以极简 Chatbox 为默认入口；
- 用户可以看到端到端体验路径，而不是猜 prompt；
- examples guided flow 能生成事实、项目卡、JD 分析、匹配报告、申请包、导出文件、面试准备、实时提示、复盘和训练任务；
- 默认 provider 仍为 mock；
- 验收使用 examples 匿名真实感数据；
- 导出仍写入 workspace `exports/`；
- 不把 MCP、CLI、ASR、会议平台、自动投递或 SaaS 化纳入 P2 出门条件。

未自动验收：

- 真实个人简历 / JD / transcript；
- 用户上传资料的完整手动路径；
- 移动端完整视觉体验；
- 长时间稳定性和并发压测。

P2-M6 后补验收：

- MiniMax API Key 连通性；
- MiniMax OpenAI-compatible provider examples 受控 E2E；
- provider-backed `profile_extract_facts`、`job_parse_jd`、`job_match_profile`、`application_create_package`；
- Markdown / DOCX 导出；
- provider_invocation API Key 脱敏和摘要长度收敛。

## 5. 目标架构检视

通过：

- Experience Flow 已作为 Chatbox 顶部工作流面板落地；
- Workflow Orchestrator 已通过 `services/workflows/p2_demo.py` 落地；
- Workflow Route 已通过 `POST /api/workflows/p2-demo/run` 落地；
- Workflow 复用现有 Domain Tools，没有复制业务生成逻辑；
- Chatbox 没有直接写业务表；
- Provider 默认 mock，真实外部调用未被自动触发；
- Artifact version、regenerate、export 仍由后端工具和存储层处理；
- Evidence Gates 已覆盖 pytest、frontend build、guided flow eval、drawio 和截图证据。

## 6. 虚假验收风险控制

本阶段原始冻结报告不声明：

- 真实个人资料已通过；
- P2 已支持 MCP/CLI/ASR/会议平台；
- 用户上传资料完整手动路径已通过；
- 截图等价于全部业务正确性。

补充说明：P2-M6 已通过 MiniMax opt-in examples 受控验收，但不等于真实个人资料、用户上传完整手动路径或默认真实 provider 已通过。

当前可以声明：

> P2 examples-guided 端到端体验路径已通过本地自动化测试、前端构建、文档/drawio 检查和已有 Chrome 可见截图证据；可以进入人工体验复核。

## 7. 是否允许 P2 冻结

自动化门槛：允许冻结。  
人工体验门槛：等待用户审核 HTML 报告和截图后确认。

如果人工体验认为工作流面板、摘要或截图证据不足，应打回 P2-M4 做 UX 小步修正和重新截图。
