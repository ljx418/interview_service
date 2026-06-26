# JobPilot AI P5 真实资料本地闭环里程碑与交付计划

## P5 阶段目标

P4 已在 2026-06-25 完成本地/mock Chatbox 体验冻结。P5 的目标是把 P4 的示例路径推进到“真实资料本地闭环”：用户可以在本地 Chatbox 中导入或粘贴自己的资料和目标 JD，完成解析、匹配、事实确认、申请材料生成、编辑再生成、导出和连续追问。P5 不默认启用真实外部 provider，不进入 SaaS、ASR、会议平台、自动投递或 MCP/CLI 产品入口。

执行顺序：

```text
P5-M0 文档、drawio、风险边界和验收门槛锁定
→ P5-M1 真实资料本地导入与解析 UX
→ P5-M2 JD 导入、解析和缺失信息恢复
→ P5-M3 事实确认与 questions_to_confirm 闭环
→ P5-M4 申请包生成、编辑、再生成和导出 preflight
→ P5-FC 围绕真实资料/JD/申请包的本地多轮追问
→ P5-M5 脱敏自动化验收报告、截图证据和 PRD 规格检视
→ P5-Freeze 回归复验、人工体验记录和阶段冻结
```

## P5-M0 - 文档、drawio、风险边界和验收门槛锁定

交付物：

- P5 阶段 PRD；
- P5 目标架构和当前架构差异；
- P5 里程碑、验收门槛、追踪矩阵；
- P5 drawio gap 图和文本镜像；
- README/TODO/active docs 同步；
- 真实资料、外部 provider、API Key、报告脱敏和人工确认点清单。

出门条件：

- 文档明确 P5 是当前阶段，P4 是已冻结基线；
- drawio 不超过 8 页，覆盖目标架构、当前架构差异、代码实体关系、开发计划、里程碑、验收门槛和安全边界；
- 文档没有把 P6 外部 provider、P7 产品化 Beta 或 P8+ 高风险能力写成 P5 必交付；
- 进入代码开发前，审计无致命或重大规格偏差。

P5-M0 文档审计结论：

- 当前 PRD、目标架构、里程碑、验收门槛、追踪矩阵、drawio 文本镜像和 drawio 本体已经能支撑 P5 进入自动化开发；
- 文档已明确 P5 的默认技术路线是复用现有 FastAPI、ChatCore、Domain Tools、Artifact/Export、SQLite workspace 和 mock/local provider；
- 文档已明确真实外部 provider、provider-backed 自由智能聊天、SaaS、ASR、会议平台、自动投递、MCP/CLI 不进入 P5 出门条件；
- 后续开发不得跳过 P5-M1/M2/M3/M4/P5-FC 的分阶段验收直接制作 P5-Freeze 结论。

P5 自动化候选收口结论：

- P5-M1/M2/M3/M4/P5-FC/P5-M5 已用本地/mock + 脱敏 fixture 完成自动化候选验收；
- 当前证据为 P5 HTML 报告、多视口真实界面截图、P5 eval、`.venv/bin/python -m pytest` 88 passed, 1 warning、前端 build 通过、drawio XML parse 通过，以及三身份合成资料 Chrome/CDP 可视化验收通过；
- 该结论只允许支撑“P5 自动化候选通过”，不得写成“P5 已冻结”“真实个人资料路径已通过”或“真实外部 provider 默认路径已通过”；
- 剩余主线是 P5-REAL 和 P5-Freeze：等待用户提供明确本地脱敏真实资料路径和允许展示字段，随后完成真实资料复核、人工体验记录、最终回归和 final closure audit。

若启动开发前发现以下任一问题，必须先打回文档阶段：

- 现有 API 无法表达 P5 关键用户状态，且没有最小新增接口契约；
- `questions_to_confirm` 无法影响生成、导出或报告验收；
- 自动化报告无法脱敏；
- 普通多轮追问仍可能误触发 artifact 写入；
- P5 drawio 与 active docs 口径不一致；
- 开发计划要求使用真实外部 provider 作为默认路径。

## P5-M1 - 真实资料本地导入与解析 UX

交付物：

