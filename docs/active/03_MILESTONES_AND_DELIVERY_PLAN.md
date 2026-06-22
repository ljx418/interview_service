# JobPilot AI P4 UX 里程碑与交付计划

## P4 阶段目标

P4 的目标是在 P3 自动化验收已完成的基础上，解决人工审查指出的核心体验问题：首屏不够自然、对话和推进台仍有认知负担、产物卡工程味重、provider 状态易误解、移动端只是可用但不够顺手。P4B 进一步把“全尺寸桌面工作台体验”纳入 hard gate：1200px、1440px、1600px、1920px 不能只是窄屏布局放大后停靠在左侧，也不能留下由布局错误造成的大面积空白。P4 不新增 MCP/CLI/ASR/会议平台等入口，不重写后端架构。

执行顺序：

```text
P4-M0 文档、drawio 和 Gemini 审查包锁定
→ P4-M1 信息架构和 Chatbox 空状态任务入口优化
→ P4-M2 对话反馈和任务启动体验优化
→ P4-M3 推进台与产物卡可读性优化
→ P4-M4 状态、错误恢复和 provider 语义优化
→ P4-M5 响应式精修与可访问性冒烟验收
→ P4-M5A 全尺寸桌面工作台与截图脚本隔离修正
→ P4-M6 before/after 截图报告、Gemini 审查反馈和阶段冻结
```

## P4-M0 - 文档、drawio 和 Gemini 审查包锁定

交付物：

- P4 PRD 增补；
- P4 目标 UX 架构；
- P4 里程碑；
- P4 验收门槛；
- P4 drawio gap 图和文本镜像；
- Gemini 前端页面审查包，文件数小于 20；
- README/TODO/active docs 同步。

出门条件：

- 文档明确 P4 是当前 UX 体验强化阶段；
- drawio 覆盖目标架构与当前架构差异、开发及验收计划、项目里程碑、验收门槛和出门条件；
- Gemini 审查包可独立阅读，包含页面方案、组件状态、交互验收、静态原型和推荐提示词；
- 没有把 MCP、CLI、ASR、会议平台、自动海投或 SaaS 放入 P4 hard gate；
- P4 启动审计无致命或重大规格偏差。

## P4-M1 - 信息架构和 Chatbox 空状态任务入口优化

交付物：

- 首屏从工程状态堆叠改为 Chatbox 空状态 suggested prompts；
- 建议任务覆盖导入资料、粘贴 JD、生成申请包、准备面试；
- 点击建议任务后填入 composer 或直接触发对话；
- workspace / mode / provider 状态降级为清晰状态条；
- 空状态直接给出下一步。

出门条件：

- 用户 5 秒内能判断第一步；
- examples 和我的资料路径入口清楚；
- 任务入口和对话区形成闭环，不再割裂；
- Chrome 初始页 before/after 截图可对比；
- 不隐藏本地优先和外部 provider 边界。

## P4-M2 - 对话反馈和任务启动体验优化

交付物：

- 有效输入返回计划、处理中或结果摘要；
- 缺资料、无效任务、后端错误提供恢复路径；
- loading / thinking 状态显示正在读取资料、对比 JD 或生成草稿；
- 错误气泡附带重新上传、补充 JD、查看格式等恢复 action；
- 长 JD、长计划和长摘要具备折叠策略；
- 快捷任务不只是按钮，而要映射到明确任务流；
- Composer 在移动端不遮挡消息。

出门条件：

- 点击发送不会出现“无反应”；
- 错误态不伪造成成功；
- 任务启动截图覆盖有效、缺资料、错误三类状态。

## P4-M3 - 推进台与产物卡可读性优化

交付物：

- 推进台聚焦当前任务、下一步、产物和确认项；
- 推进台空状态说明“导入资料后，求职产物将在此生成”；
- 产物卡使用求职语义命名；
- source refs、questions_to_confirm、version 信息可展开但不喧宾夺主；
- 导出、确认、编辑、regenerate 操作层级更清楚；
- 阻塞卡片突出 primary action，例如“补充事实 / 去确认”，secondary action 降低权重；
- 待确认项文案使用求职辅导语气。

