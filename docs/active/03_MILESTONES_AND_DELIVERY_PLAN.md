# JobPilot AI P3 里程碑与交付计划

## P3 阶段目标

P3 的目标是在 P2 examples-guided 端到端体验基础上，交付真实用户可用的 Chatbox 工作台。P3 必须修复“演示面板能跑，但用户不知道怎么聊天、窄屏体验差、Chatbox 与推进台边界不清”的问题。

执行顺序：

```text
P3-M0 文档和门禁锁定
→ P3-M1 Chatbox 对话响应闭环
→ P3-M2 示例模式 / 真实资料模式工作流
→ P3-M3 推进台与产物区重构
→ P3-M4 响应式 UX 与可访问性冒烟验收
→ P3-M5 Chrome 截图证据与 HTML 报告
→ P3-M6 回归验收与阶段冻结
```

## P3-M0 - 文档和门禁锁定

交付物：

- P3 PRD 增补；
- P3 目标架构增补；
- P3 里程碑；
- P3 验收门槛；
- P3 详细开发及验收计划；
- P3 drawio gap 图；
- README/TODO 同步。

出门条件：

- 文档明确 P2 已完成但人类体验审查仍驱动 P3；
- drawio 覆盖目标架构与当前架构差异、开发计划、里程碑、验收门槛和出门条件；
- 没有把 MCP、CLI、ASR、会议平台、自动海投或 SaaS 放入 P3 hard gate；
- P3 启动审计无致命或重大规格偏差。

## P3-M1 - Chatbox 对话响应闭环

交付物：

- Chatbox 发送任意支持任务后有可见消息响应；
- 空输入、无效任务、缺少资料、后端错误都有明确反馈；
- “上传资料 / 粘贴 JD / 生成申请包 / 准备面试”形成稳定意图入口；
- chatbot 无响应问题有 eval 或浏览器证据覆盖。

出门条件：

- 用户不需要看 README 也知道下一步；
- 前端不把业务生成逻辑写死；
- API 失败不伪造成成功；
- Chrome 截图能看到消息响应和错误态。

## P3-M2 - 示例模式 / 真实资料模式工作流

交付物：

- 示例模式继续支持一键 examples E2E；
- 真实资料模式显示本地隐私边界、provider 状态和人工确认提示；
- 上传、粘贴 JD、生成产物的入口文案一致；
- mock / external provider 状态不混淆。

出门条件：

- examples 路径不退化；
- 真实资料模式不会自动触发外部 provider；
- 外部 provider 只在用户确认后进入受控验收；
- 未使用真实个人资料时不得写成“真实个人资料验收通过”。

## P3-M3 - 推进台与产物区重构

交付物：

- 对话区和推进台视觉分离；
- 推进台显示阶段、下一步、产物摘要、版本、确认项和导出；
- 产物卡支持查看当前版本、编辑 / regenerate / export 入口；
- 空状态不出现大面积无意义空白。

出门条件：

- 用户能区分“聊天输入”和“结果管理”；
- 右侧或下方推进台不截断关键内容；
- source refs、questions_to_confirm、version 不丢失。

## P3-M4 - 响应式 UX 与可访问性冒烟验收

交付物：

- 桌面、720px 窄屏、390px 移动宽度截图；
- 无严重横向滚动；
- 输入区不遮挡消息；
- 卡片、按钮、状态标签不发生文字溢出；
- 键盘 Enter / Shift+Enter 行为清楚。

出门条件：

- `npm --prefix apps/chatbox run build` 通过；
- Chrome 截图证明 1280、720、390 三个宽度可用；
- 发现体验重大偏差时打回 P3-M3，不做虚假验收。

## P3-M5 - Chrome 截图证据与 HTML 报告

交付物：

- P3 HTML 验收报告；
- 截图证据包；
- 目标架构、当前实现、体验路径、已验证/未验证范围；
- PRD 规格检视和审计意见。

出门条件：

- 报告不把未执行的真实外部调用写成已通过；
- 报告列出截图路径、测试命令和失败风险；
- 人类能在 3 分钟内理解当前项目可实现的用户体验。

## P3-M6 - 回归验收与阶段冻结

交付物：

- 全量或相关 pytest；
- 前端 build；
- P0/P1/P2 回归路径；
- README/TODO/active docs/drawio 同步；
- P3 冻结审计。

出门条件：

- P0/P1/P2 核心路径不退化；
- P3 验收门槛全部有证据；
- 不存在致命或重大规格偏差；
- 未完成的人类体验审查项明确列入残留风险。

