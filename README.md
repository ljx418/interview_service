# JobPilot AI

JobPilot AI 是一个面向转行程序员的本地优先、免费开源 AI 求职 Agent 服务。默认入口是极简 Chatbox，但真正的核心是后端 Agent Tool Service：同一套能力后续可以被 Chatbox、HTTP API、CLI、MCP Client 或外部 Agent 调用。

## 当前 MVP / P3 基线

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

当前进入 P3：把 Chatbox 从“可演示的一键体验”推进到“真实用户可理解、可对话、可管理产物、可在窄屏使用”的求职工作台。默认验收仍使用 mock provider 和 examples 真实感数据；真实个人资料和真实外部调用范围仍需人工确认。

## 当前阶段设计文档

当前阶段的执行依据在 `docs/active/`。

- `docs/active/00_README.md` - 阅读顺序和当前阶段基线。
- `docs/active/01_STAGE_PRD.md` - P3 目标体验路径和历史阶段基线。
- `docs/active/02_TARGET_ARCHITECTURE.md` - 目标架构深度设计。
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md` - 里程碑和出门条件。
- `docs/active/04_ACCEPTANCE_GATES.md` - P3 验收门槛和最终出门条件。
- `docs/active/05_IMPLEMENTATION_SPEC.md` - P0 强化实现规格基线。
- `docs/active/06_TRACEABILITY_MATRIX.md` - 目标、模块、证据、测试和验收追踪矩阵。
- `docs/active/07_REMAINING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` - P0 完成范围和历史验收基线。
- `docs/active/08_P0_PROMPT_AND_OUTPUT_SCHEMAS.md` - P0 prompt、输出 schema、source refs、待确认分级和 eval 断言。
- `docs/active/09_AUTOMATED_DEVELOPMENT_SCOPE.md` - P3 自动化开发范围、验收边界、高风险确认点和历史阶段边界。
- `docs/active/10_P0_FREEZE_AUDIT_AND_ACCEPTANCE_REPORT.md` - P0 冻结审计、验收结果、残留风险和后续开发大纲。
- `docs/active/11_P1_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` - P1 开发及验收计划。
- `docs/active/12_P1_DETAILED_IMPLEMENTATION_SPEC.md` - P1 数据模型、API、provider、versioning、regenerate、export、eval 和打回条件。
- `docs/active/13_P2_END_TO_END_EXPERIENCE_PLAN_AND_AUDIT.md` - P2 端到端用户体验开发计划、验收门槛和启动审计。
- `docs/active/15_P3_REAL_USER_CHATBOX_EXPERIENCE_PLAN.md` - P3 真实用户 Chatbox 体验开发及验收计划。
- `docs/active/stage-reviews/` - P2/P3 子阶段审计记录；P1 阶段审计已归档到 `docs/archive/stage-reviews/p1/`。
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio` - P3 架构模块、组件职责、调用关系、数据所有权、安全边界和验收证据图。
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

P3 不把 MCP Server、CLI、ASR 或会议平台作为出门条件；P3 的核心是可对话、可管理产物、响应式可用的 Chatbox 求职工作台。
