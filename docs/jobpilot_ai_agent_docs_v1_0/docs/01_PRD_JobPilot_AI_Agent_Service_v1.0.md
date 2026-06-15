# JobPilot AI PRD v1.0

**项目名称**：JobPilot AI  
**项目形态**：免费开源、本地优先、Agent-first、Chatbox-first  
**目标用户**：转行程序员  
**核心入口**：极简 Chatbox + 文件上传 + 本地工作区  
**核心服务**：可被 Chatbox、CLI、HTTP API、MCP Client 或外部 Agent 调用的求职 Agent Service  
**不做**：注册登录、多租户 SaaS、复杂 Dashboard、自动海投、隐蔽式面试作弊工具  
**版本**：v1.0  
**日期**：2026-06-09

---

## 1. 背景与产品判断

转行程序员的求职问题，本质不是“缺一个漂亮前端页面”，而是缺一个能够持续帮他把真实经历、技术项目、岗位要求和面试表达连接起来的 Agent。

用户真正需要得到的是：

- 能被简历和面试使用的职业事实库；
- 每项技能背后的证据；
- 能讲清楚的技术项目卡；
- 一份面向具体 JD 的岗位适合度判断；
- 一份可以继续修改和投递的申请包；
- 一套贴合岗位的面试准备包；
- 面试中的快速结构提示；
- 面试后的复盘和下一步训练计划。

因此，本项目不再聚焦复杂前端交互，而是聚焦 **用户实际得到的结果**。前端只作为轻量 Chatbox，承载对话、上传、确认和产物展示。

---

## 2. 一句话定位

**JobPilot AI 是一个面向转行程序员的免费开源 AI 求职 Agent 服务，通过极简 Chatbox 帮助用户完成资料整理、JD 分析、申请包生成、面试训练、实时面试提示和面试后复盘。**

---

## 3. 产品原则

### 3.1 Agent-first

核心能力必须以服务和工具形式存在，而不是绑定某个页面。Chatbox 只是默认客户端，后续应支持 CLI、HTTP API、MCP Server 和外部 Agent 调用。

### 3.2 Chatbox-first

用户默认通过一个聊天窗口完成任务。用户不需要理解复杂导航，不需要看求职漏斗，不需要配置一堆控制台。

### 3.3 Outcome-first

每轮交互都应尽量给用户一个可落地的产物或下一步行动。不要只输出长篇分析。

### 3.4 Local-first

项目默认本地运行，数据默认保存在用户本地工作区。无需注册登录。用户可以自带 LLM API Key，也可以接入本地模型。

### 3.5 Evidence-first

所有涉及用户经历、技能、项目、数字和成就的内容，都必须尽量来自用户提供的资料或用户确认过的事实。对不确定内容要标注“需要确认”。

### 3.6 Low-pressure

面向转行程序员时，文案要温和、清楚、可执行。少用“失败、严重不足、风险很高”，多用“建议补强、下一步可以做、这个岗位更看重”。

### 3.7 Human-in-the-loop

所有对外材料都需要用户确认。简历、消息、Cover Letter、申请表回答、面试提示，都不能直接替用户提交。

---

## 4. 目标用户

### 4.1 核心用户

当前版本只服务 **转行程序员**：

- 自学编程者；
- Bootcamp 毕业生；
- 非科班转码者；
- 从运营、产品、设计、测试、技术支持、数据分析、教育、金融等岗位转向开发岗位的人；
- 有项目作品但不知道怎么写进简历的人；
- 技术能力正在成长，但求职表达薄弱的人；
- 面试时能做项目，但讲不清思路、取舍和结果的人。

### 4.2 优先岗位方向

P0/P1 优先支持：

- Junior Frontend Developer；
- Junior Backend Developer；
- Full-stack Developer；
- Web Developer；
- AI Application Developer；
- QA Automation Engineer；
- Data Engineer 入门岗位；
- Developer Advocate 入门岗位。

### 4.3 暂不优先服务

- 资深工程师跳槽；
- 高阶工程经理；
- 非技术岗位泛求职；
- 招聘方/HR；
- 批量海投用户；
- 需要伪造经历或绕过面试规则的用户。

---

## 5. 用户核心问题

### 5.1 资料问题

用户有简历、项目、GitHub、学习经历，但没有整理成可复用的求职资产。

### 5.2 JD 理解问题

