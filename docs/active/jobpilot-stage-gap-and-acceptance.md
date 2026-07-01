# JobPilot AI P8-JD Intake 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。当前图示主线是 P8-JD Intake 与简历生成体验强化文档阶段。P4/P5/P5.5/P6/P7 已实现能力作为自动化候选基线保留；P6-REAL / P7-post 审计已完成但真实 provider 质量和真实个人资料路径仍未执行。

任何真实 API Key、真实个人资料、真实外部 provider 调用、招聘平台登录、绕风控抓取、自动沟通、自动投递、workspace 删除、不可逆迁移、ASR/会议平台/SaaS 操作都必须先获得用户确认。当前图示不代表这些高风险路径已经执行或通过。

## 图示页结构

drawio 保持 6 页，不超过 8 页：

1. 目标体验与当前差距；
2. 当前架构与目标架构；
3. 代码实体与分层交互关系；
4. 开发及验收计划；
5. 里程碑门槛与出门条件；
6. 安全边界证据与复验。

颜色含义：

- 绿色：已实现自动化候选，包括 P4/P5/P5.5/P6/P7 本地、mock、fake provider、synthetic-style workspace 或 dry-run 证据；
- 蓝色：P8 需要修改或扩展的现有实体；
- 黄色：P8 计划新增能力，包括资料准备向导、JD 导入中心、岗位列表、JD 定制简历；
- 红色：高风险需用户确认或虚假验收打回项；
- 灰色：后续独立阶段，包括合规招聘平台接入、自动投递、SaaS、ASR、会议平台、MCP/CLI。

## 第 1 页 - 目标体验与当前差距

目标体验主链路：

```text
User
→ 打开 Chatbox
→ 看到资料准备向导，而不是孤立上传按钮
→ 按简历、项目经历、作品链接、目标 JD、求职偏好五类补充资料
→ 从 BOSS / 猎聘 / 拉勾 / LinkedIn / 公司官网等来源手动粘贴 JD
→ 保存来源 URL、平台标签和用户备注
→ 在岗位列表中选择当前目标 JD
→ 生成 JD 定制简历草稿
→ 查看 source refs、pending confirmations 和导出 preflight
```

当前差距：

- 已有资料上传、JD 解析、匹配报告、申请包和候选人画像，但入口仍让用户不知道该提供什么资料；
- 已有 `job.source_url`，但没有完整 JD 导入中心和岗位列表；
- 已有 `resume_version` 和申请包导出链路，但缺少以目标 JD 为中心的简历生成体验；
- BOSS/招聘平台主动接入存在合规、账号、风控和隐私风险，不进入第一版默认能力。

## 第 2 页 - 当前架构与目标架构

第 2 页改为“当前已实现自动化候选 → 后续高风险”的差异图，而不是抽象能力清单。

当前已实现自动化候选基线：

```text
React Chatbox
→ FastAPI Agent Service
→ Document upload / ingest
→ JD parse / match report
→ Candidate Profile Aggregator
→ Application Package / Export Guard
→ Artifact Versioning
→ SQLite Workspace
→ P5.5 / P6 / P7 Reports
```

P8 需要修改的现有实体：

```text
Chatbox Experience Shell
→ apps/chatbox/src/main.tsx
→ apps/chatbox/src/styles.css
→ 将孤立上传按钮改为资料准备入口
→ 将 JD / 简历任务移动到输入框上方和 Workbench 可见区域

FastAPI API Boundary
→ services/api/main.py
→ services/api/schemas.py
→ 扩展资料 kind、JD intake、jobs list、resume generate request/response
→ 保持 Chatbox 不直写 SQLite
```

P8 已实现自动化候选的用户可见能力：

```text
Material Intake Wizard
→ 简历 / 项目经历 / 作品链接 / 目标 JD / 求职偏好
→ 用途 / 示例 / 可跳过条件 / 缺失影响 / 完成状态

JD Intake Center
→ 用户粘贴 JD
→ source_url / platform / user_notes 归档
→ 不抓取 URL

Job Target List
→ 多 JD 列表
→ 解析状态 / 匹配摘要 / 资料缺口
→ 当前目标岗位选择

Resume Generation Plane
→ selected job_id
→ JD-tailored resume_version
→ source refs / pending confirmations
→ export preflight
```

