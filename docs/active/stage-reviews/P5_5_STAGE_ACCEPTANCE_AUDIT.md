# P5.5 阶段性验收、代码检视与可视化报告审计

日期：2026-06-30  
状态：阶段性自动化验收通过；仅支持 examples / synthetic-style workspace + mock provider 自动化候选。

## 1. 审计范围

本轮重新基于原始 PRD 和当前 active P5.5 文档执行阶段性审计：

- 原始 PRD：`docs/jobpilot_ai_agent_docs_v1_0/docs/01_PRD_JobPilot_AI_Agent_Service_v1.0.md`
- 当前 PRD：`docs/active/01_STAGE_PRD.md`
- 目标架构：`docs/active/02_TARGET_ARCHITECTURE.md`
- 验收门槛：`docs/active/04_ACCEPTANCE_GATES.md`
- 追踪矩阵：`docs/active/06_TRACEABILITY_MATRIX.md`
- P5.5 计划：`docs/active/20_P5_5_CANDIDATE_PROFILE_PLAN.md`
- 可视化报告：`docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html`

## 2. 代码检视结论

| 区域 | 结论 | 风险 |
| --- | --- | --- |
| `services/profile/candidate.py` | 复用既有 `candidate_profile`、`career_fact`、`skill_evidence`、`tech_project`、`job`、`match_report`、artifact/version，不新增不可逆 DB 迁移。 | 未发现致命或重大问题 |
| `services/api/main.py` / `services/api/schemas.py` | `GET /api/profile/candidate` 与 `POST /api/profile/candidate/refresh` 提供最小读/刷新入口。 | 未发现致命或重大问题 |
| `apps/chatbox/src/main.tsx` / `styles.css` | Workbench 展示画像、能力矩阵、项目可信度、岗位短板和 source refs；刷新画像为显式动作。 | 未发现致命或重大问题 |
| Chat 边界 | 普通追问不写 `candidate_profile` artifact，由 `test_p5_5_chat_boundary_eval.py` 覆盖。 | 未发现致命或重大问题 |

## 3. 文档审计结论

本轮发现并修复了 P5.5 文档中的旧口径：

- `01_STAGE_PRD.md` 顶部仍写“只做文档开发，不进入具体代码编写”；
- `02_TARGET_ARCHITECTURE.md` 的 P5.5 代码实体表仍写“待新增 / 待开发”。

修复后，P5.5 相关文档一致表达为：

- P5.5 自动化开发候选已完成；
- 结论只覆盖 examples / synthetic-style workspace + mock provider；
- 真实个人资料、真实 provider、P5-REAL、SaaS、ASR、会议平台、自动投递、MCP/CLI 均未验收；
- P6/P7 历史章节作为已完成自动化候选基线和后续复验边界保留。

## 4. 功能覆盖检查

| PRD / Gate 功能点 | 覆盖证据 | 结论 |
| --- | --- | --- |
| 专业背景画像可追溯 | `test_p5_5_candidate_profile_eval.py`、报告截图、artifact source refs | 通过 |
| 能力矩阵解释证据强弱 | `test_p5_5_capability_matrix_eval.py`、`p5_5_profile_overview.png` | 通过 |
| 项目可信度不夸大 | `test_p5_5_project_credibility_eval.py`、项目可信度截图 | 通过 |
| 岗位短板可行动 | `test_p5_5_gap_analysis_eval.py`、岗位短板截图 | 通过 |
| 普通聊天不误写画像产物 | `test_p5_5_chat_boundary_eval.py` | 通过 |
| 中文 HTML 报告和截图证据 | `test_p5_5_acceptance_report_eval.py`、`docs/reports/evidence/p5_5_candidate_profile/` | 通过 |

## 5. 自动化验收结果

| 命令 | 结果 |
| --- | --- |
| `.venv/bin/python -m pytest tests/evals/test_p5_5_candidate_profile_eval.py tests/evals/test_p5_5_capability_matrix_eval.py tests/evals/test_p5_5_project_credibility_eval.py tests/evals/test_p5_5_gap_analysis_eval.py tests/evals/test_p5_5_chat_boundary_eval.py tests/evals/test_p5_5_acceptance_report_eval.py -q` | 8 passed, 1 warning |
| `npm --prefix apps/chatbox run build` | 通过 |
| drawio XML parse | 通过，6 页 |
| `.venv/bin/python -m pytest -q` | 109 passed, 1 warning |
| `node scripts/browser_tools/browser-acceptance.mjs --start-chrome --scenario .tmp/p5-5-candidate-profile.scenario.json --output-dir docs/reports/evidence/p5_5_candidate_profile --report docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html --port 9235` | 通过，Headless Chrome/CDP 生成报告 |
| `.venv/bin/python -m pytest tests/evals/test_p5_5_acceptance_report_eval.py -q` | 1 passed |

## 6. 截图证据

截图目录：`docs/reports/evidence/p5_5_candidate_profile/`

- `p5_5_initial_desktop.png`
- `p5_5_profile_overview.png`
- `p5_5_source_refs.png`
- `p5_5_profile_1200.png`
- `p5_5_profile_1600.png`
- `p5_5_profile_1920.png`
- `p5_5_profile_720.png`
- `p5_5_profile_mobile_390.png`

## 7. 未验证范围

- 未使用用户真实个人资料；
- 未执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼；
- 未验证 P5-REAL / P5-Freeze；
- 未验证 SaaS、ASR、会议平台、自动投递、MCP/CLI；
- 未声明人工体验冻结或最终产品化发布通过。

## 8. 验收评价

P5.5 Candidate Profile 阶段性自动化验收通过。当前代码、文档、测试和截图证据能够支撑“本地/mock + examples/synthetic-style workspace 下可生成并审查候选人画像、能力矩阵、项目可信度、岗位短板和 source refs”的结论。

该结论不能扩展为真实个人资料路径、真实 provider 质量、P5-REAL、SaaS 或最终产品化通过。若进入下一阶段，应继续把真实资料和真实 provider 作为高风险 opt-in 流程单独验收。
