# JobPilot AI Agent / MCP Tool 草案 v1.0

本文件定义 JobPilot AI 的工具化能力。即使 P0 不完整实现 MCP Server，也应按工具边界设计服务，方便后续被 Chatbox、CLI、MCP Client、Codex、Cursor 或其他 Agent 调用。

---

## 1. 工具设计原则

1. 每个工具只做一个明确动作；
2. 输入输出使用 JSON Schema；
3. 输出尽量包含结构化字段和用户可读摘要；
4. 写入文件、删除文件、导出材料等操作需要确认；
5. 所有工具只访问当前 workspace；
6. 对外材料必须标记待确认内容；
7. 出错时返回可理解错误，不暴露内部堆栈给用户。

---

## 2. 工具列表

### 2.1 workspace.init

用途：初始化本地工作区。

输入：

```json
{
  "name": "my-job-search",
  "root_path": "~/JobPilotWorkspace",
  "llm_provider": "openai_compatible | local | mock",
  "privacy_mode": "local_first"
}
```

输出：

```json
{
  "workspace_id": "ws_xxx",
  "root_path": "...",
  "created": true,
  "next_actions": ["上传简历", "添加项目 README", "设置目标岗位"]
}
```

---

### 2.2 profile.ingest_resume

用途：导入简历并抽取文本。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "file_path": "files/resume.pdf",
  "target_role": "Junior Frontend Developer"
}
```

输出：

```json
{
  "document_id": "doc_xxx",
  "text_preview": "...",
  "next_tool": "profile.extract_facts"
}
```

---

### 2.3 profile.extract_facts

用途：从简历/项目资料中提取职业事实。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "document_ids": ["doc_xxx"],
  "target_roles": ["Junior Frontend Developer"]
}
```

输出：

```json
{
  "facts": [
    {
      "type": "skill",
      "title": "React",
      "content": "用户在 TodoPlus 项目中使用 React 构建任务管理界面。",
      "source": "resume.pdf",
      "confidence": 0.82,
      "needs_confirmation": false
    }
  ],
  "missing_info": ["TodoPlus 是否已部署上线？", "是否使用 TypeScript？"]
}
```

---

### 2.4 profile.build_skill_evidence

用途：把技能和证据连接起来。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "skill_names": ["React", "Node.js", "PostgreSQL"]
}
```

输出：

```json
{
  "skill_evidence": [
    {
      "skill": "React",
      "evidence": "TodoPlus 项目中的组件化任务列表和状态管理",
      "strength": "usable",
      "suggested_improvement": "README 中补充组件结构说明"
    }
  ]
}
```

---

### 2.5 project.create_project_card

用途：创建技术项目卡。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "project_name": "TodoPlus",
  "source_document_ids": ["doc_readme_xxx"],
  "target_role": "Junior Frontend Developer"
}
```

输出：

```json
{
  "project_id": "proj_xxx",
  "summary": "TodoPlus 是一个任务管理 Web App，用于展示前端组件化、API 调用和基础鉴权能力。",
  "tech_stack": ["React", "Node.js", "PostgreSQL"],
  "resume_bullets": ["..."],
  "interview_questions": ["讲一下登录鉴权怎么实现的？"],
  "improvements": ["补充部署链接", "补充测试说明"]
}
```

---

### 2.6 job.parse_jd

用途：解析岗位 JD。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "jd_text": "...",
  "source_url": "optional"
}
```

输出：

```json
{
  "job_id": "job_xxx",
  "title": "Junior Frontend Developer",
  "company": "Unknown",
  "requirements": {
    "must_have": ["React", "JavaScript", "HTML/CSS"],
    "nice_to_have": ["TypeScript", "Jest"]
  },
  "responsibilities": ["Build UI components", "Work with APIs"],
  "seniority_guess": "junior"
}
```

---

### 2.7 job.match_profile

用途：岗位与用户资料匹配。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "job_id": "job_xxx"
}
```

输出：

```json
{
  "match_report_id": "match_xxx",
  "fit_label": "比较适合",
  "strengths": ["有 React 项目经验", "有前后端交互项目"],
  "gaps": ["TypeScript 证据较弱", "测试经验表达不足"],
  "next_actions": ["完善 TodoPlus README", "简历突出 React 组件开发", "准备项目深挖回答"],
  "apply_recommendation": "建议申请，但投递前先优化项目描述"
}
```

---

### 2.8 application.create_package

用途：生成申请包。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "job_id": "job_xxx",
  "style": "junior_developer",
  "language": "zh-CN | en-US | bilingual"
}
```

输出：

```json
{
  "package_id": "pkg_xxx",
  "resume_markdown": "...",
  "project_description": "...",
  "recruiter_message": "...",
  "questions_to_confirm": ["TodoPlus 是否已部署上线？"],
  "source_fact_refs": ["fact_xxx", "proj_xxx"]
}
```

---

### 2.9 application.export_package

用途：导出申请包。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "package_id": "pkg_xxx",
  "formats": ["markdown", "pdf"]
}
```

输出：

```json
{
  "exports": [
    {"format": "markdown", "path": "exports/company_role_resume.md"},
    {"format": "pdf", "path": "exports/company_role_resume.pdf"}
  ]
}
```

---

### 2.10 interview.prepare