架构关系：

- Chatbox 负责资料向导、JD 导入中心、岗位列表和简历生成入口；
- FastAPI 负责资料上传分类、JD intake、岗位列表和简历生成边界；
- Domain Tools 继续负责 document、career_fact、skill_evidence、job、match_report、resume_version 和 application_package；
- Evidence Layer 负责中文 HTML 报告、截图、PRD 检视和虚假验收扫描。

禁止或后续独立阶段：

- URL 自动抓取；
- BOSS / 猎聘 / 拉勾等平台登录或绕风控；
- 自动沟通或自动投递；
- 真实 provider 默认调用；
- 扫描未授权个人目录；
- 合规招聘平台 API、浏览器辅助读取当前页、SaaS、ASR、会议平台、MCP/CLI 均需要后续独立阶段。

## 第 3 页 - 代码实体与分层交互关系

第 3 页按五层显示具体代码实体、当前状态和依赖方向：

```text
1 Chatbox UI Layer
→ 2 API Boundary Layer
→ 3 Domain / Orchestration Layer
→ 4 SQLite Workspace / Artifact Layer
→ 5 Evidence / Acceptance Layer
```

### 1. Chatbox UI Layer

| 实体 | 状态 | P8 职责 |
| --- | --- | --- |
| `apps/chatbox/src/main.tsx` | 现有实体需修改 | 承载资料向导、JD 导入中心、岗位列表、当前目标岗位、JD 定制简历入口 |
| `apps/chatbox/src/styles.css` | 现有实体需修改 | 五类资料卡、JD 列表、响应式布局、状态标签、按钮对齐 |
| `MaterialIntakeWizard` / `JDIntakeCenter` / `JobTargetList` / `ResumeGenerationPlane` | 已实现自动化候选 UI 平面 | 作为用户可见入口，不直接写数据库 |
| Conversation Plane / Workbench / Artifact Review / Export actions | 已实现自动化候选 | 复用现有会话、产物审查和导出体验 |

### 2. API Boundary Layer

| 实体 | 状态 | P8 职责 |
| --- | --- | --- |
| `services/api/main.py` | 现有实体需修改 | 扩展 `job intake`、`jobs list`、`resume generate` 路由 |
| `services/api/schemas.py` | 现有实体需修改 | 增加或扩展 `MaterialKind`、`JobIntakeRequest`、`JobListItem`、`ResumeGenerateRequest` |
| `POST /api/job/intake` | 已实现自动化候选接口契约 | 保存用户粘贴 JD、来源 URL、平台标签和备注，不抓取 URL |
| `GET /api/jobs` | 已实现自动化候选接口契约 | 返回岗位列表、解析状态、匹配摘要和当前目标状态 |
| `POST /api/resume/generate` | 已实现自动化候选接口契约 | 基于 `job_id` 生成 JD 定制简历版本 |

### 3. Domain / Orchestration Layer

| 实体 | 状态 | P8 职责 |
| --- | --- | --- |
| `services/tools/jobpilot.py` | 现有实体需修改 | 复用 ingest、parse_jd、match、application_package、export；扩展 JD 来源保存和目标 JD 简历生成 |
| `services/profile/candidate.py` | 已实现自动化候选 | 作为简历生成证据层，提供 CandidateProfile、能力矩阵、项目可信度、岗位短板 |
| source refs / pending confirmations / export preflight | 已实现机制，P8 需强制使用 | 防止简历生成编造事实，blocking 项未确认不得正式导出 |

### 4. SQLite Workspace / Artifact Layer

| 实体 | 状态 | P8 职责 |
| --- | --- | --- |
| `document` | 现有实体需修改 | 扩展或规范 `kind=resume|project|portfolio|notes|jd` |
| `job` / `match_report` | 现有实体需修改 | 承载 JD 解析、`source_url`、`platform`、匹配摘要和当前目标岗位 |
| `resume_version` | 现有实体需修改 | 保存目标 JD 简历版本、生成状态和导出前状态 |
| `application_package` / `artifact` / `artifact_version` | 已实现自动化候选 | 复用版本、source refs、确认项和导出机制 |