用户看到 JD 后不知道哪些是硬要求、哪些是加分项，不知道自己是否值得申请。

### 5.3 项目表达问题

转行程序员常见问题不是完全没项目，而是项目讲不清楚：

- 为什么做；
- 解决什么问题；
- 技术栈如何选择；
- 遇到什么难点；
- 做了什么取舍；
- 结果是什么；
- 如何证明是自己做的。

### 5.4 简历定制问题

用户不知道如何针对不同岗位改简历，也担心 AI 改写后夸大或不真实。

### 5.5 面试准备问题

用户不知道如何回答：

- 自我介绍；
- 转行动机；
- 项目深挖；
- 技术基础；
- 失败和冲突；
- 学习能力；
- 为什么适合这个岗位。

### 5.6 实时表达问题

面试中用户可能听懂问题，但一紧张就组织不好回答。因此需要快速提示：当前问题类型、推荐项目、回答结构、是否要收尾。

---

## 6. 产品形态

### 6.1 组成

JobPilot AI 由四层组成：

```text
Chatbox Client / CLI / MCP Client / 外部 Agent
                  ↓
Agent Service API / MCP Tool Server
                  ↓
Orchestrator + Domain Tools + Realtime Service
                  ↓
Local Workspace: SQLite + Files + Vector Index + Config
```

### 6.2 默认客户端

默认前端是一个 Chatbox：

- 对话区；
- 文件上传；
- JD 粘贴；
- 语音输入；
- 开启实时助手；
- 产物卡片；
- 用户确认按钮；
- 本地设置。

### 6.3 不需要的前端形态

不做：

- 复杂 Dashboard；
- 企业后台式控制台；
- 大量图表；
- 大型 Kanban 作为默认入口；
- 登录注册页；
- 付费订阅页；
- 多租户管理后台。

---

## 7. 核心体验路径

### 路径 A：第一次使用，建立本地工作区

```text
用户启动本地项目
→ 打开 Chatbox
→ 选择或创建本地 Workspace
→ 配置 LLM：自带 API Key 或本地模型
→ 系统说明不会要求注册登录，数据默认在本地
→ 用户上传简历 / 项目 README / GitHub 说明
→ Agent 提取职业事实、技能证据和项目卡
→ 用户确认或修改
→ Agent 给出 1-3 个下一步建议
```

用户得到：

- 职业事实库初版；
- 技能证据库初版；
- 技术项目卡初版；
- 可补强清单。

验收标准：

- 用户无需注册登录即可完成；
- 系统能从简历和项目资料提取技能、项目和可补强点；
- 输出温和、可执行，不制造焦虑；
- 用户能看到哪些信息需要自己确认。

---

### 路径 B：粘贴 JD，判断是否值得申请

```text
用户：帮我看看这个 Junior Frontend Developer 岗位适不适合我。
用户粘贴 JD
→ Agent 解析岗位要求
→ 区分 must-have / nice-to-have
→ 与用户职业事实库和技能证据库匹配
→ 输出岗位适合度报告
→ 给出是否建议申请和投前补强建议
```

用户得到：

- 岗位摘要；
- 岗位更看重的能力；
- 用户已经具备的证据；
- 建议补强点；
- 是否值得申请；
- 下一步行动。

示例输出：

```text
这个岗位比较适合你尝试。

它更看重：
- React 组件开发
- API 调用
- TypeScript 基础
- 能讲清楚项目结构

你已经具备：
- React 项目经验
- TodoPlus 项目可以证明前后端交互能力
- 有持续学习路径

建议补强：
- 简历中突出状态管理和 API 调用
- README 中补充项目架构图
- 准备一个项目深挖回答
```

验收标准：

- 能解析 JD；
- 能输出适合度、差距和下一步建议；
- 不只给分数；
- 输出能帮助用户决定是否申请。

---

### 路径 C：生成申请包

```text
用户：那就生成申请包。
→ Agent 基于 JD 和事实库生成定制简历草稿
→ 优化项目描述
→ 生成 Recruiter Message / Cover Letter 可选
→ 标记需要用户确认的内容
→ 导出 Markdown / PDF / DOCX
→ 保存到本地 Workspace
```

用户得到：

- 定制简历草稿；
- 项目描述优化版；
- Recruiter Message；
- 可选 Cover Letter；
- 需要确认的问题；
- 导出文件。

验收标准：

