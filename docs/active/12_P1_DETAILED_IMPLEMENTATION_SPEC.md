# JobPilot AI P1 详细实现规格与验收矩阵

## 1. 目的

本文档把 P1 计划转成工程实现可执行规格。它回答：

- 每个工作包要改哪些模块；
- 要新增或扩展哪些数据模型；
- 要提供哪些 API；
- provider、artifact version、regenerate、export 如何失败回滚；
- 每个阶段必须新增哪些测试和验收证据；
- 什么情况下必须打回计划或找用户确认。

P1 实现必须同时满足：

- P0 mock provider 路径不退化；
- Pi Agent Core 继续只接管编排，不直接写库；
- Python Domain Tools 继续负责真实业务写入；
- OpenAI-compatible provider opt-in；
- artifact 编辑和 regenerate 不覆盖旧版本；
- export preflight 阻止高风险导出。

## 2. 当前代码基线

主要模块：

```text
services/api/main.py              FastAPI routes
services/api/schemas.py           API request schemas
services/chat/core.py             KeywordChatCore
services/chat/piagent_adapter.py  Pi bridge adapter
services/chat/pi_node_bridge.mjs  Pi Agent Core bridge
services/llm/provider.py          P0 provider stub
services/llm/contracts.py         P0 output contracts
services/storage/db.py            SQLite schema
services/storage/workspace.py     workspace and path sandbox
services/tools/jobpilot.py        Domain Tools and artifact writes
apps/chatbox/src/main.tsx         Chatbox UI
tests/evals/                      P0 eval gates
```

当前 P1 主要差距：

- `OpenAICompatibleProvider` 仍是 P0 offline stub；
- `.env.example` 使用旧 `OPENAI_*` 命名，需要统一为 `JOBPILOT_OPENAI_*`；
- `artifact` 表缺 `current_version_id`；
- 缺 `artifact_version`；
- 缺 provider invocation / redaction 记录；
- `PATCH /api/artifacts/{artifact_id}` 只更新 artifact metadata，不创建版本；
- `POST /api/artifacts/{artifact_id}/regenerate` 只记录请求，不生成新版本；
- export 尚未执行 P1 preflight；
- PDF 是 P0 软占位，不是 P1 正式导出。

## 3. P1 实现顺序

实现必须按以下顺序推进，除非新的审计意见要求调整：

```text
Step 0 文档冻结和测试基线
→ Step 1 Provider Runtime
→ Step 2 Provider-backed JD / Application
→ Step 3 Artifact Versioning
→ Step 4 Regenerate
→ Step 5 Export Preflight + PDF/DOCX
→ Step 6 Chatbox P1 UX
→ Step 7 Release Readiness
→ Step 8 P1 冻结审计
```

每一步完成后：

- 跑对应 targeted tests；
- 跑 `python3 -m pytest`；
- 跑 `npm --prefix apps/chatbox run build`；
- 如涉及 HTTP，使用 examples 数据跑端到端验收；
- 写阶段审计和 PRD 规格检视。

## 4. 配置与环境变量

P1 统一使用以下变量：

```text
JOBPILOT_DEFAULT_WORKSPACE=.jobpilot_workspace
JOBPILOT_LLM_PROVIDER=mock | openai_compatible | fixture
JOBPILOT_OPENAI_BASE_URL=
JOBPILOT_OPENAI_API_KEY=
JOBPILOT_OPENAI_MODEL=
JOBPILOT_LLM_TIMEOUT_SECONDS=30
JOBPILOT_LLM_MAX_RETRIES=1
JOBPILOT_LLM_LOG_PAYLOADS=0
JOBPILOT_CHAT_CORE=keyword | piagent
JOBPILOT_CHAT_CORE_STRICT=0 | 1
```

规则：

- 默认 `JOBPILOT_LLM_PROVIDER=mock`；
- `fixture` 只用于自动测试，不访问网络；
- `openai_compatible` 需要用户确认 API Key 和调用范围；
- API Key 不写入 SQLite、tool logs、provider logs、HTTP error response、README、测试快照；
- `JOBPILOT_LLM_LOG_PAYLOADS=1` 只能用于本地调试，不进入自动验收。

## 5. Provider Runtime 规格

### 5.1 目标文件

