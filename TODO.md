# JobPilot AI TODO

## P0

- [x] 创建 FastAPI 服务骨架。
- [x] 创建 SQLite 本地 workspace schema。
- [x] 实现 MVP 闭环所需的核心 Agent Tool 函数。
- [x] 增加极简 React Chatbox。
- [x] 增加示例简历、项目 README、JD 和 transcript。
- [x] 增加端到端 demo flow 测试。
- [x] 增加 active 阶段 PRD、目标架构、里程碑、验收门槛和 drawio gap 文档。
- [x] 将 active 阶段文档中文化，并补充目标架构深度设计。
- [x] 增加 P0 强化实现规格和追踪矩阵。
- [x] 增加剩余开发及验收计划，明确工作包、证据和最终验收路径。
- [x] 增加 P0 prompt/output schema、统一 artifact/PDF/realtime/eval 口径。
- [x] 增加结构化 LLM Provider 边界、P0 输出 schema 和 schema validation。
- [x] 增加 artifact、chat session 和 tool invocation 持久化。
- [x] 增加 Chatbox 产物卡确认 UI。
- [x] 在 Chatbox 中增加 Markdown 导出下载按钮。
- [x] 增加 JD 解析、事实安全、实时提示边界、完整 demo flow 和 workspace 隐私 eval gates。
- [x] 完成真实感示例数据 HTTP 端到端验收。
- [x] 完成 M5 P0 Maintenance 加固：artifact/session 恢复、tool log 脱敏、schema/docs 防漂移 eval。
- [x] 完成 P0 收口复验和下一阶段门禁定义。
- [x] 完成 M7/M8 P0 Maintenance：realtime end workspace 定位、导出下载边界、确认状态即时 UX、Chatbox 最新会话与产物卡恢复。
- [x] 完成 M9 PiAgent ChatCore 接入边界：抽出默认 KeywordChatCore，新增 PiAgent adapter、切换环境变量、严格模式和 eval。

## 当前阶段状态

P0 已冻结并完成 M5、M7、M8、M9/M13 维护和 PiAgent 编排接入。P1 已完成本地工程闭环和可见验收。P2 已完成 examples-guided Chatbox 端到端体验，并补充 MiniMax opt-in 真实 provider 受控验收。P3 已完成本地自动化验收：真实用户 Chatbox 体验、对话响应闭环、对话区/推进台分离、响应式 UX、截图证据和 HTML 报告已落地；真实个人资料和真实外部调用仍需人工确认。人工审查认可 P3 验收报告的大部分内容，但对当前用户体验不完全认同，当前 P4 阶段优先做 UX 体验强化。P4B 已把全尺寸桌面体验列为 hard gate：1200px、1440px、1600px、1920px 不能出现布局错误造成的大面积空白，截图脚本也不能污染人工审查浏览器 viewport。

P4B 自动化开发闭环已完成：Chatbox suggested prompts、loading/error recovery、产物卡可读性、provider 隐私语义、全尺寸桌面三栏工作台、移动端推进台抽屉、截图脚本隔离、P4/P4B HTML 报告和 PRD 规格检视均已落地。P4C-FC 本地/mock 连续对话开发闭环已完成：自由聊两轮、状态查询、显式工具触发、会话恢复、390px 移动端按钮可达性、Chrome/CDP 截图报告、pytest 和前端 build 均已通过。P4 final closure 自动化审计已完成，当前证据为 71 passed、前端 build 通过、drawio 解析通过和最终 HTML 截图报告。2026-06-25 人工体验审查认可 P4B/P4C 本地 Chatbox 体验，P4 冻结复验通过：`.venv/bin/python -m pytest` 71 passed、`npm --prefix apps/chatbox run build` 通过、drawio XML parse 通过。当前主线处于 P5 真实资料本地闭环自动化验收候选阶段：本地/mock + 脱敏 fixture 路径已通过 P5 自动化报告、多视口截图和回归测试，最新全量回归为 `88 passed, 1 warning`；真实个人资料路径、真实外部 provider 默认路径、P5 人工体验记录和 P5 final closure audit 仍未验收。

## 当前剩余风险