- 用户拿到可直接修改和投递的材料；
- 关键经历有来源；
- 不确定内容被标记；
- 申请包能保存和导出。

---

### 路径 D：准备面试

```text
用户：我明天要面这个岗位，帮我准备。
→ Agent 读取岗位 JD、定制简历和项目卡
→ 生成面试准备包
→ 生成故事卡
→ 生成自我介绍、项目深挖、转行动机、技术问题清单
→ 用户选择模拟面试
→ Agent 提问、追问、评分、复盘
```

用户得到：

- 面试准备包；
- 高频问题；
- 项目深挖问题；
- 30 秒 / 2 分钟 / 5 分钟故事卡；
- 模拟面试反馈；
- 下一步训练计划。

验收标准：

- 能根据目标岗位生成准备包；
- 能推荐用户真实项目作为回答素材；
- 模拟面试后能给出可执行反馈。

---

### 路径 E：实时面试提示

```text
用户：开启面试实时助手。
→ 用户确认模式和保存策略
→ 系统开启麦克风/音频转写
→ 实时识别面试问题
→ 检索 JD、项目卡、故事卡
→ 输出极简提示
→ 用户回答时提示时长和遗漏点
→ 面试结束后生成复盘
```

默认正式面试模式只提供：

- 当前问题；
- 问题类型；
- 推荐项目/故事；
- 回答结构；
- 时长提醒；
- 不要说不真实内容的提醒；
- 面试后复盘。

不默认提供：

- 完整逐字答案；
- 隐蔽浮窗；
- 绕过监考；
- 自动答题；
- 面试官人脸/情绪/敏感属性分析。

验收标准：

- 能听懂问题；
- 能推荐合适项目；
- 能在短时间内给出回答结构；
- 面试后能形成复盘和下一步训练计划。

---

### 路径 F：复盘与继续推进

```text
面试结束
→ Agent 整理问题清单
→ 总结用户回答
→ 标记表现较弱的问题
→ 推荐补强项目或故事
→ 生成感谢消息草稿
→ 更新申请记录
→ 给出 1-3 个下一步行动
```

用户得到：

- 面试复盘；
- 改进建议；
- 后续训练计划；
- 申请记录更新；
- 感谢消息草稿。

验收标准：

- 每次面试都能沉淀；
- 用户知道下一步做什么；
- 系统能持续积累用户表现和项目表达能力。

---

## 8. 基本能力集概览

P0 基本能力包括：

1. 本地工作区；
2. Chatbox；
3. 文件上传与解析；
4. 职业事实库；
5. 技能证据库；
6. 技术项目卡；
7. JD 解析；
8. 岗位适合度分析；
9. 申请包生成；
10. Markdown / PDF 导出；
11. 面试准备包；
12. 故事卡；
13. 模拟面试；
14. 实时语音转写；
15. 实时问题识别；
16. 实时提示生成；
17. 面试后复盘；
18. 申请记录轻量保存；
19. Agent Tool API；
20. Codex/CLI 友好文档。

详细能力清单见 `02_BASIC_CAPABILITY_SET.md`。

---

## 9. Agent 服务能力设计

### 9.1 Agent 工具原则

每个能力都应尽量可被工具化，输入输出结构清晰，便于 Chatbox、CLI、MCP 或外部 Agent 调用。

### 9.2 核心工具分组

#### Workspace Tools

- `workspace.init`
- `workspace.status`
- `workspace.export`
- `workspace.delete_item`

#### Profile Tools

- `profile.ingest_resume`
- `profile.extract_facts`
- `profile.update_fact`
- `profile.list_facts`
- `profile.build_skill_evidence`

#### Project Tools

- `project.ingest_readme`
- `project.create_project_card`
- `project.improve_project_description`
- `project.generate_interview_deep_dive`

#### Job Tools

- `job.parse_jd`
- `job.match_profile`
- `job.explain_fit`
- `job.suggest_next_actions`

#### Application Tools

- `application.generate_resume`
- `application.generate_project_bullets`
- `application.generate_message`
- `application.create_package`
- `application.export_package`

#### Interview Tools

- `interview.prepare`
- `interview.create_story_cards`
- `interview.simulate`
- `interview.score_answer`
- `interview.review`

#### Realtime Tools

- `realtime.start_session`
- `realtime.transcribe_chunk`
- `realtime.detect_question`
- `realtime.generate_hint`
- `realtime.end_session`

