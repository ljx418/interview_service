# JobPilot AI

JobPilot AI 是一个面向转行程序员的本地优先、免费开源 AI 求职 Agent 服务。默认入口是极简 Chatbox，但真正的核心是后端 Agent Tool Service：同一套能力后续可以被 Chatbox、HTTP API、CLI、MCP Client 或外部 Agent 调用。

## 当前 MVP / P8-JD Intake 自动化候选阶段

当前骨架已经具备：

- 本地 workspace 初始化；
- 覆盖 PRD 主要实体的 SQLite schema；
- chat session、artifact 和 tool invocation 持久化；
- P0 输出 schema、source refs 和待确认分级；
- 从本地文件或上传文件导入简历/项目资料；
- CareerFact 与 SkillEvidence 抽取；
- TechProject 项目卡生成；
- JD 解析和岗位匹配报告；
- Markdown-first 申请包导出和下载 API；
- 面试准备、故事卡和模拟面试反馈；
- 文本模式实时问题识别和 formal_assist 安全结构提示；
- 面试复盘和训练任务；
- 极简 React Chatbox 产物卡、确认按钮、Markdown 导出入口和最新本地会话恢复；
- 后端 ChatCore 接入层，支持默认 `KeywordChatCore` 和 PiAgent adapter；
- Pi Agent Core 可接管基础业务编排，Python Domain Tools 继续执行真实业务写入。

P0 已冻结。P1 已完成本地可验收实现：OpenAI-compatible provider opt-in 基础、核心工具 provider-backed contract 路径、artifact 编辑/版本/regenerate、DOCX 正式导出和 Chatbox P1 UX。P2 已完成 examples-guided Chatbox 端到端体验、HTML 验收报告和 MiniMax opt-in provider 受控验收。

P3 已完成本地自动化验收：Chatbox 已从“可演示的一键体验”推进到“真实用户可理解、可对话、可管理产物、可在窄屏使用”的求职工作台。默认验收仍使用 mock provider 和 examples 真实感数据；真实个人资料和真实外部调用仍需人工确认。

人工审查已认可 P3 验收报告的大部分内容，但对当前用户体验不完全认同。当前 P4 阶段优先做 UX 体验强化，包括信息架构、任务入口、产物卡可读性、状态反馈、响应式细节、Gemini 前端审查包和人工体验审查包。P4B 已把全尺寸桌面体验纳入 hard gate：1200px、1440px、1600px、1920px 下页面必须像完整求职材料工作台，不能出现由布局错误造成的大面积空白或窄屏布局停靠在左侧。

P4B 自动化开发闭环已完成：全尺寸桌面三栏工作台、720px/390px 响应式证据、截图脚本 viewport emulation 清理、P4/P4B HTML 报告、PRD 规格检视、pytest 和前端 build 均已通过。P4C-FC 本地/mock 连续对话闭环也已完成：自由聊两轮、状态查询、显式工具触发、会话恢复、390px 移动端按钮可达性、Chrome/CDP 截图报告、pytest 和前端 build 均已通过。P4 final closure 自动化审计已重新基于原始 PRD 和 P4 gates 执行，当前证据为 71 passed、前端 build 通过、drawio 解析通过和最终 Chrome/CDP 截图报告。2026-06-25 人工体验审查认可当前 P4B/P4C 本地 Chatbox 体验，P4 冻结复验通过：`.venv/bin/python -m pytest` 71 passed、`npm --prefix apps/chatbox run build` 通过、drawio XML parse 通过。不能声称真实个人资料或真实外部 provider 默认路径已通过。

自由 Chatbox 与无中断连续多轮对话已落盘到 `docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`，本地/mock 连续对话验收报告为 `docs/reports/P4C_FC_CONTINUOUS_DIALOGUE_ACCEPTANCE_REPORT.html`。当前只证明本地/mock 连续对话基线；完整 provider-backed 自由智能聊天必须进入 P6 opt-in，并在用户明确确认真实外部调用后验收。

当前 P5 已按用户决策进入“冻结延期复验”状态：P5 本地/mock + 脱敏 fixture 自动化候选、三身份合成资料可视化验收和 P4 冻结体验均已作为后续基线保留；P5-REAL 和 P5-Freeze 不再作为当前阶段继续推进，也不得写成真实个人资料路径或真实外部 provider 默认路径已通过。P5-REAL/P5-Freeze 将在 P7 完成后作为 P7-post 复验项目重新执行。

