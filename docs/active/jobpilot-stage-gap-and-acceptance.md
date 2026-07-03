# JobPilot AI P8.1 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。当前图示主线是 **P8.1 Chatbox-first 工作台信息架构修正文档阶段**。

P8-JD Intake 与简历生成体验强化已经完成自动化候选。P8.1 不推翻 P8 的资料准备向导、JD 手动导入中心、多 JD 目标岗位、JD 定制简历、source refs、pending confirmations 和 export preflight；P8.1 只修正这些能力在前端工作台中的主次关系。

当前图示不代表 P8.1 UI 已经实现，也不代表真实 provider、真实个人资料、招聘平台自动接入、自动沟通、自动投递、workspace 删除、不可逆迁移、ASR、会议平台或 SaaS 已经通过。

## 图示页结构

drawio 保持 7 页，不超过 8 页：

1. P8.1 Chatbox-first 修正；
2. 目标体验与当前差距；
3. 当前架构与目标架构；
4. 代码实体与分层交互关系；
5. 开发及验收计划；
6. 里程碑门槛与出门条件；
7. 安全边界证据与复验。

颜色含义：

- 绿色：已实现自动化候选，包括 P8 或更早阶段已经有本地/mock、fake provider、synthetic-style workspace、dry-run 或截图证据的实体；
- 蓝色：P8.1 待修改或待强化的现有 UI 实体；
- 黄色：P8 已实现但 P8.1 需要重新摆放入口和优先级的能力；
- 红色：禁止关系、高风险能力或虚假验收打回项；
- 灰色：后续独立阶段或需要单独授权的复验路径。

## 第 1 页 - P8.1 Chatbox-first 修正

第 1 页锁定 P8.1 的核心体验：

```text
用户指导（左侧，辅助）
→ Chatbox（中央，主路径）
→ 工作台（右侧，产物和确认）
```

左侧只承担资料清单、缺失影响、示例路径和下一步建议；中央承担 Agent 状态机、聊天时间线、输入框和紧贴输入框的工具入口；右侧承担岗位列表、当前目标 JD、CandidateProfile、简历草稿、source refs、pending confirmations 和 export preflight。

当前 P8 风险：

- `p8-workflow-strip` 位于聊天时间线前；
- 资料、JD、岗位和简历生成入口在中央形成较重任务区；
- 用户容易认为必须先填表，而不是先和 Agent 对话。

P8.1 处理原则：

- 保留 P8 能力，但重排入口；
- `MaterialIntakeWizard` 转为左侧指导或轻弹层；
- `JDIntakeCenter` 转为输入框工具或右侧岗位列表；
- `JobTargetList` 转入右侧工作台；
- `ResumeGenerationPlane` 由对话意图或工具触发。

## 第 2 页 - 目标体验与当前差距

第 2 页对比当前 P8 实现、体验差距和 P8.1 目标状态。

当前实现基线：

- 资料准备向导已实现；
- JD 手动导入已实现；
- 多 JD 目标岗位已实现；
- JD 定制简历已实现；
- 问题是入口在中央过重，workflow strip 抢占聊天首屏。

P8.1 目标体验：

```text
打开 Chatbox
→ 直接对话或补资料
→ 粘贴 JD 并保存来源
→ 选择当前目标岗位
→ 生成简历并确认事实
```

不得用以下内容替代验收：

- 保存 `source_url` 不等于招聘平台接入；
- 目标概念图不等于真实实现截图；
- 合成资料不等于真实个人资料路径通过；
- mock/fake provider 不等于真实 provider 质量通过。

## 第 3 页 - 当前架构与目标架构

第 3 页说明 P8.1 是信息架构修正，不是业务层重写。

当前 P8 架构：

```text
React Chatbox
→ Material / JD / Job / Resume UI
→ FastAPI routes
→ Domain Tools
→ SQLite Workspace / Artifact
→ P8 HTML 报告
```

P8.1 目标架构：

```text
Chatbox Experience Shell
→ 左侧 User Guidance
→ 中央 Conversation Plane + Composer Tool Rail
→ 右侧 Workbench
→ 复用 P8 API / Domain / Storage
→ P8.1 多视口验收报告
```

P8.1 复用的接口：

- `POST /api/files/upload`
- `POST /api/job/intake`
- `GET /api/jobs`
- `POST /api/resume/generate`

P8.1 复用的数据实体：

