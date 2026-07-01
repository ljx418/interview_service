# P5.5 阶段性验收、代码检视与可视化报告审计

日期：2026-06-30  
状态：阶段性自动化验收通过；仅支持 examples / synthetic-style workspace + mock provider 自动化候选。

## 0. 复核结论和打回修复记录

本文件在首次生成后被复核为“不足以让第三方完整审计本阶段自动化开发工作”，原因如下：

- 缺少从原始 PRD / active PRD / acceptance gates 到代码、测试、截图的逐项映射；
- 缺少证据文件清单、尺寸和 hash，第三方无法确认报告引用的截图是否就是本轮证据；
- 缺少人工审计操作步骤，读者只能相信结论，不能按文档独立复验；
- 缺少失败条件和虚假验收拦截项，无法判断哪些情况必须打回；
- 缺少代码实体和接口行号，人工审计时定位成本过高。

本次修复后，本文件的定位是“P5.5 人工审计入口文档”：人类审计者可以只从本文开始，定位代码、报告、截图、测试和未验证范围，并决定本阶段自动化候选是否可以接受。

## 1. 审计范围

本轮重新基于原始 PRD 和当前 active P5.5 文档执行阶段性审计：

- 原始 PRD：`docs/jobpilot_ai_agent_docs_v1_0/docs/01_PRD_JobPilot_AI_Agent_Service_v1.0.md`
- 当前 PRD：`docs/active/01_STAGE_PRD.md`
- 目标架构：`docs/active/02_TARGET_ARCHITECTURE.md`
- 验收门槛：`docs/active/04_ACCEPTANCE_GATES.md`
- 追踪矩阵：`docs/active/06_TRACEABILITY_MATRIX.md`
- P5.5 计划：`docs/active/20_P5_5_CANDIDATE_PROFILE_PLAN.md`
- 可视化报告：`docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html`
- 实现提交：`30576ce feat: complete P5.5 candidate profile acceptance`
- 审核证据增强提交：`b4ff0f9 docs: strengthen P5.5 audit evidence`
- 报告证据目录：`docs/reports/evidence/p5_5_candidate_profile/`

## 1.1 人工审计操作步骤

第三方审计者应按以下顺序复验，不需要推断隐藏前提：

1. 打开 `docs/active/01_STAGE_PRD.md`，确认 P5.5 当前目标是 Candidate Profile，且未把真实资料、真实 provider、SaaS、ASR、会议平台、自动投递或 MCP/CLI 写入本阶段通过范围。
2. 打开 `docs/active/02_TARGET_ARCHITECTURE.md`，确认 P5.5 代码实体是 Chatbox、profile API、`services/profile/candidate.py`、既有 SQLite 表和 artifact/version/source refs。
3. 打开 `docs/active/04_ACCEPTANCE_GATES.md`，逐项核对 P5.5 Gate 0-6。
4. 打开 `docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html`，确认报告为中文、状态为 passed、包含目标架构、当前实现、自动化步骤、命令结果、PRD 规格检视、代码检视、文档审计、截图证据和未验证范围。
5. 检查 `docs/reports/evidence/p5_5_candidate_profile/` 中 8 张截图，确认图片非空、能看到真实 Chatbox 界面、Candidate Profile 面板、岗位短板和 source refs 展开。
6. 运行或核对以下命令结果：P5.5 定向 pytest、全量 pytest、前端 build、drawio XML parse、Headless Chrome/CDP 报告生成、报告断言测试。
7. 检查实现提交 `30576ce`，确认变更集中在 P5.5 代码、文档、测试、报告和截图证据，没有 `.env`、真实 API Key 或真实个人资料。
8. 检查审核证据增强提交 `b4ff0f9`，确认该提交只补强人工审计入口、证据 hash、复验步骤、失败条件和未验证范围，没有改变 P5.5 功能行为。

## 1.2 关键代码入口

