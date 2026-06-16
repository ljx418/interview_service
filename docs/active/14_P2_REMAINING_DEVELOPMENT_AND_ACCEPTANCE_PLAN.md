# JobPilot AI P2 剩余开发及验收计划

生成日期：2026-06-12  
适用阶段：P2-M4 Acceptance Evidence、P2-M5 Freeze Regression  
审计结论：当前文档体系可以支撑 P2 剩余开发；新增本文档用于把 P2-M4/M5 落到文件、命令、截图、报告字段和打回条件级别。

## 1. 当前完成状态

已完成：

- P2 PRD、目标架构、里程碑、验收门槛、实现规格、追踪矩阵、自动化范围和 drawio；
- `services/workflows/p2_demo.py`；
- `POST /api/workflows/p2-demo/run`；
- `tests/evals/test_p2_guided_demo_flow_eval.py`；
- Chatbox `端到端体验路径` 工作流面板；
- `?autorun=1` 本地可见验收入口；
- 关键 artifact 最小人类可读摘要；
- P2 初始、完成、总结/导出截图证据；
- `python3 -m pytest` 曾通过，当前记录为 46 passed；
- `npm --prefix apps/chatbox run build` 曾通过。

剩余：

- P2 HTML 验收报告；
- P2 截图证据整理和引用；
- P2 冻结回归；
- P2 冻结审计；
- README/TODO/active docs/drawio 最终一致性检查。

## 2. 剩余开发工作包

## WP4.1 - P2 HTML 验收报告

目标：

- 生成一个人类可快速阅读的 P2 HTML 验收报告；
- 报告必须使用真实截图证据；
- 报告必须明确已验证和未验证范围；
- 报告不得做虚假验收。

文件：

```text
docs/reports/P2_END_TO_END_ACCEPTANCE_REPORT.html
```

报告必须包含：

- 人类快速结论；
- 截图证据区；
- 当前可实现的用户场景体验路径；
- P2 目标架构；
- 当前架构实现；
- 关键实现清单；
- 自动化验收结果；
- Chrome 可见验收结果；
- 已验证范围；
- 未验证范围；
- PRD 规格检视；
- 目标架构检视；
- 虚假验收风险控制；
- 人工体验复核建议；
- 相关文档路径。

不得声明：

- 真实外部 Provider 已通过；
- 真实 API Key 已通过；
- 真实个人资料已通过；
- P2 已支持 MCP/CLI/ASR/会议平台；
- 截图等价于全部业务正确性；
- 用户上传真实资料路径已完整验收。

## WP4.2 - 截图证据整理

目标：

- 把已有截图变成报告可引用的证据包；
- 如果截图包含终端或裁剪不完整，报告中必须如实说明；
- 可补充更干净截图，但不能删除原始证据。

当前证据文件：

```text
docs/reports/evidence/p2_initial_guided_flow.png
docs/reports/evidence/p2_completed_guided_flow.png
docs/reports/evidence/p2_summary_exports.png
docs/reports/evidence/p2_summary_exports_chrome_wide.png
```

报告中每张截图必须说明：

- 截图证明了什么；
- 截图不能证明什么；
- 是否包含非产品区域；
- 对应验收门槛。

## WP4.3 - P2 阶段审计补全

目标：

- 把 P2-M4/M5 的开发计划、验收标准、审计意见和 PRD 检视写入 stage review；
- 不能把 P2-M1~M3 通过误写成 P2 全部完成。

建议文件：

```text
docs/active/stage-reviews/P2_M4_M5_ACCEPTANCE_EVIDENCE_AND_FREEZE_AUDIT.md
```

必须包含：

- P2-M4 计划；
- P2-M4 验收结果；
- P2-M5 冻结计划；
- PRD 规格检视；
- 目标架构检视；
- 虚假验收风险；
- 是否允许 P2 冻结；
- 未进入 P2 的高风险/非目标功能。

## WP5.1 - 自动化冻结复验

必须执行：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
python3 -m pytest tests/evals/test_schema_and_docs_hardening_eval.py
python3 -m pytest tests/evals/test_p2_guided_demo_flow_eval.py
```

必须记录：

- pytest 总数；
- build 是否通过；
- 文档硬化测试是否通过；
- P2 guided flow eval 是否通过；
- 如果失败，失败原因和打回计划。

## WP5.2 - 文档和 drawio 冻结检查

必须执行或等价检查：

```bash
find docs/active -name '*.md' -type f | wc -l
python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/active/jobpilot-stage-gap-and-acceptance.drawio')"
```

必须确认：

- active Markdown 文档数小于 20；
- drawio XML 可解析；
- drawio 页数为 5；
- drawio 页名覆盖架构、计划、里程碑、验收门槛和追踪矩阵；
- README/TODO 不再把 P2 剩余工作误写成 P1；
- active docs、drawio、测试结果和 HTML 报告口径一致。

## WP5.3 - 本地服务与 Chrome 可见验收

必须执行：

```bash
python3 -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000
npm --prefix apps/chatbox run dev -- --host 127.0.0.1 --port 5174
open -a "Google Chrome" "http://127.0.0.1:5174/?autorun=1"
```

必须确认：

- `/api/workflows/p2-demo/run` 返回 200；
- Chrome 页面显示 workflow 完成状态；
- 页面显示总结和导出文件；
- 服务结束后没有本项目 uvicorn/vite 进程残留。

如果 Chrome 截图失败：

- 不得声称可见验收通过；
- 必须保留失败原因；
- 必须打回 WP4.2 或 WP5.3。

## 3. P2 最终验收路径

P2 最终验收必须覆盖：

```text
启动 API 和 Chatbox
→ 打开 Chatbox
→ 查看 workspace 和 provider 状态
→ 触发 examples guided flow
→ 查看步骤 1~9 完成状态
→ 查看本次结果摘要
→ 查看 Markdown / DOCX 导出文件
→ 查看关键 artifact 摘要和待确认项
→ 查看面试准备、实时提示、复盘训练任务
→ 打开 P2 HTML 验收报告
→ 检查报告中的已验证 / 未验证范围
```

## 4. 打回条件

出现以下任一情况，必须打回开发计划阶段：

- `python3 -m pytest` 失败；
- 前端 build 失败；
- P2 guided flow eval 失败；
- workflow 需要真实 API Key 才能跑；
- Chatbox 业务生成逻辑进入前端；
- 导出文件写出 workspace；
- formal_assist 返回逐字代答；
- HTML 报告把未执行的真实外部调用写成已通过；
- HTML 报告未引用截图证据；
- drawio 和 active docs 口径不一致；
- active Markdown 文档数达到或超过 20。

## 5. 人工确认边界

以下不允许自动越过：

- 真实 API Key；
- 真实外部 Provider 调用；
- 真实个人简历、真实 JD、真实 transcript；
- 不可逆 workspace 迁移；
- 删除用户导出文件；
- ASR、会议平台、MCP、CLI、自动投递、SaaS 化。

## 6. 最终审计意见

P2 当时文档体系可以完整支撑本阶段剩余开发。剩余工作已经收敛为证据、报告和冻结验收，不再存在重大规格空白。

当前不应启动 P3；P2 必须先完成 HTML 验收报告、截图证据整理、全量回归和冻结审计。
