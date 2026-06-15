# JobPilot AI 开发计划 v1.0

版本：v1.0  
日期：2026-06-09  
目标：用尽量小的前端和清晰的 Agent 服务，跑通“资料 → JD → 申请包 → 面试准备 → 实时提示 → 复盘”的核心闭环。

---

## 1. 开发总原则

1. **先能力，后页面**：优先实现 Agent Tools，不围绕复杂前端切功能。  
2. **先闭环，后增强**：先让用户得到申请包和面试复盘，再做更多集成。  
3. **先本地，后云端**：默认本地运行，无注册登录。  
4. **先文本，后实时音频**：实时助手可先支持手动/字幕文本，再接 ASR。  
5. **先 Markdown，后 DOCX/PDF 优化**：申请包先 Markdown-first，PDF 用简单模板。  
6. **先示例数据，后复杂导入**：用 mock 简历和 JD 保证开发者能快速验证。  
7. **每周都要可演示**：每个阶段必须产出可运行 demo。

---

## 2. 推荐技术栈

### 2.1 前端

- Vite + React + TypeScript；
- Tailwind CSS；
- 简单 Chatbox UI；
- 不做复杂 dashboard。

选择理由：轻量、启动快、开源贡献者容易上手。

### 2.2 后端

推荐二选一：

**方案 A：Python FastAPI**

适合：文档解析、LLM orchestration、ASR、本地 AI 工具更顺。  
建议默认使用该方案。

**方案 B：Node.js/NestJS**

适合：前后端统一 TypeScript。  
如果团队偏前端/全栈，可选。

本文开发计划默认使用：**Python FastAPI + React**。

### 2.3 存储

- SQLite：结构化数据；
- 本地文件系统：上传文件和导出材料；
- Chroma / LanceDB / sqlite-vec：向量索引，P0 可先简单关键词 + embedding adapter；
- YAML/JSON：本地配置。

### 2.4 LLM / ASR

- LLM：OpenAI-compatible adapter + local model adapter；
- ASR：P0 支持文本模式和可插拔 ASR adapter；P1 接 Whisper/local whisper；
- Export：Markdown-first，P0 简单 PDF，P1 DOCX。

---

## 3. 代码结构建议

```text
jobpilot-ai/
├── apps/
│   ├── chatbox/                    # React Chatbox
│   └── cli/                        # CLI 入口，P1
├── services/
│   ├── api/                        # FastAPI HTTP API
│   ├── mcp/                        # MCP Server，P1
│   ├── orchestrator/               # Intent router + tool planner
│   ├── tools/
│   │   ├── workspace/
│   │   ├── profile/
│   │   ├── project/
│   │   ├── job/
│   │   ├── application/
│   │   ├── interview/
│   │   ├── realtime/
│   │   └── training/
│   ├── storage/
│   │   ├── db.py
│   │   ├── repositories/
│   │   └── migrations/
│   ├── export/
│   └── llm/
│       ├── providers/
│       ├── prompts/
│       └── schemas/
├── packages/
│   └── shared-schemas/             # JSON Schema / OpenAPI schema
├── examples/
│   ├── resumes/
│   ├── projects/
│   └── jds/
├── docs/
└── docker-compose.yml
```

---

## 4. 8 周 MVP 开发计划

### Week 0：项目初始化与决策锁定

目标：让项目能跑起来。

任务：

- 初始化 monorepo；
- 确定 FastAPI + React；
- 建立 docs；
- 建立示例数据；
- 建立 SQLite schema 初版；
- 建立 LLM provider adapter；
- 建立基础测试框架；
- Docker Compose 初版。

产出：

- `make dev` 或 `docker compose up` 能启动；
- Chatbox 空壳可打开；
- API health check 可用；
- README 能说明如何运行。

验收：

```text
新贡献者 10 分钟内能启动本地项目。
```

---

### Week 1：Workspace + Chatbox + 文件导入

目标：跑通本地工作区和上传资料。

任务：

- Workspace 初始化；
- 本地配置文件；
- 文件上传接口；
- 简历文本抽取；
- Chatbox 对话流；
- 产物抽屉初版；
- 文件保存到 workspace。

API：

- `POST /workspace/init`
- `GET /workspace/status`
- `POST /files/upload`
- `POST /chat/message`

产出：

- 用户上传简历；
- Agent 返回“我已收到资料，下一步可以解析”。

验收：

```text
用户无需登录即可上传文件，并在本地 workspace 中看到文件记录。
```

