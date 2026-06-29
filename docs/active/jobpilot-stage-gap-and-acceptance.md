# JobPilot AI P5.5 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。当前图示主线是 P5.5 Candidate Profile：候选人画像、能力矩阵、项目可信度、岗位短板、source refs 和可视化验收。P6+P7 自动化候选作为已完成基线保留。

任何真实 API Key、真实个人资料、真实外部 provider 调用、workspace 删除、不可逆迁移、敏感属性分析、ASR/会议平台/自动投递/SaaS 操作都必须先获得用户确认。

## 图示页结构

drawio 保持 6 页，不超过 8 页：

1. P5.5 目标体验与当前差距；
2. 当前架构与 P5.5 目标架构；
3. 代码实体、分层结构与交互关系；
4. P5.5 开发及验收计划；
5. 项目里程碑、验收门槛与出门条件；
6. 安全边界、证据、状态标记和后续复验。

颜色含义：

- 绿色：已实现并冻结或作为基线保留，包括 P0-P7 本地/mock/自动化候选能力；
- 蓝色：P5.5 本阶段计划新增能力；
- 黄色：需修改或复验的既有能力；
- 橙色：需要用户确认的高风险流程；
- 灰色：P8+ 后续能力；
- 红色：禁止路径、打回条件或虚假验收风险。

## 第 1 页 - P5.5 目标体验与当前差距

目标体验主链路：

```text
User
→ 本地 Chatbox
→ 导入或粘贴资料 / JD
→ career_facts / skill_evidence / tech_project / match_report
→ CandidateProfile 聚合
→ 能力矩阵、项目可信度、岗位短板、补强建议
→ source refs 和待确认项可展开
→ 中文 HTML 报告和截图证据
```

当前差距：

- P5 本地资料闭环已完成自动化候选，但没有独立画像面板；
- 数据库已有 `candidate_profile`、`career_fact`、`skill_evidence`、`tech_project`、`match_report`，但缺少画像聚合器；
- Chatbox 已有 Workbench，但缺少能力矩阵、项目可信度和短板视图；
- 报告链路成熟，但缺少 P5.5 专项中文 HTML 报告；
- 真实资料、真实 provider、敏感属性分析、SaaS/ASR/会议平台/自动投递/MCP/CLI 不属于本阶段。

## 第 2 页 - 当前架构与 P5.5 目标架构

当前已实现基线：

```text
React Chatbox
→ FastAPI Agent Service
→ ChatCore / PiAgent Adapter
→ Domain Tools
→ Artifact Versioning
→ SQLite Workspace
→ P5/P6/P7 Evidence
```

P5.5 目标新增或改造：

```text
Candidate Profile Workbench
→ Profile Aggregation Routes
→ CandidateProfile Aggregator
→ Evidence Scorer
→ Project Credibility Evaluator
→ Job Gap Analyzer
→ Profile Artifact / Source refs
→ P5.5 Visual Acceptance Report
```

架构关系：

- Chatbox 只展示画像、确认项、证据和下一步建议；
- FastAPI 负责 profile 读取/刷新请求边界；
- Profile Aggregator 聚合职业事实、技能证据、项目和岗位匹配；
- Evidence Scorer 评价证据强弱，不评价人格或敏感属性；
- Project Credibility Evaluator 只评价项目证据、贡献、缺口和风险；
- Job Gap Analyzer 将能力矩阵和 JD 要求对齐；
- Artifact/Storage 继续负责版本、source refs 和本地持久化。

## 第 3 页 - 代码实体、分层结构与交互关系

必须在图中出现的具体代码实体：

- `apps/chatbox/src/main.tsx`：Candidate Profile Workbench、能力矩阵、项目可信度、岗位短板、source refs；
- `apps/chatbox/src/styles.css`：画像面板、多视口布局、证据展开和风险标签；
- `services/api/main.py`：`GET /api/profile/candidate`、`POST /api/profile/candidate/refresh`、profile summary、capability matrix、project credibility、gap analysis 路由；
- `services/api/schemas.py`：P5.5 请求/响应 schema；
- `services/chat/core.py`：画像状态查询、普通追问不写 artifact、明确工具意图边界；
- `services/profile/` 或等价模块：CandidateProfile Aggregator、Evidence Scorer、Project Credibility Evaluator、Job Gap Analyzer；
- `services/storage/db.py`：`candidate_profile`、`career_fact`、`skill_evidence`、`tech_project`、`job`、`match_report`、`artifact`；P5.5 v1 不新增数据库表；
- `docs/reports/` 与截图脚本：P5.5 HTML 验收报告、真实界面截图和 PRD 规格检视。

禁止关系：

- 无 source refs 的画像判断；
- 弱证据技能被写成强能力；
- 未确认本人贡献被写成事实；
- 敏感属性、人格、年龄、性别、健康、政治、民族等分析；
- 默认真实 provider 外呼；
- 把合成资料写成真实资料验收；
- 普通聊天误写画像 artifact。

默认实现路线：

- 刷新画像写入 `candidate_profile` 行和 `artifact_type=candidate_profile` artifact/version；
- 能力矩阵、项目可信度和岗位短板进入 artifact `content_json`；
- v1 只做只读聚合、刷新和证据展开，不做复杂手工编辑画像。

## 第 4 页 - P5.5 开发及验收计划

执行顺序：

```text
P5.5-DOC-M0 文档 / drawio / 风险边界锁定
→ P5.5-M0 启动审计
→ P5.5-M1 CandidateProfile 聚合
→ P5.5-M2 能力矩阵和证据强度
→ P5.5-M3 项目可信度和风险标签
→ P5.5-M4 JD 对齐短板分析
→ P5.5-M5 Chatbox/Profile Workbench
→ P5.5-M6 Visual Acceptance 与冻结候选
```

每个子阶段必须先写启动审计、验收标准和打回条件，再进入实质开发。完成后必须有端到端验收、PRD 规格检视和虚假验收风险检查。

## 第 5 页 - 项目里程碑、验收门槛与出门条件

P5.5 门槛：

1. 文档和边界完整；
2. CandidateProfile 可追溯；
3. 能力矩阵可解释；
4. 项目可信度不夸大；
5. 岗位短板可行动；
6. Chatbox / Workbench 体验成立；
7. 可视化验收报告完整。

最终出门体验：

```text
本地 Chatbox 可用
→ 用户看到职业画像、能力矩阵、项目可信度和岗位短板
→ 每条判断有 source refs、证据强度、待确认项和风险标签
→ 用户知道哪些能力可用于申请材料、哪些项目可信、下一步补什么
→ 报告展示真实界面截图、PRD 检视和未验证范围
```

## 第 6 页 - 安全边界、状态标记、证据和后续复验

证据包：

- P5.5 中文 HTML 自动化验收报告；
- 桌面、宽屏、移动端真实界面截图；
- 画像概览、能力矩阵、项目可信度、岗位短板、source refs、普通聊天不写 artifact 截图；
- pytest、frontend build、drawio XML parse；
- PRD 规格检视、隐私审计和虚假验收风险清单。

高风险边界：

- 真实个人资料必须用户授权；
- 真实 provider 必须 opt-in；
- API Key 不得进入仓库、报告、日志或截图；
- 敏感属性分析禁止进入 P5.5；
- workspace 删除和迁移 apply 默认不执行；
- ASR、会议平台、自动投递、SaaS、多租户、Billing、MCP/CLI 不是本阶段出门条件；
- 文档通过不等于实现通过，drawio 方向认可不等于功能验收通过。
