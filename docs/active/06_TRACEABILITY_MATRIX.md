# JobPilot AI P6+P7 长程对话与产品化 Beta 追踪矩阵

## -1. P6+P7 当前阶段追踪矩阵

| P6/P7 目标 | 实现区域 | 主要文件 / 模块 | 证据 | 验收门槛 |
| --- | --- | --- | --- | --- |
| P0-P5 本地基线不退化 | 全路径回归 | `services/`, `apps/chatbox/`, `tests/` | `.venv/bin/python -m pytest`, frontend build | P6+P7 门槛 0 |
| Provider 默认安全 | Provider status / consent / policy | `services/api/main.py`, provider runtime/policy, `apps/chatbox/src/main.tsx` | 默认不外呼截图、configured/consented/called 状态 eval | P6 门槛 1 |
| 模型设置和调用前确认 | Chatbox Model Settings / Provider Consent UI | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css`, provider preferences route | 模型设置、调用前确认、取消确认截图 | P6 门槛 1 |
| Provider-backed chat | Provider-backed Dialogue Adapter | `services/llm/`, `services/chat/core.py` | fake provider eval、受控真实 provider E2E 记录 | P6 门槛 2 |
| 失败降级 | Local Fallback Dialogue / Error Recovery | `services/chat/core.py`, provider runtime, message UI | timeout/429/schema error 降级截图和测试 | P6 门槛 2 |
| 长程连续对话 | Long Context Manager | 建议新增 `services/chat/context.py`, chat session storage, message UI | 20-50 轮 eval、rolling summary、refresh recovery 截图 | P6 门槛 3 |
| 上下文来源边界 | Context Snapshot / Retrieval | artifact/JD/profile retrieval, workspace snapshot | source refs、summary、context snapshot 报告 | P6 门槛 3 / 5 |
| Tool Safety | Intent Router / Artifact Guard / Export Guard | `services/chat/core.py`, artifact/export services | 普通聊天不写 artifact、blocking export 拦截测试 | P6 门槛 4 |
| Provider invocation 脱敏 | Invocation Log / Redaction | tool/provider logs, redaction helpers | configured/called/failed/fallback 脱敏日志、敏感扫描 | P6 门槛 5 |
| P6 可视化验收 | Browser evidence / HTML report | screenshot scripts, `docs/reports/` | 中文 HTML 报告、多视口真实截图、PRD 规格检视 | P6 门槛 6 |
| Workspace 生命周期 | Workspace lifecycle service / routes | SQLite workspace、本地文件目录、workspace routes | backup/export/cleanup dry-run/migration dry-run 测试和截图 | P7 门槛 7 |
| 不可逆操作确认 | Cleanup / Migration confirm UI | workspace lifecycle routes, Chatbox UI | 删除/迁移 apply 前确认截图 | P7 门槛 7 |
| 诊断报告 | Diagnostics service / report generator | diagnostics route, redaction, report scripts | 脱敏诊断报告、敏感扫描 | P7 门槛 8 |
| 发布部署回滚 | Release docs / scripts / checklist | README、RELEASE_CHECKLIST、scripts | 启动、部署、回滚文档审计 | P7 门槛 8 |
| Beta 支持流程 | User guide / support runbook | docs active/reports | Beta 使用说明、支持流程、故障排查 | P7 门槛 9 |
| P7 隐私审计 | Privacy audit | provider/workspace/diagnostics/export/report | 安全隐私审计记录 | P7 门槛 9 |
| P7-post P5 复验 | P5-REAL acceptance scripts/reports | `scripts/generate_p5_real_data_acceptance.py`, P5 stage reviews | 用户授权路径后的 P5-REAL 报告和 final audit | P7-post 门槛 |
| 文档和 drawio 同步 | Active Docs / Drawio | `docs/active/`, drawio | XML parse、文本镜像、README/TODO sync | P6+P7 门槛 |

## -0. P6+P7 防止过度计划的边界

以下内容不能作为 P6+P7 出门条件或已完成能力：

- 真正无限 token、无限上下文或无限成本；
- 默认真实外部 provider；
- 未经确认的真实个人资料外发；
- SaaS 登录、多租户、Billing；
- ASR / Whisper、系统音频、会议平台；
- 自动投递、岗位数据源聚合、Offer 分析；
- MCP Server 或 CLI 产品入口；
- 未授权真实个人资料自动验收；
- workspace 删除或迁移 apply 的默认执行。

## -0.1 P6+P7 防止规格不足的边界

缺少以下任一项，不能认为 P6+P7 完成：

- 用户能判断 provider configured、consented、called、failed、fallback；
- 未确认不外呼；
- API Key 不进入前端、仓库、日志、报告、截图说明或 fixture；
- provider 失败能降级并保留会话；
- 20-50 轮长程连续对话有 rolling summary、context snapshot 和 refresh recovery；
- 普通聊天不写 artifact，provider-backed chat 不绕过 confirmation/export preflight；
- workspace backup/export/cleanup dry-run/migration dry-run 可验收；
- diagnostics report 脱敏；
- release/deploy/rollback/support 文档可复现；
- P7 后 P5-REAL/P5-Freeze 复验路径不被 synthetic personas 替代；
- README/TODO/active docs/drawio 口径一致。

## -0.2 P6+P7 自动化开发任务映射

| 开发任务 | 代码边界 | 建议测试 | 截图 / 报告证据 |
| --- | --- | --- | --- |
| P6-M1 Provider opt-in UX | Chatbox 模型设置、provider status/consent routes、policy gate | provider default safety eval | 默认不外呼、模型设置、调用前确认、取消确认 |
| P6-M2 Provider-backed adapter | provider runtime、chat adapter、redaction、retry/timeout | fake provider eval、受控真实 provider 记录 | provider-backed 回复、失败降级 |
| P6-M3 Long Context Manager | chat context module、session storage、summary/retrieval | long conversation eval | 20-50 轮、rolling summary、refresh recovery |
| P6-M4 Tool Safety | intent router、artifact/export guards | chat/artifact/export safety eval | 普通聊天不写 artifact、blocking export 拦截 |
| P6-M5 Privacy / Invocation Log | provider invocation log、redaction helpers、report filters | sensitive scan eval | configured/called/failed/fallback 脱敏日志 |
| P6-M6 Visual Acceptance | browser evidence script、HTML report | acceptance report eval | 中文报告、真实界面截图、多视口 |
| P7-M1 Workspace lifecycle | workspace lifecycle service/routes、Chatbox lifecycle UI | lifecycle eval | backup/export/cleanup dry-run/migration dry-run |
| P7-M2 Diagnostics / Release | diagnostics service、release docs/scripts | diagnostics/report/docs eval | 脱敏诊断报告、启动/部署/回滚证据 |
| P7-M3 Beta closure | guide、support runbook、privacy audit、final report | P7 acceptance report eval | Beta 使用说明、支持流程、隐私审计 |
| P7-post P5 revalidation | P5-REAL scripts/reports/stage review | P5 real data revalidation eval | 用户授权资料路径后的脱敏复验报告 |

## -0.3 P6+P7 文档支撑与开发准入结论

当前文档在补齐 P6+P7 PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap 和 drawio 后，可以支撑下一阶段自动化开发，前提是开发严格遵守以下边界：

- P6 真实 provider 必须 opt-in，不默认外呼；
- “无限对话”统一写成“长程连续对话”，以 20-50 轮、滚动摘要、刷新恢复和失败降级验收；
- P7 只做产品化 Beta 基础，不混入 SaaS、多租户、Billing、ASR、会议平台或自动投递；
- P5-REAL/P5-Freeze 只在 P7 完成后复验，且必须用户提供真实/脱敏资料路径；
- 每个子阶段先完成开发计划、验收标准和启动审计，再进入实质开发。

## 0. P5 历史追踪矩阵与 P7-post 复验依据

| P5 目标 | 实现区域 | 主要文件 / 模块 | 证据 | 验收门槛 |
| --- | --- | --- | --- | --- |
| P0-P4 不退化 | 全路径回归 | `services/`, `apps/chatbox/`, `tests/` | `.venv/bin/python -m pytest`, frontend build | P5 门槛 0 |
| 真实资料本地导入 | Upload / Composer / Workspace files | `apps/chatbox/src/main.tsx`, `services/api/main.py`, workspace storage | 上传/粘贴截图、导入 eval、隐私提示 | P5 门槛 1 |
| 资料解析摘要 | Profile / Project tools | `services/tools/`, artifact service | 资料摘要、source refs、待确认项截图 | P5 门槛 1 / 3 |
| JD 导入与解析 | Job tools / Chat route | JD parsing tools、ChatCore、message UI | JD 解析截图、缺失信息恢复测试 | P5 门槛 2 |
| 事实确认闭环 | Confirmation model / Artifact cards | artifact/version services、Workbench UI | blocking/warning/optional 状态、确认操作截图 | P5 门槛 3 |
| 申请包生成 | Application tools / Workflow | application package tools、P5 workflow | 申请包草稿、匹配说明、面试准备截图 | P5 门槛 4 |
| 编辑与再生成 | Artifact versioning | artifact routes、version UI | edit/regenerate/version 测试和截图 | P5 门槛 4 |
| 导出 preflight | Export service | export routes/service | Markdown/DOCX 文件、preflight 记录 | P5 门槛 4 |
| 本地多轮追问 | Chat Intent Router / Context Snapshot | `services/chat/core.py`, chat session storage, message UI | 普通追问不写 artifact、状态查询截图 | P5 门槛 5 |
| provider 和隐私边界 | Provider Policy Gate / Logs | provider runtime、tool invocation logs | 无外呼审计、脱敏日志、provider 状态截图 | P5 门槛 6 |
| 多视口体验 | Responsive UI | `apps/chatbox/src/styles.css`, screenshot scripts | 1200/1440/1600/1920/720/390 截图 | P5 门槛 7 |
| 文档和 drawio 同步 | Active Docs / Drawio | `docs/active/`, drawio | XML parse、文本镜像、README/TODO sync | P5 门槛 7 |

## 0.1 P5 防止过度计划的边界

以下内容不能作为 P5 出门条件：

- 默认真实外部 provider；
- provider-backed 自由智能聊天默认路径；
- SaaS 登录、多租户、Billing；
- ASR / Whisper、系统音频、会议平台；
- 自动投递、岗位数据源聚合、Offer 分析；
- MCP Server 或 CLI 产品入口；
- 未授权真实个人资料自动验收；
- workspace 删除、不可逆迁移或外部同步。

## 0.2 P5 防止规格不足的边界

缺少以下任一项，不能认为 P5 完成：

- 用户能导入或粘贴资料，并理解本地处理边界；
- 用户能导入或粘贴 JD，并看到可读解析和缺失信息；
- `questions_to_confirm` 能影响生成和导出；
- 申请包支持编辑、版本、重新生成和导出 preflight；
- 普通多轮追问不误触发工具写入；
- P5 报告脱敏，且不把 examples 写成真实个人资料验收；
- P0-P4 回归、前端 build、drawio parse 和 PRD 规格检视均通过；
- README/TODO/active docs/drawio 口径一致。

## 0.3 P5 自动化开发任务映射

| 开发任务 | 代码边界 | 建议测试 | 截图 / 报告证据 |
| --- | --- | --- | --- |
| P5-M1 资料导入 | Chatbox upload/paste UI、`/api/files/upload`、`/api/files/ingest-local`、`extract_facts` | `test_p5_real_data_local_flow_eval.py` | 资料入口、解析中、解析摘要、失败恢复 |
| P5-M2 JD 解析 | ChatCore JD intent、`/api/job/parse-jd`、`/api/job/match-profile` | `test_p5_jd_gap_recovery_eval.py` | JD 解析、缺资料、缺 JD、可生成申请包状态 |
| P5-M3 事实确认 | Artifact cards、confirmation model、`/api/artifacts/{id}/confirm` | `test_p5_confirmation_gate_eval.py` | blocking/warning/optional、补充事实、确认后状态 |
| P5-M4 申请包闭环 | `create_application_package`、artifact update/version/regenerate、export service | `test_p5_application_package_loop_eval.py`, `test_p5_export_preflight_eval.py` | 草稿、编辑、再生成、版本、导出 preflight、导出完成 |
| P5-FC 本地多轮追问 | `services/chat/core.py`、chat session storage、Context Snapshot | `test_p5_local_dialogue_eval.py` | 两轮普通追问不写 artifact、明确工具意图执行 |
| P5 隐私边界 | Provider Policy Gate、tool logs、report generator | `test_p5_privacy_redaction_eval.py` | 报告未出现 API Key、完整真实资料、provider raw response |
| P5 自动化报告 | browser evidence script、HTML report | `test_p5_acceptance_report_eval.py` | 中文报告、真实界面截图、未验证范围、虚假验收风险 |
| P5 drawio/docs | active docs、drawio、文本镜像 | XML parse + `rg` 口径检查 | drawio 6 页、颜色语义、P5/P6/P7/P8 边界一致 |

## 0.3.1 P5 自动化候选实现状态

| P5 项 | 当前证据 | 结论 | 冻结前剩余事项 |
| --- | --- | --- | --- |
| P5-M1 资料导入 | `test_p5_local_data_closure_eval.py`、P5 HTML 初始/导入后截图 | 脱敏 fixture 本地路径通过 | 用户提供真实脱敏资料路径后复核 |
| P5-M2 JD 解析 | P5 HTML `p5_jd_match_desktop.png`、JD/match eval | 本地/mock 路径通过 | 真实授权 JD 局部片段复核 |
| P5-M3 确认闭环 | blocking export eval、artifact/version confirmed eval | 自动化通过 | 人工确认文案是否可理解 |
| P5-M4 申请包/导出 | 编辑后重新阻塞、确认后 Markdown/DOCX 导出 eval | 自动化通过 | 人工复核编辑/再生成/版本 UI |
| P5-FC 多轮追问 | 普通追问不写 artifact、目标 JD 申请包路由 eval | 自动化通过 | 人工复核连续对话体验 |
| P5-M5 报告 | `docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html`、1200/1440/1600/1920/720/390 截图 | 自动化候选通过 | 真实资料脱敏复核 |
| P5-REAL | 待用户提供明确本地脱敏真实资料路径和允许展示字段 | 未执行 | 只读用户指定路径，完成真实资料/JD 局部片段复核 |
| P5-Freeze | `88 passed, 1 warning`、frontend build passed、drawio parse passed、三身份合成资料 Chrome/CDP 可视化验收通过，可作为候选证据 | 冻结延期到 P7-post | 真实资料路径、人工体验清单、final closure audit 需 P7 后复验 |

## 0.4 P5 文档支撑与冻结前审计结论

当前文档在补齐接口契约、数据脱敏、自动化验收矩阵、路线选择和打回规则后，已经支撑 P5 自动化候选开发。当前需要继续支撑的是 P5-REAL 和 P5-Freeze：真实授权资料复核、人工体验审查、最终回归和 final closure audit。默认路线仍为“复用现有本地工具链并逐步加固”，不默认引入真实外部 provider 或大规模重构。

仍需冻结前用证据关闭的风险：

- 当前本地/mock 生成质量不等于真实 provider 质量；
- 真实资料样式不可控，自动化只能覆盖 examples 或脱敏 fixture，用户授权资料必须单独复核；
- ChatCore 意图识别仍是启发式，普通追问不误写 artifact 已自动化覆盖，但仍需人工体验复核；
- 事实确认和导出 preflight 已形成自动化硬约束，但真实资料导出仍需脱敏复核；
- UI 多状态已可通过自动化候选路径，编辑/再生成/版本 UI 仍需人工体验判断是否可理解。

以下 P4 内容作为已冻结基线和历史背景保留。

## 1. 历史 P4 UX 体验强化追踪矩阵

| P4 目标 | 实现区域 | 主要文件 / 模块 | 证据 | 验收门槛 |
| --- | --- | --- | --- | --- |
| P0/P1/P2/P3 不退化 | 全路径回归 | `services/`, `apps/chatbox/`, `tests/` | `python3 -m pytest`, frontend build | P4 门槛 0 |
| Chatbox 空状态任务入口清楚 | Conversation Empty State / Suggested Prompts | `apps/chatbox/src/main.tsx`, `apps/chatbox/src/styles.css` | 初始页 before/after、点击 prompt 后 composer 或对话截图 | P4 门槛 1 |
| 对话反馈可理解 | Conversation Plane / Chat API | ChatCore、chat routes、message UI | 有效/缺资料/错误态、loading 状态截图 | P4 门槛 2 |
| 自由连续多轮对话 | Chat Intent Router / Free Local Dialogue / Context Snapshot | `services/chat/core.py`, chat session storage, message UI | 自由追问两轮不触发工具的 eval、状态/下一步回复截图、会话恢复证据 | P4 门槛 2 / P4C-FC |
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
- 普通自由追问、状态查询、下一步问题不会误触发工具写入；
- 明确工具意图仍能稳定触发对应 Domain Tools；
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
