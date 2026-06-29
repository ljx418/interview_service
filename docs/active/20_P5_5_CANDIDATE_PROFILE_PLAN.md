# P5.5 Candidate Profile 开发及验收计划

日期：2026-06-29  
状态：自动化开发候选已完成；仅证明 examples / synthetic-style workspace + mock provider 路径，不代表 P5-REAL、真实 provider 或真实个人资料路径通过。

## 1. 阶段目标

P5.5 解决的问题是：P5 已能导入资料、解析 JD、生成申请包，但用户仍缺少一张可反复审查的“我是谁、我有什么证据、我适合哪些岗位、短板在哪里、下一步补什么”的画像面板。

目标体验：

```text
用户导入或粘贴资料
→ 系统生成职业事实、技能证据、项目卡和 JD 匹配
→ P5.5 聚合 CandidateProfile
→ 展示能力矩阵、项目可信度、岗位短板和补强建议
→ 用户查看每条判断的 source refs 和待确认项
→ 用户围绕画像继续追问，普通聊天不写画像产物
```

## 2. 用户可见结果

| 结果 | 内容 | 约束 |
| --- | --- | --- |
| 专业背景画像 | 目标岗位、转型路径、当前层级、主要经历摘要 | 只能基于资料和 artifact，不臆造履历 |
| 能力矩阵 | 技能、类别、证据类型、证据强度、岗位相关性 | 每项能力必须有 source refs 或待确认 |
| 项目可信度 | 本人贡献、技术难点、可验证材料、量化结果缺口 | 不能把未确认贡献写成事实 |
| 岗位短板 | must-have / nice-to-have 缺口、表达风险、补强行动 | 缺口必须可行动，不做羞辱性评价 |
| 画像面板 | Workbench 中的概览、证据、风险、下一步 | 不暴露内部 id 作为主标题 |

## 3. 架构边界

P5.5 复用现有本地优先架构，不引入新外部依赖作为默认方案：

```text
Chatbox Workbench
→ Candidate Profile Plane
→ FastAPI Profile routes
→ Profile Aggregator
→ Evidence Scorer
→ Project Credibility Evaluator
→ Gap Analyzer
→ Artifact / Storage / Source refs
```

优先复用的代码实体：

- `candidate_profile`：候选人画像摘要和目标岗位偏好；
- `career_fact`：职业事实、经历线索和技能事实；
- `skill_evidence`：技能证据、岗位相关性和验证状态；
- `tech_project`：项目背景、贡献、技术难点和可信度线索；
- `job` / `match_report`：岗位要求、匹配优势和短板；
- `artifact` / `artifact_version`：画像产物、版本和 source refs；
- `services/chat/core.py`：普通追问、状态查询和工具意图边界；
- `apps/chatbox/src/main.tsx`：画像面板、能力矩阵、项目可信度和短板展示。

## 3.1 实现默认路线和接口契约

后续自动化开发必须采用以下默认路线，不再留给实现阶段临时决策：

- 验收数据：默认只使用 `examples/`、`examples/p5_synthetic_personas/` 和测试临时 workspace；不读取真实个人资料。
- 最小后端入口：必须新增 profile 读取和刷新路由，不复用通用 chat message 作为唯一入口。
- 持久化方式：刷新画像时更新或创建 `candidate_profile` 行，并写入 `artifact_type=candidate_profile` 的 artifact/version；能力矩阵、项目可信度和岗位短板进入 artifact `content_json`。
- Schema 策略：P5.5 v1 不新增数据库表；优先复用 `candidate_profile`、`career_fact`、`skill_evidence`、`tech_project`、`job`、`match_report`、`artifact`。
- 交互策略：v1 先做只读画像聚合、刷新和证据展开；不做复杂手工编辑画像。用户事实修正仍走既有 fact / artifact confirmation 路径。
- Provider 策略：默认 local/mock，不调用真实 provider；若后续要让真实 provider 辅助画像，必须另行走 P6 opt-in。

最小接口契约：

| 接口 | 输入 | 输出 | 约束 |
| --- | --- | --- | --- |
| `GET /api/profile/candidate` | `workspace_id`, 可选 `job_id` | profile summary、capability matrix、project credibility、job gaps、source refs、artifact ref | 只读；没有画像时返回可恢复空态 |
| `POST /api/profile/candidate/refresh` | `workspace_id`, 可选 `job_id`, `target_role` | 刷新后的完整画像、artifact ref、questions_to_confirm | 写入 `candidate_profile` 和 `candidate_profile` artifact；不访问 workspace 外路径 |