```text
services/llm/provider.py
services/llm/contracts.py
services/llm/prompts/
services/api/main.py
services/api/schemas.py
tests/evals/test_p1_provider_runtime_eval.py
tests/evals/test_p1_provider_redaction_eval.py
```

### 5.2 Provider 接口

目标接口：

```python
class LLMProvider:
    def generate_structured(
        self,
        prompt_name: str,
        input_payload: dict,
        output_schema: type[BaseModel],
        safety_mode: str = "normal",
        request_options: dict | None = None,
    ) -> dict:
        ...
```

Provider 返回前必须完成：

- JSON parse；
- schema validation；
- output normalization；
- error mapping。

### 5.3 Provider 类型

`MockProvider`：

- 默认；
- 不访问网络；
- 使用 deterministic fixture；
- 支撑 P0 / P1 自动验收。

`FixtureProvider`：

- 只用于测试；
- 从 `tests/fixtures/provider/` 读取响应；
- 可模拟 timeout、invalid JSON、schema mismatch。

`OpenAICompatibleProvider`：

- opt-in；
- 支持 base URL / model / API key；
- 支持 timeout 和 retry；
- 只发送 redacted 或最小必要 payload；
- 返回 JSON object；
- 不默认进入 CI。

### 5.4 Provider 错误码

```text
PROVIDER_NOT_CONFIGURED
LLM_TIMEOUT
LLM_FAILED
PROVIDER_BAD_RESPONSE
VALIDATION_FAILED
PROVIDER_RATE_LIMITED
```

API 层映射为统一错误结构：

```json
{
  "ok": false,
  "error_code": "LLM_FAILED",
  "message": "模型调用失败，请稍后重试或切换 mock provider。",
  "recoverable": true,
  "suggested_action": "检查 provider 配置、重试，或切换到 mock provider。"
}
```

### 5.5 Provider 日志

新增或等价实现：

```text
provider_invocation
- id
- workspace_id
- provider_name
- prompt_name
- schema_name
- input_summary
- redaction_applied
- status: success | failed
- error_code
- latency_ms
- created_at
```

禁止记录：

- API Key；
- 完整简历；
- 完整 JD；
- 完整 transcript；
- 完整 provider raw response。

## 6. Prompt Contract 接入规格

P1 必须补齐以下 prompt 的 provider-backed contract：

| prompt_name | 输出模型 | P1 优先级 |
|---|---|---|
| `job_parse_jd` | `JobParseOutput` | P1-M2 必做 |
| `application_create_package` | `ApplicationPackageOutput` | P1-M2 必做 |
| `profile_extract_facts` | 新增 `ProfileExtractFactsOutput` | P1-M2 |
| `job_match_profile` | `MatchReportOutput` | P1-M2 |
| `interview_prepare` | 新增 `InterviewPrepOutput` | P1-M2 |

每个 prompt 必须有：

```text
input schema
output schema
safety_mode
source_ref_policy
confirmation_policy
redaction_policy
fixture_success
fixture_malformed
fixture_low_confidence
```

Prompt 输入必须使用结构化 payload，不允许拼接不可审计的大段 prompt 字符串作为唯一实现。

## 7. 数据模型与迁移规格

### 7.1 artifact 扩展

新增字段：

```text
artifact.current_version_id TEXT
```

迁移规则：

- 使用 idempotent migration；
- 如果字段已存在，不重复添加；
- 对旧 artifact 创建 v1；
- v1 内容从 artifact.content_json/content_path/source_refs/questions_to_confirm 恢复；
- 设置 artifact.current_version_id = v1.id；
- 不删除旧字段。

### 7.2 artifact_version

新增表：

```text
artifact_version
- id TEXT PRIMARY KEY
- artifact_id TEXT NOT NULL
- workspace_id TEXT NOT NULL
- version_number INTEGER NOT NULL
- status TEXT NOT NULL
- content_json TEXT
- content_path TEXT
- source_refs TEXT NOT NULL DEFAULT '[]'
- questions_to_confirm TEXT NOT NULL DEFAULT '[]'
- change_reason TEXT NOT NULL
- parent_version_id TEXT
- created_by TEXT NOT NULL
- created_by_tool TEXT
- created_at TEXT NOT NULL
```