以下 P2 内容作为已完成基线和历史背景保留。

## 阶段目标

P2 的目标是在 P0/P1 已完成的本地工程闭环之上，交付完整端到端 Chatbox 用户体验。P2 必须让人类能通过 UI、截图和 HTML 报告理解项目已经实现的体验路径、架构能力和未验证范围。

执行顺序：

```text
P2-M0 文档和门禁锁定
→ P2-M1 Workflow Orchestrator API
→ P2-M2 Chatbox Guided Flow
→ P2-M3 Human-readable Artifact Summary
→ P2-M4 Acceptance Evidence
→ P2-M5 回归验收与阶段冻结
```

## P2-M0 - 文档和门禁锁定

交付物：

- P2 PRD；
- P2 目标架构；
- P2 里程碑；
- P2 验收门槛；
- P2 drawio gap 图；
- README/TODO 同步。

出门条件：

- 文档明确 P0/P1 已完成、P2 当时目标和当时后续非目标；
- drawio 覆盖目标架构、当前架构差异、开发计划、里程碑、验收门槛和出门条件；
- 没有把 MCP、CLI、ASR、会议平台纳入 P2 出门条件；
- P2 启动审计无致命或重大规格偏差。

当前状态：已完成。

## P2-M1 - Workflow Orchestrator API

交付物：

- `services/workflows/p2_demo.py`；
- `POST /api/workflows/p2-demo/run`；
- `P2DemoWorkflowRequest`；
- workflow 返回 `steps`、`artifacts`、`exports`、`summary`、`key_outputs`；
- `tests/evals/test_p2_guided_demo_flow_eval.py`。

出门条件：

- examples 完整路径通过；
- workflow 复用现有 Domain Tools；
- 默认不触发真实外部 Provider；
- 导出文件只进入 workspace `exports/`；
- 新增 eval 通过。

当前状态：已完成，新增 eval 通过。

## P2-M2 - Chatbox Guided Flow

交付物：

- Chatbox 工作流面板；
- 一键体验完整路径按钮；
- 步骤完成状态；
- 结果摘要；
- `?autorun=1` 本地可见验收入口。

出门条件：

- 用户可以在 Chatbox 中触发 examples demo flow；
- UI 显示至少 7 个关键步骤；
- workflow 完成后显示结果摘要和导出文件；
- 前端 build 通过；
- Chrome 初始页和完成页截图采集。

当前状态：已完成最小闭环。

## P2-M3 - Human-readable Artifact Summary

交付物：

- ApplicationPackage 摘要；
- MatchReport 摘要；
- Job 摘要；
- CareerFacts 摘要；
- InterviewPrep 摘要；
- JSON 仍保留为开发者详情，但不再是唯一可读信息。

出门条件：

- 关键产物卡能让人类快速理解结果；
- 不隐藏 source refs、待确认项或版本信息；
- 不把未确认内容包装成确定事实。

当前状态：已完成最小摘要，后续可继续增强。

## P2-M4 - Acceptance Evidence

交付物：

- P2 Chrome 截图包；
- P2 HTML 验收报告；
- 截图证据、自动化测试、架构说明、用户场景路径；
- 已验证 / 未验证范围；
- 虚假验收风险控制。

出门条件：

- 至少 3 张截图：初始页、完成页、总结/导出页；
- HTML 报告能被人类快速阅读；
- 报告列出目标架构、当前架构实现、体验路径和测试结果；
- 报告明确真实外部 Provider、真实 API Key、真实个人资料未验收。

当前状态：进行中。

## P2-M5 - 回归验收与阶段冻结

交付物：

- 全量 pytest；
- 前端 build；
- PRD 规格检视；
- P2 冻结审计；
- README/TODO/active docs/drawio 同步。

出门条件：

- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过；
- P2 guided flow eval 通过；
- Chrome 截图证据存在；
- P2 HTML 报告存在且无虚假验收；
- active 文档数量保持可审计；
- docs/drawio 与实现一致；
- 没有新增 P2 非目标功能。

## 需人类确认的节点

以下节点不能自动越过：

- 配置真实 API Key；
- 使用真实个人资料；
- 进行真实外部模型调用；
- 执行不可逆数据库迁移；
- 删除 workspace 或清理用户导出文件；
- 接入 ASR、会议平台、MCP 或 CLI；
- 判断当前 UI 是否达到人类体验验收标准。