#### Training Tools

- `training.create_plan`
- `training.update_task`
- `training.review_progress`

---

## 10. 功能需求

### 10.1 本地工作区

#### 功能描述

用户第一次运行项目时创建本地工作区，用于保存资料、产物、配置和索引。

#### 功能要求

- 无需注册登录；
- 支持选择本地目录；
- 支持 SQLite 存储结构化数据；
- 支持本地文件保存上传文件和导出产物；
- 支持本地配置 LLM Provider；
- 支持清空/导出工作区。

#### 验收标准

- 用户能在 5 分钟内启动并创建工作区；
- 关闭后重新打开，历史资料仍在；
- 删除工作区后，本地数据清除。

---

### 10.2 Chatbox 客户端

#### 功能描述

极简对话入口，承载任务输入、文件上传、产物展示和用户确认。

#### 功能要求

- 文本输入；
- 文件上传；
- JD 粘贴；
- 语音入口；
- 产物卡片展示；
- 用户确认/编辑/重新生成；
- 导出按钮；
- 设置入口。

#### 验收标准

- 用户不需要理解复杂导航即可完成一个申请包生成流程；
- 每次任务结束能看到“已生成什么”和“下一步建议”；
- Chatbox 不只是闲聊，必须调用 Agent 工具完成任务。

---

### 10.3 职业事实库

#### 功能描述

从用户上传的简历、项目和自述中抽取真实经历、技能、项目、学习路径和转行动机。

#### 功能要求

- 抽取经历；
- 抽取技能；
- 抽取项目；
- 抽取成果；
- 抽取学习路径；
- 标记来源；
- 标记置信度；
- 标记是否已由用户确认；
- 支持用户修改。

#### 验收标准

- 每条关键事实有来源；
- 不确定事实标记为待确认；
- 简历和面试生成时优先引用已确认事实。

---

### 10.4 技能证据库

#### 功能描述

把技能和证据连接起来，避免简历中写了技能但无法证明。

#### 功能要求

每项技能至少包含：

- 技能名称；
- 熟练度自评；
- 证据来源；
- 对应项目；
- 可写进简历的描述；
- 可回答的面试问题；
- 是否足以用于目标岗位。

#### 验收标准

- 用户能看到 React、Node.js、TypeScript 等技能对应哪些项目；
- 系统能指出没有证据支撑的技能；
- 系统能建议如何补强证据。

---

### 10.5 技术项目卡

#### 功能描述

把项目整理成可用于简历和面试的结构化资产。

#### 项目卡字段

- 项目名称；
- 项目背景；
- 目标用户；
- 技术栈；
- 主要功能；
- 技术难点；
- 关键实现；
- 技术取舍；
- 用户负责部分；
- 结果或 Demo；
- README 建议；
- 可回答的问题；
- 简历 bullet 候选。

#### 验收标准

- 一个项目能生成 3-5 条简历 bullet；
- 一个项目能生成项目深挖面试问题；
- 系统能指出项目描述中缺少的关键信息。

---

### 10.6 JD 解析与适合度分析

#### 功能描述

解析岗位 JD，并判断对用户是否值得申请。

#### 功能要求

- 提取职位名称；
- 提取公司和地点；
- 提取岗位职责；
- 拆分 must-have / nice-to-have；
- 提取技术栈；
- 推断岗位级别；
- 匹配用户技能证据；
- 输出适合度说明；
- 输出建议补强点；
- 输出是否建议申请。

#### 验收标准

- 不只输出分数；
- 能解释适合在哪里、不足在哪里；
- 能输出下一步行动。

---

### 10.7 申请包生成

#### 功能描述

基于 JD 和用户事实库生成可投递材料。

#### 功能要求

- 定制简历；
- 项目描述优化；
- Recruiter Message；
- Cover Letter 可选；
- 内推请求可选；
- 申请表回答可选；
- Markdown / PDF / DOCX 导出；
- 标记待确认事实；
- 保存版本。

#### 验收标准

- 用户能拿到可修改、可投递的材料；
- 不编造经历；
- 关键项目和技能能对应 JD 要求；
- 生成材料可以导出。

---

### 10.8 面试准备与模拟面试

#### 功能描述

帮助用户针对具体岗位准备面试。

#### 功能要求