约束：

- 同一 artifact 的 `version_number` 单调递增；
- 旧版本不可覆盖；
- current version 只能指向同 workspace 的版本；
- regenerate 必须写 `parent_version_id`。

### 7.3 provider_invocation

见第 5.5 节。

### 7.4 迁移测试

必须新增：

```text
tests/evals/test_p1_schema_migration_eval.py
```

最低断言：

- 空库 init 后存在 `artifact_version`；
- 旧 artifact 可迁移出 v1；
- 重复打开 workspace 不重复创建字段或重复 v1；
- current_version_id 指向存在版本。

## 8. API 规格

### 8.1 Provider API

```http
GET /api/provider/status?workspace_id=...
```

返回：

```json
{
  "provider": "mock",
  "configured": true,
  "external_calls_enabled": false,
  "model": null,
  "redaction": true
}
```

```http
POST /api/provider/check
```

用途：

- mock / fixture 可自动检查；
- openai-compatible 只能在用户确认后检查；
- 不发送真实简历/JD。

### 8.2 Artifact Version API

```http
GET /api/artifacts/{artifact_id}/versions?workspace_id=...
GET /api/artifacts/{artifact_id}/versions/{version_id}?workspace_id=...
PATCH /api/artifacts/{artifact_id}
POST /api/artifacts/{artifact_id}/regenerate
POST /api/artifacts/{artifact_id}/versions/{version_id}/restore
```

`PATCH /api/artifacts/{artifact_id}` P1 行为：

- validate content；
- create new version；
- write back business table or create new business record；
- update current_version_id；
- return artifact with current version。

### 8.3 Export API

当前：

```http
POST /api/application/export-package
GET /api/application/download
```

P1 扩展：

- `formats` 支持 `markdown` 和 `pdf` 或 `docx`；
- 可选 `artifact_version_id`；
- 默认导出 current version；
- export 前执行 preflight；
- preflight 失败返回 `EXPORT_PRECHECK_FAILED`。

## 9. Domain Tool 修改规格

### 9.1 job.parse_jd

P1 行为：

- mock provider 继续 deterministic；
- openai-compatible provider 构造 JD parse input；
- provider output validate as `JobParseOutput`；
- 写 `job` 表；
- 写 artifact + version；
- 写 provider_invocation 和 tool_invocation。

失败：

- provider failed：不写 job；
- validation failed：不写 job；
- 返回 recoverable error。

### 9.2 application.create_package

P1 行为：

- 读取 job、facts、skill evidence、projects；
- 构造最小必要 provider input；
- output validate as `ApplicationPackageOutput`；
- blocking confirmation 标记为不可导出；
- 写 resume_version / application_package；
- 写 artifact + version。

失败：

- 不生成 application_package；
- 不更新 current artifact；
- 记录 tool_invocation error。

### 9.3 artifact.update

P1 行为：

- 从直接 update artifact content 改为 create version；
- 对 supported source_table 写回业务表；
- unsupported source_table 只能更新 artifact version，不能伪称业务表已更新。

支持优先级：

1. `application_package`
2. `resume_version`
3. `career_fact`
4. `tech_project`

### 9.4 artifact.regenerate

P1 行为：

- 找 current version；
- 基于 source_refs 和 artifact_type 构造 regenerate input；
- 调 provider/mock；
- validate；
- create new version；
- success 后更新 current_version_id。

必须保证：

- 失败不改 current；
- 旧版本仍可读；
- parent_version_id 非空。

## 10. Export Preflight 规格

Preflight 输入：

```text
workspace_id
package_id
artifact_id optional
artifact_version_id optional
formats
```

检查：

- package 属于 workspace；
- version 属于 workspace；
- version 是 current 或用户显式选择；
- source_refs 非空；
- blocking questions_to_confirm 为空或已解决；
- warning confirmations 写入导出文件；
- export path 在 workspace `exports/` 内。

失败错误：

```text
EXPORT_PRECHECK_FAILED
EXPORT_FAILED
PERMISSION_DENIED
```

P1 正式导出选择：

- 推荐先实现 PDF；
- 如 PDF 依赖过重，则实现 DOCX；
- P1 hard gate 是 PDF/DOCX 至少一种正式可打开，不要求两种都完成。