| 审计对象 | 文件和行号 | 人工审计重点 |
| --- | --- | --- |
| 读取画像 API | `services/api/main.py:390` | `GET /api/profile/candidate` 只读返回空态或画像态 |
| 刷新画像 API | `services/api/main.py:395` | `POST /api/profile/candidate/refresh` 显式刷新画像 |
| 读取画像实现 | `services/profile/candidate.py:226` | 从 artifact / candidate_profile 读取结构化画像 |
| 刷新画像实现 | `services/profile/candidate.py:259` | 写入 `candidate_profile` 和 `artifact_type=candidate_profile`，保留 source refs |
| 前端画像面板 | `apps/chatbox/src/main.tsx:1296` | 展示画像概览、能力矩阵、项目可信度、岗位短板 |
| 前端刷新动作 | `apps/chatbox/src/main.tsx:1675` | 画像刷新由显式用户动作触发 |
| 画像样式 | `apps/chatbox/src/styles.css:1250` | 多视口下保持画像面板可读 |

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
| 原始 PRD 的本地优先、可审查、可追溯求职 Agent 方向 | `docs/jobpilot_ai_agent_docs_v1_0/docs/01_PRD_JobPilot_AI_Agent_Service_v1.0.md`、active P5.5 PRD、HTML 报告 PRD 规格检视 | 通过，仅限 local/mock |
| 专业背景画像可追溯 | `test_p5_5_candidate_profile_eval.py`、`p5_5_profile_overview.png`、artifact source refs | 通过 |
| 能力矩阵解释证据强弱 | `test_p5_5_capability_matrix_eval.py`、`p5_5_profile_overview.png` | 通过 |
| 项目可信度不夸大 | `test_p5_5_project_credibility_eval.py`、`p5_5_profile_overview.png` / `p5_5_source_refs.png` | 通过 |
| 岗位短板可行动 | `test_p5_5_gap_analysis_eval.py`、`p5_5_source_refs.png` | 通过 |
| 普通聊天不误写画像产物 | `test_p5_5_chat_boundary_eval.py` | 通过 |
| 中文 HTML 报告和截图证据 | `test_p5_5_acceptance_report_eval.py`、`docs/reports/evidence/p5_5_candidate_profile/` | 通过 |
| 多视口可读性 | `p5_5_profile_1200.png`、`p5_5_profile_1600.png`、`p5_5_profile_1920.png`、`p5_5_profile_720.png`、`p5_5_profile_mobile_390.png` | 通过，但只证明 P5.5 画像路径 |

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

| 证据文件 | 大小 | SHA-256 | 证明内容 |
| --- | ---: | --- | --- |
| `p5_5_initial_desktop.png` | 195251 bytes | `d3a6aeec74950fe7edbfe6d5a6653d87bd01d2f69c4734c457f1188784e2e66e` | 初始桌面状态、本地/mock 边界和入口 |
| `p5_5_profile_overview.png` | 167416 bytes | `4b7ecefb725d1d58c899e2b126cf8263c3dea88ef5d8b9709ead1190b758510a` | 画像刷新后 Workbench 可见，展示能力矩阵、项目可信度和岗位短板 |
| `p5_5_source_refs.png` | 165300 bytes | `3da8dc9fa87f02976559134f8f0f8dfeba912b76ae83e15cb7f81ae87dc01f48` | source refs 与未验证范围展开可见 |
| `p5_5_profile_1200.png` | 155088 bytes | `b3601ca0fc40bec21dd6b898a77554a9bf97f1e07c8a2626926434a876c320bf` | 1200px 视口画像路径可读 |
| `p5_5_profile_1600.png` | 172797 bytes | `dc7f55a5427c4bce895945e40453d179dc33c321abc55a0def011d5c903072ab` | 1600px 视口画像路径可读 |
| `p5_5_profile_1920.png` | 190054 bytes | `ff3a96bbb7dc83b4cbdf618dc4f680949111c8c42dc803c75099f41e92913fac` | 1920px 视口画像路径可读 |
| `p5_5_profile_720.png` | 68655 bytes | `2a759f9eb62e453a126cfe19f14e22c8e8237904e1774714c8657ab8bec2819e` | 720px 窄屏画像路径可读 |
| `p5_5_profile_mobile_390.png` | 60562 bytes | `7ecf1a84c13bba312a295848e5141fda367b687b1a87498f3ebbcf73e9c18fe7` | 390px 移动端画像路径可读 |
| `p5_5_multi_turn_dialogues.json` | 53919 bytes | `573af6bd046b9aa54bc82bf9d7aba9b8c853701db5ba90f76f5f686f62f54330` | 三个不同技术背景合成候选人的虚拟资料和每组 20 轮 fake provider opt-in transcript |

HTML 报告 hash：

- `docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html`
- SHA-256：`b9ebd796e2c4cff223be7c1e5186418ecae868d45e90f95c062e6f8cf3a08983`

## 6.1 自动化场景复验说明

报告由以下两步生成：

