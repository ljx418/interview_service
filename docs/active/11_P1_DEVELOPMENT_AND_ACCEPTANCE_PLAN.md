# JobPilot AI P1 开发及验收计划

## 1. 阶段结论

P0 已完成并冻结。P1 可以启动，但必须按本计划执行：每个子阶段先完成计划、验收标准和审计意见，再进入实质开发；每个子阶段完成后必须做端到端验收和 PRD 规格检视。

P1 当前目标：

```text
真实 Provider
→ 核心工具 provider-backed 生成
→ Artifact 编辑 / 版本 / regenerate
→ 正式导出和发布体验
→ P1 冻结验收
```

详细工程实现以 `12_P1_DETAILED_IMPLEMENTATION_SPEC.md` 为准。本文定义阶段和验收顺序，`12` 文档定义数据模型、API、provider、versioning、regenerate、export、eval 文件和打回条件。

## 2. P1 工作包

| 工作包 | 目标 | 主要实现区域 | 验收证据 |
|---|---|---|---|
| WP1 | Provider Runtime | `services/llm/`, `services/api/`, `.env.example` | provider tests、redaction tests、schema failure tests |
| WP2 | 核心工具接入 Provider | `services/tools/jobpilot.py`, prompt contracts, eval fixtures | JD / application provider-backed outputs |
| WP3 | Artifact Versioning | storage schema、artifact APIs、Chatbox cards | version tests、edit/regenerate E2E |
| WP4 | Regenerate 闭环 | tool planner、provider、artifact version | failed regenerate 不改 current version，成功 regenerate 有 parent |
| WP5 | Export Service | export renderer、preflight、download API | Markdown + PDF/DOCX、preflight tests |
| WP6 | Chatbox P1 UX | `apps/chatbox/src/` | provider mode、version display、edit/regenerate/export |
| WP7 | Release Readiness | README、TODO、docs、drawio、CI/Docker | tests/build、quickstart、release checklist |

## 3. WP1 - Provider Runtime

### 范围

建立真实 provider 可选运行路径，同时保留 mock provider 默认基线。

### 实现内容

- Provider factory：
  - `mock`
  - `openai_compatible`
- OpenAI-compatible 配置：
  - base URL
  - model
  - API Key env
  - timeout
  - retry count
- provider request redaction；
- provider invocation log；
- provider error mapping；
- schema validation failure 不写业务表；
- 测试 fake HTTP provider 或 fixture provider。

### 验收

- 无 API Key 时 P0 tests 通过；
- OpenAI provider 未配置时返回 `PROVIDER_NOT_CONFIGURED`；
- timeout 返回 `LLM_FAILED`；
- invalid JSON 返回 `VALIDATION_FAILED`；
- API Key 不进入日志或 SQLite；
- `python3 -m pytest` 通过。

### 审计意见

可自动执行 provider runtime 和 fake provider 测试。真实 API Key 和真实外部调用必须由用户确认。

## 4. WP2 - 核心工具接入 Provider

### 范围

将核心生成路径接入 Provider Runtime，同时保留 mock/heuristic fallback。

### 优先级

1. `job.parse_jd`
2. `application.create_package`
3. `profile.extract_facts`
4. `job.match_profile`
5. `interview.prepare`

### 实现内容

- 每个工具构造 prompt input；
- 调用 provider；
- schema validate；
- 写业务表；
- 写 artifact + version；
- 写 source refs 和 questions_to_confirm；
- provider 失败时返回可恢复错误。

### 验收

- fixture provider 下 JD parse 和 application package 通过；
- malformed output 不写业务表；
- factuality eval 继续通过；
- source refs / questions_to_confirm 不缺失；
- mock provider demo flow 继续通过。

### 审计意见

不能把 provider 输出质量评价简化为“能返回文本”。必须以 schema、source refs、待确认和事实安全为验收核心。

## 5. WP3 - Artifact Versioning

### 范围

实现 artifact 当前版本、历史版本、编辑版本和恢复能力。

### 数据模型

新增或等价实现：

```text
artifact_version
- id
- artifact_id
- workspace_id
- version_number
- status
- content_json
- content_path
- source_refs
- questions_to_confirm
- change_reason
- parent_version_id
- created_by
- created_by_tool
- created_at
```

扩展 artifact：

```text
current_version_id
```

### 验收

- 创建 artifact 时自动创建 v1；
- 编辑 artifact 时创建 v2；
- 当前版本指向 v2；
- v1 仍可读取；
- Chatbox 可恢复当前版本；
- 版本字段不破坏 P0 artifact tests。

