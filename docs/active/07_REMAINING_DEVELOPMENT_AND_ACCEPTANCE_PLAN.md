# JobPilot AI P0 开发及验收计划

## 1. 评估结论

本文档最初用于指导 P0 剩余开发。当前 WP1-WP8 已完成实现、阶段审计和真实感示例数据端到端验收；本文件现在作为 P0 完成范围、验收证据和后续开发边界的基准记录。

当前文档体系可以支撑：

- P0 范围内的自动化维护、bugfix、测试补强和文档同步；
- 按 PRD 体验路径做端到端回归验收；
- 对后续 P1/P2 能力做计划和审计。

不应把本文中的 WP1-WP8 再解释为“待开发任务”。后续自动化开发范围以 `09_AUTOMATED_DEVELOPMENT_SCOPE.md` 为准。

## 2. P0 工作包完成状态

| 工作包 | 目标 | 主要产物 | 对应门槛 |
|---|---|---|---|
| WP1 | 建立结构化 LLM Provider 与 Prompt Contract | provider interface、mock provider、schema、校验测试 | 已完成 |
| WP2 | 强化工具层输出和错误处理 | 工具输出 schema 校验、友好错误、source refs | 已完成 |
| WP3 | 增加 Artifact 与 Chat Session 持久化 | artifact 状态、chat session、tool invocation log | 已完成 |
| WP4 | 完成 Chatbox 确认、编辑和导出 UX | 事实卡、产物卡、确认/导出按钮，复杂编辑留 P1 | 已完成 |
| WP5 | 强化申请包生成和导出闭环 | Markdown 下载、待确认标记、导出记录 | 已完成 |
| WP6 | 强化面试准备、故事卡和实时提示安全 | source-cited story cards、formal_assist 边界测试 | 已完成 |
| WP7 | 强化复盘、训练任务和 transcript 策略 | review 输出、training task、保存策略 API | 已完成 |
| WP8 | 建立 eval gates 和发布验收包 | eval fixtures、测试脚本、README 对齐、release checklist | 已完成 |

字段级 schema、source refs、questions_to_confirm、artifact record、PDF 口径和 P0 realtime 硬边界以 `08_P0_PROMPT_AND_OUTPUT_SCHEMAS.md` 为准。

## 3. WP1 - 结构化 LLM Provider 与 Prompt Contract

### 范围

实现 `services/llm/` 下的最小 provider 边界，使工具层不再直接依赖启发式生成逻辑。P0 仍必须保留 mock provider，保证无 API Key 时 demo flow 可稳定运行。

### 实现内容

- 新增 provider interface：`generate_structured(prompt_name, input_payload, output_schema, safety_mode)`。
- 新增 mock provider：返回稳定、可测试、符合 schema 的结构化结果。
- 新增 OpenAI-compatible provider adapter：读取 `.env` 配置，但不要求 P0 默认启用。
- 新增 prompt contract：profile、project、job、application、interview、realtime、review。
- 新增输出 schema：使用 Pydantic model 或 JSON Schema，优先与 API schema 共享。

### 验收

- 无 API Key 时 mock provider 跑通 demo flow。
- provider 返回非法结构时，工具层返回 `VALIDATION_FAILED`。
- prompt contract 中包含来源字段、待确认字段、安全边界说明。
- 新增 malformed provider output 测试。

## 4. WP2 - 工具层输出和错误处理强化

### 范围

把 profile、project、job、application、interview、realtime、review 工具输出统一为结构化结果，并保证写库前校验。

### 实现内容

- 为每类工具定义输入/输出模型。
- 工具输出统一包含 `summary`、`artifact_refs`、`source_refs`、`questions_to_confirm` 中的必要字段。
- 统一错误码：`INVALID_INPUT`、`MISSING_WORKSPACE`、`LLM_FAILED`、`VALIDATION_FAILED`、`EXPORT_FAILED`、`PERMISSION_DENIED`。
- 工具不直接暴露内部堆栈。
- tool invocation log 记录工具名、输入摘要、输出 artifact、错误码和时间。

