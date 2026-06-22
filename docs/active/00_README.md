# JobPilot AI 当前阶段设计文档

本目录是当前阶段的执行依据。原始文档包 `docs/jobpilot_ai_agent_docs_v1_0/` 保留为产品背景和 v1.0 资料；本目录文档用于指导当前 P4 UX 体验强化阶段的开发、验收和方向评审。

## 阅读顺序

1. `01_STAGE_PRD.md`：P4 当前阶段 PRD、目标用户、目标体验路径、非目标和历史阶段基线。
2. `02_TARGET_ARCHITECTURE.md`：P4 目标 UX 架构、当前架构差距、模块职责和关联关系。
3. `03_MILESTONES_AND_DELIVERY_PLAN.md`：P4 项目里程碑、阶段产物和出门条件。
4. `04_ACCEPTANCE_GATES.md`：P4 UX、功能、安全、隐私、开源可用性的验收门槛。
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
17. `stage-reviews/`：P2/P3 子阶段审计记录，以及 `P4_GEMINI_UX_REVIEW_ACTIONS.md` 外部 UX 审查处理记录；P1 阶段审计已归档到 `docs/archive/stage-reviews/p1/`。
18. `jobpilot-stage-gap-and-acceptance.md`：drawio 图的文本镜像，方便审查和 diff。
19. `jobpilot-stage-gap-and-acceptance.drawio`：P4 UX 目标架构、当前差距、组件职责、计划、门槛和验收证据图。
20. `../gemini-frontend-review-package/`：给 Gemini 独立审查的前端页面方案和静态原型。

## 当前阶段目标

在已冻结 P0、已完成 P1 本地工程闭环、已完成 P2 examples-guided 端到端体验，并完成 P3 自动化验收之后，P4 聚焦把 Chatbox 从“可运行的工程工作台”提升为“人类愿意使用、容易理解、操作顺手的求职材料工作台”：

```text
打开本地 Chatbox
→ 在首屏看到清晰任务入口：导入资料、粘贴 JD、生成申请包、准备面试
→ 选择示例模式或真实资料模式，并理解 provider 是否会外呼
→ 在对话区输入任务并获得可理解反馈、计划、错误或下一步
→ 在分离的推进台查看当前任务、产物、确认项、版本和导出
→ 通过更自然的产物卡完成确认、编辑、regenerate 和导出
→ 在 1200px、1440px、1600px、1920px 桌面、720px 窄屏和 390px 移动宽度下都能顺手完成关键路径
→ 通过 Chrome 截图、HTML 报告和人工体验审查完成验收
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
- 真实 API Key 和真实外部 provider 调用仍必须人工确认。
- 人工审查已认可 P3 验收报告的大部分内容，但未完全认可当前用户体验；P4 作为当前阶段，优先做 UX 体验强化。

P4 需要解决的 P3 后继限制：

- 当前体验仍偏“工程验收控制台”，首屏缺少自然任务入口；
- Chatbox、计划、推进台、产物卡的信息层级仍需要进一步分离；
- 产物卡仍暴露过多工程字段，用户需要更快理解“这份材料能不能用”；
- provider、示例模式、真实资料模式需要更低歧义的隐私和外呼表达；
- 全尺寸桌面不能出现窄屏布局停靠在左侧或由布局错误造成的大面积空白；
- Chrome 截图脚本必须隔离或清理 viewport emulation，不能污染人工审查浏览器；
- 移动端不能只做到“不坏”，必须做到关键任务顺手；
- P4 必须用真实感示例数据和 Chrome 可见截图验收，不得把未人工审查的体验写成已通过。

## 范围边界

本阶段不做 MCP Server、CLI、完整 ASR、会议平台集成、自动海投、隐蔽式面试浮窗、面试官敏感属性分析、SaaS 登录、多租户或 Billing。上述能力只能作为 P5 或更后阶段规划，不能进入 P4 出门条件。