P6+P7 一体规划和自动化候选已完成并作为当前后续基线保留：P6 负责真实 provider opt-in、长程连续对话、Provider Policy Gate、Long Context Manager、Provider Invocation Log、隐私脱敏和失败降级；P7 负责产品化 Beta，包括 workspace 生命周期、备份/迁移、诊断报告、发布/部署/回滚、安全隐私审计和 Beta 使用支持流程。任何真实 API Key、真实个人资料、真实外部 provider 调用、workspace 删除、不可逆迁移、ASR/会议平台/自动投递/SaaS 操作仍必须先暂停并获得用户确认。

2026-06-29 P6+P7 自动化候选实现已完成：provider-backed free chat 当前通过 fake provider 验收，覆盖 opt-in consent、20 轮长程连续对话、失败 fallback、tool safety 和脱敏 provider chat log；Chatbox 已展示 Long context 与 Workspace ops；P7 backup manifest、cleanup dry-run、migration dry-run 和 diagnostics metadata-only 已有 UI、API、测试和中文 HTML 报告证据。该结论不代表真实 MiniMax/DeepSeek/OpenAI-compatible provider 质量通过，不代表真实个人资料路径通过，也不代表 SaaS GA、workspace 删除或迁移 apply 通过。

当前 P5.5 Candidate Profile 自动化开发候选已完成：在 P5 本地资料闭环、P6/P7 自动化候选基线上，新增候选人画像聚合、能力矩阵、项目可信度、岗位短板、source refs 画像面板、显式“生成画像”入口、P5.5 eval 和中文 HTML 自动化验收报告。该结论只证明 examples / synthetic-style workspace + mock provider 路径，不分析敏感属性、不默认调用真实 provider、不读取未授权真实个人资料，也不把合成资料写成 P5-REAL 通过。

当前最新主线为 P8-JD Intake 与简历生成体验强化自动化候选：资料准备向导、JD 手动导入中心、岗位列表、当前目标岗位选择、JD 定制简历、source refs、pending confirmations、export preflight、专项 eval 和中文 HTML 截图验收报告已经落地。该结论只覆盖本地/mock + examples / 受控真实感数据路径；P8 第一版不登录 BOSS/猎聘/拉勾等招聘平台，不绕风控抓取，不自动沟通或自动投递，不默认调用真实 provider，也不读取未授权真实个人资料。

## 当前阶段设计文档

当前阶段的执行依据在 `docs/active/`。

