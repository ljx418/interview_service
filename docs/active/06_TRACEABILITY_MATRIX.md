# JobPilot AI P4 UX 追踪矩阵

## 0. P4 当前阶段追踪矩阵

| P4 目标 | 实现区域 | 主要文件 / 模块 | 证据 | 验收门槛 |
| --- | --- | --- | --- | --- |
| P0/P1/P2/P3 不退化 | 全路径回归 | `services/`, `apps/chatbox/`, `tests/` | `python3 -m pytest`, frontend build | P4 门槛 0 |
| Chatbox 空状态任务入口清楚 | Conversation Empty State / Suggested Prompts | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 初始页 before/after、点击 prompt 后 composer 或对话截图 | P4 门槛 1 |
| 对话反馈可理解 | Conversation Plane / Chat API | ChatCore、chat routes、message UI | 有效/缺资料/错误态、loading 状态截图 | P4 门槛 2 |
| 错误恢复路径 | Error Recovery UI | message components、upload/JD prompts | 重新上传、补充 JD、查看格式截图 | P4 门槛 2 |
| 推进台职责清楚 | Workbench Plane | Workbench components、workflow summary | 当前任务和产物截图 | P4 门槛 3 |
| 产物卡可读 | Artifact Review Cards | artifact UI、artifact routes | 申请包/匹配报告/面试准备截图、primary/secondary action 截图 | P4 门槛 3 |
| Provider 语义不误导 | Mode and Provider Strip | provider routes、status UI | mock/external/未调用/需确认截图 | P4 门槛 4 |
| 全尺寸桌面工作台成立 | Full-size Desktop Workbench Controller | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css`, 截图脚本 | 1200/1440/1600/1920 Chrome 截图、桌面空白审查记录 | P4 门槛 5 |
| 响应式顺手 | Responsive Layout Controller / Mobile Workbench Drawer | CSS layout、composer、scroll regions | 1200/1440/1600/1920/720/390 Chrome 截图、390px Workbench 抽屉或折叠截图 | P4 门槛 5 |
| 截图证据可信 | Evidence Capture Controller | `scripts/capture_p4_workbench_evidence.mjs` | viewport emulation 清理逻辑、真实浏览器宽度检查、截图报告说明 | P4 门槛 5 / 6 |
| 可访问性冒烟 | Controls / Focus / Naming | button labels、focus styles、semantic regions | keyboard/focus 检查记录 | P4 门槛 5 |
| Gemini 审查包 | Frontend Review Package | `docs/gemini-frontend-review-package/` | 文件数、静态原型、提示词 | P4 门槛 6 |
| 报告和规格检视 | Evidence Package | `docs/reports/`, stage review | P4 HTML 报告、PRD review | P4 门槛 6 |
| 文档和 drawio 同步 | Active Docs / Drawio | `docs/active/`, drawio | XML parse、文本镜像 | P4 门槛 6 |

## 0.1 P4 防止过度计划的边界

以下内容不能作为 P4 出门条件：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台助手；
- 自动海投；
- SaaS 登录、多租户、Billing；
- 默认真实外部 Provider；
- 真实个人资料自动验收；
- 岗位数据源接入和 Offer 分析；
- 全量重写前端或复杂 Dashboard。

## 0.2 P4 防止规格不足的边界

缺少以下任一项，不能认为 P4 完成：

- Chatbox 空状态能让用户知道第一步；
- suggested prompts 能填入 composer 或触发对话；
- 有效输入、缺资料、错误都有可见反馈；
- loading / thinking / executing 状态可见；
- 错误状态有恢复 action；
- 推进台和对话职责清楚；
- 产物卡不依赖 JSON 才能理解，且按钮主次分明；
- provider 状态不误导外呼；
- 1200/1440/1600/1920 全尺寸桌面截图可用，且没有布局错误造成的大面积空白；
- 截图脚本隔离或清理 viewport emulation，不能污染人工审查者浏览器；
- 720/390 宽度截图可用，390px 下 Workbench 不压缩 Chatbox；
- mode toggle 具备 `aria-pressed` 或等价状态；
- Gemini 前端审查包存在且文件数小于 20；
- P4 HTML 报告不做虚假验收；
- README/TODO/active docs/drawio 口径一致。

以下 P3 追踪矩阵作为已完成基线和历史背景保留。

## 0.3 历史 P3 阶段追踪矩阵

| P3 目标 | 实现区域 | 主要文件 / 模块 | 证据 | 验收门槛 |
| --- | --- | --- | --- | --- |
| P0/P1/P2 不退化 | 全路径回归 | `services/`, `apps/chatbox/`, `tests/` | `python3 -m pytest`, frontend build | P3 门槛 0 |
| Chatbox 有响应 | Conversation UX / Chat API | `apps/chatbox/src/main.tsx`, `services/api/main.py`, ChatCore | Chrome 发送消息截图、错误态截图、eval | P3 门槛 1 |
| 模式边界清楚 | Mode and Provider State | Chatbox header/status, provider routes | 示例/真实资料模式截图、provider 状态截图 | P3 门槛 2 |
| 对话区和推进台分离 | Workbench Layout | `apps/chatbox/src/main.tsx`, `styles.css` | 桌面/窄屏截图 | P3 门槛 3 |
| 产物可管理 | Artifact Cards | artifact routes, version/export UI | version、confirm、regenerate、export 截图 | P3 门槛 3 / 5 |
| 响应式体验 | Responsive CSS / UX smoke | `apps/chatbox/src/styles.css` | 1280/720/390 Chrome 截图 | P3 门槛 4 |
| 真实感端到端体验 | Workflow + Domain Tools | `services/workflows/p2_demo.py`, tool APIs | examples E2E、导出文件、训练任务 | P3 门槛 5 |
| 验收报告 | Evidence Package | `docs/reports/`, `docs/reports/evidence/` | P3 HTML 报告、截图证据 | P3 门槛 6 |
| 文档和 drawio 同步 | Active Docs / Drawio | `docs/active/`, drawio | XML parse、文档审计 | P3 门槛 6 |

## 0.1 P3 防止过度计划的边界

以下内容不能作为 P3 出门条件：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台助手；
- 自动海投；
- SaaS 登录、多租户、Billing；
- 默认真实外部 Provider；
- 真实个人资料自动验收；
- 岗位数据源接入和 Offer 分析。

## 0.2 P3 防止规格不足的边界

缺少以下任一项，不能认为 P3 完成：

- Chatbox 对有效输入有可见响应；
- 无效输入和后端失败有明确错误反馈；
- 示例模式和真实资料模式边界可见；
- 对话区和推进台职责分离；
- 1280/720/390 三个宽度截图可用；
- examples 真实感数据端到端路径不退化；
- P3 HTML 报告不做虚假验收；
- README/TODO/active docs/drawio 口径一致。

以下 P2 追踪矩阵作为已完成基线和历史背景保留。

## 1. 目的

本矩阵把 P2 产品目标、实现区域、代码模块、证据产物和验收门槛连起来，避免后续开发出现范围不足或过度承诺。

## 2. P2 追踪矩阵

| P2 目标 | 实现区域 | 主要文件 / 模块 | 证据 | 验收门槛 |
| --- | --- | --- | --- | --- |
| P0/P1 不退化 | 全路径回归 | `services/tools/`, `services/llm/`, `apps/chatbox/`, `tests/` | `python3 -m pytest`, frontend build | 门槛 0 |
| 完整体验路径 | Workflow Orchestrator | `services/workflows/p2_demo.py`, `services/api/main.py` | `test_p2_guided_demo_flow_eval.py` | 门槛 1 |
| Chatbox 引导体验 | Guided Flow UI | `apps/chatbox/src/main.tsx`, `styles.css` | Chrome 初始/完成截图 | 门槛 2 |
| 一键本地可见验收 | Autorun入口 | `?autorun=1`, Chatbox workflow panel | 自动触发 demo flow 的 Chrome 截图 | 门槛 2 / 门槛 5 |
| 产物人类可读 | Artifact summary | `ArtifactReadableSummary` | 完成页截图、待确认项可见 | 门槛 3 |
| 版本和确认边界 | Artifact Cards | `apps/chatbox/src/main.tsx`, `services/tools/jobpilot.py` | version、edit、regenerate、confirm、export 入口 | 门槛 3 |
| 导出本地边界 | Export Service | `export_application_package`, download guard | Markdown/DOCX 文件、export eval | 门槛 4 |
| 截图证据 | Evidence Package | `docs/reports/evidence/` | 初始、完成、总结/导出截图 | 门槛 5 |
| HTML 验收报告 | Acceptance Report | `docs/reports/P2_END_TO_END_ACCEPTANCE_REPORT.html` | 报告文件、截图引用 | 门槛 5 |
| 文档和 drawio 同步 | Active Docs / Drawio | `docs/active/`, `jobpilot-stage-gap-and-acceptance.drawio` | XML parse、5 页结构、active docs count | 门槛 6 |

## 3. 防止过度计划的边界

以下内容不能作为 P2 出门条件：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台助手；
- 默认真实外部 Provider；
- 真实个人资料自动验收；
- 自动申请或自动投递；
- SaaS 登录、多租户、Billing；
- 岗位数据源接入；
- Offer 分析。

## 4. 防止规格不足的边界

缺少以下任一项，不能认为 P2 完成：

- P0/P1 回归测试通过；
- workflow API 能跑 examples 完整路径；
- Chatbox 可从 UI 触发 demo flow；
- UI 显示步骤状态和结果摘要；
- 关键产物不只展示 JSON；
- Markdown 和 DOCX 导出文件存在；
- Chrome 截图至少覆盖初始、完成、总结/导出；
- P2 HTML 报告存在；
- 报告明确未验证真实外部 Provider、真实 API Key 和真实个人资料；
- drawio 与 active docs 口径一致。

## 5. 方案评审问题

评审任何 P2 实现方案时必须回答：

- 这个改动是否让用户更接近完整 Chatbox 体验路径？
- 是否保持 P0/P1 可验收路径？
- 是否仍然本地优先、无登录、mock 默认可用？
- 是否复用 Domain Tools，而不是把业务生成逻辑写到前端？
- 是否避免真实 API Key 和真实个人资料自动进入验收？
- 是否能产生截图或测试证据？
- 是否避免把 MCP/CLI/ASR/会议平台误放进 P2 hard gate？

## 6. 执行计划入口

- P2 PRD：`01_STAGE_PRD.md`；
- P2 目标架构：`02_TARGET_ARCHITECTURE.md`；
- P2 里程碑：`03_MILESTONES_AND_DELIVERY_PLAN.md`；
- P2 验收门槛：`04_ACCEPTANCE_GATES.md`；
- P2 实现规格：`05_IMPLEMENTATION_SPEC.md`；
- P2 开发及审计计划：`13_P2_END_TO_END_EXPERIENCE_PLAN_AND_AUDIT.md`；
- P2 drawio：`jobpilot-stage-gap-and-acceptance.drawio`。
