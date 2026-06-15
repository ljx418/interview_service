# JobPilot AI P0 Prompt 与输出 Schema

## 1. 目的

本文档定义 P0 阶段所有 Prompt Contract 和工具输出的最小字段级 schema，避免后续实现时每个模块自行定义结构。

P0 实现可以使用 Pydantic model、JSON Schema 或等价类型系统，但字段语义必须与本文档一致。

## 2. 通用类型

### 2.1 SourceRef

所有对外产物必须能追溯来源。统一使用以下结构：

```json
{
  "source_type": "career_fact | skill_evidence | tech_project | document | job | story_card | transcript | artifact | resume_version | application_package | interview | realtime_session",
  "source_id": "string",
  "field": "optional string",
  "quote": "optional short excerpt",
  "confidence": "high | medium | low"
}
```

规则：

- `source_type` 和 `source_id` 必填；
- `quote` 只保存短摘录，不保存完整简历原文；
- 对外材料中的项目、技能、经历、数字、证书必须有 `source_refs`，否则进入待确认。

### 2.2 ConfirmationQuestion

```json
{
  "question": "string",
  "confirmation_level": "blocking | warning | optional",
  "reason": "optional string",
  "source_refs": ["SourceRef"]
}
```

导出规则：

- `blocking`：必须确认，否则不能导出；
- `warning`：允许导出，但导出文件中必须保留明显提醒；
- `optional`：作为补强建议，不阻塞导出。

示例：

- “是否拥有 AWS 证书？”：`blocking`
- “TodoPlus 是否已经部署上线？”：`warning`
- “是否可以补充性能优化数据？”：`optional`

### 2.3 ArtifactStatus

```text
draft | needs_confirmation | confirmed | exported
```

状态规则：

- LLM 或工具新生成的对外产物默认是 `needs_confirmation`；
- 用户确认后变为 `confirmed`；
- 导出成功后变为 `exported`；
- 如果用户编辑了已导出内容，应回到 `needs_confirmation` 或新建版本。

### 2.4 ArtifactRecord 与 ArtifactRef

SQLite 中的统一 artifact row 模型：

```text
artifact
- id
- workspace_id
- artifact_type
- source_table
- source_id
- status
- content_json
- content_path
- source_refs
- questions_to_confirm
- created_by_tool
- created_at
- updated_at
```

说明：

- `content_json` 用于保存轻量可展示内容；
- `content_path` 用于保存大文本或导出文件路径；
- 如果内容保存在业务表中，`content_json` 可以为空，但必须通过 `source_table + source_id` 恢复；
- Chatbox 展示 artifact 时必须能通过 artifact record 恢复内容；
- regenerate 不能覆盖旧 artifact，应生成新版本或更新 `source_id` 并保留 tool invocation 记录。

API 工具结果中的轻量 artifact 引用使用 `ArtifactRef`：

```json
{
  "artifact_id": "string",
  "artifact_type": "string",
  "status": "draft | needs_confirmation | confirmed | exported",
  "source_refs": ["SourceRef"],
  "questions_to_confirm": ["ConfirmationQuestion"]
}
```

规则：

- 数据库存储使用 `artifact.id`；
- API 返回可使用 `artifact_id`，其值必须等于对应 `artifact.id`；
- 自动化实现不得把 `ArtifactRef` 当作完整内容恢复来源，恢复内容必须读取 `artifact` row 的 `content_json`、`content_path` 或 `source_table + source_id`。

## 3. Prompt Contract 列表

P0 prompt 必须覆盖：

- `profile_extract_facts`
- `project_create_card`
- `job_parse_jd`
- `job_match_profile`
- `application_create_package`
- `interview_prepare`
- `interview_create_story_cards`
- `realtime_generate_hint`
- `interview_review`

每个 prompt contract 必须声明：

- 输入 schema；
- 输出 schema；
- 必需 source refs；
- 必需 questions_to_confirm；
- safety mode；
- eval fixture。

## 4. 输出 Schema

### 4.1 CareerFactOutput

```json
{
  "facts": [
    {
      "type": "experience | project | skill | achievement | education | transition_reason | soft_skill | metric",
      "title": "string",
      "content": "string",
      "source_refs": ["SourceRef"],
      "confidence": "high | medium | low",
      "user_verified": false,
      "visibility": "public | application_only | interview_only | private | blocked",
      "questions_to_confirm": ["ConfirmationQuestion"]
    }
  ],
  "summary": "string",
  "missing_info": ["ConfirmationQuestion"]
}
```

### 4.2 SkillEvidenceOutput

```json
{
  "skill_evidence": [
    {
      "skill_name": "string",
      "category": "frontend | backend | database | devops | testing | ai | soft_skill | general",
      "evidence_type": "project | work | course | certification | github | demo | document",
      "evidence_ref": "string",
      "description": "string",
      "strength": "strong | usable | weak | missing",
      "target_role_relevance": "high | medium | low",
      "source_refs": ["SourceRef"],
      "questions_to_confirm": ["ConfirmationQuestion"]
    }
  ],
  "suggested_improvements": ["string"]
}
```