### 5. Evidence / Acceptance Layer

| 实体 | 状态 | P8 职责 |
| --- | --- | --- |
| `docs/reports/` / `docs/reports/evidence/` | 已实现自动化候选验收产物 | 生成中文 HTML 报告、1200px/720px/390px 截图、PRD 检视和未验证范围 |
| `docs/active/` / drawio / stage reviews | 已完成文档基线 | 防止实现阶段偏离 P8 架构和安全边界 |

### 明确禁止的实体关系

- `source_url` 触发自动网页抓取；
- 保存链接被写成 BOSS/招聘平台已接入；
- 自动登录、绕反爬、自动沟通、自动投递；
- 简历生成编造学历、工作年限、项目贡献或量化结果；
- 普通聊天静默覆盖 `resume_version`；
- 真实 provider 或真实个人资料路径被写成已通过。

## 第 4 页 - 开发及验收计划

当前文档阶段执行顺序：

```text
P8-DOC-M0 文档口径和产品边界锁定
→ P8-DOC-M1 资料准备向导规格
→ P8-DOC-M2 JD 导入中心和平台合规边界
→ P8-DOC-M3 JD 定制简历与 source refs / 待确认项
→ P8-DOC-M4 drawio / 验收门槛 / 审计收口
```

后续代码阶段建议：

```text
P8-M1 Material Intake Wizard
→ P8-M2 JD Intake Center
→ P8-M3 Job Target List
→ P8-M4 JD-tailored Resume Generation
→ P8-M5 Visual Acceptance Report
```

每个代码子阶段必须先有启动审计、验收标准和 PRD 检视，不得直接进入平台自动化。

## 第 5 页 - 里程碑门槛与出门条件

当前文档阶段出门条件：

1. 文档状态口径一致：P8 是文档阶段，不是代码实现阶段；
2. 资料准备向导完整：五类资料、示例、用途、缺失影响和完成状态齐全；
3. JD 导入中心边界完整：用户粘贴 JD、保存 URL、平台标签、岗位列表，URL 不触发抓取；
4. JD 定制简历完整：绑定目标 `job_id`，包含 source refs、pending confirmations 和导出 preflight；
5. drawio 不超过 8 页，图中条目是具体 UI 平面、路由、数据表、工具、报告或验收证据；
6. 审计记录明确本轮只做文档开发，未进入业务代码实现。

后续 P8 执行出门体验：

```text
用户知道该提供什么资料
→ 用户能粘贴并管理多个 JD
→ 用户能选择当前目标岗位
→ 用户能生成可追溯 JD 定制简历
→ 缺证据项可见且阻止正式导出
```

## 第 6 页 - 安全边界证据与复验

当前证据包：

- P5.5 中文 HTML 自动化验收报告；
- P6/P7 本地 Beta 自动化候选报告；
- P6-REAL / P7-post 阶段审计报告；
- 桌面、宽屏、移动端真实界面截图；
- pytest、frontend build、drawio XML parse；
- PRD 规格检视、隐私审计和虚假验收风险清单。

需要明确保留的未验证范围：

- BOSS/猎聘/拉勾等招聘平台账号接入；
- 自动抓取职位列表；
- 自动沟通或自动投递；
- 真实 MiniMax、DeepSeek、OpenAI-compatible 或其他 provider 质量；
- 用户真实个人资料路径；
- workspace 删除、cleanup apply、migration apply；
- SaaS、ASR、会议平台、多租户、Billing、MCP/CLI。

高风险边界：

- 招聘平台接入必须单独合规审计；
- 真实 provider 必须 opt-in；
- 真实个人资料必须用户授权；
- API Key 不得进入仓库、报告、日志或截图；
- 文档通过不等于实现通过，drawio 方向认可不等于功能验收通过。