- Chatbox 中上传/粘贴资料入口清楚，紧邻输入框和任务动作；
- 支持简历、项目 README、经历说明或作品材料的本地导入；
- 导入后显示本地处理边界、解析状态、资料摘要、来源和待确认项；
- 缺资料、格式不支持、解析失败时给出恢复路径；
- 真实资料报告默认脱敏，未授权时使用 examples 真实感数据。

出门条件：

- 用户知道资料不会默认外呼；
- 资料导入后能看到可读摘要和下一步；
- 系统不把导入失败伪造成成功；
- API Key、完整简历或完整资料原文不进入报告、日志或测试 fixture。

## P5-M2 - JD 导入、解析和缺失信息恢复

交付物：

- 支持粘贴或导入目标 JD；
- 解析岗位要求、关键词、硬性条件、隐含风险和缺失信息；
- 当资料或 JD 缺失时，Chatbox 给出补充问题和恢复动作；
- Workbench 中能看到当前目标 JD 和解析状态。

出门条件：

- 用户能区分“资料已导入但缺 JD”“JD 已导入但资料不足”“可生成申请包”三种状态；
- JD 解析不只展示 JSON；
- 缺失信息能进入 `questions_to_confirm` 或等价确认队列。

## P5-M3 - 事实确认与 `questions_to_confirm` 闭环

交付物：

- 展示 blocking / warning / optional 三类确认项；
- 用户可以补充事实、确认、暂缓或编辑相关内容；
- 确认状态影响申请包生成和导出 preflight；
- 产物卡保留 source refs、确认项和版本信息。

出门条件：

- blocking confirmation 未处理时不得导出正式申请材料；
- 用户能看懂哪些事实需要补充，为什么会影响申请材料；
- 版本历史不被覆盖，旧版本仍可追溯。

## P5-M4 - 申请包生成、编辑、再生成和导出 preflight

交付物：

- 基于用户资料和 JD 生成申请包草稿；
- 支持编辑草稿、保存新版本、重新生成、切换版本；
- 支持 Markdown/DOCX 导出；
- 导出前显示 source refs、确认项、warning 和导出路径；
- Workbench 以求职语义展示申请包、匹配说明、面试准备等产物。

出门条件：

- 用户不读 JSON 也能理解产物价值、风险和下一步；
- 导出只写 workspace 允许路径；
- 导出文件、版本和确认项可追踪；
- 不绕过 blocking confirmation。

## P5-FC - 围绕真实资料/JD/申请包的本地多轮追问

交付物：

- 用户可以连续追问“当前进展如何”“我还缺什么”“这个经历能用于这个 JD 吗”；
- 普通追问不写入 artifact；
- 明确“生成 / 重新生成 / 导出 / 解析”才触发工具；
- 会话恢复后仍能看到上下文和当前 workspace 摘要。

出门条件：

- 至少两轮非执行型追问不误触发工具；
- 明确工具意图仍能稳定进入对应流程；
- 前端文案不暗示 provider-backed 自由智能聊天默认启用。

## P5-M5 - 脱敏自动化验收报告、截图证据和 PRD 规格检视

交付物：

- P5 HTML 自动化验收报告；
- 多视口真实界面截图；
- 资料导入、JD 解析、事实确认、申请包、编辑再生成、导出、多轮追问体验路径截图；
- PRD 规格检视和虚假验收风险清单；
- 测试、build、drawio XML parse 和文档一致性检查记录。

出门条件：

- 报告中文可读，能让人类快速理解目标架构、当前实现和用户路径；
- 报告不得暴露完整真实个人资料；
- 报告明确未验证的真实外部 provider、SaaS、ASR、会议平台、自动投递等范围。

## P5-Freeze - 回归复验、人工体验记录和阶段冻结

交付物：

- `.venv/bin/python -m pytest`；
- `npm --prefix apps/chatbox run build`；
- drawio XML parse；
- P5 人工体验审查清单；
- P5-REAL 真实授权资料脱敏复核记录；
- P5 final closure audit；
- README/TODO/active docs 最终同步。

出门条件：

- P0-P4 冻结基线不退化；
- P5 自动化验收、真实授权资料复核和人工体验记录均通过；
- final closure audit 未发现致命或重大规格偏差；
- 没有把真实外部 provider 默认路径、未授权真实个人资料或 P6/P7/P8 能力写成已通过。