- [x] OpenAI-compatible provider 已有 P1 opt-in 运行路径、timeout、retry、redaction、provider_invocation 和 schema validation 基础；MiniMax 已在用户授权后使用 examples 完成受控真实 provider E2E。
- [x] Artifact 编辑已支持 metadata/content_json 更新、artifact version、regenerate 和旧版本保留；复杂版本 diff 不属于 P2 hard gate。
- [x] DOCX 已作为 P1 正式可用导出；PDF 样式优化不属于 P2 hard gate。
- [x] PiAgent 已接管基础业务编排；provider/edit/export 仍通过 Python Domain Tools 执行。
- [x] P2 已把 P1 能力组织成用户可点击、可截图验收的完整 Chatbox 工作流。

## P1

- [x] P1-M0：完成 P1 PRD、目标架构、里程碑、验收门槛、开发计划、详细实现规格和 drawio gap 文档同步。
- [x] P1-M1：实现 Provider Runtime，保留 mock 默认基线，新增 OpenAI-compatible opt-in。
- [x] P1-M2：核心工具接入 provider-backed 生成，优先 JD 分析和申请包。
- [x] P1-M3：实现 artifact_version、current version、编辑保存新版本。
- [x] P1-M4：实现 regenerate 新版本闭环，不覆盖旧版本。
- [x] P1-M5：强化 Export Service，Markdown 继续稳定，PDF 或 DOCX 至少一种正式可用。
- [x] P1-M6：补齐 Chatbox P1 UX：provider mode、版本显示、编辑、regenerate、当前版本导出。
- [x] P1-M7：更新 README、TODO、active docs、drawio、release checklist，并完成 P1 本地自动化冻结验收。

P1 冻结说明：

- [x] `python3 -m pytest` 通过，45 passed。
- [x] `npm --prefix apps/chatbox run build` 通过。
- [x] drawio XML 解析通过，5 页。
- [x] active Markdown 文档数 19，仍小于 20。
- [x] P1 使用 examples 匿名真实感数据完成本地验收。
- [x] MiniMax 真实外部 OpenAI-compatible provider 调用已在用户授权后用 examples 完成受控验收；真实个人资料仍未自动验收。

执行编号映射：

- P1-M1 = WP1 Provider Runtime。
- P1-M2 = WP2 核心工具 provider-backed。
- P1-M3 = WP3 Artifact Versioning + WP4 Regenerate。
- P1-M4 = WP5 Export Service + WP6 Chatbox P1 UX。
- P1-M5/P1-M7 收口 = WP7 Release Readiness + full regression。

## P2 已完成计划

- [x] P2-M0：完成端到端用户体验阶段计划、验收门槛和启动审计。
- [x] P2-M1：新增 Workflow Orchestrator API，一键使用 examples 跑完整求职体验路径。
- [x] P2-M2：Chatbox 增加 Guided Flow 面板、步骤状态、下一步动作和一键体验按钮。
- [x] P2-M3：关键产物增加人类可读摘要，降低纯 JSON 暴露。
- [x] P2-M4：补充 Chrome 多截图证据和 P2 HTML 验收报告。
- [x] P2-M5：全量 pytest、前端 build、PRD 规格检视和 P2 冻结审计。
- [x] P2-M6：MiniMax opt-in provider 受控验收，覆盖 examples 事实抽取、JD 解析、匹配报告、申请包和 Markdown/DOCX 导出。

## P3 当前计划

- [x] P3-M0：制定 P3 PRD 增补、目标架构、里程碑、验收门槛、开发计划和 drawio gap 文档。
- [x] P3-M1：完成 Chatbox 对话响应闭环，覆盖有效输入、无效输入、缺资料和后端错误。
- [x] P3-M2：完成示例模式 / 真实资料模式边界和 provider 状态表达。
- [x] P3-M3：重构对话区与推进台分离，强化产物、确认项、版本和导出管理。
- [x] P3-M4：修复响应式 UX，完成 1280px、720px、390px Chrome 截图验收。
- [x] P3-M5：制作 P3 HTML 验收报告，包含截图证据、目标架构、当前实现、体验路径、测试结果和 PRD 规格检视。
- [x] P3-M6：完成 pytest、frontend build、P0/P1/P2 回归、README/TODO/active docs/drawio 同步和 P3 冻结审计。

## P4 当前计划

