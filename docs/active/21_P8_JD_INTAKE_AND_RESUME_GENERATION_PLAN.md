# P8-JD Intake 与简历生成体验强化计划

状态：自动化候选已完成；本地/mock + examples / 受控真实感数据路径已通过专项 eval 和中文 HTML 截图报告。仍不代表招聘平台自动接入、真实 provider、真实个人资料或自动投递通过。

## 1. 问题定义

当前 Chatbox 已能导入资料、解析 JD、生成申请包和候选人画像，但真实用户仍会卡在入口处：

```text
用户不知道该上传什么
→ 不知道简历、项目、作品、求职偏好和 JD 哪些是必须资料
→ 不知道缺少某类资料会影响哪些结果
→ 没有清晰的 JD 获取和导入路径
→ 简历生成更像工具产物，不像围绕目标岗位的求职流程
```

P8-JD Intake 要解决的是“资料准备和目标岗位输入”的体验问题，不是招聘平台自动化问题。第一版必须把用户从“上传资料”引导到“准备一份可用于生成定制简历和申请材料的资料包”。

## 2. 目标体验

```text
用户打开本地 Chatbox
→ 看到资料准备向导，而不是单个上传按钮
→ 按简历、项目经历、作品链接、目标 JD、求职偏好五类补充资料
→ 每类资料都看到示例、用途、可跳过条件和缺失影响
→ 用户从 BOSS / 猎聘 / 拉勾 / LinkedIn / 公司官网等平台手动粘贴 JD
→ 系统保存 JD 文本、来源链接、平台来源和用户备注
→ 用户可以在岗位列表中比较多个 JD 的匹配度和资料缺口
→ 选择一个目标 JD 后生成 JD 定制简历草稿
→ 简历草稿显示 source refs、岗位关键词覆盖、待确认项和导出入口
```

## 3. 本阶段必须产出的用户结果

- 资料准备向导：简历、项目经历、作品链接、目标 JD、求职偏好五类资料的说明、示例、缺失影响和完成状态；
- JD 导入中心：粘贴 JD、保存来源 URL、平台来源、用户备注、解析状态和岗位列表；
- JD 对比与选择：多个 JD 的岗位标题、公司、技术栈、must-have、匹配状态和推荐下一步；
- JD 定制简历：基于目标 JD 的 Markdown 简历草稿、岗位关键词覆盖、经历取舍说明、source refs 和待确认项；
- 验收报告：中文 HTML 报告展示资料向导、JD 导入、岗位列表、简历生成路径和未验证范围。

## 4. 非目标和高风险边界

P8-JD Intake 第一版不做：

- BOSS 直聘、猎聘、拉勾等平台登录；
- 绕过平台风控、反爬、验证码或账号权限；
- 平台列表抓取、批量岗位采集或隐蔽浏览器自动化；
- 自动开聊、自动沟通、自动投递；
- 默认调用真实 MiniMax、DeepSeek 或 OpenAI-compatible provider；
- 未授权读取真实个人目录、聊天软件目录、下载目录或浏览器缓存；
- SaaS、多租户、Billing、ASR、会议平台或 MCP/CLI。

如果后续要接入 BOSS 或其他招聘平台，只能单独立项为合规平台接入阶段，并满足以下前置条件：

- 用户明确授权平台、账号、读取范围和操作范围；
- 平台有官方 API、用户导出能力或明确允许的页面读取方式；
- 不保存平台账号密码；
- 不执行自动沟通或自动投递；
- 报告明确区分“用户粘贴 JD”“浏览器辅助读取当前页”“官方 API 接入”。

## 5. 目标架构草案

```text
Chatbox Experience Shell
→ Material Intake Wizard
  → Resume input
  → Project experience input
  → Portfolio / repo links
  → Target JD input
  → Job-search preference input
→ JD Intake Center
  → paste JD
  → source_url / platform / user_notes
  → job parse
  → job list and status
→ Resume Generation Plane
  → select target job
  → generate resume_version
  → source refs / pending confirmations
  → export preflight
→ Existing Domain Tools
  → document / career_fact / skill_evidence
  → job / match_report
  → resume_version / application_package
  → artifact / artifact_version
```

第一版应优先复用现有能力：

- `document.kind` 承载 `resume`、`project`、`portfolio`、`notes`、`jd`；
- `job.source_url` 保存 JD 来源链接；
- `resume_version` 保存 JD 定制简历；
- `application_package` 继续承载申请包和导出；
- `artifact` / `artifact_version` 继续承载 source refs、确认项和版本。

## 6. 最小接口草案

这些接口是后续开发建议，不代表当前文档阶段已实现。

| 能力 | 建议接口 | 输入 | 输出 | 约束 |
| --- | --- | --- | --- | --- |
| 资料上传分类 | 扩展 `POST /api/files/upload` | `workspace_id`, `file`, `kind` | document artifact | 兼容旧 `upload`，不读取 workspace 外路径 |
| JD 导入 | `POST /api/job/intake` | `workspace_id`, `jd_text`, `source_url?`, `platform?`, `import_method`, `user_notes?` | parsed job, match suggestion | 不抓取 URL，只保存来源 |
| 岗位列表 | `GET /api/jobs` | `workspace_id` | job list, parse status, match summary | 不返回完整敏感资料 |
| JD 定制简历 | `POST /api/resume/generate` | `workspace_id`, `job_id?`, `mode`, `language`, `style` | resume_version, source refs, pending confirmations | 不编造未证实经历 |

