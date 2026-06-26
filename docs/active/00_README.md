# JobPilot AI 当前阶段设计文档

本目录是当前阶段的执行依据。原始文档包 `docs/jobpilot_ai_agent_docs_v1_0/` 保留为产品背景和 v1.0 资料；本目录文档用于指导当前 P5 真实资料本地闭环阶段的开发、验收和方向评审。P4 已作为本地/mock Chatbox 体验冻结基线保留。

## 阅读顺序

1. `01_STAGE_PRD.md`：P5 当前阶段 PRD、目标用户、目标体验路径、非目标和历史阶段基线。
2. `02_TARGET_ARCHITECTURE.md`：P5 目标架构、当前架构差距、代码实体职责和关联关系。
3. `03_MILESTONES_AND_DELIVERY_PLAN.md`：P5 项目里程碑、阶段产物和出门条件。
4. `04_ACCEPTANCE_GATES.md`：P5 功能、体验、安全、隐私和证据验收门槛。
5. `05_IMPLEMENTATION_SPEC.md`：可直接交付工程实现的 P0 强化规格。
6. `06_TRACEABILITY_MATRIX.md`：目标、模块、证据、测试和验收门槛追踪矩阵。
7. `07_REMAINING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`：剩余开发工作包、验收证据和最终验收路径。
8. `08_P0_PROMPT_AND_OUTPUT_SCHEMAS.md`：P0 prompt、输出 schema、source refs、待确认分级和 eval 断言。
9. `09_AUTOMATED_DEVELOPMENT_SCOPE.md`：P4 自动化开发范围、验收边界、高风险确认点和历史阶段边界。
10. `10_P0_FREEZE_AUDIT_AND_ACCEPTANCE_REPORT.md`：P0 冻结审计、验收结果、残留风险和后续开发大纲。
11. `11_P1_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`：P1 开发工作包、验收证据、审计意见和端到端路径。
12. `12_P1_DETAILED_IMPLEMENTATION_SPEC.md`：P1 数据模型、API、provider、versioning、regenerate、export、eval 和打回条件。
13. `13_P2_END_TO_END_EXPERIENCE_PLAN_AND_AUDIT.md`：P2 端到端用户体验开发计划、验收门槛和启动审计意见。
14. `14_P2_REMAINING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`：P2-M4/M5 历史开发、验收、截图、报告和冻结计划。
15. `15_P3_REAL_USER_CHATBOX_EXPERIENCE_PLAN.md`：P3 真实用户 Chatbox 体验、响应式 UX、验收计划和启动审计。
16. `16_P4_UX_EXPERIENCE_HARDENING_PLAN.md`：P4 UX 体验强化开发及验收计划，承接 P3 人工审查反馈。
17. `17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`：P5 当前阶段、P6/P7/P8+ 后续路线图、边界和回到验收主线的动作。
18. `18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`：自由 Chatbox、不中断连续多轮对话、本地连续对话基线和 provider-backed 后续目标的分层计划。
19. `stage-reviews/`：P2/P3 子阶段审计记录，`P4_GEMINI_UX_REVIEW_ACTIONS.md` 外部 UX 审查处理记录，`P4_UX_IMPLEMENTATION_AND_ACCEPTANCE_REVIEW.md` P4 自动化实现评审，`P4B_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md` 人工体验审查清单，`P4B_DOCUMENTATION_COVERAGE_AUDIT.md` 开发文档覆盖度审计，`P5_M0_DOCUMENTATION_READINESS_AUDIT.md` P5-M0 文档就绪审计，`P5_FREEZE_EXIT_AUDIT_PLAN.md` P5 最终冻结审计计划，`P5_EXTERNAL_REVIEW_REVISION_AUDIT.md` 外部意见修订审计，`P5_DOCUMENTATION_COVERAGE_REAUDIT.md` P5 文档覆盖度复审，`P5_REAL_DATA_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` P5-REAL 真实授权资料开发及验收计划，`P5_SYNTHETIC_REALISM_ACCEPTANCE_AUDIT.md` P5 合成真实感资料验收审计，以及 `P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_AUDIT.md` P5 阶段性可视化验收审计；P1 阶段审计已归档到 `docs/archive/stage-reviews/p1/`。
20. `jobpilot-stage-gap-and-acceptance.md`：drawio 图的文本镜像，方便审查和 diff。
21. `jobpilot-stage-gap-and-acceptance.drawio`：P5 目标架构、当前差距、代码实体关系、计划、门槛和验收证据图。
22. `../reports/P5_SYNTHETIC_PROFILE_REVIEW.html`：P5-REAL 前置合成简历、背景资料、目标 JD 和允许展示字段审核页。
23. `../reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html`：P5 三身份合成资料 Chrome/CDP 可视化验收聚合报告，不代表 P5-REAL 通过。
24. `../gemini-frontend-review-package/`：给 Gemini 独立审查的前端页面方案和静态原型。

## 当前阶段目标

在已冻结 P0、已完成 P1 本地工程闭环、已完成 P2 examples-guided 端到端体验、完成 P3 自动化验收，并完成 P4 本地/mock Chatbox 体验冻结之后，P5 聚焦把示例路径推进到真实资料本地闭环：

