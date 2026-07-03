# JobPilot AI 当前阶段设计文档

本目录是当前阶段的执行依据。原始文档包 `docs/jobpilot_ai_agent_docs_v1_0/` 保留为产品背景和 v1.0 资料；本目录文档用于记录 P5.5 Candidate Profile 自动化开发候选、P6/P7 自动化候选基线、P6-REAL / P7-post 真实验收准备、P8-JD Intake 与简历生成体验强化自动化候选、P8.1 Chatbox-first 自动化候选，以及当前 P9 Chatbox-native 求职情报与申请包工作台自动化候选。P4 已作为本地/mock Chatbox 体验冻结基线保留；P5/P5.5/P6/P7/P8/P8.1 自动化候选证据保留为后续基线。P9 已完成第一轮本地 UI 信息架构和求职态势可视化自动化候选，不得写成全网 JD 搜索已完成、ASR 已实现、BOSS/招聘平台自动接入、自动投递、真实个人资料路径、真实外部 provider 默认路径或 MCP/Skill 连通性已通过。

## 阅读顺序

1. `01_STAGE_PRD.md`：P9 Chatbox-native 求职情报与申请包工作台 PRD、P8.1/P8 自动化候选结论、目标体验路径、非目标和历史阶段边界。
2. `02_TARGET_ARCHITECTURE.md`：P9 顶部服务中心、左侧求职态势图、中央 Chatbox、右侧产物台目标架构、当前架构、具体代码实体职责和关联关系。
3. `03_MILESTONES_AND_DELIVERY_PLAN.md`：P9 文档阶段和后续开发里程碑、P8.1/P8 历史计划、平台合规边界和出门条件。
4. `04_ACCEPTANCE_GATES.md`：P9 Chatbox-native 求职工作台门槛、P8.1/P8 历史门槛，以及 P5.5/P6/P7 历史自动化候选门槛。
5. `05_IMPLEMENTATION_SPEC.md`：可直接交付工程实现的 P0 强化规格。
6. `06_TRACEABILITY_MATRIX.md`：目标、模块、证据、测试、真实验收待办和验收门槛追踪矩阵。
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
17. `17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`：P8-JD Intake 自动化候选、P5.5 自动化候选、P6/P7 自动化候选、P6-REAL/P7-post 准备阶段和后续路线图边界。
18. `18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`：自由 Chatbox、不中断连续多轮对话、本地连续对话基线和 provider-backed 后续目标的分层计划。
19. `19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md`：P6 fake provider 自动化候选、真实 provider opt-in 待执行验收、长程连续对话、上下文压缩、隐私边界和受控外呼执行单。
20. `20_P5_5_CANDIDATE_PROFILE_PLAN.md`：P5.5 候选人画像、能力矩阵、项目可信度、岗位短板、source refs 和验收计划。
21. `21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`：P8-JD Intake、资料准备向导、JD 手动导入中心、JD 定制简历和招聘平台合规边界。
22. `22_P8_1_CHATBOX_FIRST_WORKSPACE_PLAN.md`：P8.1 Chatbox-first 工作台信息架构修正计划，定义“用户指导 - Chatbox - 工作台”和聊天优先验收门槛。
23. `23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`：P9 Chatbox-native 求职情报与申请包工作台计划，定义顶部服务中心、左侧求职态势图、中央 Chatbox、右侧产物台和后续开发验收边界。
24. `stage-reviews/`：阶段审计记录，包含 P5/P6/P7/P5.5/P8/P8.1/P9 审计；其中 `P9_DOCUMENTATION_DEVELOPMENT_AUDIT.md` 记录 P9 仍是文档阶段、不进入代码实现、不虚假声明高风险能力通过，`P9_DOCUMENTATION_COVERAGE_REAUDIT.md` 复审 P9 是否完整解决用户诉求、是否落盘到 Markdown/drawio、是否足以支撑 P9-M0 到 P9-M9，`P9_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` 定义 P9-M0 到 P9-M9 每阶段开发范围、验收标准、证据和打回条件，`P9_EXTERNAL_REVIEW_REVISION_AUDIT.md` 记录外部审计意见采纳并把 P9 锁定为 Chatbox-first UI/信息结构重构和求职情报可视化层。
25. `jobpilot-stage-gap-and-acceptance.md`：drawio 图的文本镜像，方便审查和 diff。
26. `jobpilot-stage-gap-and-acceptance.drawio`：P9 Chatbox-native 目标体验、当前差距、代码实体分层交互关系、开发验收计划、门槛和安全边界图。
25. `../reports/P5_SYNTHETIC_PROFILE_REVIEW.html`：P5-REAL 前置合成简历、背景资料、目标 JD 和允许展示字段审核页。
26. `../reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html`：P5 三身份合成资料 Chrome/CDP 可视化验收聚合报告，不代表 P5-REAL 通过。
27. `../gemini-frontend-review-package/`：给 Gemini 独立审查的前端页面方案和静态原型。