- `document`
- `job`
- `match_report`
- `candidate_profile`
- `resume_version`
- `artifact`
- `artifact_version`

禁止扩展为招聘平台登录、URL 自动抓取、自动沟通、自动投递、真实 provider 默认外呼、真实个人资料默认读取、SaaS、ASR 或会议平台。

## 第 4 页 - 代码实体与分层交互关系

第 4 页是本轮重点修订页。它按五层展示具体代码实体、状态和依赖方向，而不是抽象能力清单。

```text
User Action
→ Chatbox UI Layer
→ API Boundary Layer
→ Domain / Orchestration Layer
→ SQLite Workspace / Artifact Layer
→ Evidence / Acceptance Layer
```

### Chatbox UI Layer

| 实体 | 状态 | 上游 / 下游 | P8.1 职责 |
| --- | --- | --- | --- |
| `DesktopContextPanel` | P8.1 待强化 | 上游读取 workspace 摘要；下游辅助 `Conversation Plane` | 左侧用户指导，只解释资料缺口、缺失影响和下一步，不写业务数据 |
| `Conversation Plane` | P8.1 待修改 | 上游接收用户输入；下游触发工具入口 | 中央首屏主路径，显示 Agent 状态机、聊天时间线和 Composer |
| `p8-workflow-strip` | P8.1 待重排 | 上游来自现有 P8 UI；下游拆给工具入口 | 不再位于 timeline 前，拆为 Composer Tool Rail、弹层、抽屉或左右辅助面板 |
| `MaterialIntakeWizard` | P8 已实现，P8.1 重排入口 | 上游由输入框工具或左侧指导触发；下游调用 upload/ingest | 保留五类资料能力，但不抢占中央聊天首屏 |
| `JDIntakeCenter` | P8 已实现，P8.1 重排入口 | 上游由输入框工具触发；下游调用 `/api/job/intake` | 用户粘贴 JD、保存来源 URL、平台标签和备注 |
| `JobTargetList` | P8 已实现，P8.1 重排入口 | 上游读取 `/api/jobs`；下游影响简历生成目标 | 进入右侧工作台，展示多 JD 和当前目标 |
| `ResumeGenerationPlane` | P8 已实现，P8.1 重排入口 | 上游由对话意图或工具触发；下游调用 `/api/resume/generate` | 生成 JD 定制简历草稿并进入工作台 |
| `Workbench` | P8.1 待强化 | 上游读取 workspace/artifact；下游提供确认和导出入口 | 右侧展示岗位、画像、简历、source refs、待确认项和导出预检 |

### API Boundary Layer

| 实体 | 状态 | P8.1 关系 |
| --- | --- | --- |
| `POST /api/files/upload` | 已实现自动化候选 | P8.1 复用，不改变上传分类语义 |
| `POST /api/job/intake` | 已实现自动化候选 | P8.1 复用，不因 `source_url` 抓取网页 |
| `GET /api/jobs` | 已实现自动化候选 | P8.1 复用，为右侧岗位列表提供数据 |
| `POST /api/resume/generate` | 已实现自动化候选 | P8.1 复用，为右侧简历草稿提供版本 |

### Domain / Orchestration Layer

| 实体 | 状态 | P8.1 关系 |
| --- | --- | --- |
| `services/tools/jobpilot.py` | 已实现自动化候选 | 复用 ingest、parse_jd、match、application_package、export |
| `services/profile/candidate.py` | 已实现自动化候选 | 复用 CandidateProfile、能力矩阵、项目可信度和岗位短板 |
| source refs / pending confirmations / export preflight | 已实现机制 | 防止简历生成编造事实；blocking 项未确认不得正式导出 |

### SQLite Workspace / Artifact Layer

| 实体 | 状态 | P8.1 关系 |
| --- | --- | --- |
| `document` | 已实现自动化候选 | 承载简历、项目、作品、偏好和 JD 等资料 |
| `job` / `match_report` | 已实现自动化候选 | 承载 JD 解析、来源、平台标签、匹配摘要和当前目标 |
| `candidate_profile` | 已实现自动化候选 | 作为简历生成和工作台画像摘要证据 |
| `resume_version` | 已实现自动化候选 | 保存目标 JD 简历版本、状态、source refs 和待确认项 |
| `artifact` / `artifact_version` | 已实现自动化候选 | 复用版本、确认项和导出机制 |

### Evidence / Acceptance Layer

