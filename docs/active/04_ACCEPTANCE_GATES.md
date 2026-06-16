# JobPilot AI P3 验收门槛

## P3 验收门槛 0 - P0/P1/P2 回归不退化

通过条件：

- mock provider 默认路径仍可跑通 P0/P1/P2 examples 体验；
- P1 provider runtime、artifact version、regenerate、DOCX export 继续可用；
- P2 workflow API、guided flow、HTML 报告和截图证据仍可追溯；
- Pi Agent Core 业务编排仍能生成 intent/tool plan；
- Chatbox 仍是薄入口，不承载业务生成逻辑；
- workspace 路径沙箱、tool log 脱敏、formal_assist 边界不退化。

最低证据：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

## P3 验收门槛 1 - Chatbox 可对话和可失败

通过条件：

- 用户发送支持任务后，Chatbox 必须显示可理解响应；
- 空输入、无效任务、缺少资料、API 失败都有明确错误或下一步；
- 上传入口、JD 输入和发送按钮在桌面/窄屏/移动宽度可见；
- Enter 发送、Shift+Enter 换行行为不破坏输入。

不通过条件：

- 点击发送没有任何可见变化；
- 错误被静默吞掉；
- 前端伪造完成结果。

## P3 验收门槛 2 - 示例模式 / 真实资料模式边界

通过条件：

- 示例模式可一键跑 examples 完整路径；
- 真实资料模式明确说明本地处理、provider 状态和外部调用确认边界；
- mock / external provider 标签清楚；
- MiniMax 或其他外部 provider 只能在用户明确授权后受控验收；
- 未使用真实个人资料时，报告只能写“真实感示例数据验收”。

不通过条件：

- 把 examples 结果写成用户真实资料结果；
- 默认触发外部 provider；
- 把 API Key、完整简历、完整 JD 或 transcript 写入日志。

## P3 验收门槛 3 - 对话区和推进台分离

通过条件：

- 对话区负责输入、消息、计划和错误反馈；
- 推进台负责阶段、下一步、artifact、版本、确认项和导出；
- 用户能在视觉上区分“我要说什么”和“系统已经产出了什么”；
- 空状态提供下一步，不出现大面积无意义空白；
- artifact source refs、questions_to_confirm、version 信息不丢失。

## P3 验收门槛 4 - 响应式 UX

通过条件：

- 桌面宽度可完整展示对话区和推进台；
- 720px 窄屏下布局单列或合理堆叠，不出现半屏空洞；
- 390px 移动宽度下无严重横向滚动，输入区不遮挡消息；
- 卡片、按钮、状态标签文字不溢出；
- 滚动区域清楚，分区不被硬截断。

最低证据：

- Chrome 1280px 截图；
- Chrome 720px 截图；
- Chrome 390px 截图；
- 前端 build 通过。

## P3 验收门槛 5 - 端到端真实感数据体验

通过条件：

- 使用 examples 真实感数据完成导入资料、分析 JD、生成申请包、导出、面试准备、实时文本提示、复盘；
- 若使用外部 provider，只能使用匿名 examples 数据和用户授权的 API Key；
- 导出文件只写 workspace `exports/`；
- blocking confirmation 不得绕过导出 preflight；
- warning/optional confirmation 不得静默删除。

## P3 验收门槛 6 - 截图证据、HTML 报告和 PRD 规格检视

通过条件：

- P3 HTML 报告存在；
- 报告使用真实 Chrome 截图证据；
- 报告列出目标架构和当前架构实现；
- 报告列出当前可实现的用户场景体验路径；
- 报告列出自动化测试结果、未验证范围和虚假验收风险；
- 报告包含 PRD 规格检视和审计意见。

## P3 最终出门条件

一个用户可以在本地打开 Chatbox，明确选择示例模式或真实资料模式，通过聊天区上传/输入资料和 JD，看到系统响应、计划、错误或下一步；同时在分离的推进台中看到阶段、产物、确认项、版本和导出。项目必须在桌面、窄屏和移动宽度下完成截图验收，并通过 P0/P1/P2 回归测试和 P3 PRD 规格检视。

## P3 不通过条件

出现以下任一情况，P3 不得验收通过：

- Chatbox 对有效输入无可见响应；
- 真实资料模式默认触发外部 provider；
- examples 结果被写成真实个人资料验收；
- 窄屏或移动宽度出现严重截断、不可操作输入区或横向滚动；
- 推进台与聊天区职责混乱，用户无法理解下一步；
- P0/P1/P2 核心路径退化；
- 截图或报告把未执行事项写成已通过；
- MCP、CLI、ASR、会议平台、自动投递或 SaaS 被误作为 P3 必交付。

以下 P2 验收门槛作为已完成基线和历史背景保留。