---

### Week 2：职业事实库 + 技能证据库 + 项目卡

目标：从资料中抽取可复用求职资产。

任务：

- 简历解析 prompt + schema；
- CareerFact 数据表；
- SkillEvidence 数据表；
- TechProject 数据表；
- 项目卡生成工具；
- 用户确认/修改机制；
- 示例简历评测。

Agent Tools：

- `profile.ingest_resume`
- `profile.extract_facts`
- `profile.build_skill_evidence`
- `project.create_project_card`

产出：

- 职业事实库；
- 技能证据库；
- 技术项目卡；
- 可补强建议。

验收：

```text
给一份示例转行前端简历，系统能提取至少 5 个技能、2 个项目、3 条可补强建议。
```

---

### Week 3：JD 解析 + 岗位适合度分析

目标：让用户粘贴 JD 后知道是否值得申请。

任务：

- JD 解析工具；
- must-have / nice-to-have 分类；
- 岗位级别推断；
- 与技能证据库匹配；
- 适合度报告生成；
- 下一步建议生成；
- Chatbox 中展示岗位分析结果。

Agent Tools：

- `job.parse_jd`
- `job.match_profile`
- `job.explain_fit`
- `job.suggest_next_actions`

产出：

- 岗位适合度报告。

验收：

```text
粘贴 Junior Frontend JD 后，系统能输出适合度、已具备、建议补强、是否建议申请。
```

---

### Week 4：申请包生成 + 导出

目标：用户拿到可修改和投递的材料。

任务：

- 定制简历生成；
- 项目描述优化；
- Recruiter Message 生成；
- 待确认事实标记；
- Markdown 导出；
- 简单 PDF 导出；
- 申请包保存。

Agent Tools：

- `application.generate_resume`
- `application.generate_project_bullets`
- `application.generate_message`
- `application.create_package`
- `application.export_package`

产出：

- 申请包；
- 导出文件。

验收：

```text
用户粘贴 JD 后，可以生成一份 Markdown/PDF 简历草稿和 Recruiter Message，且不确定内容会被标记。
```

---

### Week 5：面试准备包 + 故事卡 + 模拟面试

目标：从申请进入面试准备。

任务：

- 面试准备包生成；
- 自我介绍生成；
- 转行动机回答；
- 项目深挖问题；
- 技术基础问题；
- 故事卡生成；
- 模拟面试对话；
- 回答评分。

Agent Tools：

- `interview.prepare`
- `interview.create_story_cards`
- `interview.simulate`
- `interview.score_answer`

产出：

- 面试准备包；
- 故事卡；
- 模拟面试反馈。

验收：

```text
针对一个岗位，系统能生成 8-12 个面试问题、3-5 张故事卡，并完成一次模拟面试反馈。
```

---

### Week 6：实时提示基础版

目标：先实现可用的“实时结构提示”，不追求完整视频/会议集成。

任务：

- RealtimeSession 数据表；
- 手动输入/粘贴问题模式；
- 麦克风 ASR adapter 接口；
- 问题边界检测；
- 问题类型分类；
- 项目/故事检索；
- 实时提示卡；
- 时长提醒。

Agent Tools：

- `realtime.start_session`
- `realtime.transcribe_chunk`
- `realtime.detect_question`
- `realtime.generate_hint`
- `realtime.end_session`

产出：

- 实时提示卡。

验收：

```text
输入或转写出“讲一个你解决技术难题的经历”，系统能推荐一个项目并给 3-5 条回答结构提示。
```

---

### Week 7：面试复盘 + 申请记录 + 训练计划

目标：让面试后能沉淀。

任务：

- 面试复盘生成；
- 问题清单；
- 用户回答摘要；
- 弱项分析；
- 感谢消息草稿；
- 训练计划；
- 轻量申请记录；
- Chatbox 查询申请记录。

Agent Tools：

- `interview.review`
- `training.create_plan`
- `application_record.update`
- `application_record.list`

产出：

- 复盘报告；
- 下一步训练计划；
- 申请记录。

验收：

```text
面试结束后，系统能生成复盘、感谢消息草稿和 3 个训练任务。
```

---

### Week 8：开源化打磨与 MVP 发布

目标：让项目能被外部开发者试用和贡献。

任务：

- README 完善；
- 示例数据；
- Quickstart；
- Docker Compose；
- 环境变量模板；
- 测试样例；
- Eval 样例；
- 贡献指南；
- Issue 模板；
- 安全说明；
- 隐私说明；
- MVP demo 录屏脚本。