- [x] P4-UX0：基于当前 P3 截图和人工反馈制定 UX 问题清单、验收标准和 before/after 截图计划。
- [x] P4-M0：同步 P4 PRD、目标架构、里程碑、验收门槛、自动化范围、追踪矩阵、drawio 和 Gemini 前端审查包。
- [x] P4-UX1：优化信息架构和首屏层级，降低 Chatbox / 推进台认知负担；自动化实现和人工体验认可已完成。
- [x] P4-UX2：优化任务入口和下一步引导，让上传资料、粘贴 JD、生成申请包形成自然流程；自动化实现和人工体验认可已完成。
- [x] P4-UX3：优化产物卡可读性，减少 JSON 暴露，突出摘要、确认项、版本和导出；自动化实现和人工体验认可已完成。
- [x] P4-UX4：强化处理中、失败、缺资料和恢复路径的状态反馈；自动化实现和人工体验认可已完成。
- [x] P4-UX5：做响应式精修，让 390px / 720px / 1280px 不只是可用，而是顺手；自动化截图和人工体验认可已完成。
- [x] P4-UX5A：修复全尺寸桌面工作台体验，覆盖 1200px / 1440px / 1600px / 1920px，消除布局错误造成的大面积空白；自动化截图和人工体验认可已完成。
- [x] P4-UX5B：修复截图脚本 viewport emulation 清理，避免自动截图污染人工审查浏览器。
- [x] P4-UX6：制作 UX before/after HTML 审查包，并把全尺寸桌面、窄屏、移动端人工体验意见作为出门条件；报告已完成，人工体验意见待填写。
- [x] P4-UX7：收集 Gemini 前端审查意见，评估是否存在重大 UX 偏差或过度承诺。

## 当前下一步

- [x] P4B-Roadmap：将 P4B 之后的 P4C 人工体验微调、P5 真实资料闭环、P6 外部 provider 受控接入、P7 产品化 Beta 和 P8+ SaaS/高风险能力路线落盘到 `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`。
- [x] P4C-FC-Plan：将自由 Chatbox、无中断连续多轮对话、本地连续对话基线和 provider-backed 后续目标落盘到 `docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`。
- [x] P4B-H1：使用 `docs/active/stage-reviews/P4B_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md` 完成人工体验审查记录。
- [x] P4B-H2：人工评分 26/26，决定进入 P4 冻结复验。
- [x] P4B-H3：已完成 P4C-FC 本地连续对话和本轮 UI 体验微调；未新增阻塞项，真实资料和 provider-backed 能力转入 P5/P6。
- [x] P4C-FC：按 `18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md` 完成本地/mock 连续多轮对话验收；报告为 `docs/reports/P4C_FC_CONTINUOUS_DIALOGUE_ACCEPTANCE_REPORT.html`，不得默认外呼真实 provider，不代表人工体验已通过。
- [x] P4-Final-Audit：重新基于原始 PRD 和 P4 gates 完成代码检视、文档审计、功能检查和全量端到端自动化验收；报告为 `docs/reports/P4_FINAL_CLOSURE_AUTOMATED_ACCEPTANCE_REPORT.html`，审计为 `docs/active/stage-reviews/P4_FINAL_CLOSURE_AUDIT.md`。
- [ ] P4C-EP：如需真实外部 provider + 脱敏个人资料验收，必须先按 `docs/active/stage-reviews/P4C_EXTERNAL_PROVIDER_DESENSITIZED_ACCEPTANCE_PLAN.md` 确认数据路径、允许字段、provider、调用次数和报告脱敏范围；该路径默认转入 P6 opt-in，不属于 P5 默认验收。
- [x] P4-Freeze：人工认可 P4B 后已补齐冻结记录，并再次运行 `.venv/bin/python -m pytest`、`npm --prefix apps/chatbox run build` 和 drawio XML parse，均通过。

## P5 当前计划

文档开发阶段：

- [x] P5-M0-DOC：制定 P5 PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、drawio 文本镜像、drawio gap 图和 P5-M0 文档就绪审计。

自动化候选实现阶段：