### 审计意见

迁移必须可重复、可测试。若涉及不可逆迁移或删除旧字段，必须暂停确认。

## 6. WP4 - Regenerate 闭环

### 范围

将 P0 的 regenerate request 升级为真实新版本生成。

### 实现内容

- 根据 artifact type 找到 source refs 和当前版本；
- 生成 regenerate prompt；
- provider/mock 输出；
- schema validate；
- 创建新 artifact_version；
- parent_version_id 指向旧版本；
- 成功后更新 current_version_id；
- 失败时不改变当前版本。

### 验收

- ApplicationPackage regenerate 成功生成新版本；
- provider failure 不改变 current version；
- regenerate tool invocation 可追踪；
- Chatbox 能展示 regenerate 后版本。

### 审计意见

regenerate 不得覆盖旧版本；不得在失败时产生半成品导出或半成品业务记录。

## 7. WP5 - Export Service

### 范围

强化导出服务，完成正式 PDF 或 DOCX 之一。

### 实现内容

- export preflight；
- Markdown renderer 保持稳定；
- PDF 或 DOCX renderer；
- export snapshot；
- download path guard；
- blocking/warning/optional confirmation 规则；
- export tests。

### 验收

- Markdown 可打开；
- PDF 或 DOCX 可打开；
- blocking confirmation 阻止导出；
- warning confirmation 保留在导出文件；
- 导出文件在 workspace `exports/`；
- workspace 外路径下载被拒绝。

### 审计意见

PDF/DOCX 是 P1 范围，但只要求至少一种正式可用。不得把两种都作为硬门槛，避免过度承诺。

## 8. WP6 - Chatbox P1 UX

### 范围

保持 Chatbox 极简，但补齐 P1 必需控制。

### 实现内容

- provider mode 显示；
- provider 错误提示；
- artifact version 显示；
- edit save new version；
- regenerate 按钮；
- export current version；
- session recovery 包含 version。

### 验收

- 使用 examples 数据手动或自动跑通；
- 刷新后当前版本和导出入口仍可见；
- UI 不出现复杂 dashboard；
- 不在前端保存 API Key。

### 审计意见

Chatbox 只做操作面板和结果展示，不承载 provider prompt 或业务生成逻辑。

## 9. WP7 - Release Readiness

### 范围

让新贡献者能复现 P1。

### 实现内容

- README 更新；
- TODO 更新；
- `.env.example` 更新；
- Docker 或 CI 至少一个路径完善；
- release checklist；
- docs/drawio 与实现状态同步。

### 验收

- README quickstart 可执行；
- tests/build 通过；
- docs/active 文件数保持可审计；
- drawio 和文本镜像一致；
- P1 冻结审计报告完成。

## 10. P1 总体验收路径

```text
mock provider:
创建 workspace
→ 导入 examples 简历和项目 README
→ 通过 Chatbox 触发 Pi 编排
→ 生成事实、项目卡、JD 分析、申请包、面试准备
→ 编辑申请包生成新版本
→ regenerate 生成新版本
→ 导出 Markdown + PDF/DOCX
→ 复盘生成训练任务
→ 恢复 session 和 artifact versions
```

```text
OpenAI-compatible provider:
用户确认 API Key 和外部调用
→ 配置 provider
→ 使用匿名 examples 数据
→ 跑 JD parse 和 application package
→ 验证 schema、source refs、questions_to_confirm
→ 不记录 API Key 和完整敏感原文
```

## 11. 必须执行的验收命令

每个子阶段：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

涉及 HTTP：

```bash
uvicorn services.api.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/api/health
```

涉及 provider：

```text
先使用 fake/fixture provider 自动验收；
真实外部 provider 需要用户确认 API Key 和调用范围。
```

## 12. 当前审计意见

P1 可以启动。没有发现阻塞 P1 计划阶段的致命或重大规格偏差。

当前必须防止三类风险：

- 把外部 provider 调用默认化，破坏本地优先；
- 把 regenerate 做成覆盖旧产物，破坏可追溯；
- 把 MCP/CLI/ASR/会议平台提前塞进 P1，造成范围失控。

处理方式：

- provider 默认仍为 mock；
- versioning 是 regenerate 前置条件；
- P1 文档和 drawio 明确 MCP/CLI/ASR/会议平台为 P2 非目标。

补充 `12_P1_DETAILED_IMPLEMENTATION_SPEC.md` 后，P1 已达到“可完整指导后续开发”的文档水平。后续不需要继续增加主设计文档，除非实质开发中发现新的致命或重大规格偏差。