最小画像 `content_json` 必须包含：

```json
{
  "profile_summary": {
    "target_roles": [],
    "background_summary": "",
    "transition_goal": "",
    "current_level": "",
    "source_refs": []
  },
  "capability_matrix": [
    {
      "skill": "",
      "category": "",
      "evidence_level": "strong|usable|weak|missing",
      "target_role_relevance": "high|medium|low|unknown",
      "source_refs": [],
      "questions_to_confirm": []
    }
  ],
  "project_credibility": [
    {
      "project_name": "",
      "credibility_label": "verified|plausible|needs_evidence|risky",
      "strengths": [],
      "evidence_gaps": [],
      "source_refs": [],
      "questions_to_confirm": []
    }
  ],
  "job_gaps": [
    {
      "requirement": "",
      "gap_level": "covered|partial|missing",
      "impact": "",
      "next_action": "",
      "source_refs": []
    }
  ]
}
```

评分默认规则：

- `strong`：有 source refs，且用户已确认或有明确项目/文档证据；
- `usable`：有资料或项目来源，但仍缺少量化结果或本人贡献确认；
- `weak`：只有单一线索、表达模糊或缺少项目支撑；
- `missing`：JD 要求中出现，但当前 workspace 没有可追踪证据；
- `verified` 项目：本人贡献、技术难点、可验证材料三项均有来源；
- `plausible` 项目：有项目来源，但缺少量化结果或验证材料；
- `needs_evidence` 项目：只有宽泛描述，缺本人贡献或技术细节；
- `risky` 项目：存在未确认贡献、夸大风险或与 JD 表达冲突。

## 4. 里程碑

| 阶段 | 交付物 | 出门条件 |
| --- | --- | --- |
| P5.5-M0 文档锁定 | PRD、架构、门槛、drawio、审计 | 文档无重大规格缺口 |
| P5.5-M1 CandidateProfile 聚合 | 画像聚合接口和数据契约 | 能从现有事实/项目/JD 生成画像摘要 |
| P5.5-M2 能力矩阵 | skill evidence 分级、证据强度、待确认项 | 每项能力有来源或明确缺证据 |
| P5.5-M3 项目可信度 | 项目可信度标签、本人贡献、验证材料缺口 | 未确认贡献不写成事实 |
| P5.5-M4 岗位短板 | JD 对齐、缺口、风险和补强建议 | 短板可行动、有证据来源 |
| P5.5-M5 画像 Workbench | Chatbox 画像面板、多视口可读 | 用户能看懂当前画像和下一步 |
| P5.5-M6 验收报告 | 中文 HTML 报告、截图、PRD 规格检视 | 不做真实资料或真实 provider 虚假验收 |

## 5. 验收门槛

- 画像结论必须来自 `career_fact`、`skill_evidence`、`tech_project`、`job`、`match_report` 或 artifact source refs；
- 能力矩阵必须区分 strong / usable / weak / missing 或等价等级；
- 项目可信度必须说明证据、缺口、风险和待确认项；
- 岗位短板必须对应 JD 要求，并给出补强行动；
- 普通聊天不得误写画像 artifact；
- blocking 待确认项不得在画像中被隐藏；
- 报告不得包含完整真实个人资料、API Key、provider raw response 或未授权长原文；
- P5.5 不分析敏感属性，不做背景调查，不声明真实个人资料路径已通过。

## 6. 自动化验收计划

已补充并执行的 P5.5 自动化验收：

- `test_p5_5_candidate_profile_eval.py`：画像聚合、profile 读取/刷新、artifact/version/source refs、缺证据边界；
- `test_p5_5_capability_matrix_eval.py`：能力矩阵、strong / usable / weak / missing、待确认项；
- `test_p5_5_project_credibility_eval.py`：项目可信度、本人贡献、量化结果缺口、待确认项；
- `test_p5_5_gap_analysis_eval.py`：JD 短板、补强建议、gap_level 和 source refs；
- `test_p5_5_chat_boundary_eval.py`：普通聊天不写 candidate_profile artifact；
- `test_p5_5_acceptance_report_eval.py`：中文 HTML 报告、截图证据、未验证范围。

## 7. 非目标和高风险确认

P5.5 不做：

