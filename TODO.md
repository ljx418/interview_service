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

P0 已冻结并完成 M5、M7、M8、M9/M13 维护和 PiAgent 编排接入。P1 已完成本地工程闭环和可见验收。P2 已完成 examples-guided Chatbox 端到端体验，并补充 MiniMax opt-in 真实 provider 受控验收。当前进入 P3：真实用户 Chatbox 体验、对话响应闭环、对话区/推进台分离、响应式 UX 和截图验收。

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
- [ ] P3-M1：完成 Chatbox 对话响应闭环，覆盖有效输入、无效输入、缺资料和后端错误。
- [ ] P3-M2：完成示例模式 / 真实资料模式边界和 provider 状态表达。
- [ ] P3-M3：重构对话区与推进台分离，强化产物、确认项、版本和导出管理。
- [ ] P3-M4：修复响应式 UX，完成 1280px、720px、390px Chrome 截图验收。
- [ ] P3-M5：制作 P3 HTML 验收报告，包含截图证据、目标架构、当前实现、体验路径、测试结果和 PRD 规格检视。
- [ ] P3-M6：完成 pytest、frontend build、P0/P1/P2 回归、README/TODO/active docs/drawio 同步和 P3 冻结审计。

## P4+ 候选

- [ ] MCP Server wrapper。
- [ ] CLI 命令。
- [ ] 本地 Whisper / ASR adapter。
- [ ] 会议平台接入。
- [ ] 更完整岗位数据源、Offer 分析和申请跟踪。
