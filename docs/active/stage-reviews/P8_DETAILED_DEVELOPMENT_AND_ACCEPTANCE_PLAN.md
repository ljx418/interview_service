# P8-JD Intake 详细开发及验收计划

日期：2026-07-01

状态：文档开发阶段通过并已收口；本文件只定义后续自动化开发和验收计划，不代表代码实现已经开始或完成。

## 1. 目标和边界

P8 要解决三个用户体验断点：

1. 用户不知道需要提供什么资料；
2. 用户没有清晰的 JD 导入和岗位选择路径；
3. 简历生成没有围绕目标 JD、source refs 和待确认项形成可追溯体验。

P8 第一版采用手动 JD 导入路线：

```text
资料准备向导
→ JD 手动导入中心
→ 多 JD 岗位列表和当前目标岗位
→ JD 定制简历
→ 中文 HTML 自动化验收报告
```

P8 第一版不做：

- BOSS、猎聘、拉勾等招聘平台账号登录；
- 平台自动抓取、绕风控、验证码处理、批量岗位采集；
- 自动开聊、自动沟通、自动投递；
- 默认真实 provider 调用；
- 未授权真实个人资料读取；
- SaaS、ASR、会议平台、MCP/CLI。

## 2. 多轮独立文档审计结论

### 第一轮：PRD 覆盖审计

审计对象：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`

结论：通过。

理由：

- PRD 明确了五类资料：简历、项目经历、作品链接、目标 JD、求职偏好；
- PRD 明确了 JD 第一版只支持用户手动粘贴和来源归档；
- PRD 明确了简历生成必须绑定目标 JD、source refs 和 pending confirmations；
- 非目标和高风险边界足以防止把招聘平台接入、真实 provider、真实资料写成本阶段能力。

### 第二轮：目标架构覆盖审计

审计对象：

- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`

结论：通过。

理由：

- drawio 第 2 页已经区分当前已实现基线、P8 需修改实体、P8 待新增能力和后续高风险阶段；
- drawio 第 3 页已经按 Chatbox UI、API Boundary、Domain / Orchestration、SQLite / Artifact、Evidence 五层展示实体；
- 目标架构文档已经列出具体代码实体、当前状态、P8 职责和上下游依赖；
- 禁止实体关系已经明确：Chatbox 不直写 SQLite、`source_url` 不触发抓取、普通聊天不静默覆盖 `resume_version`。

### 第三轮：验收和虚假验收风险审计

审计对象：

- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/stage-reviews/P8_DOCUMENTATION_COVERAGE_REAUDIT.md`

结论：通过；本文件已经补齐子阶段执行颗粒度。

理由：

- 已有文档能说明 P8 总目标、总门槛和高风险边界；
- 本文件明确了每阶段改哪些实体、产出什么证据、如何打回；
- 当前文档可以完整支撑 P8-M0 启动审计，以及 P8-M1 到 P8-M5 的自动化开发和出门验收。

### 第四轮：ChatGPT 外部意见核查

审计对象：

- 用户提供的 ChatGPT 外部审计意见；
- `docs/active/stage-reviews/P8_DOCUMENTATION_COVERAGE_REAUDIT.md`；
- 本文件第 3 至第 5 节。

结论：通过。

采纳意见：

- P8 文档已经可以完整支撑本阶段后续自动化开发；
- 不建议继续扩写主设计文档，继续扩写会稀释执行重点；
- 下一步应进入 P8-M0 开发前启动审计；
- P8-M0 之后再按 P8-M1 到 P8-M5 逐阶段开发、验收和打回。

保留限定：

- 这不是 P8 代码实现通过；
- 这不是招聘平台自动接入通过；
- 这不是真实 provider 质量通过；
- 这不是真实个人资料路径通过；
- 这不是自动投递、SaaS、ASR 或会议平台能力通过。

## 3. 子阶段开发计划

### P8-M0：开发前启动审计

目标：进入代码开发前确认本轮范围、数据、接口、截图和报告口径。

交付物：

- P8-M0 启动审计记录；
- 本阶段测试清单；
- 本阶段截图路径和报告路径；
- 不进入真实 provider、不读取真实资料、不接招聘平台账号的执行确认。

准入条件：

- drawio XML 可解析且页数不超过 8；
- `01_STAGE_PRD.md`、`02_TARGET_ARCHITECTURE.md`、`04_ACCEPTANCE_GATES.md` 口径一致；
- 没有把平台接入、真实 provider 或真实个人资料写成本阶段已通过。

出门条件：

- 明确 P8-M1 到 P8-M5 顺序；
- 明确每个子阶段完成后必须做 PRD 规格检视和端到端验收；
- 若发现规格偏差，先回到文档修订，不进入代码开发。

### P8-M1：资料准备向导

用户目标：用户打开 Chatbox 后知道需要提供什么资料，以及缺少资料会影响什么。

开发实体：

- `apps/chatbox/src/main.tsx`
- `apps/chatbox/src/styles.css`
- `services/api/schemas.py`
- `document.kind`

功能范围：

- 将资料输入拆成简历、项目经历、作品链接、目标 JD、求职偏好五类；
- 每类展示用途、示例、可接受输入、可跳过条件、缺失影响和完成状态；
- 资料入口应位于首屏或文字输入框上方，不再只有孤立“上传资料”按钮；
- 保持上传/粘贴资料只进入本地 workspace，不扫描用户目录。

验收证据：

- 后端或 schema eval：资料 `kind` 分类不破坏旧上传；
- 前端 build；
- 1200px、720px、390px 截图；
- PRD 检视：用户不读文档也能理解需要提供什么资料。

打回条件：

- UI 仍只展示“上传资料”而没有资料类型说明；
- 缺少项目经历、作品链接或目标 JD 的影响没有展示；
- 页面要求用户理解 artifact、workspace、表结构等内部概念。

### P8-M2：JD 手动导入中心

用户目标：用户可以从 BOSS、猎聘、拉勾、LinkedIn、公司官网等来源手动粘贴 JD，并保存来源信息。

开发实体：

- `apps/chatbox/src/main.tsx`
- `apps/chatbox/src/styles.css`
- `services/api/main.py`
- `services/api/schemas.py`
- `services/tools/jobpilot.py`
- `job` / `match_report`

功能范围：

- 新增或扩展 `POST /api/job/intake`；
- 支持 `jd_text`、`source_url`、`platform`、`import_method`、`user_notes`；
- `source_url` 只保存，不触发任何网络抓取；
- JD 缺少公司、地点、薪资、技术栈时进入待确认项，不自动补全为事实；
- Chatbox 中默认入口文案为“粘贴目标 JD”。

验收证据：

- API eval：传入 URL 不触发抓取，只保存来源；
- JD 解析 eval：可生成 job 和 match suggestion；
- 前端截图：JD 导入弹窗/区域、平台标签、来源 URL、备注、解析状态；
- 安全扫描：报告和日志不出现“平台已接入”误导结论。

打回条件：

- 保存 URL 后发生网络读取；
- 文档或报告写成 BOSS/招聘平台已接入；
- UI 暗示系统会自动抓取岗位、登录平台或自动投递。

### P8-M3：多 JD 列表和当前目标岗位

用户目标：用户能管理多个 JD，比较匹配摘要和资料缺口，并选择当前目标岗位。

开发实体：

- `apps/chatbox/src/main.tsx`
- `apps/chatbox/src/styles.css`
- `services/api/main.py`
- `services/api/schemas.py`
- `job` / `match_report` / artifact refs

功能范围：

- 新增或扩展 `GET /api/jobs`；
- 展示岗位标题、公司、平台、解析状态、must-have、技术栈、匹配摘要、资料缺口；
- 支持选择当前目标岗位；
- 当前目标岗位必须成为后续简历生成的默认 `job_id`；
- 多 JD 列表不得暴露完整敏感资料。

验收证据：

- API eval：返回多 JD 列表和当前目标状态；
- 前端截图：多个 JD、当前目标标识、缺口提示；
- PRD 检视：用户能清楚知道系统正在围绕哪个 JD 生成材料。

打回条件：

- 无法区分当前目标岗位；
- 多 JD 列表只展示裸 JSON；
- 缺失公司、地点或薪资被自动补成事实。

### P8-M4：JD 定制简历

用户目标：用户能通过 ChatBox 对话或显式按钮生成围绕目标 JD 的简历草稿，并知道哪些内容来自资料、哪些还要确认。

开发实体：

- `apps/chatbox/src/main.tsx`
- `services/api/main.py`
- `services/api/schemas.py`
- `services/tools/jobpilot.py`
- `services/profile/candidate.py`
- `resume_version`
- `application_package` / `artifact` / `artifact_version`

功能范围：

- 新增或扩展 `POST /api/resume/generate`；
- 输入至少包含 `workspace_id`、`job_id`、`mode`、`language`、`style`；
- 生成 Markdown-first `resume_version`；
- 简历草稿展示岗位关键词覆盖、经历取舍说明、source refs、pending confirmations；
- blocking 待确认项未处理时不得正式导出；
- 普通聊天不能静默覆盖已有 `resume_version`。

验收证据：

- 后端 eval：生成简历必须绑定 `job_id` 或明确通用模式；
- source refs eval：每个核心经历或技能亮点有来源或待确认项；
- export preflight eval：blocking 未确认时阻止正式导出；
- 前端截图：简历草稿、source refs、待确认项、导出前提示；
- 对话场景截图：用户说“基于这个 JD 生成一版简历”能进入受控生成路径。

打回条件：

- 简历编造学历、年限、公司、量化结果或本人贡献；
- 缺少 source refs；
- 普通闲聊覆盖已有简历版本；
- blocking 项未确认仍允许正式导出。

### P8-M5：可视化验收报告和阶段收口

用户目标：人类审查者能通过中文 HTML 报告快速判断 P8 实现了什么、没有实现什么、证据是否真实。

开发实体：

- `docs/reports/`
- `docs/reports/evidence/`
- browser screenshot scripts
- report eval
- stage review

功能范围：

- 生成中文 HTML 自动化验收报告；
- 报告包含目标架构、当前架构实现、用户路径、截图证据、测试结果、PRD 检视和未验证范围；
- 截图至少覆盖 1200px、720px、390px；
- 报告必须明确 BOSS/招聘平台自动接入、自动投递、真实 provider、真实个人资料均未验收。

验收证据：

- `.venv/bin/python -m pytest`；
- `npm --prefix apps/chatbox run build`；
- P8 eval；
- drawio XML parse；
- 多视口截图；
- HTML 报告 eval；
- PRD 规格检视。

打回条件：

- 报告截图缺失、不可见或与实际界面不对应；
- 报告把文档计划写成功能实现；
- 报告把手动粘贴 JD 写成平台接入；
- 报告把 mock/fake provider 或合成资料写成真实 provider/真实资料通过。

## 4. 端到端验收路径

P8 完成后至少需要覆盖以下路径：

| 路径 | 用户场景 | 必须证明 |
| --- | --- | --- |
| E2E-1 | 新用户打开 Chatbox，尚未提供资料 | 能看到五类资料向导和缺失影响 |
| E2E-2 | 用户补充简历、项目、作品、偏好 | 每类资料有完成状态和下一步 |
| E2E-3 | 用户粘贴目标 JD 并保存来源 URL | URL 只归档，不抓取；平台标签可见 |
| E2E-4 | 用户导入多个 JD | 列表可读，能选择当前目标岗位 |
| E2E-5 | 用户基于当前目标 JD 生成简历 | 生成 `resume_version`，包含 source refs 和 pending confirmations |
| E2E-6 | 简历存在 blocking 待确认项 | 正式导出被 preflight 阻止，并给出恢复路径 |
| E2E-7 | 用户确认 blocking 项后导出 | Markdown/DOCX 或既有导出路径可用 |
| E2E-8 | 移动端或窄屏使用 | 390px/720px 下资料入口、JD 列表、简历草稿不重叠 |

## 5. 测试与证据矩阵

| 能力 | 建议测试 | 报告证据 |
| --- | --- | --- |
| 资料分类 | P8 material intake eval | 五类资料截图、缺失影响截图 |
| JD 导入 | P8 job intake eval | JD 导入表单、URL 不抓取断言 |
| 岗位列表 | P8 job list eval | 多 JD 列表和当前目标截图 |
| 定制简历 | P8 resume generation eval | 简历草稿、source refs、pending confirmations 截图 |
| 导出前确认 | Export preflight eval | blocking 阻止导出和确认后导出截图 |
| 安全边界 | false green scan / privacy scan | 未验证范围、无平台接入误写、无 API Key |
| 响应式 | browser screenshots | 1200px、720px、390px |
| 回归 | `.venv/bin/python -m pytest`、frontend build | 测试摘要进入 HTML 报告 |

## 6. 最终文档支撑结论

在补齐本文件并采纳 ChatGPT 外部审计意见后，P8 文档已能完整支撑后续自动化开发和出门验收。当前不存在必须继续修订主设计文档才能进入 P8-M0 启动审计的重大缺口。

剩余风险不是文档不足，而是后续实现阶段必须严格执行：

- 每个子阶段先落盘启动审计；
- 每个子阶段完成后做 PRD 规格检视；
- 验收不过则回到计划阶段修订；
- 任何平台自动接入、真实 provider、真实资料、自动投递、SaaS、ASR、会议平台都必须单独授权。

## 7. ChatGPT 外部审计结论和审计包

本轮已经收到 ChatGPT 外部审计意见。外部意见同意当前文档可以进入 P8-M0 开发前启动审计，并明确不建议继续扩写主设计文档。后续不强制需要再次交给 ChatGPT 审计；若仍需要外部复核，建议只发送以下文档，数量小于 20：

1. `README.md`
2. `TODO.md`
3. `docs/active/00_README.md`
4. `docs/active/01_STAGE_PRD.md`
5. `docs/active/02_TARGET_ARCHITECTURE.md`
6. `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
7. `docs/active/04_ACCEPTANCE_GATES.md`
8. `docs/active/06_TRACEABILITY_MATRIX.md`
9. `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
10. `docs/active/21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`
11. `docs/active/jobpilot-stage-gap-and-acceptance.md`
12. `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
13. `docs/active/stage-reviews/P8_JD_INTAKE_DOCUMENTATION_DEVELOPMENT_AUDIT.md`
14. `docs/active/stage-reviews/P8_DOCUMENTATION_COVERAGE_REAUDIT.md`
15. `docs/active/stage-reviews/P8_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`

外部审计重点问题：

- P8 是否足以解决“用户不知道提供什么资料”和“围绕目标 JD 生成简历”的体验问题；
- P8 是否错误承诺了招聘平台接入、自动投递、真实 provider 或真实个人资料；
- 第 2/3 页 drawio 是否足以让开发者理解当前架构、目标架构和代码实体关系；
- P8-M1 到 P8-M5 的验收证据是否能防止虚假通过。