### 验收

- demo flow 仍通过。
- 针对缺 workspace、缺 job、provider 校验失败、导出失败都有测试。
- 对外材料不存在无来源的确定性经历、数字或证书。

## 5. WP3 - Artifact 与 Chat Session 持久化

### 范围

让 Chatbox 可恢复历史上下文，并让事实、项目卡、匹配报告、申请包、面试准备、实时提示和复盘都有统一状态。

### 建议数据模型

可新增以下轻量表，或用等价字段扩展现有表：

```text
chat_session
- id
- workspace_id
- title
- created_at
- updated_at

chat_message
- id
- session_id
- role
- content
- artifact_refs
- created_at

artifact
- id
- workspace_id
- artifact_type
- source_table
- source_id
- status: draft / needs_confirmation / confirmed / exported
- content_json
- content_path
- source_refs
- questions_to_confirm
- created_by_tool
- created_at
- updated_at

tool_invocation
- id
- workspace_id
- tool_name
- input_summary
- output_refs
- error_code
- created_at
```

说明：

- 如果内容保存在业务表，`content_json` 可为空，但必须通过 `source_table + source_id` 恢复；
- 如果内容是大文本或导出文件，用 `content_path` 指向 workspace 内路径；
- artifact 编辑时必须写回对应业务表或生成新版本；
- regenerate 不覆盖旧 artifact，必须保留版本或 tool invocation 记录。

### 建议接口

```http
GET  /api/chat/sessions
GET  /api/chat/sessions/{session_id}
POST /api/chat/sessions
POST /api/artifacts/{artifact_id}/confirm
PATCH /api/artifacts/{artifact_id}
POST /api/artifacts/{artifact_id}/regenerate
```

### 验收

- 重启前后能恢复 chat session 和已生成产物。
- 产物状态在数据库和 UI 中一致。
- 已确认和未确认产物可区分。

## 6. WP4 - Chatbox 确认、编辑和导出 UX

### 范围

让用户不需要调用 API，也能完成“导入资料 → JD → 申请包 → 导出”的主路径。

### 实现内容

- 文件上传后展示 Document artifact。
- “整理资料”后展示 CareerFact、SkillEvidence、TechProject cards。
- JD 分析后展示 MatchReport card。
- 申请包展示 resume markdown preview、recruiter message、待确认列表。
- 每张关键卡支持确认、编辑、重新生成。
- 申请包卡支持 Markdown 导出下载。

### 验收

- 用示例数据手动跑通主路径。
- 用户在导出前能看到待确认列表。
- 修改事实后，后续申请包使用更新后的事实。
- UI 不出现复杂 dashboard 或求职漏斗大屏。

## 7. WP5 - 申请包生成和导出闭环

### 范围

强化申请包，让它真正成为用户可修改、可导出、可追溯的产物。

### 实现内容

- `application.create_package` 基于 Job、CareerFact、SkillEvidence、TechProject 生成。
- ResumeVersion 保存 source fact refs 和 pending confirmations。
- Markdown 导出保存到 workspace `exports/`。
- Markdown 导出是 P0 硬门槛。
- 简单 PDF 在 P0 是软门槛，可以继续为占位或轻量实现，但必须明确标注 P0 限制。
- PDF 样式不完善不阻塞 P0 发布。
- 导出前检查 artifact 是否仍有高风险待确认项。

### 验收

- Markdown 文件可下载和打开。
- 导出文件名包含岗位/公司或 package id。
- 申请包不包含编造项目、指标、证书、雇主或职位。
- 待确认内容不会在导出中消失。

## 8. WP6 - 面试准备、故事卡和实时提示安全

### 范围

让面试准备和实时提示帮助用户组织表达，但不越过正式面试辅助边界。

### 实现内容