```text
打开本地 Chatbox
→ 上传或粘贴自己的简历、项目说明、经历材料
→ 粘贴或导入目标 JD
→ 查看资料解析、JD 解析、来源和待确认项
→ 补充事实并确认 blocking/warning/optional 项
→ 生成申请包、编辑、重新生成和导出 Markdown/DOCX
→ 围绕当前资料、JD 和申请包继续多轮追问
→ 通过脱敏截图、HTML 报告、PRD 规格检视和人工体验审查完成验收
```

## 当前实现基线

已经具备：

- React 极简 Chatbox 骨架；
- FastAPI Agent Service；
- SQLite 本地 workspace 和文件路径沙箱；
- 基于启发式规则的完整 demo 工具链；
- 结构化 provider 边界、P0 输出 schema、source refs 和待确认分级；
- chat session、artifact 和 tool invocation 持久化；
- Chatbox 产物卡确认、Markdown 导出入口和最新本地会话恢复；
- 后端 ChatCore 接入层，支持默认 KeywordChatCore 和 PiAgent adapter；
- Pi Agent Core 已可接管基础业务编排，Python Domain Tools 继续执行真实业务写入；
- 示例简历、项目 README、JD 和 transcript；
- demo flow、JD 解析、事实安全、实时提示边界和 workspace 安全 eval gates。

当前状态：

- P0 已冻结并完成 M5、M7、M8、M9/M13 维护和 PiAgent 编排接入；
- P0 收口复验和 P1 启动许可已完成；
- P1 Provider Runtime、核心工具 provider-backed、Artifact Versioning、Regenerate、Export Service 和 Chatbox P1 UX 已完成本地自动化验收；
- P2 examples-guided Chatbox 端到端体验、HTML 报告、截图证据和 MiniMax opt-in 受控验收已完成；
- P3 已完成本地自动化验收：Chatbox 响应闭环、示例/真实资料模式边界、对话区/推进台分离、响应式截图和 HTML 报告已落地；
- P4B 已完成自动化开发闭环：Chatbox suggested prompts、loading/error recovery、产物卡可读性、provider 隐私语义、全尺寸桌面三栏工作台、移动端推进台抽屉、截图脚本隔离、P4/P4B HTML 报告和 PRD 规格检视已落地；
- 真实 API Key 和真实外部 provider 调用仍必须人工确认。
- 2026-06-25 人工体验审查认可当前 P4B/P4C 本地 Chatbox 体验，人工评分记录为 26/26；
- P4 冻结复验已完成：`.venv/bin/python -m pytest` 71 passed、`npm --prefix apps/chatbox run build` 通过、drawio XML parse 通过；
- 真实个人资料、真实外部 provider 默认路径仍未验收；
- “自由 Chatbox / 无中断连续多轮对话”已完成本地/mock 最小连续对话基线，并已在 P5 自动化候选中扩展到当前资料/JD/申请包上下文；完整 provider-backed 自由智能聊天仍需 P6 opt-in 规划和用户确认。

P5 当前阶段问题：

- P5 真实资料闭环已进入自动化验收候选阶段，本地/mock + 脱敏 fixture 路径已有 `docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html` 作为证据；
- P5-REAL 前置资料结构审核页为 `docs/reports/P5_SYNTHETIC_PROFILE_REVIEW.html`，其中人物和经历均为合成示例，不代表真实个人资料验收通过；
- P5-REAL 执行器为 `scripts/generate_p5_real_data_acceptance.py`，执行前必须由用户提供简历、项目资料、目标 JD 三个明确路径，报告默认仅脱敏摘要；
- 用户不提供真实资料时，使用 `examples/p5_synthetic_personas/` 和 `scripts/generate_p5_synthetic_realism_acceptance.py` 做多身份合成资料验收增强；该路径不能替代 P5-REAL；
- P5-M1/M2/M3/M4/P5-FC/P5-M5 已达到自动化候选通过，但 P5 最终冻结前仍必须完成真实授权资料路径确认、脱敏报告复核、人工体验审查、最终回归和 final closure audit；
- 最新 P5 收口证据为 `.venv/bin/python -m pytest` 88 passed, 1 warning、前端 build 通过、drawio XML parse 通过，以及三身份合成资料 Chrome/CDP 可视化验收通过；该证据不代表真实个人资料路径或真实外部 provider 默认路径已通过；
- P6 provider-backed 自由智能聊天和真实外部 provider 路径必须 opt-in，并在用户明确确认后验收；
- P7 产品化 Beta 需要补齐 workspace 生命周期、备份/迁移、监控、隐私审计和发布流程；
- ASR、会议平台、自动投递、SaaS、多租户、Billing 等能力仍属于 P8+ 或独立高风险阶段。

## 范围边界

本阶段不做 MCP Server、CLI、完整 ASR、会议平台集成、自动海投、隐蔽式面试浮窗、面试官敏感属性分析、SaaS 登录、多租户、Billing 或默认真实外部 provider。上述能力只能作为 P6/P7/P8+ 或独立高风险阶段规划，不能进入 P5 出门条件。