## P5 技术路线选择与风险控制

P5 当前采用路线 A。路线 B 和路线 C 仅作为备选，不在本阶段默认执行。

| 路线 | 做法 | 优点 | 缺点 | 本阶段结论 |
| --- | --- | --- | --- | --- |
| A：复用现有本地工具链 | 复用现有 API、ChatCore、Domain Tools、Artifact/Export 和 SQLite workspace，补齐 P5 状态、测试和报告 | 改动最小，能保持 P0-P4 回归稳定；隐私风险最低；适合自动化开发 | 生成质量受 mock/local 规则限制，不等于真实 LLM 智能体验 | 采用 |
| B：P5 同时引入真实外部 provider | 在 P5 直接让真实 provider 参与资料解析、JD 匹配和申请包生成 | 可能提升文本质量和自由问答能力 | API Key、隐私、费用、失败降级和虚假验收风险显著上升；需要用户逐次确认 | 不采用，转 P6 opt-in |
| C：重构为新工作流/状态管理架构 | 大幅拆分前端、引入新 workflow 层或状态库 | 长期可维护性更好 | 容易扩大范围，影响 P4 冻结基线，延迟真实资料闭环 | 仅在现有结构阻塞 P5-M1/M2 后局部采用 |

主要残余风险和控制：

- 真实资料质量不可控：P5 使用 examples 自动化覆盖结构性路径，真实资料只做用户授权人工审查；
- 本地/mock 生成质量有限：P5 只验收本地闭环和可确认产物，不声称 provider-backed 质量；
- 确认项与导出耦合不足：P5-M3/M4 必须把 blocking confirmation 作为导出硬门槛；
- 前端状态复杂度上升：先复用现有组件，若出现状态不可维护，再按 Conversation / Workbench / Artifact / Export 局部拆分；
- 报告泄露风险：P5-M5 必须使用脱敏截图和报告，并加入隐私审计。

以下 P4 内容作为已冻结基线和历史背景保留。

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

## P4B 后置人工审查门槛（历史，已完成）

P4B 自动化开发闭环完成后曾要求人工体验审查。2026-06-25 人工体验审查已认可 P4B/P4C 本地 Chatbox 体验，P4 冻结复验已通过。历史人工审查记录位于：

```text
docs/active/stage-reviews/P4B_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md
```

历史判定规则：

- 人工认可：补冻结记录，并复跑 `python3 -m pytest`、`npm --prefix apps/chatbox run build`、drawio XML parse；
- 人工认为可接受但需微调：进入 P4C polish，不扩大阶段范围；
- 人工不认可：将阻塞项转成 P4C backlog，不进入 P5。

P4C 当时只允许处理体验微调和审查反馈，例如对话语气、Workbench 信息密度、产物详情非 JSON 预览、移动端抽屉路径、真实资料模式低风险引导，以及本地/mock 的自由 Chatbox 连续多轮对话基线。MCP、CLI、ASR、会议平台、自动投递、SaaS 和默认真实外部 provider 仍必须作为 P5+ 独立规划。

## P4C-FC - 自由 Chatbox 与本地连续多轮对话候选

触发条件：

- 人工体验审查认为 Chatbox 仍像任务控制台；
- 普通追问仍容易误触发工具；
- 用户无法围绕求职方向、偏好、下一步和当前状态连续对话。

交付物：

- Chat Intent Router 区分自由对话、状态查询、下一步、澄清和明确工具意图；
- 普通自由追问不写入 artifact；
- 明确“整理资料 / 解析 JD / 生成申请包 / 准备面试”才执行工具；
- 会话恢复后保留自由对话上下文；
- 前端提示用户可以连续追问，但不暗示真实外部模型默认启用；
- `18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`、TODO、报告和 drawio 同步。

出门条件：

- 自由追问两轮不触发工具的 eval 通过；
- 明确工具意图仍能生成对应 artifact；
- 前端 build 通过；
- 浏览器截图或 HTML 报告能证明“自由聊”和“执行工具”两条路径可区分；
- 未把 provider-backed 自由智能聊天写成当前完成。

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