- Interview prep 包含自我介绍、转行动机、项目深挖、技术基础、行为问题、反问问题。
- StoryCard 引用 TechProject 或 CareerFact。
- realtime session 保存 mode 和 save policy。
- formal_assist 模式只允许 minimal/outline。
- realtime hint 包含 question type、recommended project/story、structure、reminder。
- 禁止 formal_assist 返回完整逐字答案。
- P0 realtime 只要求 text question → structured hint。
- P0 不实现真实麦克风 ASR、系统音频采集、会议平台接入或视频解析。

### 验收

- 输入“讲一个你解决技术难题的经历”，系统推荐真实项目并给结构提示。
- formal_assist 测试确认不出现完整答案字段。
- 故事卡和实时提示包含 source refs。
- 不保存原始音视频。

## 9. WP7 - 复盘、训练任务和 Transcript 策略

### 范围

让面试结束后形成可执行的下一步，而不是只输出一段泛泛总结。

### 实现内容

- Review 提取问题清单、用户回答摘要、优点、改进点。
- Review 生成至少 3 个 TrainingTask。
- 支持 thank-you message draft。
- Transcript 保存策略在 UI 和 API 中可见。
- 用户可选择不保存、只保存 transcript、或删除 transcript。

### 验收

- 示例 transcript 可生成 review。
- TrainingTask 写入 SQLite。
- 用户能看到下一步训练计划。
- transcript 删除或不保存策略有测试或手动验收记录。

## 10. WP8 - Eval Gates 和发布验收包

### 范围

建立可重复执行的验收证据，确保开发完成后能证明 PRD 体验和目标架构已经达成。

### Eval fixtures

- JD 解析：示例 JD 能正确区分 must-have / nice-to-have。
- 事实安全：申请包不得编造简历中不存在的项目、证书、数字。
- 实时提示安全：formal_assist 不返回完整逐字答案。
- Workspace 隐私：路径沙箱阻止 workspace 外读写。
- Demo flow：示例简历、项目 README、JD、transcript 完整跑通。

### Eval 测试文件和最低断言

```text
tests/evals/test_jd_parse_eval.py
- assert must_have contains React
- assert nice_to_have contains TypeScript
- assert seniority_guess in ["junior", "entry"]

tests/evals/test_factuality_eval.py
- assert generated package does not contain "AWS Certified" if source absent
- assert invented metrics are placed into questions_to_confirm

tests/evals/test_realtime_safety_eval.py
- formal_assist must not include full_answer
- formal_assist hint_level in ["minimal", "outline"]

tests/evals/test_workspace_privacy_eval.py
- reject ../ path traversal

tests/evals/test_full_demo_flow_eval.py
- full example path reaches application package, realtime hint, review, and training tasks
```

### 必须通过命令

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
curl http://127.0.0.1:8000/api/health
```

### 发布验收

- README 与实际命令一致。
- `.env.example` 覆盖 provider 配置。
- Docker Compose 可启动 API。
- examples 可跑通验收路径。
- active docs 和 drawio 与实际实现一致。

## 11. P0 最终验收路径

使用 `examples/` 中的示例数据，完成：

```text
创建 workspace
→ 上传简历和 TodoPlus README
→ 生成事实、技能证据和项目卡
→ 粘贴 Junior Frontend JD
→ 生成岗位分析
→ 生成申请包
→ 用户确认并导出 Markdown
→ 生成面试准备包和故事卡
→ 输入实时问题并获得结构提示
→ 输入 transcript 并生成复盘和训练任务
```

最终验收通过标准：

- 用户不需要注册登录；
- 数据保存在本地 workspace；
- 申请包可确认、可修改、可导出；
- 面试准备和实时提示引用真实项目；
- formal_assist 不提供隐蔽式逐字答案；
- 复盘生成下一步训练任务；
- 所有自动化测试和前端构建通过；
- active 文档和 drawio 与实现一致。
