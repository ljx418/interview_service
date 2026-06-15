# P1-M1 / WP1 Provider Runtime 开发计划与审计

## 1. 阶段目标

本阶段只实现 Provider Runtime 基础设施，不把核心业务工具全面切到真实 provider。目标是让 P1 后续 WP2 可以在稳定、可测试、可回滚的 provider 边界上开发。

必须保持：

- `mock` 是默认 provider；
- 无 API Key、无外部网络时 P0 demo flow 和 eval 继续可用；
- OpenAI-compatible provider 只能 opt-in；
- provider 输出必须 schema validate 后才返回调用方；
- provider 失败、JSON 解析失败或 schema 失败不得写半成品业务数据；
- API Key、完整简历、完整 JD、完整 transcript 和完整 raw response 不进入日志或 SQLite。

## 2. 开发范围

代码范围：

- `services/llm/provider.py`
- `services/api/main.py`
- `services/api/schemas.py`
- `services/storage/db.py`
- `.env.example`
- `tests/evals/test_p1_provider_runtime_eval.py`
- `tests/evals/test_p1_provider_redaction_eval.py`

本阶段允许新增轻量 helper，但不引入新的第三方依赖。

## 3. 非目标

本阶段不做：

- 真实业务工具 provider-backed 生成；
- artifact_version；
- regenerate 新版本；
- PDF/DOCX 正式导出；
- Chatbox P1 UX；
- MCP、CLI、ASR、会议平台；
- 自动读取或调用用户真实 API Key。

## 4. 实现计划

1. 扩展 Provider Runtime：
   - `MockProvider`
   - `FixtureProvider`
   - `OpenAICompatibleProvider`
   - provider factory
   - timeout / retry
   - JSON parse
   - schema validation
   - error code normalization

2. 增加 redaction 和 input summary：
   - 对 API Key、长文本、email、疑似 token 做摘要/脱敏；
   - provider logs 只记录摘要，不记录完整 payload。

3. 增加 provider_invocation 表：
   - `provider_name`
   - `prompt_name`
   - `schema_name`
   - `input_summary`
   - `redaction_applied`
   - `status`
   - `error_code`
   - `latency_ms`
   - `created_at`

4. 增加 API：
   - `GET /api/provider/status`
   - `POST /api/provider/check`

5. 更新 `.env.example`：
   - 使用 `JOBPILOT_OPENAI_*` 命名；
   - 不包含真实 key。

## 5. 验收标准

必须通过：

- missing OpenAI API Key 返回 `PROVIDER_NOT_CONFIGURED`；
- timeout 返回 `LLM_TIMEOUT` 或 API 层可恢复 `LLM_FAILED`；
- invalid JSON 返回 `PROVIDER_BAD_RESPONSE`；
- schema mismatch 返回 `VALIDATION_FAILED`；
- `provider_invocation` 不包含 API Key、完整简历、完整 JD、完整 transcript；
- `mock` 默认路径仍能通过 P0 回归；
- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过。

## 6. 端到端验收

使用 examples 匿名真实感数据，不使用用户真实简历或真实 API Key：

```text
创建 workspace
→ 查询 provider/status，确认默认 mock
→ provider/check mock 通过
→ provider/check openai-compatible 在无 key 时返回可恢复错误
→ fake/fixture provider 返回结构化输出并 schema validate
→ provider_invocation 只记录脱敏摘要
→ P0 demo flow 回归通过
```

## 7. PRD 规格检视

本阶段对应 P1 PRD 的 Provider 与 Prompt Contract 范围。完成后必须证明：

- 本地优先没有退化；
- mock provider 仍可无 key 验收；
- openai-compatible 是 opt-in；
- provider 错误可理解、可恢复；
- provider 输入脱敏和输出 schema validation 已进入代码；
- 未把真实 provider 调用默认化。

## 8. 审计意见

当前计划没有新增致命或重大规格偏差。可以进入 P1-M1 / WP1 实质开发。

必须暂停找用户确认的情况：

- 需要真实 API Key；
- 需要真实外部模型调用；
- 需要真实个人资料；
- 需要不可逆数据库迁移；
- 试图把 provider-backed 工具扩展到 WP2 之外。

## 9. 实现结果

已完成：

- 扩展 `LLMProvider.generate_structured`，兼容现有调用并支持 `request_options`；
- 实现 `ProviderError`、错误码归一、JSON parse、schema validation；
- 实现 `MockProvider`、`FixtureProvider`、`OpenAICompatibleProvider`；
- 实现 provider input summary 和 redaction；
- 新增 `provider_invocation` 表；
- 新增 `GET /api/provider/status`；
- 新增 `POST /api/provider/check`；
- 更新 `.env.example` 为 `JOBPILOT_OPENAI_*` 变量；
- 新增 P1 provider runtime 和 redaction eval。

未执行：

- 未使用真实 API Key；
- 未发起真实外部模型调用；
- 未使用真实个人资料；
- 未实现 WP2 的核心业务工具 provider-backed 生成。

## 10. 验收结果

自动化测试：

```text
python3 -m pytest tests/evals/test_p1_provider_runtime_eval.py tests/evals/test_p1_provider_redaction_eval.py
结果：7 passed

python3 -m pytest
结果：31 passed

npm --prefix apps/chatbox run build
结果：通过
```

HTTP E2E：

```text
GET /api/health
结果：200 OK

GET /api/provider/status
结果：mock provider, configured=true, external_calls_enabled=false

POST /api/provider/check {"provider":"mock"}
结果：200 OK，返回 schema validated sample

POST /api/provider/check {"provider":"openai_compatible","confirm_external_call":true}
结果：400 PROVIDER_NOT_CONFIGURED，recoverable=true
```

## 11. PRD 规格检视

通过：

- mock provider 仍是默认可验收路径；
- OpenAI-compatible provider 仍是 opt-in；
- 未配置真实 provider 时返回可理解、可恢复错误；
- provider 输出先 schema validation；
- provider_invocation 只记录脱敏摘要；
- API Key、完整简历、完整 JD、完整 transcript 未进入日志或 SQLite；
- P0 demo flow 和 eval 未退化。

未完成但不属于本阶段：

- 核心工具 provider-backed 生成；
- artifact versioning；
- regenerate；
- PDF/DOCX 正式导出；
- Chatbox P1 UX。

## 12. 目标架构检视

通过。P1-M1 已补齐目标架构中的 `LLM Provider Runtime` 基础层，并保持边界：

- Provider Runtime 不直接写业务表；
- Domain Tools 仍是后续业务写入边界；
- Pi Agent Core 未被改成持久化层；
- Chatbox 未承担 provider prompt 或业务生成逻辑。

## 13. 残留风险

- OpenAI-compatible provider 的真实外部调用仍未验收，必须等用户确认 API Key 和调用范围；
- WP2 需要把 JD / application 等工具接入 provider runtime，并继续证明失败不写半成品业务数据；
- 当前 provider/check 只使用 schema sample，不代表真实求职产物质量。

## 14. 是否允许进入下一阶段

允许进入 `P1-M2 / WP2: Core Tools Provider-backed`。

当前没有新增致命或重大规格偏差，也没有虚假验收风险；本阶段结论仅代表 Provider Runtime 通过，不代表 P1 已整体实现。