- 生成面试准备包；
- 生成自我介绍；
- 生成转行动机回答；
- 生成项目深挖问题；
- 生成技术基础问题；
- 生成行为面问题；
- 生成反问问题；
- 支持模拟面试；
- 支持回答评分；
- 支持训练计划。

#### 验收标准

- 模拟面试能追问；
- 反馈不是泛泛而谈；
- 用户能得到下一次练习任务。

---

### 10.9 实时面试提示

#### 功能描述

在面试过程中解析音频或转录文本，快速给出结构提示。

#### 模式

1. **模拟面试模式**：可给完整示范答案、追问、评分。  
2. **正式面试合规辅助模式**：默认模式，只给结构、项目推荐、时长提醒、复盘。  
3. **AI 允许模式**：用户确认面试允许 AI 后，可给更详细提纲和简短答案草稿。

#### 功能要求

- 实时语音转文字；
- 问题边界检测；
- 问题类型分类；
- 检索项目卡和故事卡；
- 生成极简提示；
- 回答时长提醒；
- 面试后复盘；
- 暂停/删除/不保存选项。

#### 验收标准

- 能在问题出现后快速提示回答结构；
- 默认不输出完整逐字答案；
- 用户能控制是否保存；
- 不分析面试官敏感属性。

---

### 10.10 申请记录

#### 功能描述

轻量保存用户正在推进的岗位和产物。

#### 功能要求

- 保存岗位；
- 关联申请包；
- 关联面试准备包；
- 记录状态；
- 记录下一步行动；
- 支持简单列表查看。

#### 验收标准

- 不做复杂看板作为默认入口；
- 用户能查到某个岗位对应的材料和复盘；
- 系统能给下一步提醒。

---

## 11. 信息架构

默认只有一个主界面：Chatbox。

可折叠区域：

```text
Chatbox
├── 对话区
├── 输入区
├── 文件上传
├── 产物抽屉
│   ├── 个人资料
│   ├── 岗位分析
│   ├── 申请包
│   ├── 面试准备包
│   └── 复盘记录
└── 设置
    ├── Workspace
    ├── LLM Provider
    ├── 隐私与保存策略
    └── 开发者模式
```

---

## 12. 数据模型初稿

### 12.1 Workspace

- id
- name
- root_path
- created_at
- updated_at
- llm_provider
- privacy_mode

### 12.2 CandidateProfile

- id
- workspace_id
- target_roles
- target_locations
- target_language
- background_summary
- transition_goal
- current_level
- created_at
- updated_at

### 12.3 CareerFact

- id
- workspace_id
- type：experience / project / skill / achievement / education / transition_reason
- title
- content
- source_file
- source_quote
- confidence
- user_verified
- visibility：public / application_only / interview_only / private / blocked
- created_at
- updated_at

### 12.4 SkillEvidence

- id
- workspace_id
- skill_name
- category：frontend / backend / database / devops / testing / ai / soft_skill
- evidence_type：project / work / course / certification / github / demo
- evidence_ref
- description
- confidence
- target_role_relevance
- user_verified

### 12.5 TechProject

- id
- workspace_id
- name
- summary
- tech_stack
- problem
- implementation
- technical_challenges
- tradeoffs
- user_contribution
- demo_url
- repo_url
- readme_path
- resume_bullets
- interview_questions
- verified

### 12.6 Job

- id
- workspace_id
- title
- company
- location
- jd_raw
- jd_summary
- source_url
- requirements_json
- tech_stack
- seniority_guess
- created_at

### 12.7 MatchReport

- id
- workspace_id
- job_id
- fit_label：strong / good / maybe / not_now
- fit_score_optional
- strengths
- gaps
- suggested_next_actions
- apply_recommendation
- evidence_refs
- created_at

### 12.8 ApplicationPackage

- id
- workspace_id
- job_id
- resume_version_id
- project_description
- recruiter_message
- cover_letter
- questions_to_confirm
- export_paths
- created_at

### 12.9 ResumeVersion

- id
- workspace_id
- job_id
- title
- content_markdown
- source_fact_refs
- pending_confirmations
- export_pdf_path
- export_docx_path
- created_at

### 12.10 ApplicationRecord

- id
- workspace_id
- job_id
- status：interested / preparing / applied / interview / offer / rejected / archived
- next_action
- next_action_due
- application_package_id
- notes
- created_at
- updated_at

### 12.11 StoryCard

