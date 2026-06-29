# P5.5 Candidate Profile 文档开发审计

日期：2026-06-29  
状态：开发前文档复审通过；后续 P5.5 自动化开发候选已按该审计进入实现并完成。

## 1. 审计范围

本轮原始审计只审计文档，不进入代码开发；后续实现阶段已追加 M0-M6 审计、eval 和可视化报告。原始审计对象：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/20_P5_5_CANDIDATE_PROFILE_PLAN.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `README.md`
- `TODO.md`

## 2. 覆盖结论

| 维度 | 结论 |
| --- | --- |
| 目标体验 | 已明确：职业画像、能力矩阵、项目可信度、岗位短板、source refs 画像面板 |
| 架构实体 | 已绑定现有表和模块：candidate_profile、career_fact、skill_evidence、tech_project、match_report、artifact、ChatCore、Chatbox |
| 开发计划 | 已拆分为 P5.5-M0 到 P5.5-M6 |
| 验收门槛 | 已覆盖来源证据、能力等级、项目可信度、短板可行动、普通聊天不写 artifact、报告脱敏 |
| 风险边界 | 已声明不做真实资料默认验收、真实 provider 默认外呼、敏感属性分析和 P8+ 高风险能力 |
| drawio | 保持 6 页，不超过 8 页，并同步文本镜像 |

## 3. 规格完整性判断

当前文档可以支撑 P5.5 后续自动化开发。后续实现者不需要重新决定 P5.5 的产品目标、架构层级、主要代码实体、验收门槛、非目标或高风险边界。

以下实现决策已在文档中闭环，不再留给实现阶段临时决定：

- 后续自动化验收默认继续只使用 `examples/`、`examples/p5_synthetic_personas/` 和测试临时 workspace；
- 必须新增 `GET /api/profile/candidate` 和 `POST /api/profile/candidate/refresh` 两个最小 profile routes；
- 刷新画像必须更新或创建 `candidate_profile` 行，并写入 `artifact_type=candidate_profile` 的 artifact/version；
- P5.5 v1 先做只读画像聚合、刷新和证据展开，不做复杂手工编辑画像；
- 能力矩阵、项目可信度和岗位短板保存到 profile artifact `content_json`，不新增数据库表。

进入代码开发前仍需生成短启动审计，但其作用是确认执行顺序和验收环境，不再承担产品/架构决策。

## 4. 原始开发前未验证范围

- 原始文档审计时尚未实现 P5.5 业务代码；
- 原始文档审计时尚未生成 P5.5 HTML 验收报告；
- 未执行真实个人资料路径；
- 未执行真实 provider 调用；
- 未验证任何敏感属性分析能力，且该能力明确不属于 P5.5；
- 未实现 SaaS、ASR、会议平台、自动投递、MCP/CLI。

## 5. 审计意见

P5.5 文档开发已收口。后续已按本审计意见完成 P5.5-M0 启动审计，并按 CandidateProfile 聚合、能力矩阵、项目可信度、岗位短板、Workbench 展示和可视化验收报告的顺序实现。

## 6. 2026-06-30 独立复审记录

本轮按三轮独立审计执行：

1. PRD 体验审计：检查 P5.5 目标体验是否覆盖专业背景画像、能力矩阵、项目可信度、岗位短板、source refs、普通聊天边界和可视化验收报告。结论：覆盖完整。
2. 架构实现审计：检查目标架构是否绑定具体代码实体、现有数据表、最小 API 契约、artifact/version/source refs 和禁止职责。结论：覆盖完整。
3. 验收和防虚假审计：检查里程碑、验收门槛、追踪矩阵、drawio 和报告要求是否能防止真实资料、真实 provider、敏感属性和未实现功能被写成已通过。结论：修正历史 P6/P7 “当前目标”残留口径后通过。

本轮修订关闭了以下口径风险：

- `01_STAGE_PRD.md` 中历史 P6+P7 段落不再声称当前有效目标是 P6+P7；
- `02_TARGET_ARCHITECTURE.md` 中 P6+P7 章节明确为已完成自动化候选基线；
- `17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md` 中 P6+P7 主线明确为历史主线，当前主线为 P5.5；
- `06_TRACEABILITY_MATRIX.md` 中 P6+P7 开发准入结论明确为历史基线；
- `20_P5_5_CANDIDATE_PROFILE_PLAN.md` 补充 P5.5-M0 到 M6 详细开发及验收计划。

最终结论：当前文档足以支撑 P5.5 自动化开发，不需要在进入 P5.5-M0 前再交给 ChatGPT 外部审计。若用户希望做外部审计，可使用本审计文件第 7 节列出的文档包。

## 6.1 后续实现闭环记录

2026-06-30 后续实现已完成：

- 已新增 profile 读取/刷新 API、profile aggregator、能力矩阵、项目可信度和岗位短板；
- 已新增 Chatbox Candidate Profile Workbench 和显式“生成画像”入口；
- 已新增 P5.5 M1-M6 阶段审计、eval、中文 HTML 自动化验收报告和截图证据；
- 当前仍未验证真实个人资料、真实 provider、敏感属性分析、SaaS、ASR、会议平台、自动投递或 MCP/CLI。

## 7. 可选 ChatGPT 外部审计包

当前判断为“不必须外部审计”。如需额外审计，建议只提供以下 9 个文件，少于 20 个：

1. `README.md`
2. `TODO.md`
3. `docs/active/00_README.md`
4. `docs/active/01_STAGE_PRD.md`
5. `docs/active/02_TARGET_ARCHITECTURE.md`
6. `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
7. `docs/active/04_ACCEPTANCE_GATES.md`
8. `docs/active/20_P5_5_CANDIDATE_PROFILE_PLAN.md`
9. `docs/active/stage-reviews/P5_5_DOCUMENTATION_DEVELOPMENT_AUDIT.md`
