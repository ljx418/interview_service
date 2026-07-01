# P8-JD Intake 文档覆盖度复审

日期：2026-07-01

状态：通过；P8 文档开发已可收口，下一步进入 P8-M0 开发前启动审计；不代表 P8 代码实现、招聘平台接入、真实 provider 或真实个人资料验收通过。

## 1. 复审结论

当前 P8-JD Intake 与简历生成体验强化文档已经可以完整支撑后续自动化开发准备。文档对目标体验、目标架构、当前架构差异、具体代码实体、开发顺序、验收门槛、出门条件和高风险边界均有明确描述。补充的 `P8_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` 已将 P8-M1 到 P8-M5 的执行颗粒度细化到开发实体、验收证据、端到端路径和打回条件。ChatGPT 外部意见已复核并同意该结论：不建议继续扩写主设计文档，下一步应进入 P8-M0 开发前启动审计。

结论：

- 可以进入 P8-M0 开发前启动审计；
- 不需要改变为 BOSS/招聘平台自动接入路线；
- 不需要把真实 provider、真实个人资料、自动投递、ASR、会议平台或 SaaS 纳入 P8 当前阶段；
- 当前文档通过不等于功能实现通过，P8-M1 到 P8-M5 仍必须逐项开发、验收和打回。

## 2. 覆盖矩阵

| P8 目标 | 支撑文档 | 覆盖结论 | 备注 |
| --- | --- | --- | --- |
| 用户知道需要提供什么资料 | `01_STAGE_PRD.md`、`21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`、`04_ACCEPTANCE_GATES.md`、drawio 第 1/4/5 页 | 完整 | 已拆成简历、项目经历、作品链接、目标 JD、求职偏好五类，并定义用途、示例和缺失影响 |
| JD 手动导入中心 | `02_TARGET_ARCHITECTURE.md`、`21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`、drawio 第 2/3 页 | 完整 | 只保存 `jd_text`、`source_url`、`platform`、`user_notes`，不抓取 URL |
| 岗位列表和当前目标岗位 | `03_MILESTONES_AND_DELIVERY_PLAN.md`、`06_TRACEABILITY_MATRIX.md`、drawio 第 3/4 页 | 完整 | 已要求多 JD 列表、解析状态、匹配摘要和当前目标选择 |
| JD 定制简历 | `21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`、`04_ACCEPTANCE_GATES.md`、drawio 第 2/3/5 页 | 完整 | 已绑定 `resume_version`、source refs、pending confirmations 和导出 preflight |
| 招聘平台合规边界 | `01_STAGE_PRD.md`、`04_ACCEPTANCE_GATES.md`、`17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`、drawio 第 6 页 | 完整 | 明确 BOSS/猎聘/拉勾等只支持用户手动粘贴 JD，不声明自动接入 |
| 自动化验收与出门条件 | `03_MILESTONES_AND_DELIVERY_PLAN.md`、`04_ACCEPTANCE_GATES.md`、`06_TRACEABILITY_MATRIX.md`、`stage-reviews/P8_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` | 完整 | 已要求 eval、前端 build、截图、中文 HTML 报告、PRD 规格检视、端到端路径和未验证范围说明 |

## 3. 目标达成评估

若后续 P8-M1 到 P8-M5 按当前文档实现，预期可以达成：

- 用户不再面对孤立的“上传资料”按钮，而是通过资料准备向导理解需要提供什么；
- 用户可以把 BOSS、猎聘、拉勾、LinkedIn 或公司官网中的 JD 手动粘贴到本地系统；
- 系统可以保存来源链接和平台标签，但不会自动抓取、登录或绕过平台风控；
- 用户可以管理多个 JD，并选择当前目标岗位；
- 系统可以围绕目标 JD 生成可追溯的简历草稿；
- 简历草稿能暴露 source refs、pending confirmations 和导出前阻塞项；
- 中文 HTML 验收报告可以让人工审查者快速判断实现范围、截图证据和未验证范围。

当前文档不能也不应承诺：

- 主动登录 BOSS、猎聘、拉勾或其他招聘平台；
- 自动抓取岗位列表、自动沟通或自动投递；
- 真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 默认质量通过；
- 真实个人资料路径通过；
- SaaS、多租户、Billing、ASR、会议平台、MCP/CLI 完成。

## 4. 风险评估

当前未发现会阻止 P8 自动化开发启动的致命或重大规格风险。剩余风险已被文档约束到可验收范围：

| 风险 | 等级 | 当前消减方式 | 是否需要用户选择路线 |
| --- | --- | --- | --- |
| 招聘平台接入被误解为已实现 | 中 | 文档统一写为“手动粘贴 JD”，并把登录、抓取、自动沟通、自动投递列入非目标和打回条件 | 否 |
| 简历生成编造事实 | 中 | 要求 source refs、pending confirmations、export preflight 和缺证据阻塞 | 否 |
| `source_url` 被实现为自动抓取 | 中 | 验收门槛明确 URL 只归档，不触发网页读取 | 否 |
| P8 与 P6/P7/P5-REAL 口径混淆 | 中 | README/TODO/active docs 已把 P8 写为文档阶段，把真实 provider 和真实资料留在单独授权路径 | 否 |
| UI 实现难度导致体验回退 | 中 | drawio 和计划已要求资料向导、输入框上方入口、岗位列表、多视口截图和中文报告 | 否 |

不建议的替代路线：

| 路线 | 优点 | 缺点 | 当前建议 |
| --- | --- | --- | --- |
| 直接接入 BOSS/猎聘等平台 | 用户少复制粘贴，体验更自动化 | 账号、验证码、平台规则、隐私、风控和虚假验收风险高 | 不进入 P8，后续单独合规阶段 |
| 浏览器辅助读取当前页 | 可减少用户粘贴成本 | 仍涉及页面权限、隐私、选择器脆弱和报告边界 | 仅可作为后续高风险确认路线 |
| 当前 P8 手动 JD 导入 | 合规、安全、可验收，能先解决资料和 JD 输入体验 | 自动化程度较低 | 采用 |

## 5. 开发准入与验收闭环

进入任何 P8 代码开发前，必须先为对应子阶段落盘启动审计和验收计划。建议顺序保持：

1. P8-M1：资料准备向导；
2. P8-M2：JD 手动导入中心；
3. P8-M3：多 JD 列表和当前目标岗位；
4. P8-M4：JD 定制简历；
5. P8-M5：中文可视化验收报告。

每个子阶段出门前至少需要：

- PRD 规格检视；
- 后端/API 或 eval 证据；
- 前端 build；
- 真实界面截图，至少覆盖 1200px、720px、390px；
- 中文 HTML 验收报告或阶段审计；
- 明确未验证范围，不能把平台接入、真实 provider 或真实资料写成通过。

## 6. 复审结论

当前文档已经足以支撑 P8-JD Intake 与简历生成体验强化的后续自动化开发和出门验收准备。未发现需要继续扩大文档开发范围的缺口，也未发现必须让用户选择替代技术路线的高风险阻塞点。

下一步应进入 P8-M0 开发前启动审计；在 P8-M0 完成前不得直接进入 P8-M1 代码实现。当前不建议继续扩写主设计文档，也不强制需要额外 ChatGPT 外部审计。若后续仍要外部审计，可使用 `P8_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` 第 7 节列出的 15 个文档路径。