| 实体 | 状态 | P8.1 关系 |
| --- | --- | --- |
| `docs/reports/` | 已实现机制，P8.1 待新增报告 | 生成中文 HTML 验收报告 |
| `docs/reports/evidence/` | 已实现机制，P8.1 待新增截图 | 保存 1200、1440、1920、720、390 多视口真实截图 |
| `docs/active/` / drawio / stage reviews | 当前文档阶段产物 | 防止后续实现偏离 PRD、目标架构和安全边界 |

明确禁止的实体关系：

- Chatbox 直写 SQLite；
- `source_url` 触发网页抓取；
- 打回：保存链接被写成 BOSS/招聘平台已接入；
- 自动登录、绕风控、自动沟通或自动投递；
- 普通聊天静默覆盖 `resume_version`；
- 缺少 source refs 的简历内容被写成事实；
- 真实 provider 或真实个人资料路径被写成已通过。

## 第 5 页 - 开发及验收计划

P8.1 后续自动化开发顺序：

```text
P8.1-M0 开发前启动审计
→ P8.1-M1 Chatbox-first 布局重构
→ P8.1-M2 资料 / JD / 简历入口迁移
→ P8.1-M3 Agent 状态机和工作台职责稳定
→ P8.1-M4 响应式和视觉质量修复
→ P8.1-M5 中文自动化验收报告
```

每个子阶段出门前必须：

- 单独制定开发计划；
- 单独制定验收标准；
- 落盘审计意见；
- 闭环致命或重大规格偏差；
- 完成端到端验收；
- 做 PRD 规格检视。

若出现重大规格偏差、虚假验收风险或高风险能力越界，必须打回计划阶段。

## 第 6 页 - 里程碑门槛与出门条件

文档出门条件：

- PRD、目标架构、里程碑、验收门槛、追踪矩阵、roadmap、drawio 和文本镜像口径一致；
- drawio 不超过 8 页；
- 第 4 页能看清实体关系、状态颜色、上游/下游和本阶段修改职责；
- 不把 P8.1 写成 UI 已实现或已人工验收。

开发出门条件：

- 中央 Chatbox 首屏优先；
- 工具入口紧贴输入框或处于清晰辅助面板；
- 右侧工作台职责稳定；
- 普通聊天不静默写 artifact；
- 左侧用户指导不承载大型编辑表单。

验收出门证据：

```bash
.venv/bin/python -m pytest
npm --prefix apps/chatbox run build
drawio XML parse
P8.1 browser acceptance screenshots: 1200px, 1440px, 1920px, 720px, 390px
P8.1 Chinese HTML acceptance report
```

用户体验出门条件：

- 用户第一眼知道可以直接聊天；
- 用户知道需要补哪些资料、为什么补、缺失会影响什么；
- 用户能粘贴 JD、选择目标岗位、生成简历；
- 用户能看到 source refs、pending confirmations 和 export preflight；
- 多视口下无按钮错位、文字重叠或核心入口不可达。

## 第 7 页 - 安全边界、证据与复验

当前可用证据：

- P8 中文 HTML 自动化验收报告；
- P8.1 前端审查指导页；
- P5.5 / P6 / P7 自动化候选报告；
- pytest、frontend build、drawio parse；
- 多视口真实截图机制。

仍未验证范围：

- 真实 MiniMax、DeepSeek、OpenAI-compatible 或其他 provider 质量；
- 用户真实个人资料路径；
- BOSS、猎聘、拉勾等平台账号接入；
- 自动抓取职位列表；
- 自动沟通或自动投递；
- workspace 删除、cleanup apply、migration apply；
- SaaS、ASR、会议平台、多租户、Billing、MCP/CLI。

后续复验要求：

- 真实 provider 必须用户确认 provider、model、调用次数、预算、数据范围和脱敏报告字段；
- 真实资料必须用户提供明确路径，默认脱敏，不扫描个人目录；
- 招聘平台接入必须使用官方 API、用户授权导出或用户明确打开页面后的合规浏览器辅助读取，并单独立项审计。

虚假验收扫描不得出现以下结论：

- 不得出现：P8.1 已实现；
- 不得出现：Chatbox-first UI 已验收通过；
- 不得出现：招聘平台已接入；
- 不得出现：真实 provider 已通过；
- 不得出现：真实个人资料已通过；
- 不得出现：自动投递已通过。