```bash
JOBPILOT_LLM_PROVIDER=mock .venv/bin/python scripts/generate_p5_5_candidate_profile_acceptance.py
node scripts/browser_tools/browser-acceptance.mjs \
  --start-chrome \
  --scenario .tmp/p5-5-candidate-profile.scenario.json \
  --output-dir docs/reports/evidence/p5_5_candidate_profile \
  --report docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html \
  --port 9235
```

`scripts/browser_tools/browser-acceptance.mjs` 使用 `--headless=new` 启动 Chrome。若未来改为可见 Chrome 或会抢占焦点，必须提前告知用户。

## 6.2 人工截图核对要求

审计者不应只看文件存在，必须实际打开截图并确认：

- `p5_5_profile_overview.png` 中右侧 Workbench 出现候选人画像内容，而不是空白占位；
- `p5_5_source_refs.png` 中 source refs 与未验证范围展开可见；
- 多视口截图不是同一张图复制，且宽度布局确实不同；
- 图片中没有真实姓名、联系方式、真实账号、API Key 或 provider raw response；
- 截图只证明可视路径，不单独证明后端写入正确，后端写入由 pytest 和 artifact/source refs 断言证明。

## 7. 未验证范围

- 未使用用户真实个人资料；
- 未执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼；
- 未验证 P5-REAL / P5-Freeze；
- 未验证 SaaS、ASR、会议平台、自动投递、MCP/CLI；
- 未声明人工体验冻结或最终产品化发布通过。

## 7.1 必须打回的情况

出现以下任一情况，不能接受本阶段审计结论：

- 报告或文档出现“真实个人资料路径已通过”“真实 provider 默认路径已通过”“P5-REAL 已通过”等扩展结论；
- `docs/reports/evidence/p5_5_candidate_profile/` 缺少任一截图，或截图无法打开、为空白、与报告不对应；
- `test_p5_5_chat_boundary_eval.py` 失败，说明普通聊天可能写入画像 artifact；
- `test_p5_5_candidate_profile_eval.py` 失败，说明 profile row、artifact/version 或 source refs 不能被证明；
- 全量 pytest 或前端 build 失败，说明 P5.5 可能破坏既有本地基线；
- drawio 超过 8 页或 XML 无法解析，说明架构审计图不可复验；
- 发现 `.env`、真实 API Key、真实个人资料、workspace 数据库或未脱敏 raw provider response 被提交。

## 7.2 仍需后续补证的内容

以下不是 P5.5 自动化候选的失败项，但必须在后续阶段单独补证：

- 用户真实个人资料的脱敏导入、解析和人工复核；
- MiniMax / DeepSeek / OpenAI-compatible 真实 provider 的 opt-in 调用质量；
- 长程真实 provider 连续对话的费用、隐私、失败降级和日志审计；
- SaaS、多租户、Billing、ASR、会议平台、自动投递、MCP/CLI；
- 人工体验认可和最终产品化发布。

## 8. 验收评价

P5.5 Candidate Profile 阶段性自动化验收通过。当前代码、文档、测试和截图证据能够支撑“本地/mock + examples/synthetic-style workspace 下可生成并审查候选人画像、能力矩阵、项目可信度、岗位短板和 source refs”的结论。

该结论不能扩展为真实个人资料路径、真实 provider 质量、P5-REAL、SaaS 或最终产品化通过。若进入下一阶段，应继续把真实资料和真实 provider 作为高风险 opt-in 流程单独验收。

## 9. 人工审计最终勾选表

审计者完成以下勾选后，才能接受本阶段自动化候选：

- [ ] 已打开 HTML 报告并确认状态为 passed；
- [ ] 已打开至少 `p5_5_profile_overview.png`、`p5_5_source_refs.png`、`p5_5_profile_mobile_390.png` 三张截图；
- [ ] 已确认报告和截图没有真实个人资料、真实 API Key 或 provider raw response；
- [ ] 已核对 P5.5 Gate 0-6 均有测试或截图证据；
- [ ] 已确认普通聊天不写画像 artifact 的测试存在并通过；
- [ ] 已确认全量 pytest、前端 build、drawio parse 均通过；
- [ ] 已确认实现提交 `30576ce` 的变更范围与 P5.5 相关；
- [ ] 已确认审核证据增强提交 `b4ff0f9` 只补强审计证据和复验说明；
- [ ] 已确认未验证范围没有被写成已完成能力。
