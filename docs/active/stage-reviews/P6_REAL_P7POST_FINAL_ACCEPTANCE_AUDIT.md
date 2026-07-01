# P6-REAL / P7-post Final Acceptance Audit

日期：2026-07-01

## 1. 范围

本审计汇总本轮 P6-REAL / P7-post 自动化开发执行结果。本轮真实 provider real mode 未授权，真实个人资料未授权，因此两者均不执行。

## 2. 交付物

- `scripts/generate_p6_real_provider_acceptance.py`
- `scripts/generate_p6_real_p7post_stage_acceptance.py`
- `tests/evals/test_p6_real_provider_acceptance_eval.py`
- `docs/reports/P6_REAL_PROVIDER_ACCEPTANCE_REPORT.html`
- `docs/reports/P6_REAL_P7POST_STAGE_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p6_real_provider_acceptance/p6_real_provider_evidence.json`
- `docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p5_5_candidate_profile/`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_multi_turn_dialogues.json`

## 2.1 本轮执行命令

| 命令 | 结果 |
| --- | --- |
| `JOBPILOT_LLM_PROVIDER=mock .venv/bin/python scripts/generate_p5_5_candidate_profile_acceptance.py` | 通过，生成 P5.5 browser scenario 和三身份 20 轮 fake provider 对话证据 |
| `node scripts/browser_tools/browser-acceptance.mjs --start-chrome --scenario .tmp/p5-5-candidate-profile.scenario.json --output-dir docs/reports/evidence/p5_5_candidate_profile --report docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html --port 9235` | 通过，Headless Chrome/CDP 刷新真实界面截图 |
| `.venv/bin/python scripts/generate_p6_real_provider_acceptance.py --mode gate-only` | 通过，未授权真实 provider 未执行 |
| `.venv/bin/python scripts/generate_p6_real_p7post_stage_acceptance.py --pytest-result passed --build-result passed --browser-result passed --drawio-result passed --scan-result passed` | 通过，生成最终中文 HTML 汇总报告 |
| `.venv/bin/python -m pytest tests/evals/test_p5_5_acceptance_report_eval.py tests/evals/test_p6_real_provider_acceptance_eval.py -q` | 5 passed |
| `.venv/bin/python -m pytest` | 113 passed, 1 warning |
| `npm --prefix apps/chatbox run build` | 通过 |
| `drawio XML parse` | 通过，6 页，未压缩 XML |
| 敏感信息与虚假声明扫描 | 通过，无命中 |

## 3. 阶段结论

| 项目 | 结论 |
| --- | --- |
| P6-REAL gate-only | 通过 |
| P6-REAL real provider | 未授权，未执行 |
| P5.5 visual evidence | 通过，Headless Chrome/CDP 截图可见真实 Chatbox 画像界面和多视口路径 |
| P7-post synthetic | 通过，用作自动化真实性增强；不能替代真实资料复验 |
| P5-REAL | 未授权真实资料，未执行 |
| SaaS / ASR / 会议平台 / 自动投递 | 未进入范围 |

## 3.1 PRD 规格检视

| PRD / Gate 要求 | 本轮证据 | 结论 |
| --- | --- | --- |
| 本地优先和默认安全 | 默认 mock / fake provider；P6-REAL gate-only 证明 configured 不等于 called | 通过 |
| Candidate Profile 可追溯 | P5.5 HTML 报告、画像总览、source refs、多视口截图和 eval | 通过 |
| 长程对话边界 | 三身份各 20 轮 fake provider opt-in transcript，含 rolling summary / privacy boundary | 通过 fake provider 路径 |
| 真实 provider 必须 opt-in | P6-REAL gate-only 未授权时 fallback，真实 real mode 未执行 | 通过门禁，不代表真实质量 |
| 真实资料必须用户授权 | 本轮未读取真实资料，报告保持 P5-REAL not-executed | 通过边界 |
| 不做虚假验收 | 报告和扫描均未出现真实 provider / 真实资料已通过结论 | 通过 |

## 3.2 证据文件

- `docs/reports/evidence/p5_5_candidate_profile/p5_5_initial_desktop.png`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_profile_overview.png`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_source_refs.png`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_profile_1200.png`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_profile_1600.png`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_profile_1920.png`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_profile_720.png`
- `docs/reports/evidence/p5_5_candidate_profile/p5_5_profile_mobile_390.png`

## 4. 出门评价

本轮可以作为 P6-REAL / P7-post 的自动化门禁候选收口。它证明了：

- 未授权真实 provider 不会被写成已调用；
- configured 不等于 called；
- 缺少 consent 时 fallback 可用；
- 合成资料不会被写成真实个人资料；
- 未执行路径保持未执行。
- 中文 HTML 汇总报告能让人类从目标架构、当前实现、截图证据、PRD 检视、命令结果和未验证范围审计本阶段自动化开发结果。

它不证明：

- 真实 provider 回复质量；
- 真实个人资料路径；
- 最终产品化；
- SaaS、ASR、会议平台、自动投递、MCP/CLI。

## 5. 后续触发条件

- 若用户授权真实 provider，执行 `scripts/generate_p6_real_provider_acceptance.py --mode real`；
- 若用户提供真实资料路径，执行 P5-REAL 真实资料复验；
- 任何删除、清理 apply、迁移 apply、ASR、会议平台、自动投递、SaaS 操作仍需单独确认。