### 4.3 TechProjectOutput

```json
{
  "name": "string",
  "summary": "string",
  "tech_stack": ["string"],
  "problem": "string",
  "implementation": "string",
  "technical_challenges": ["string"],
  "tradeoffs": ["string"],
  "user_contribution": "string",
  "resume_bullets": ["string"],
  "interview_questions": ["string"],
  "improvements": ["string"],
  "source_refs": ["SourceRef"],
  "questions_to_confirm": ["ConfirmationQuestion"]
}
```

### 4.4 JobParseOutput

```json
{
  "title": "string",
  "company": "string | Unknown",
  "location": "optional string",
  "jd_summary": "string",
  "requirements": {
    "must_have": ["string"],
    "nice_to_have": ["string"]
  },
  "responsibilities": ["string"],
  "tech_stack": ["string"],
  "seniority_guess": "junior | entry | unknown",
  "interview_focus": ["string"],
  "source_refs": ["SourceRef"]
}
```

### 4.5 MatchReportOutput

```json
{
  "fit_label": "strong | good | maybe | not_now",
  "fit_summary": "string",
  "strengths": [
    {
      "text": "string",
      "source_refs": ["SourceRef"]
    }
  ],
  "gaps": [
    {
      "text": "string",
      "severity": "high | medium | low",
      "suggested_action": "string"
    }
  ],
  "next_actions": ["string"],
  "apply_recommendation": "string",
  "questions_to_confirm": ["ConfirmationQuestion"]
}
```

### 4.6 ApplicationPackageOutput

```json
{
  "resume_markdown": "string",
  "project_description": "string",
  "recruiter_message": "string",
  "cover_letter": "optional string",
  "source_refs": ["SourceRef"],
  "questions_to_confirm": ["ConfirmationQuestion"],
  "export_policy": {
    "markdown_required": true,
    "pdf_required": false,
    "pdf_note": "P0 PDF 是软门槛，可为占位或轻量实现，不阻塞发布。"
  }
}
```

### 4.7 StoryCardOutput

```json
{
  "story_cards": [
    {
      "title": "string",
      "applicable_questions": ["string"],
      "situation": "string",
      "task": "string",
      "action": "string",
      "result": "string",
      "short_version": "string",
      "medium_version": "string",
      "long_version": "string",
      "tags": ["string"],
      "source_refs": ["SourceRef"],
      "questions_to_confirm": ["ConfirmationQuestion"]
    }
  ]
}
```

### 4.8 RealtimeHintOutput

```json
{
  "question_text": "string",
  "question_type": "project_deep_dive | technical | behavioral | transition_motivation | general",
  "recommended_project_id": "optional string",
  "recommended_story_id": "optional string",
  "hint_level": "minimal | outline",
  "structure": ["string"],
  "reminder": "string",
  "source_refs": ["SourceRef"],
  "forbidden_fields": ["full_answer", "stealth_overlay", "auto_answer"]
}
```

P0 realtime 硬边界：

```text
P0 realtime = text question → structured hint。
P0 不实现真实麦克风 ASR、系统音频采集、会议平台接入、视频解析。
```

### 4.9 InterviewReviewOutput

```json
{
  "questions": ["string"],
  "answer_summary": "string",
  "strengths": ["string"],
  "improvements": ["string"],
  "training_tasks": ["TrainingTaskOutput"],
  "thank_you_message": "optional string",
  "source_refs": ["SourceRef"],
  "questions_to_confirm": ["ConfirmationQuestion"]
}
```

### 4.10 TrainingTaskOutput

```json
{
  "title": "string",
  "description": "string",
  "priority": "high | medium | low",
  "source": "interview_review | match_report | realtime_hint | user_request",
  "status": "open | in_progress | done",
  "due_date": "optional ISO date"
}
```

## 5. Eval Fixture 要求

P0 至少需要以下测试文件：

```text
tests/evals/test_jd_parse_eval.py
tests/evals/test_factuality_eval.py
tests/evals/test_realtime_safety_eval.py
tests/evals/test_workspace_privacy_eval.py
tests/evals/test_full_demo_flow_eval.py
```

最低断言：

- JD 解析：must-have 包含 React，nice-to-have 包含 TypeScript，seniority guess 为 junior 或 entry。
- 事实安全：如果来源不存在 AWS 证书，申请包不得出现 “AWS Certified” 等确定性表述。
- 事实安全：编造指标必须进入 `questions_to_confirm`，不能直接写成确定结果。
- 实时提示：formal_assist 不包含 `full_answer` 字段。
- 实时提示：formal_assist 的 hint_level 只能是 `minimal` 或 `outline`。
- Workspace 隐私：拒绝 `../` 路径穿越。
- Demo flow：示例资料完整跑通到 application package、realtime hint、review 和 training tasks。