## 11. Chatbox P1 UX 规格

必须展示：

- provider mode；
- provider recoverable error；
- artifact status；
- current version number；
- change reason；
- questions_to_confirm 分级；
- edit action；
- regenerate action；
- export current version action。

不允许：

- 前端保存 API Key；
- 前端拼 prompt；
- 前端绕过 preflight 直接下载；
- 前端隐藏 blocking confirmation。

## 12. 测试与验收矩阵

P1 必须新增或更新：

```text
tests/evals/test_p1_provider_runtime_eval.py
tests/evals/test_p1_provider_redaction_eval.py
tests/evals/test_p1_provider_tool_integration_eval.py
tests/evals/test_p1_schema_migration_eval.py
tests/evals/test_p1_artifact_versioning_eval.py
tests/evals/test_p1_regenerate_eval.py
tests/evals/test_p1_export_preflight_eval.py
tests/evals/test_p1_full_flow_eval.py
```

最低断言：

| 测试 | 最低断言 |
|---|---|
| provider runtime | missing key -> PROVIDER_NOT_CONFIGURED；timeout -> LLM_FAILED；invalid JSON -> VALIDATION_FAILED |
| provider redaction | API Key、完整简历、完整 JD 不出现在 logs / SQLite |
| provider tool integration | JD parse 和 application package 可用 fixture provider 写库 |
| schema migration | artifact_version 可重复迁移，current_version_id 有效 |
| artifact versioning | edit creates v2，v1 still readable |
| regenerate | success creates child version；failure keeps current |
| export preflight | blocking confirmation prevents export；warning remains in file |
| full flow | examples 数据跑通 edit -> regenerate -> export -> recovery |

每个 WP 的最低命令：

```bash
python3 -m pytest tests/evals/test_p1_*.py
python3 -m pytest
npm --prefix apps/chatbox run build
```

## 13. HTTP E2E 验收脚本要求

P1 至少需要一个脚本或测试覆盖：

```text
创建 workspace
→ 导入 examples resume/project
→ 创建 chat session
→ Pi 编排整理资料
→ Pi 编排 JD 分析
→ 生成申请包
→ 编辑申请包生成 v2
→ regenerate 生成 v3
→ export current version Markdown + PDF/DOCX
→ GET chat session 恢复 messages/artifacts/versions
```

如果使用真实 provider：

```text
必须先用户确认 API Key 和调用范围；
只使用 examples 匿名真实感数据；
记录验收结果时不得输出 API Key 或完整 provider payload。
```

## 14. 阶段审计模板

每个 P1 子阶段完成后，在 `docs/active/stage-reviews/` 或 P1 冻结报告中记录：

```text
目标
计划
实现文件
验收标准
测试结果
HTTP E2E 结果
PRD 规格检视
目标架构检视
残留风险
是否允许进入下一阶段
```

不允许只写“测试通过”。必须说明是否存在：

- 规格偏差；
- 虚假验收风险；
- P1 非目标混入；
- 高风险流程被自动执行。

## 15. 打回计划条件

出现以下任一情况，必须停止开发、回到计划阶段：

- provider 默认访问外部网络；
- provider failure 写入半成品业务表；
- API Key 或完整敏感原文进入日志/数据库；
- artifact edit/regenerate 覆盖旧版本；
- export preflight 可被绕过；
- P0 mock demo flow 失败；
- formal_assist 输出逐字答案；
- MCP/CLI/ASR/会议平台进入 P1 hard gate；
- P1 文档、drawio 和实现不一致。

## 16. P1 文档支撑性审计

补齐本文档后，P1 文档体系可以支撑完整开发：

```text
01_STAGE_PRD
→ 02_TARGET_ARCHITECTURE
→ 03_MILESTONES_AND_DELIVERY_PLAN
→ 04_ACCEPTANCE_GATES
→ 06_TRACEABILITY_MATRIX
→ 11_P1_DEVELOPMENT_AND_ACCEPTANCE_PLAN
→ 12_P1_DETAILED_IMPLEMENTATION_SPEC
→ jobpilot-stage-gap-and-acceptance.drawio
```

仍需在实质开发过程中按子阶段补充 stage review，但不需要在 P1 开工前继续增加主设计文档。
