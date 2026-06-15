# JobPilot AI P2 实现规格

## 1. 目的

本文档把 P2 PRD、目标架构、里程碑和验收门槛转成可交付工程规格。P2 的核心不是新增更多入口，而是把 P0/P1 已完成能力组织成完整端到端 Chatbox 用户体验。

P2 实现必须服务这条体验路径：

```text
打开 Chatbox
→ 看到 workspace / provider 状态
→ 一键或按引导导入资料
→ 生成事实、项目卡、JD 分析、申请包
→ 确认 / 编辑 / regenerate
→ 导出 Markdown + DOCX
→ 面试准备 / 实时文本提示 / 复盘训练
→ 查看推进摘要、产物和导出文件
```

## 2. P2-M1 Workflow Orchestrator API

目标：

- 提供后端一键体验 API，使用 examples 匿名真实感数据跑完整求职路径；
- workflow 只编排现有 Domain Tools，不复制业务逻辑；
- 默认不触发真实外部 Provider。

实现要求：

- 模块：`services/workflows/p2_demo.py`；
- API：`POST /api/workflows/p2-demo/run`；
- Request：`P2DemoWorkflowRequest`；
- 输出字段：
  - `workspace_id`;
  - `steps`;
  - `artifacts`;
  - `exports`;
  - `summary`;
  - `key_outputs`;
- 每个 step 必须包含：
  - `key`;
  - `title`;
  - `status`;
  - `summary`;
  - `artifact_refs`;
  - `metrics`;
- 失败时不能伪造后续完成步骤。

验收证据：

- `tests/evals/test_p2_guided_demo_flow_eval.py`；
- workflow 返回 9 个关键步骤；
- Markdown 和 DOCX 导出文件存在；
- training tasks 至少 3 个。

## 3. P2-M2 Chatbox Guided Flow

目标：

- 让用户在 Chatbox 中看到明确的端到端体验路径和下一步动作；
- 用户可以点击“一键体验完整路径”触发 examples demo flow；
- 支持 `?autorun=1` 作为本地可见验收入口。

实现要求：

- 文件：`apps/chatbox/src/main.tsx`；
- 文件：`apps/chatbox/src/styles.css`；
- UI 必须展示：
  - workspace 状态；
  - provider 状态；
  - workflow title；
  - 一键体验按钮；
  - step list；
  - step status；
  - workflow summary；
  - exports summary；
- `?autorun=1` 只能触发本地 demo flow，不允许触发真实外部 Provider；
- Chatbox 不得拼业务 prompt 或直接写业务表。

验收证据：

- `npm --prefix apps/chatbox run build` 通过；
- Chrome 初始页截图；
- Chrome 完成页截图；
- Chrome 总结/导出截图。

## 4. P2-M3 Human-readable Artifact Summary

目标：

- 关键产物不再只靠 JSON 展示；
- 人类能快速理解结果、待确认项和下一步。

实现要求：

- `ApplicationPackage` 显示项目描述和 recruiter message 摘要；
- `MatchReport` 显示匹配结论、优势和缺口；
- `Job` 显示岗位和技术栈；
- `CareerFacts` 显示事实数量和前几条事实；
- `InterviewPrep` 显示问题和故事卡数量；
- JSON 可以保留为开发者详情；
- 待确认项、版本、edit/regenerate/export 入口不能被隐藏。

验收证据：

- 完成页截图可见人类可读摘要；
- 待确认项仍可见；
- 版本和操作入口仍可见。

## 5. P2-M4 Acceptance Evidence

目标：

- 让人类能快速理解本阶段做了什么、证明了什么、没有证明什么。

实现要求：

- 生成 `docs/reports/P2_END_TO_END_ACCEPTANCE_REPORT.html`；
- 报告必须包含：
  - 人类快速结论；
  - 截图证据；
  - 目标架构；
  - 当前架构实现；
  - 用户场景体验路径；
  - 自动化测试结果；
  - 已验证范围；
  - 未验证范围；
  - PRD 规格检视；
  - 虚假验收风险控制；
  - 人工体验复核建议；
- 截图至少包含：
  - 初始页；
  - workflow 完成页；
  - 总结/导出页。

验收证据：

- HTML 报告可打开；
- 报告引用真实存在的截图；
- 报告不声称真实外部 Provider、真实 API Key 或真实个人资料已验收。

## 6. P2-M5 Freeze Regression

目标：

- 冻结 P2 阶段，确认文档、实现、截图、测试和 drawio 一致。

必须通过：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

必须检查：

- drawio XML 可解析；
- drawio 页数为 5；
- active 文档数量保持可审计；
- README/TODO 与 active docs 一致；
- stage review 写明已验证和未验证范围；
- 本地服务结束后不留下本项目进程。

## 7. P2 禁止实现

P2 不得把以下内容作为出门条件：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台；
- 自动申请 / 自动投递；
- SaaS 登录、多租户或 Billing；
- 默认真实外部 Provider；
- 真实个人资料自动验收。

## 8. 高风险人工确认

以下动作必须暂停找用户确认：

- 使用真实 API Key；
- 调用真实外部模型；
- 使用真实个人简历、私有 JD 或 transcript；
- 删除 workspace；
- 执行不可逆迁移；
- 接入 ASR、会议平台、屏幕解析或视频解析。