- `docs/active/00_README.md` - 阅读顺序和当前阶段基线。
- `docs/active/01_STAGE_PRD.md` - P8-JD Intake 自动化候选 PRD、P5.5/P6/P7 自动化候选基线和历史阶段边界。
- `docs/active/02_TARGET_ARCHITECTURE.md` - P8 资料准备向导、JD 导入中心、JD 定制简历目标架构、当前架构差异和具体代码实体关系。
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md` - 里程碑和出门条件。
- `docs/active/04_ACCEPTANCE_GATES.md` - P8 文档验收门槛、P7-post P5-REAL 复验条件和最终出门条件。
- `docs/active/05_IMPLEMENTATION_SPEC.md` - P0 强化实现规格基线。
- `docs/active/06_TRACEABILITY_MATRIX.md` - 目标、模块、证据、测试和验收追踪矩阵。
- `docs/active/07_REMAINING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` - P0 完成范围和历史验收基线。
- `docs/active/08_P0_PROMPT_AND_OUTPUT_SCHEMAS.md` - P0 prompt、输出 schema、source refs、待确认分级和 eval 断言。
- `docs/active/09_AUTOMATED_DEVELOPMENT_SCOPE.md` - P4 自动化开发范围、验收边界、高风险确认点和历史阶段边界。
- `docs/active/10_P0_FREEZE_AUDIT_AND_ACCEPTANCE_REPORT.md` - P0 冻结审计、验收结果、残留风险和后续开发大纲。
- `docs/active/11_P1_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` - P1 开发及验收计划。
- `docs/active/12_P1_DETAILED_IMPLEMENTATION_SPEC.md` - P1 数据模型、API、provider、versioning、regenerate、export、eval 和打回条件。
- `docs/active/13_P2_END_TO_END_EXPERIENCE_PLAN_AND_AUDIT.md` - P2 端到端用户体验开发计划、验收门槛和启动审计。
- `docs/active/15_P3_REAL_USER_CHATBOX_EXPERIENCE_PLAN.md` - P3 真实用户 Chatbox 体验开发及验收计划。
- `docs/active/16_P4_UX_EXPERIENCE_HARDENING_PLAN.md` - P4 UX 体验强化开发及验收计划。
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md` - P8-JD Intake 自动化候选、P5/P5.5/P6/P7 自动化候选基线和 P8+ 产品化路线图。
- `docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md` - 自由 Chatbox、不中断连续多轮对话、本地连续对话基线和 provider-backed 后续目标分层计划。
- `docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md` - P6 真实 provider opt-in、长程连续对话、上下文压缩、隐私边界、P6-M0/P7-M0 开发前执行细则和验收计划。
- `docs/active/20_P5_5_CANDIDATE_PROFILE_PLAN.md` - P5.5 候选人画像、能力矩阵、项目可信度、岗位短板、source refs 和验收计划。
- `docs/active/21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md` - P8 资料准备向导、JD 手动导入中心、岗位列表、JD 定制简历和招聘平台合规边界。
- `docs/active/stage-reviews/P8_JD_INTAKE_DOCUMENTATION_DEVELOPMENT_AUDIT.md` - P8 文档开发审计，记录资料向导、JD 手动导入、定制简历和平台合规边界。
- `docs/active/stage-reviews/P8_DOCUMENTATION_COVERAGE_REAUDIT.md` - P8 文档覆盖度复审，判断当前文档是否足以支撑后续自动化开发和出门验收。
- `docs/active/stage-reviews/P8_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` - P8-M1 到 P8-M5 详细开发、端到端验收、打回条件和外部审计包。
- `docs/active/stage-reviews/P8_AUTOMATED_DEVELOPMENT_AND_ACCEPTANCE_AUDIT.md` - P8 自动化开发、代码检视、文档审计、PRD 规格检视和验收结论。
- `docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html` - P8-JD Intake 中文自动化验收报告和 headless Chrome 截图证据入口。
- `docs/active/stage-reviews/P4C_FC_PLAN_AND_START_AUDIT.md` - P4C-FC 本地连续对话开发计划和启动审计。
- `docs/active/stage-reviews/P4C_FC_FINAL_AUDIT_AND_PRD_REVIEW.md` - P4C-FC 最终审计、PRD 规格检视和验收结论。
- `docs/active/stage-reviews/P4C_EXTERNAL_PROVIDER_DESENSITIZED_ACCEPTANCE_PLAN.md` - 真实外部 provider + 脱敏资料验收的高风险确认计划。
- `docs/active/stage-reviews/P4_FINAL_CLOSURE_AUDIT.md` - P4 自动化收口代码检视、文档审计、PRD 映射和验收结论。
- `docs/active/stage-reviews/P5_PRE_FREEZE_AUTOMATED_CANDIDATE_AUDIT.md` - P5 自动化验收候选审计、剩余阻塞项和真实资料验收前置条件。
- `docs/active/stage-reviews/P5_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md` - P5 人工体验审查清单；真实资料路径和人工体验记录填写前不得冻结 P5。
- `docs/active/stage-reviews/P5_FREEZE_EXIT_AUDIT_PLAN.md` - P5 final closure audit 执行计划，定义冻结前必须复验的 PRD 路径、工程证据、文档一致性和打回条件。
- `docs/active/stage-reviews/P5_EXTERNAL_REVIEW_REVISION_AUDIT.md` - P5 外部意见修订审计，记录合成资料审核页、剩余开发验收大纲和 ChatGPT 审计包。
- `docs/active/stage-reviews/P5_DOCUMENTATION_COVERAGE_REAUDIT.md` - P5 文档覆盖度复审，判断当前文档是否足以支撑 P5-REAL/P5-Freeze。
- `docs/active/stage-reviews/P6P7_DOCUMENTATION_COVERAGE_AUDIT.md` - P6+P7 文档覆盖度审计、技术路线评估和开发准入结论。
- `docs/active/stage-reviews/P5_REAL_DATA_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` - P5-REAL 真实授权资料开发及验收计划，定义路径授权门、脱敏摘要报告和 P5-Freeze 打回条件。
- `docs/active/stage-reviews/P5_SYNTHETIC_REALISM_ACCEPTANCE_AUDIT.md` - P5 合成真实感资料验收审计，定义多身份合成资料覆盖和不能替代 P5-REAL 的边界。
- `docs/active/stage-reviews/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_AUDIT.md` - P5 阶段性代码检视、文档审计、功能覆盖和三身份合成资料可视化验收记录。
- `docs/active/stage-reviews/P6_M1_PROVIDER_OPT_IN_START_AND_ACCEPTANCE_AUDIT.md` - P6-M1 provider opt-in 启动与验收审计；配置不等于外呼。
- `docs/active/stage-reviews/P6_M2_PROVIDER_BACKED_CHAT_ACCEPTANCE_AUDIT.md` - P6-M2 fake provider-backed chat adapter、consent gate 和 fallback 审计。
- `docs/active/stage-reviews/P6_M3_LONG_CONTEXT_BASELINE_AUDIT.md` - P6-M3 Long Context Manager 本地只读基线审计。
- `docs/active/stage-reviews/P6_M4_M5_TOOL_SAFETY_PRIVACY_AUDIT.md` - P6 Tool Safety、隐私脱敏和 provider_chat_invocation 审计。
- `docs/active/stage-reviews/P7_M1_M2_WORKSPACE_LIFECYCLE_AND_DIAGNOSTICS_AUDIT.md` - P7 workspace lifecycle 与 diagnostics 基线审计；只覆盖 backup manifest、dry-run 和脱敏诊断。
- `docs/active/stage-reviews/P6P7_AUTOMATED_ACCEPTANCE_AND_PRD_REVIEW.md` - P6+P7 自动化验收与 PRD 规格检视。
- `docs/active/stage-reviews/P7_M3_BETA_CLOSURE_AUDIT.md` - P7 本地 Beta 使用说明、支持流程和隐私审计。
- `docs/active/stage-reviews/P5_5_STAGE_ACCEPTANCE_AUDIT.md` - P5.5 阶段性代码检视、文档审计、功能覆盖和可视化验收评价。
- `docs/reports/P6P7_AUTOMATED_ACCEPTANCE_REPORT.html` - P6+P7 中文自动化验收报告和真实界面截图证据入口。
- `docs/reports/P4_FINAL_CLOSURE_AUTOMATED_ACCEPTANCE_REPORT.html` - P4 final closure 自动化 HTML 验收报告和截图证据入口。
- `docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html` - P5 本地/mock + 脱敏 fixture 自动化 HTML 验收报告和截图证据入口。
- `docs/reports/P5_SYNTHETIC_PROFILE_REVIEW.html` - P5-REAL 前置合成简历与背景资料审核页；不代表真实个人资料验收通过。
- `docs/reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html` - P5 三身份合成资料 Chrome/CDP 可视化验收聚合报告；不代表 P5-REAL 通过。
- `docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html` - P5.5 Candidate Profile 中文自动化验收报告和截图证据入口；只覆盖 examples / synthetic-style workspace + mock provider。
- `docs/active/stage-reviews/P4B_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md` - P4B 人工体验审查清单和 P4C backlog 入口。
- `docs/active/stage-reviews/P4B_DOCUMENTATION_COVERAGE_AUDIT.md` - P4B 开发文档覆盖度审计。
- `docs/gemini-frontend-review-package/` - 可交给 Gemini 独立审查的前端页面方案和静态原型。
- `docs/active/stage-reviews/` - P2/P3 子阶段审计记录；P1 阶段审计已归档到 `docs/archive/stage-reviews/p1/`。
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio` - P8 目标体验、当前差距、代码实体关系、开发验收计划、里程碑、门槛和出门条件图。
- `RELEASE_CHECKLIST.md` - P1 发布前检查清单。

原始 v1.0 产品文档包仍保留在 `docs/jobpilot_ai_agent_docs_v1_0/`，作为背景资料。

## 启动 API

本项目会自动读取仓库根目录的 `.env`。先复制示例配置：

```bash
cp .env.example .env
```

默认 `JOBPILOT_LLM_PROVIDER=mock`，不需要任何 API Key。要启用真实 OpenAI-compatible provider，在 `.env` 中配置：

```bash
JOBPILOT_LLM_PROVIDER=openai_compatible
JOBPILOT_OPENAI_BASE_URL=https://api.openai.com/v1
JOBPILOT_OPENAI_API_KEY=<your_api_key>
JOBPILOT_OPENAI_MODEL=gpt-4o-mini
```

MiniMax 可通过 OpenAI-compatible 方式接入：

```bash
JOBPILOT_LLM_PROVIDER=openai_compatible
JOBPILOT_OPENAI_PROVIDER_PRESET=minimax
JOBPILOT_OPENAI_BASE_URL=https://api.minimaxi.com/v1
JOBPILOT_OPENAI_API_KEY=<your_minimax_api_key>
JOBPILOT_OPENAI_MODEL=MiniMax-M3
```

`.env` 已被 `.gitignore` 忽略。不要把 API Key 粘贴到聊天记录、文档、测试 fixture 或日志中；真实外部 provider 调用仍需要人工确认。当前 MiniMax 受控验收结果记录在 `docs/reports/P2_M6_MINIMAX_PROVIDER_ACCEPTANCE_RESULT.json`。

```bash
python3 -m uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
```

## 运行测试

```bash
python3 -m pytest
```

当前测试包含真实感示例数据端到端路径、JD 解析、事实安全、实时提示安全和 workspace 隐私 eval gates。

P5-REAL 真实授权资料验收必须由用户显式提供三类文件路径，且默认只生成脱敏摘要报告：

```bash
JOBPILOT_LLM_PROVIDER=mock \
JOBPILOT_REAL_RESUME_PATH=/path/to/resume.md \
JOBPILOT_REAL_PROJECT_PATH=/path/to/project.md \
JOBPILOT_REAL_JD_PATH=/path/to/jd.md \
python3 scripts/generate_p5_real_data_acceptance.py
```

不要把真实资料路径、`.env`、API Key、日志或 workspace 数据库提交到仓库。

如果用户不提供真实个人资料，可以使用多身份合成资料加强自动化验收真实性，但该路径不能替代 P5-REAL：

```bash
JOBPILOT_LLM_PROVIDER=mock python3 scripts/generate_p5_synthetic_realism_acceptance.py
```

P1/P2/P3 前端验收还必须通过：

```bash
npm --prefix apps/chatbox run build
```

## ChatCore / PiAgent 接入

默认聊天核心是离线可验收的 `KeywordChatCore`：

```bash
python3 -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000
```

Pi Agent Core 可显式切换接管业务编排：

```bash
JOBPILOT_CHAT_CORE=piagent python3 -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000
```

严格模式会在 PiAgent 不可用时直接失败，避免误把 fallback 当作 PiAgent 验收通过：

```bash
JOBPILOT_CHAT_CORE=piagent JOBPILOT_CHAT_CORE_STRICT=1 python3 -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000
```

## 启动 Chatbox

先安装前端依赖：

```bash
npm --prefix apps/chatbox install
npm --prefix apps/chatbox run dev
```

然后打开 `http://127.0.0.1:5173`。

## Demo 路径

`examples/` 中的示例数据用于跑通关键验收路径：

```text
简历 + 项目 README
→ CareerFact / SkillEvidence / TechProject
→ Junior Frontend JD
→ MatchReport
→ ApplicationPackage Markdown
→ Interview Prep / StoryCard
→ Realtime 文本结构提示
→ Review 和 TrainingTask
```

自动化版本在 `tests/test_demo_flow.py`。

## 产品边界

MVP / P1 不做注册登录、SaaS 多租户、Billing、自动海投、隐蔽式面试浮窗、面试官人脸/情绪/敏感属性分析或完整 ASR。正式面试模式只提供结构提示和事实安全提醒。

P5-REAL/P5-Freeze 当前为冻结延期复验，不是验收通过。P6/P7 不把 ASR、会议平台、自动投递、SaaS、多租户、Billing 或默认真实外部 provider 作为隐式能力；真实 provider 只能在 P6 opt-in、用户明确确认、密钥本地配置和脱敏日志边界均满足后验收。浏览器体验验收仍至少覆盖 1200px、1440px、1600px、1920px、720px、390px，并要求截图脚本隔离或清理 viewport emulation，避免污染人工审查浏览器。
