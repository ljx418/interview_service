# P5 阶段性审计与合成资料可视化验收记录

日期：2026-06-26
阶段：P5 真实资料本地闭环 / 合成资料增强验收
结论：阶段性自动化验收通过，支持“P5 合成资料增强自动化候选通过”。不得声明 P5-REAL、真实个人资料路径、真实外部 provider 默认路径或最终产品化已经通过。

## 1. 审计依据

本轮审计重新对齐以下原始 PRD 和 active 阶段文档：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `docs/active/stage-reviews/P5_FREEZE_EXIT_AUDIT_PLAN.md`
- `docs/active/stage-reviews/P5_SYNTHETIC_REALISM_ACCEPTANCE_AUDIT.md`

本轮不读取用户真实个人资料，不搜索个人目录，不调用 MiniMax、DeepSeek 或其他真实外部 provider。

## 2. 代码检视结论

| 区域 | 检视结论 | 状态 |
| --- | --- | --- |
| `apps/chatbox/src/main.tsx` / `apps/chatbox/src/styles.css` | 当前前端能展示本地就绪、示例/我的资料、Mock 本地模式、Agent 状态机、输入区快捷动作、产物推进台和移动端抽屉。 | 通过 |
| `services/tools/jobpilot.py` | P5 申请包仍保留事实确认、版本、source refs、确认后导出门槛等本地闭环能力。 | 通过 |
| `services/chat/core.py` | 本地 mock/keyword 路径可区分自由追问、状态查询和显式工具触发。 | 通过 |
| `services/chat/piagent_adapter.py` | 本轮发现 PiAgent Node bridge 15 秒超时阈值在 WSL/Windows 下过窄，已改为 `JOBPILOT_PI_BRIDGE_TIMEOUT_SECONDS` 可配置，默认 45 秒，并捕获超时后在非 strict 模式可控降级。 | 已修复 |
| `scripts/browser_tools/browser-acceptance.mjs` | 可通过 Chrome DevTools Protocol 执行真实 UI 场景、截图并生成独立 HTML 报告。 | 通过 |

## 3. 文档审计结论

| 文档范围 | 审计结论 | 状态 |
| --- | --- | --- |
| PRD 与验收门槛 | P5 目标仍限定为本地资料闭环，P6/P7/P8+ 能力没有被写成 P5 已完成。 | 通过 |
| 目标架构 | 架构文档能对应当前代码实体：Chatbox、FastAPI、ChatCore、Domain Tools、SQLite workspace、Export、Browser Evidence。 | 通过 |
| drawio gap 文档 | XML 解析通过，分页 6 页，不超过 8 页要求。 | 通过 |
| 报告口径 | 本轮报告明确合成资料不是真实个人资料验收，不替代人工体验和 P5 final freeze。 | 通过 |
| 概念一致性 | 仍保持“mock/local 默认、本地隐私边界、外部 provider opt-in、真实资料需授权”的概念一致。 | 通过 |

## 4. 功能与测试覆盖

| PRD / Gate | 当前实现证据 | 结论 |
| --- | --- | --- |
| P0-P4 回归不退化 | `.venv/bin/python -m pytest`：88 passed, 1 warning。 | 通过 |
| 前端可构建 | `npm --prefix apps/chatbox run build`：通过。 | 通过 |
| 资料导入与解析 | 三身份合成资料通过浏览器 scenario 导入 resume/project 并触发 profile extraction。 | 通过 |
| JD 解析与匹配报告 | 三身份 scenario 均等待到“我已解析岗位并生成适合度分析”。 | 通过 |
| 申请包生成与确认门槛 | 三身份 scenario 均生成申请包，确认前导出被阻塞，确认后导出成功。 | 通过 |
| 多视口体验 | 每个 persona 均覆盖 1440、1200、1600、1920、720、390 视口截图。 | 通过 |
| 隐私与 provider 边界 | 本轮使用 mock provider 和合成资料；不调用外部 provider。 | 通过 |
| 真实个人资料路径 | 用户明确不提供真实资料，本轮未执行。 | 未验证 |

## 5. 自动化证据

| 证据 | 结果 |
| --- | --- |
| 全量 pytest | `88 passed, 1 warning in 77.35s` |
| PiAgent 定向回归 | `8 passed in 53.68s` |
| 前端 build | `tsc && vite build` 通过 |
| drawio parse | `drawio_parse=passed pages=6` |
| 合成场景生成 | `ops_to_frontend`、`qa_to_fullstack`、`teacher_to_edtech` 三份 scenario 生成成功 |
| 浏览器验收 | 三份 Chrome/CDP scenario 均通过 |
| 截图可见性 | PNG 尺寸、体积、像素范围检查通过，并人工抽看桌面/移动截图可见 |

## 6. 可视化验收报告

聚合报告：

- `docs/reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html`

独立 persona 报告：

- `docs/reports/P5_SYNTHETIC_REALISM_ACCEPTANCE_ops_to_frontend.html`
- `docs/reports/P5_SYNTHETIC_REALISM_ACCEPTANCE_qa_to_fullstack.html`
- `docs/reports/P5_SYNTHETIC_REALISM_ACCEPTANCE_teacher_to_edtech.html`

截图证据目录：

- `docs/reports/p5-synthetic-realism-ops_to_frontend-evidence/`
- `docs/reports/p5-synthetic-realism-qa_to_fullstack-evidence/`
- `docs/reports/p5-synthetic-realism-teacher_to_edtech-evidence/`

## 7. 未验证范围与风险

- 未使用用户真实个人资料，因此不得声明真实个人资料路径通过。
- 未调用 MiniMax、DeepSeek、OpenAI-compatible 等真实外部 provider，因此不得声明真实 provider 默认路径通过。
- 未验证 SaaS 登录、多租户、计费、ASR、会议平台、自动投递或真实招聘平台投递。
- 未替代人工体验审查；报告只能证明本轮自动化浏览器路径通过。
- 当前仍不能声明最终产品化完成。

## 8. 审计意见

本轮证据足以支持 P5 合成资料增强自动化候选通过，并提升了“不同身份、不同背景、不同岗位”下的验收真实性。若要进入 P5 final freeze，仍必须按既有门槛补齐真实授权资料路径复核或明确调整冻结口径，且不能把合成资料路径写成 P5-REAL。