出门条件：

- 用户不需要看 JSON 也能理解产物价值和风险；
- 用户能在 5 秒内判断该优先点击哪个操作；
- 待确认项不会被隐藏；
- 内部 id 不作为主视觉信息；
- 申请包、匹配报告、面试准备至少三类产物有截图证据。

## P4-M4 - 状态、错误恢复和 provider 语义优化

交付物：

- provider 状态区分“已配置 / 本次未调用 / 将外呼需确认 / 外呼失败”；
- 状态文案优先使用“外部模型未调用（隐私安全）”“外部调用需确认”等用户语言；
- loading、progress、recoverable error 的视觉语言统一；
- 外部调用、真实资料和导出前确认的风险提示更明确。

出门条件：

- 用户不会把 provider 已配置误解为默认外呼；
- 错误提示给出可执行恢复路径；
- API Key、真实个人资料、外部调用仍需人工确认。

## P4-M5 - 响应式精修与可访问性冒烟验收

交付物：

- 1200px 桌面布局；
- 1280px 桌面布局；
- 1440px 桌面布局；
- 1600px 桌面布局；
- 1920px 桌面布局；
- 720px 窄屏布局；
- 390px 移动布局；
- 键盘、焦点、按钮命名和对比度冒烟检查。
- segmented mode toggle 使用 `aria-pressed` 或等价状态。

出门条件：

- 无严重横向滚动；
- 1200px、1440px、1600px、1920px 下页面像完整工作台，而不是窄屏 Chatbox 停靠在左侧；
- 全尺寸桌面下对话区、状态指标、快捷任务、推进台摘要和下一步建议均有明确位置；
- 输入区不遮挡消息；
- 390px 下 Conversation 优先，Workbench 收为底部抽屉、折叠面板或次级区域；
- 当前任务、消息、主要产物操作在 390px 下可达；
- `npm --prefix apps/chatbox run build` 通过。

## P4-M5A - 全尺寸桌面工作台与截图脚本隔离修正

交付物：

- 全尺寸桌面工作台布局修正，覆盖 1200px、1440px、1600px、1920px；
- 桌面宽度下补齐对话上下文、状态指标、快捷任务、推进台摘要和下一步建议；
- Chrome 截图脚本隔离或在 `finally` 中清理 viewport emulation / touch emulation；
- 报告中明确列出全尺寸桌面、窄屏和移动端截图，不把自动截图替代人工体验认可；
- 如发现大面积空白或人工浏览器 viewport 被脚本污染，必须打回 P4-M5A。

出门条件：

- 1200px、1440px、1600px、1920px 截图不存在由布局错误造成的大面积空白；
- 截图脚本结束后真实浏览器 viewport 未残留移动 emulation；
- 人工审查者能在全尺寸桌面下看见完整求职材料工作台结构；
- P4 HTML 报告和 drawio 文本镜像同步更新。

## P4-M6 - before/after 报告、外部审查反馈和阶段冻结

交付物：

- P4 UX before/after HTML 报告；
- Chrome 截图证据，至少覆盖 1200px、1440px、1600px、1920px、720px、390px；
- Gemini 审查包路径和建议提示词；
- PRD 规格检视；
- pytest、frontend build、drawio XML parse；
- README/TODO/active docs 同步。

出门条件：

- 报告明确哪些体验已改善、哪些仍需人工判断；
- 报告明确是否存在全尺寸桌面空白、截图脚本污染 viewport、或自动截图无法替代人工判断的风险；
- 不把静态原型写成已实现；
- 不把 Gemini 审查替代人工体验验收；
- P0/P1/P2/P3 核心路径不退化；
- 不存在致命或重大规格偏差。

以下 P3 内容作为已完成基线和历史背景保留。

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