## 7. UX 规格

### 资料准备向导

资料向导必须把单个“上传资料”拆为五个可理解入口：

| 资料类型 | 用户看到的说明 | 可接受输入 | 缺失影响 |
| --- | --- | --- | --- |
| 简历 | 用来提取教育、经历、技能和基础履历线索 | Markdown、txt、docx 文本导出、粘贴文本 | 无法生成完整基础简历 |
| 项目经历 | 用来证明项目贡献、技术难点和可复述故事 | README、项目总结、作品说明、仓库链接备注 | 项目可信度和 STAR 故事会变弱 |
| 作品链接 | 用来补充 demo、repo、作品集和可验证材料 | URL、截图说明、部署地址备注 | 简历亮点缺少可验证材料 |
| 目标 JD | 用来匹配岗位要求并生成定制简历 | 粘贴 JD、保存来源链接、平台备注 | 只能生成通用简历，不能定制 |
| 求职偏好 | 用来决定岗位方向、城市、薪资、远程和行业偏好 | 自然语言或表单 | 岗位推荐和取舍建议不稳定 |

### JD 导入中心

- 默认主按钮文案为“粘贴目标 JD”，不是“上传 JD”；
- 支持来源平台标签：`BOSS`、`猎聘`、`拉勾`、`公司官网`、`LinkedIn`、`其他`；
- URL 字段只用于归档和 source refs，不自动抓取；
- 多个 JD 以列表展示，并允许用户选择“当前目标岗位”；
- JD 缺少公司、地点、薪资或技术栈时，显示待确认项，不自动补全。

### JD 定制简历

- 用户必须能看到简历是针对哪个 `job_id` 生成；
- 每个核心经历或技能亮点必须能追溯到 source refs；
- 与 JD 强相关但缺证据的内容进入 `pending_confirmations`；
- 支持导出前 preflight，blocking 项未确认时不得正式导出；
- 普通聊天不能静默覆盖 `resume_version`。

## 8. 里程碑

| 阶段 | 目标 | 交付物 | 出门条件 |
| --- | --- | --- | --- |
| P8-DOC-M0 | 文档和边界锁定 | PRD、架构、门槛、追踪矩阵、drawio、审计 | 不承诺平台自动化，不进入代码实现 |
| P8-M1 | 资料准备向导 | 五类资料说明、示例、缺失影响、完成状态 | 用户知道需要提供什么资料 |
| P8-M2 | JD 导入中心 | 粘贴 JD、保存 URL、平台标签、岗位列表 | 不抓取平台，不登录平台 |
| P8-M3 | JD 对比和当前目标岗位 | 多 JD 列表、匹配摘要、短板提示 | 用户能选择当前目标 JD |
| P8-M4 | JD 定制简历 | 简历草稿、source refs、待确认项、导出 preflight | 不编造事实，缺证据可见 |
| P8-M5 | 可视化验收报告 | 中文 HTML 报告、真实界面截图、PRD 检视 | 报告明确未验证平台接入和真实 provider |

## 9. 验收门槛

P8-JD Intake 通过必须同时满足：

- 用户能在首屏或输入框上方看到资料准备向导；
- 用户能理解每类资料的用途、示例和缺失影响；
- 用户能粘贴 JD 并保存来源链接；
- 系统不会因填写 URL 自动抓取网页；
- 用户能看到岗位列表并选择当前目标 JD；
- 用户能基于目标 JD 生成可追溯简历草稿；
- 简历草稿必须包含 source refs 和 pending confirmations；
- 多视口截图覆盖 1200px、720px、390px；
- HTML 验收报告明确 BOSS/外部平台自动接入、自动沟通、自动投递、真实 provider 均未验收。

## 10. 文档开发完成判定

当前文档开发阶段完成条件：

- `00_README.md` 阅读顺序包含本文件；
- `01_STAGE_PRD.md`、`02_TARGET_ARCHITECTURE.md`、`03_MILESTONES_AND_DELIVERY_PLAN.md`、`04_ACCEPTANCE_GATES.md`、`06_TRACEABILITY_MATRIX.md`、`17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md` 均同步 P8 口径；
- drawio 和文本镜像包含 P8 目标体验、架构、代码实体、计划、门槛和安全边界；
- 阶段审计记录说明本轮只做文档开发；
- 没有把 BOSS/招聘平台接入、自动投递、真实 provider 或真实个人资料写成已通过。

当前判定：P8 文档开发已收口，P8-M0 到 P8-M5 自动化候选已完成。实现证据包括 `docs/active/stage-reviews/P8_AUTOMATED_DEVELOPMENT_AND_ACCEPTANCE_AUDIT.md`、`docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html`、`tests/evals/test_p8_jd_intake_resume_generation_eval.py` 和 `docs/reports/evidence/p8_jd_intake/`。后续若进入招聘平台合规接入、真实 provider 质量复验或真实个人资料复验，必须单独授权并制定新的验收门槛。