用途：生成面试准备包。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "job_id": "job_xxx",
  "package_id": "pkg_xxx",
  "interview_type": "hr | project_deep_dive | technical | behavioral | mixed"
}
```

输出：

```json
{
  "prep_pack_id": "prep_xxx",
  "focus_areas": ["自我介绍", "TodoPlus 项目深挖", "React 基础", "转行动机"],
  "questions": ["讲一下 TodoPlus 的架构", "为什么从原行业转前端？"],
  "reverse_questions": ["这个岗位前三个月最重要的目标是什么？"]
}
```

---

### 2.11 interview.create_story_cards

用途：生成故事卡。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "source_project_ids": ["proj_xxx"],
  "job_id": "job_xxx"
}
```

输出：

```json
{
  "story_cards": [
    {
      "title": "解决登录状态丢失问题",
      "applicable_questions": ["讲一个你解决技术难题的经历"],
      "short_version": "...",
      "medium_version": "...",
      "long_version": "...",
      "source_refs": ["proj_xxx"]
    }
  ]
}
```

---

### 2.12 interview.simulate

用途：模拟面试。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "prep_pack_id": "prep_xxx",
  "mode": "project_deep_dive",
  "user_answer": "optional"
}
```

输出：

```json
{
  "interviewer_question": "讲一下 TodoPlus 登录鉴权是怎么做的。",
  "follow_up": "为什么选择这种实现方式？",
  "feedback": "你的回答讲清了实现，但缺少技术取舍。",
  "next_practice": "用 2 分钟版本重新回答。"
}
```

---

### 2.13 realtime.start_session

用途：开启实时提示会话。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "job_id": "job_xxx",
  "mode": "practice | formal_assist | ai_allowed",
  "save_policy": "no_audio | transcript_only | save_all"
}
```

输出：

```json
{
  "session_id": "rt_xxx",
  "mode": "formal_assist",
  "allowed_hint_levels": ["minimal", "outline"],
  "message": "我会帮你识别问题、推荐项目和提示回答结构。"
}
```

---

### 2.14 realtime.detect_question

用途：从 transcript 中识别当前问题。

输入：

```json
{
  "session_id": "rt_xxx",
  "transcript_chunk": "Can you tell me about a time you solved a technical problem?"
}
```

输出：

```json
{
  "question_detected": true,
  "question_text": "Can you tell me about a time you solved a technical problem?",
  "question_type": "project_deep_dive | technical_problem",
  "confidence": 0.9
}
```

---

### 2.15 realtime.generate_hint

用途：生成实时提示。

输入：

```json
{
  "session_id": "rt_xxx",
  "question_text": "讲一个你解决技术难题的经历",
  "hint_level": "minimal | outline | draft"
}
```

输出：

```json
{
  "hint": {
    "recommended_project": "TodoPlus 登录鉴权项目",
    "structure": ["先说问题", "讲你的实现", "讲一个取舍", "用结果收尾"],
    "reminder": "不要说 OAuth，如果项目里没有。",
    "source_refs": ["proj_xxx"]
  }
}
```

---

### 2.16 interview.review

用途：生成面试复盘。

输入：

```json
{
  "workspace_id": "ws_xxx",
  "session_id": "rt_xxx",
  "transcript": "optional"
}
```

输出：

```json
{
  "review_id": "review_xxx",
  "questions": ["讲一个你解决技术难题的经历"],
  "strengths": ["能说明项目背景"],
  "improvements": ["回答中缺少结果", "技术取舍讲得不够"],
  "training_tasks": ["练习 TodoPlus 项目 2 分钟版本", "补充 TypeScript 学习证据"],
  "thank_you_message": "..."
}
```

---

## 3. MCP 暴露建议

P1/P2 中，建议将以下工具作为 MCP tools 暴露：

- `profile.extract_facts`
- `project.create_project_card`
- `job.parse_jd`
- `job.match_profile`
- `application.create_package`
- `application.export_package`
- `interview.prepare`
- `interview.create_story_cards`
- `realtime.generate_hint`
- `interview.review`

Resources 可暴露：

- `jobpilot://workspace/profile`
- `jobpilot://workspace/projects`
- `jobpilot://workspace/jobs`
- `jobpilot://workspace/applications`
- `jobpilot://workspace/interviews`

Prompts 可暴露：

- `jobpilot_analyze_jd`
- `jobpilot_generate_resume`
- `jobpilot_prepare_interview`
- `jobpilot_realtime_hint`

---

## 4. 错误处理建议

统一错误结构：

```json
{
  "ok": false,
  "error_code": "MISSING_WORKSPACE | INVALID_INPUT | LLM_FAILED | EXPORT_FAILED | PERMISSION_DENIED",
  "message": "用户可理解的错误说明",
  "recoverable": true,
  "suggested_action": "请重新上传文件或检查配置"
}
```

---

## 5. 工具验收标准

- [ ] 工具可独立调用；
- [ ] 输入输出 schema 明确；
- [ ] Chatbox 通过工具获得结果；
- [ ] 不在前端写核心业务逻辑；
- [ ] 写文件和删除文件需明确确认；
- [ ] 工具只访问 workspace；
- [ ] 对外材料有待确认标记；
- [ ] 错误信息对用户友好。