- id
- workspace_id
- title
- applicable_questions
- source_fact_refs
- situation
- task
- action
- result
- short_version
- medium_version
- long_version
- tags

### 12.12 Interview

- id
- workspace_id
- application_record_id
- type
- scheduled_at
- prep_pack
- questions
- notes
- review
- next_training_tasks

### 12.13 RealtimeSession

- id
- workspace_id
- interview_id
- mode：practice / formal_assist / ai_allowed
- started_at
- ended_at
- save_policy
- transcript_path
- review_id

### 12.14 RealtimeHint

- id
- session_id
- question_text
- question_type
- recommended_project_id
- recommended_story_id
- hint_level：minimal / outline / draft
- hint_content
- created_at

### 12.15 TrainingTask

- id
- workspace_id
- source
- title
- description
- priority
- due_date
- status
- created_at
- updated_at

---

## 13. 技术架构建议

### 13.1 Monorepo 结构

```text
jobpilot-ai/
├── apps/
│   ├── chatbox/              # 极简 Web Chatbox
│   └── cli/                  # 命令行入口
├── services/
│   ├── api/                  # HTTP API
│   ├── mcp/                  # MCP Tool Server
│   ├── orchestrator/         # Agent 编排
│   ├── tools/                # 求职领域工具
│   ├── realtime/             # 实时语音与提示
│   ├── export/               # Markdown/PDF/DOCX 导出
│   └── storage/              # SQLite/files/vector index
├── packages/
│   ├── shared/               # 类型、schema、工具函数
│   ├── prompts/              # Prompt 模板
│   └── evals/                # 评测样例
├── docs/
└── examples/
```

### 13.2 技术选型建议

推荐开源友好的默认组合：

- 前端：Next.js 或 Vite + React；
- 后端：Python FastAPI 或 Node.js/NestJS；
- 本地数据库：SQLite；
- 向量索引：LanceDB、Chroma 或 sqlite-vec；
- 文件存储：本地文件系统；
- 队列：本地轻量任务队列，后续可接 Redis；
- 文档解析：PDF/DOCX/Markdown/Text parser；
- 导出：Markdown-first，再支持 PDF/DOCX；
- LLM：BYO API Key + 本地模型适配；
- ASR：先支持浏览器语音/外部 ASR Adapter，后续接本地 Whisper；
- MCP：作为 P1/P2 增强，但工具 schema 从 P0 就按可 MCP 化设计。

### 13.3 Agent 编排

建议采用任务型编排，不要让一个大 Prompt 做全部事情。

```text
User Intent Router
→ Domain Tool Planner
→ Retrieval / Context Builder
→ Tool Executor
→ Result Composer
→ User Confirmation
→ Artifact Writer
```

### 13.4 实时链路

```text
Audio Input / Transcript Input
→ Streaming ASR
→ Question Boundary Detector
→ Question Classifier
→ Context Retriever
→ Hint Generator
→ Chatbox Realtime Hint Card
→ Session Recorder
→ Review Generator
```

---

## 14. 安全、隐私与合规

### 14.1 默认隐私策略

- 数据默认本地保存；
- 不需要注册登录；
- 不默认上传原始音视频；
- 不默认保存完整面试音频；
- API Key 存储在本地配置中；
- 用户可以删除单条事实、单份文件、整场面试记录或整个工作区。

### 14.2 面试实时助手边界

必须明确禁止：

- stealth / undetectable 浮窗作为卖点；
- 绕过监考；
- 自动替用户完成禁止使用 AI 的测评；
- 编造经历、数字、项目、证书；
- 未经授权录制或保存对方音视频；
- 面试官人脸识别、情绪识别、年龄/性别/种族等敏感属性分析。

### 14.3 工具调用安全

Agent 工具需要：

- 输入校验；
- 输出结构校验；
- 文件路径限制；
- 人工确认敏感操作；
- 日志记录；
- 可删除数据；
- 不读取工作区外的文件。

---

## 15. 非目标功能

MVP 不做：

- 注册登录；
- SaaS 付费系统；
- 企业后台；
- 复杂 Dashboard；
- 大规模爬虫；
- 自动海投；
- 自动填写所有招聘平台；
- 复杂薪资数据库；
- 面试官视频分析；
- 自动 coding 作答；
- 多用户协作；
- 招聘方 ATS。

---

## 16. MVP 范围

### 16.1 P0：最小可用闭环