- 真实个人资料默认读取或验收；
- 真实 MiniMax、DeepSeek、OpenAI-compatible provider 默认外呼；
- 敏感属性、人格、年龄、性别、健康、政治、家庭、民族等分析；
- 背景调查、社交媒体画像或隐私画像；
- workspace 删除、不可逆迁移、外部同步；
- SaaS、多租户、Billing、ASR、会议平台、自动投递、MCP/CLI。

任何触及上述范围的开发都必须另行立项并获得用户确认。

## 8. 详细开发及验收计划

后续自动化开发必须按以下顺序执行。每个子阶段开始前先落盘启动审计，审计无致命或重大规格偏差后才进入实现；每个子阶段结束后必须完成端到端验收、PRD 规格检视和虚假验收风险检查。

| 子阶段 | 开发内容 | 必须验收 | 打回条件 |
| --- | --- | --- | --- |
| P5.5-M0 启动审计 | 检查 PRD、目标架构、验收门槛、drawio、接口契约和测试数据口径 | 形成 P5.5-M0 start audit；确认只用 examples、合成资料和测试 workspace | 文档仍存在当前阶段口径冲突；真实资料/provider 被写成默认路径 |
| P5.5-M1 CandidateProfile 聚合 | 新增 profile routes、schemas、profile aggregator；刷新画像写入 `candidate_profile` 和 `artifact_type=candidate_profile` | `GET /api/profile/candidate` 空态/有数据态；`POST /api/profile/candidate/refresh` 生成 artifact/version；source refs 可追溯 | 画像没有 source refs；刷新只写前端状态不写 artifact；新增不可逆 DB 迁移 |
| P5.5-M2 能力矩阵 | 基于 `skill_evidence`、`career_fact`、artifact refs 生成技能、类别、证据等级、岗位相关性和待确认项 | 覆盖 strong/usable/weak/missing；弱证据显示补证建议；普通聊天不改变矩阵 | 弱证据被写成强能力；能力判断评价人格、潜力或敏感属性 |
| P5.5-M3 项目可信度 | 基于 `tech_project`、source refs 和待确认项生成可信度标签 | 覆盖 verified/plausible/needs_evidence/risky；本人贡献和证据缺口分开展示 | 未确认本人贡献写成事实；缺少项目证据却标记 verified |
| P5.5-M4 JD 短板分析 | 将能力矩阵与 `job` / `match_report` 的 must/nice 要求对齐 | 每个短板含 requirement、gap_level、impact、next_action、source_refs | 只输出否定评价；无 JD 来源；把 missing 写成 covered |
| P5.5-M5 Workbench | 在 Chatbox 中展示画像概览、能力矩阵、项目可信度、岗位短板、source refs 展开和下一步建议 | 桌面/宽屏/移动端截图可读；按钮对齐；文本不重叠；普通追问不写画像 artifact | 页面只能看裸 JSON；多视口布局明显破损；source refs 无法审查 |
| P5.5-M6 可视化验收报告 | 生成中文 HTML 自动化验收报告和 PRD 规格检视 | 报告列出目标架构、当前实现、真实界面截图、测试结果、未验证范围 | 报告把未实现功能写成通过；把合成资料称为真实资料；泄露 API Key 或完整真实资料 |

## 9. 自动化验收证据清单

本轮自动化候选完成时已形成以下证据：

- 后端单元/集成测试：profile refresh、profile read、artifact/version/source refs、能力矩阵、项目可信度、JD 短板、普通聊天不写 artifact；
- 前端构建：`npm --prefix apps/chatbox run build`；
- 全量回归：`.venv/bin/python -m pytest`；
- 浏览器证据：桌面、宽屏、移动端真实界面截图，覆盖画像概览、能力矩阵、项目可信度、岗位短板、source refs 展开和空态；
- 报告证据：`docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html`、PRD 规格检视、隐私/虚假验收审计；
- 文档证据：drawio XML parse、文本镜像一致性、README/TODO/active docs 口径一致。

## 10. 开发完成后的目标达成判断

若 P5.5-M1 到 P5.5-M6 全部通过，项目可以支撑 PRD 中定义的 P5.5 体验：用户能在本地 Chatbox 中看到可追溯的专业背景画像、能力矩阵、项目可信度、岗位短板和补强建议，并能围绕画像继续追问。该结论仍不代表 P5-REAL、真实 provider 质量、SaaS、ASR、会议平台、自动投递、MCP/CLI 或真实个人资料路径通过。