- [x] P5-M1：真实资料本地导入与解析 UX 已用脱敏 fixture 验证，覆盖 ingest-local、解析摘要、source refs、待确认项和本地隐私边界；真实个人资料路径仍待用户提供后人工/脱敏验收。
- [x] P5-M2：JD 导入、解析和缺失信息恢复已用真实界面截图和 eval 覆盖，包含岗位要求、匹配报告和申请包可生成状态。
- [x] P5-M3：事实确认与 `questions_to_confirm` 闭环已实现 blocking/warning/optional、artifact confirm、当前 version confirmed 和导出硬门槛。
- [x] P5-M4：申请包生成、编辑后重新阻塞、确认后 Markdown/DOCX 导出 preflight 已通过自动化 eval；重新生成/版本 UI 仍需在人工体验中复核。
- [x] P5-FC：围绕当前资料/JD/申请包的本地多轮追问已覆盖普通追问不写 artifact、目标 JD 申请包路由不误判。
- [x] P5-M5：P5 脱敏自动化验收报告已生成：`docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html`，含真实界面截图、PRD 规格检视和未验证范围。
- [ ] P5-REAL：等待用户提供明确本地脱敏真实资料路径和允许展示字段；不得擅自搜索个人资料目录，不得声称真实个人资料路径已通过。
- [ ] P5-Freeze：完成真实授权资料审查、P5 人工体验记录、最终 pytest/frontend build/drawio parse 和阶段冻结审计。

文档收口状态：

- [x] P5-DOC-SYNC：PRD、目标架构、里程碑、验收门槛、追踪矩阵、README/TODO 和 drawio 口径已调整为“自动化候选通过，P5-REAL/P5-Freeze 待完成”。
- [x] P5-FREEZE-AUDIT-PLAN：新增 `docs/active/stage-reviews/P5_FREEZE_EXIT_AUDIT_PLAN.md`，明确 P5 final closure audit 的 PRD 路径复验、工程证据、文档一致性和打回条件。
- [x] P5-SYNTHETIC-REVIEW：新增 `docs/reports/P5_SYNTHETIC_PROFILE_REVIEW.html`，作为真实资料验收前的合成简历、背景资料、目标 JD 和允许展示字段审核页。
- [x] P5-EXTERNAL-REVISION：新增 `docs/active/stage-reviews/P5_EXTERNAL_REVIEW_REVISION_AUDIT.md`，记录外部意见采纳、剩余开发验收大纲、风险和 ChatGPT 审计包。
- [x] P5-DOC-REAUDIT：新增 `docs/active/stage-reviews/P5_DOCUMENTATION_COVERAGE_REAUDIT.md`，复审当前 PRD、目标架构、验收门槛和 drawio 是否支撑 P5-REAL/P5-Freeze。
- [x] P5-REAL-PLAN：新增 `docs/active/stage-reviews/P5_REAL_DATA_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` 和 `scripts/generate_p5_real_data_acceptance.py`，真实资料执行前必须通过路径授权、文本抽取质量和脱敏摘要边界检查。
- [x] P5-SYNTHETIC-REALISM：新增 `examples/p5_synthetic_personas/`、`scripts/generate_p5_synthetic_realism_acceptance.py` 和 `docs/active/stage-reviews/P5_SYNTHETIC_REALISM_ACCEPTANCE_AUDIT.md`，用多身份合成资料加强自动化验收真实性；不能替代 P5-REAL，不能声称真实个人资料路径已通过。
- [x] P5-STAGE-VISUAL-AUDIT：重新基于 PRD 执行代码检视、文档审计、功能检查、全量回归和三身份合成资料 Chrome/CDP 可视化验收；报告为 `docs/reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html`，审计为 `docs/active/stage-reviews/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_AUDIT.md`，不替代 P5-REAL 或 P5-Freeze。
- [ ] P5-FINAL-AUDIT：真实资料授权验收完成后，更新 P5 final closure audit，不得用当前自动化候选报告替代最终冻结结论。
- [ ] P5.5-Candidate：P5 冻结后单独规划职业画像与能力评估，包含 CandidateProfile、能力矩阵、项目可信度、岗位短板和 source refs 画像面板；不得写成 P5 已完成。

## P6+ 候选

- [ ] P6-M0：真实外部 provider opt-in、provider-backed 自由智能聊天、API Key 边界、日志脱敏和失败降级验收规划。
- [ ] MCP Server wrapper。
- [ ] CLI 命令。
- [ ] 本地 Whisper / ASR adapter。
- [ ] 会议平台接入。
- [ ] 更完整岗位数据源、Offer 分析和申请跟踪。