```text
启动本地项目
→ 创建 Workspace
→ 打开 Chatbox
→ 上传简历/项目
→ 生成职业事实库、技能证据库、项目卡
→ 粘贴 JD
→ 生成岗位适合度报告
→ 生成申请包
→ 导出 Markdown/PDF
→ 生成面试准备包
→ 模拟面试
→ 实时语音提示基础版
→ 面试后复盘
```

### 16.2 P1：开源增强版

- CLI；
- MCP Server；
- DOCX 导出；
- 更完整的浏览器语音输入；
- 本地 Whisper adapter；
- 项目 README 生成；
- 简单申请记录列表；
- 更多岗位模板；
- Eval 样例集。

### 16.3 P2：高级能力

- 屏幕内容解析；
- 会议平台辅助；
- Offer 分析；
- 岗位数据源接入；
- 插件生态；
- 多语言支持；
- 本地模型一键配置。

---

## 17. 成功指标

### 17.1 结果指标

- 用户能否在 30 分钟内生成第一份可修改的申请包；
- 用户能否从简历和项目资料中得到技能证据卡；
- 用户能否从 JD 得到明确申请建议；
- 用户能否完成一次模拟面试并获得复盘；
- 用户能否通过实时助手得到可用结构提示。

### 17.2 质量指标

- 生成材料中用户标记为“事实错误”的比例；
- 待确认内容标记是否充分；
- 项目卡是否能回答项目深挖问题；
- JD 解析是否正确区分 must-have 和 nice-to-have；
- 面试提示是否引用用户真实项目。

### 17.3 开源指标

- 能否一条命令启动；
- README 是否清楚；
- 是否有示例数据；
- 是否有清晰贡献指南；
- 是否支持 BYO API Key；
- 是否能在本地无登录运行。

---

## 18. 关键风险与缓解

| 风险 | 表现 | 缓解 |
|---|---|---|
| MVP 过大 | 做了很多功能但没有闭环 | 先做“资料→JD→申请包→面试准备→复盘” |
| 前端跑偏 | 又做成复杂后台 | 默认只做 Chatbox + 产物抽屉 |
| AI 编造 | 简历和面试材料不真实 | 事实库、来源引用、待确认标记 |
| 实时面试争议 | 被定义为作弊工具 | 默认只给结构提示，模式分级，用户确认 |
| 本地部署困难 | 开源用户跑不起来 | Docker Compose、一键启动、示例数据 |
| 工具调用不安全 | 读写非工作区文件 | 路径沙箱、确认机制、日志 |
| 文档不足 | Codex/贡献者不知道从哪做 | docs 包、Codex Prompt、任务切分 |
| 模型依赖重 | 用户 API 成本高 | 支持多 Provider、本地模型、缓存 |
| ASR 延迟 | 实时体验差 | P0 支持 transcript/manual input，逐步优化 ASR |
| 用户焦虑 | 输出过多负面评分 | 文案低压力，始终给下一步行动 |

---

## 19. 开放问题

1. P0 是否必须包含完整 ASR，还是可以先支持手动输入/会议字幕粘贴作为实时提示原型？
2. 第一版前端选择 Next.js 还是 Vite + React？
3. 后端选择 Python FastAPI 还是 Node.js？
4. 向量库是否先用 SQLite + sqlite-vec，减少依赖？
5. PDF/DOCX 导出第一版是否只做 Markdown + PDF？
6. MCP Server 是否进入 P0，还是 P1？
7. 是否提供默认匿名示例数据，方便开发者体验？
8. 是否支持中文/英文双语求职材料？

---

## 20. 最小验收路径

本项目第一版验收不要看页面数量，而看用户是否完成结果闭环。

```text
1. 导入资料
   验收：能自动提取技能、项目与可补强点。

2. 分析岗位
   验收：能输出适合度、差距与下一步建议。

3. 生成申请包
   验收：用户拿到可直接修改和投递的材料。

4. 面试练习 / 实时提示
   验收：能听懂问题、推荐项目并提示回答结构。

5. 复盘与继续推进
   验收：能形成下一步行动，推动求职持续进行。
```

---

## 21. 版本结论

当前项目应明确为：

> **面向转行程序员的开源 AI 求职 Agent 服务。默认入口是 Chatbox，核心验收是用户是否实际拿到申请包、面试准备包、实时提示和复盘，而不是页面是否复杂。**

