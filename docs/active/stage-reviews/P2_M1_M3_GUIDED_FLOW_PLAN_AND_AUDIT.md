# P2-M1~M3 Guided Flow 阶段开发、验收与审计

生成日期：2026-06-12  
阶段范围：P2-M1 Workflow Orchestrator API、P2-M2 Chatbox Guided Flow、P2-M3 Human-readable Artifact Summary  
阶段结论：通过本子阶段验收；可以继续进入 P2-M4 Acceptance Evidence 和 P2-M5 Freeze Regression。当前不能声称 P2 已最终完成。

## 1. 本阶段目标

把 P1 已实现的后端 Domain Tools、artifact version、export 和 Chatbox 基础能力，组织成一条用户能在 Chatbox 中理解和触发的端到端体验路径。

本阶段不新增 MCP、CLI、ASR、会议平台或真实外部 Provider 默认调用。

## 2. 实现内容

### 后端

- 新增 `services/workflows/p2_demo.py`；
- 新增 `POST /api/workflows/p2-demo/run`；
- 新增 `P2DemoWorkflowRequest`；
- workflow 复用现有 Domain Tools，按顺序执行：

```text
导入示例简历和项目 README
→ extract_facts
→ create_project_card
→ parse_jd
→ match_profile
→ create_application_package
→ export Markdown + DOCX
→ prepare_interview
→ realtime text hint
→ review transcript
→ 返回 steps / artifacts / exports / key_outputs / summary
```

### 前端

- Chatbox 顶部新增 `端到端体验路径` 工作流面板；
- 新增“一键体验完整路径”按钮；
- 展示工作流步骤、完成状态、摘要和导出文件；
- 关键 artifact 增加人类可读摘要，减少纯 JSON 暴露；
- 新增本地可见验收入口 `?autorun=1`，用于自动触发 demo flow 截图，不需要 Chrome AppleScript JS 权限。

## 3. 自动化验收结果

```bash
python3 -m pytest tests/evals/test_p2_guided_demo_flow_eval.py
```

结果：

```text
1 passed
```

```bash
npm --prefix apps/chatbox run build
```

结果：

```text
通过
```

```bash
python3 -m pytest
```

结果：

```text
46 passed
```

## 4. Chrome 可见验收证据

已采集截图：

- `docs/reports/evidence/p2_initial_guided_flow.png`
- `docs/reports/evidence/p2_completed_guided_flow.png`
- `docs/reports/evidence/p2_summary_exports.png`
- `docs/reports/evidence/p2_summary_exports_chrome_wide.png`

截图确认：

- Chatbox 中出现 P2 端到端体验路径面板；
- 默认 provider 仍显示 `mock local`；
- `?autorun=1` 可以触发完整 demo flow；
- 步骤 1~9 均显示完成态；
- 完成态显示导出申请包、面试准备、实时文本结构提示、复盘训练任务；
- 总结区显示事实数量、匹配结论、训练任务数量和导出文件名。

说明：截图证明 UI 可见路径，不单独证明业务逻辑正确；业务正确性由 `test_p2_guided_demo_flow_eval.py` 和全量 pytest 证明。

## 5. PRD 规格检视

通过：

- 仍以极简 Chatbox 作为默认入口；
- 用户现在不需要猜 prompt，可以点击一键体验完整路径；
- workflow 复用后端 Domain Tools，没有把业务生成逻辑写入前端；
- 默认使用 examples 匿名真实感数据，不使用真实个人资料；
- 默认 provider 仍是 mock，不触发真实外部 Provider；
- 导出仍写入 workspace `exports/`；
- formal_assist 仍是结构提示边界，不输出隐蔽逐字代答。

未完成但属于 P2 后续：

- P2 HTML 最终验收报告；
- 更完整的截图包整理；
- 真实用户上传资料路径的逐步引导，而不只是 examples 一键路径；
- 更细的人类可读 artifact 卡片；
- P2 冻结审计。

## 6. 虚假验收风险控制

本阶段不声明：

- P2 已最终完成；
- 真实 API Key 已验收；
- 真实外部 Provider 调用已验收；
- 真实个人简历 / JD / transcript 已验收；
- 用户上传资料的全流程体验已完成；
- Chrome 截图等价于完整业务正确性。

当前可以声明：

> P2 的 examples-guided 端到端体验最小闭环已实现并通过自动化测试、前端构建和 Chrome 可见截图验收。

## 7. 是否允许进入下一阶段

允许进入 `P2-M4: Acceptance Evidence` 和 `P2-M5: Freeze Regression`。

当前没有发现致命或重大规格偏差。下一阶段必须补齐 P2 HTML 验收报告、更多截图证据整理、README/TODO 最终同步和冻结复验。