产出：

- v0.1.0 开源 MVP。

验收：

```text
外部开发者能用示例简历和 JD 跑通完整闭环。
```

---

## 5. 4 周原型压缩计划

如果想更快验证，可以压缩成 4 周：

### Week 1：本地工作区 + Chatbox + 简历/项目解析

验收：能上传资料并生成职业事实库、技能证据库、项目卡。

### Week 2：JD 分析 + 申请包生成

验收：能粘贴 JD，生成适合度报告和申请包 Markdown。

### Week 3：面试准备 + 故事卡 + 模拟面试

验收：能生成面试准备包，完成一次模拟面试反馈。

### Week 4：实时提示文本版 + 复盘 + 打包发布

验收：能输入当前面试问题，系统推荐项目和回答结构；能生成复盘。

---

## 6. 关键工程里程碑

| 里程碑 | 输出 | 通过条件 |
|---|---|---|
| M1 | 项目可启动 | 一条命令启动前后端 |
| M2 | 资料可解析 | 简历和项目能转成结构化事实 |
| M3 | JD 可分析 | 输出岗位适合度和建议 |
| M4 | 申请包可生成 | 生成可导出的 Markdown/PDF |
| M5 | 面试可训练 | 生成准备包和故事卡 |
| M6 | 实时可提示 | 当前问题能生成结构提示 |
| M7 | 复盘可沉淀 | 面试后能生成训练计划 |
| M8 | 开源可试用 | README + 示例数据 + Docker |

---

## 7. API 草案

### Workspace

```http
POST /api/workspace/init
GET  /api/workspace/status
POST /api/workspace/export
```

### Chat

```http
POST /api/chat/message
GET  /api/chat/sessions/{id}
```

### Profile

```http
POST /api/profile/ingest-resume
POST /api/profile/extract-facts
GET  /api/profile/facts
PATCH /api/profile/facts/{id}
POST /api/profile/build-skill-evidence
```

### Project

```http
POST /api/project/ingest
POST /api/project/create-card
POST /api/project/improve-description
GET  /api/project/{id}
```

### Job

```http
POST /api/job/parse-jd
POST /api/job/match-profile
GET  /api/job/{id}/match-report
```

### Application

```http
POST /api/application/create-package
POST /api/application/export-package
GET  /api/application/packages/{id}
```

### Interview

```http
POST /api/interview/prepare
POST /api/interview/simulate
POST /api/interview/score-answer
POST /api/interview/review
```

### Realtime

```http
POST /api/realtime/start
POST /api/realtime/transcribe-chunk
POST /api/realtime/detect-question
POST /api/realtime/generate-hint
POST /api/realtime/end
```

---

## 8. 测试与评测计划

### 8.1 示例数据

至少准备：

- 3 份转行程序员简历；
- 3 个项目 README；
- 5 个 Junior Frontend JD；
- 3 个 Backend/Full-stack JD；
- 20 个常见面试问题；
- 5 段模拟面试 transcript。

### 8.2 自动评测

评测维度：

- JD 解析准确性；
- must-have / nice-to-have 分类；
- 技能证据匹配；
- 简历生成是否编造；
- 项目卡是否完整；
- 实时提示是否引用真实项目；
- 复盘是否给出下一步行动。

### 8.3 手动验收

每周至少跑一次完整链路：

```text
示例简历 + 示例项目 + 示例 JD
→ 事实库
→ 岗位分析
→ 申请包
→ 面试准备
→ 实时提示
→ 复盘
```

---

## 9. 开源发布清单

- [ ] README
- [ ] Quickstart
- [ ] Docker Compose
- [ ] `.env.example`
- [ ] 示例数据
- [ ] 隐私说明
- [ ] 安全说明
- [ ] 贡献指南
- [ ] Issue 模板
- [ ] License
- [ ] Roadmap
- [ ] Demo GIF/截图
- [ ] Codex Prompt

---

## 10. 开发优先级结论

最先做：

```text
Chatbox + Workspace + 简历/项目解析 + JD 分析 + 申请包生成
```

其次做：

```text
面试准备 + 故事卡 + 模拟面试 + 复盘
```

再做：

```text
实时语音提示 + CLI/MCP + DOCX/插件增强
```

不要一开始做：

```text
复杂 Dashboard、注册登录、自动海投、大规模爬虫、面试官视频分析、隐蔽浮窗
```