## 当前阶段目标

在已冻结 P0、已完成 P1 本地工程闭环、已完成 P2 examples-guided 端到端体验、完成 P3 自动化验收，并完成 P4 本地/mock Chatbox 体验冻结之后，P5 本地/mock + 脱敏 fixture 自动化候选已完成，P5.5 Candidate Profile 自动化候选已完成，P6+P7 本地 Beta 自动化候选也已完成。P8-JD Intake 与简历生成体验强化、P8.1 Chatbox-first 自动化候选均已作为基线保留。当前 P9 文档目标是重新定义下一阶段产品体验：以 Chatbox 为中心，顶部展示服务状态，左侧展示可交互求职态势，右侧展示申请包和事实产物。P9 不是继续堆叠向导卡片，而是让用户通过对话完成 JD 搜索/汇总、资料补全、申请包生成、产物调整和投递流程更新。

```text
用户打开 Chatbox-native 工作台
→ 顶部看到 provider / ASR / MCP / Skill / 外部搜索 / 安全边界状态
→ 左侧通过地图、图钉、流程图或等价可视化理解岗位市场、目标机会和投递流程
→ 中央 Chatbox 发起 JD 搜索、薪资城市汇总、资料补全、申请包生成和流程更新
→ 右侧产物台展示候选人画像、事实摘要、简历、面试故事、申请包、source refs 和待确认项
→ 缺证据内容进入 pending confirmations，不写成事实；高风险能力必须单独授权
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

当前阶段问题：

- P5 真实资料闭环已完成自动化验收候选，本地/mock + 脱敏 fixture 路径已有 `docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html` 作为证据；
- P5-REAL 前置资料结构审核页为 `docs/reports/P5_SYNTHETIC_PROFILE_REVIEW.html`，其中人物和经历均为合成示例，不代表真实个人资料验收通过；
- P5-REAL 执行器为 `scripts/generate_p5_real_data_acceptance.py`，执行前必须由用户提供简历、项目资料、目标 JD 三个明确路径，报告默认仅脱敏摘要；
- 用户不提供真实资料时，使用 `examples/p5_synthetic_personas/` 和 `scripts/generate_p5_synthetic_realism_acceptance.py` 做多身份合成资料验收增强；该路径不能替代 P5-REAL；
- P5-M1/M2/M3/M4/P5-FC/P5-M5 已达到自动化候选通过，但 P5-REAL/P5-Freeze 已冻结延期到 P7 后复验；当前不得补写 P5 已通过结论；
- 最新 P5 收口证据为 `.venv/bin/python -m pytest` 88 passed, 1 warning、前端 build 通过、drawio XML parse 通过，以及三身份合成资料 Chrome/CDP 可视化验收通过；该证据不代表真实个人资料路径或真实外部 provider 默认路径已通过；
- P6 provider-backed 自由智能聊天已完成 fake provider 自动化候选，覆盖 opt-in、20 轮连续对话、失败 fallback、tool safety、脱敏日志，以及多身份合成资料多轮对话证据；这些证据不代表真实 provider 质量通过，真实外部 provider 路径仍必须用户明确确认后单独验收；
- P7 本地产品化 Beta 自动化候选已补齐 workspace 生命周期入口、备份清单、清理/迁移 dry-run、诊断报告、隐私审计和中文 HTML 报告；workspace 删除、迁移 apply 和 SaaS GA 仍未实现；
- P5.5 Candidate Profile 自动化候选已补齐 profile 读取/刷新 API、画像聚合、能力矩阵、项目可信度、岗位短板、Workbench 面板、中文 HTML 报告和多视口截图证据；
- P8-JD Intake 自动化候选已补齐资料准备向导、JD 手动导入中心、多 JD 目标岗位、JD 定制简历、专项 eval、headless Chrome 截图和中文 HTML 报告；
- ASR、会议平台、自动投递、SaaS、多租户、Billing、真实 provider 质量复验、真实个人资料复验和招聘平台合规接入仍属于 P8+ 或独立高风险阶段。

## 范围边界

P8 自动化候选只覆盖本地/mock + examples / 受控真实感数据，不做 MCP Server、CLI、完整 ASR、会议平台集成、自动海投、隐蔽式面试浮窗、面试官敏感属性分析、SaaS 登录、多租户、Billing 或默认真实外部 provider。BOSS 或其他招聘平台第一版只支持用户手动粘贴 JD 和保存来源链接，不登录、不绕过风控、不自动抓取、不自动沟通或自动投递。真实 provider 只允许在 P6 opt-in、用户明确确认、API Key 本地配置、日志脱敏、预算/次数边界和失败降级均满足时验收；真实资料只允许读取用户明确提供的路径。