## 验收门槛 0 - P0/P1 回归不退化

通过条件：

- mock provider 默认路径仍可跑通 P0 完整体验；
- P1 provider runtime、artifact version、regenerate、DOCX export 继续可用；
- Pi Agent Core 业务编排仍能生成 intent/tool plan；
- Chatbox 仍是薄入口；
- workspace 路径沙箱仍有效；
- realtime formal_assist 仍只输出结构提示。

必须通过：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

## 验收门槛 1 - Workflow Orchestrator

通过条件：

- `POST /api/workflows/p2-demo/run` 可执行；
- workflow 使用 examples 匿名真实感数据；
- workflow 串联现有 Domain Tools；
- 返回步骤、摘要、产物、导出文件和关键输出；
- 默认不触发真实外部 Provider；
- 失败时不得伪造完成步骤。

最低证据：

- `tests/evals/test_p2_guided_demo_flow_eval.py`；
- workflow 返回 9 个关键步骤；
- Markdown 和 DOCX 导出文件存在；
- training tasks 至少 3 个。

## 验收门槛 2 - Chatbox Guided Flow UX

通过条件：

- Chatbox 显示 P2 端到端体验路径面板；
- 用户可以点击一键体验完整路径；
- UI 显示步骤完成状态；
- UI 显示 provider 状态和 workspace 状态；
- UI 显示结果摘要和导出文件；
- UI 不变成复杂 dashboard。

最低证据：

- 前端 build 通过；
- Chrome 初始页截图；
- Chrome 完成页截图；
- Chrome 总结/导出截图。

## 验收门槛 3 - 产物可读性和确认边界

通过条件：

- 关键产物有可读摘要；
- JSON 可以作为详情保留，但不能是唯一表达；
- 待确认项必须可见；
- source refs 或 artifact refs 不丢失；
- version、edit、regenerate、export 入口仍可见；
- 未确认信息不能被包装为确定事实。

最低产出：

- ApplicationPackage 摘要；
- MatchReport 摘要；
- CareerFacts 摘要；
- InterviewPrep 摘要；
- 待确认项截图或测试证据。

## 验收门槛 4 - 导出和本地边界

通过条件：

- Markdown 继续可导出；
- DOCX 继续可导出；
- 导出文件只写 workspace `exports/`；
- workspace 外路径不能下载；
- blocking confirmation 规则不退化；
- warning/optional confirmation 不被静默删除。

最低产出：

- 一个 Markdown 文件；
- 一个 DOCX 文件；
- 一个导出路径截图或报告引用；
- 相关 eval 通过。

## 验收门槛 5 - 截图证据和 HTML 验收报告

通过条件：

- P2 HTML 报告存在；
- 报告使用截图证据；
- 报告列出目标架构；
- 报告列出当前架构实现；
- 报告列出当前可以实现的用户场景体验路径；
- 报告列出自动化测试结果；
- 报告明确已验证和未验证范围；
- 报告不做虚假验收。

最低产出：

- `docs/reports/P2_END_TO_END_ACCEPTANCE_REPORT.html`；
- `docs/reports/evidence/p2_initial_guided_flow.png`；
- `docs/reports/evidence/p2_completed_guided_flow.png`；
- `docs/reports/evidence/p2_summary_exports.png`；
- PRD 规格检视段落。

## 验收门槛 6 - 文档、drawio 和开源复现

通过条件：

- README 说明 P2 当时阶段目标和运行方式；
- TODO 与 active docs 不冲突；
- PRD、目标架构、里程碑、验收门槛和 drawio 口径一致；
- drawio 覆盖目标架构与当前架构差异、开发计划、里程碑、验收门槛和出门条件；
- active 文档数量保持可审计；
- 新贡献者能按 README 复现 API、Chatbox、tests、build 和 guided demo flow。

## P2 最终出门条件

一个用户可以在本地无 API Key 的 mock 模式下打开 Chatbox，看到端到端体验路径，点击一键体验 examples 完整求职流程，获得职业事实、项目卡、岗位匹配、申请包、导出文件、面试准备、实时文本提示、复盘和训练任务；人类可以通过 P2 HTML 报告和截图快速理解当前项目的目标架构、当前实现、体验路径、测试结果和未验证范围。

## P2 不通过条件

出现以下任一情况，P2 不得验收通过：

- P0/P1 回归测试失败；
- P2 workflow 需要真实 API Key 才能跑通；
- Chatbox 把业务生成逻辑写在前端；
- workflow 伪造已完成步骤；
- 导出写到 workspace 外；
- formal_assist 返回逐字代答；
- 截图或报告把未执行的真实外部调用写成已通过；
- docs/drawio 与实际范围不一致；
- MCP、CLI、ASR、会议平台被误作为 P2 必交付。
