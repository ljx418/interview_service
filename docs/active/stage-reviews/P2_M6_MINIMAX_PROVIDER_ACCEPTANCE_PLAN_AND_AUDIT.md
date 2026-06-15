# P2-M6 MiniMax 真实 Provider 受控验收计划与审计

生成日期：2026-06-14  
阶段范围：P2-M6 Real Provider Acceptance  
阶段结论：允许进入受控真实 provider 验收；不得扩大到 P3，不得使用真实个人资料。

## 1. 背景

P2-M4/M5 已完成 examples-guided Chatbox 端到端体验、HTML 报告、截图证据、全量测试和冻结审计。上一轮冻结报告明确标注以下范围未自动验收：

- 真实 API Key；
- 真实外部 Provider 调用；
- 真实个人简历 / JD / transcript；
- 用户上传资料完整手动路径。

用户已在本地 `.env` 中补充 MiniMax API Key，并明确要求验证连通性。已完成最小 POST 连通性检查：

```text
Provider: openai_compatible
Preset: minimax
Base URL: https://api.minimaxi.com/v1
Model: MiniMax-M3
HTTP: 200
Response preview: {"ok":true,"provider":"minimax"}
```

因此，本子阶段只补齐“真实 provider 与本项目结构化输出链路”的受控验收，不改变 P2 产品范围。

## 2. 开发目标

本子阶段目标：

- 保持 mock provider 作为默认可复现验收基线；
- MiniMax 只作为 opt-in provider；
- OpenAI-compatible provider 请求必须携带输出 JSON schema；
- MiniMax preset 必须关闭 thinking，避免 `<think>` 或分析文本污染 JSON；
- 使用 `examples/` 匿名真实感数据完成最小真实 provider E2E；
- 记录真实 provider 已验证和未验证范围；
- 若出现 schema validation 失败、额度失败或 provider 错误，不得伪造通过。

## 3. 开发计划

### WP6.1 Provider Prompt Contract 强化

实现区域：

```text
services/llm/provider.py
tests/evals/test_minimax_provider_config_eval.py
```

要求：

- `OpenAICompatibleProvider` 在 system prompt 中包含 `output_schema.model_json_schema()`；
- 明确要求只返回 JSON object；
- 明确禁止 markdown fence、analysis、`<think>`；
- MiniMax preset 继续发送 `thinking: {"type": "disabled"}`；
- MiniMax preset 不发送未确认兼容的 `response_format`。

验收：

```bash
python3 -m pytest tests/evals/test_minimax_provider_config_eval.py
python3 -m pytest tests/evals/test_p1_provider_runtime_eval.py
```

### WP6.2 MiniMax 真实 Provider 最小 E2E

输入数据：

```text
examples/resumes/transition_frontend_resume.md
examples/projects/todoplus_README.md
examples/jds/junior_frontend_jd.md
```

允许执行：

- 初始化临时 workspace，`llm_provider=openai_compatible`；
- 导入 examples 简历、项目 README；
- 执行 profile fact extraction；
- 创建项目卡；
- 解析 JD；
- 生成 match report；
- 生成 application package；
- 导出 Markdown / DOCX。

不允许执行：

- 使用真实个人资料；
- 默认切换所有用户 workspace provider；
- 自动重试大量真实 provider 请求；
- 继续 P3 的 MCP、CLI、ASR 或会议平台开发。

验收标准：

- provider 状态 `configured=True`；
- 至少一个真实 provider-backed tool invocation 成功；
- JD 解析输出通过 `JobParseOutput` schema；
- 申请包输出通过 `ApplicationPackageOutput` schema；
- 导出 Markdown / DOCX 文件存在；
- provider_invocation 不记录 API Key 或完整敏感 payload；
- 失败时记录失败原因和打回项。

### WP6.3 文档与报告同步

实现区域：

```text
README.md
TODO.md
docs/active/stage-reviews/
```

要求：

- 不把 MiniMax 真实 provider 通过误写成默认验收路径；
- 明确真实 provider 是 opt-in；
- 明确 P2 mock guided flow 仍是开源可复现 baseline；
- 如果真实 provider E2E 未通过，只能标记为残留风险。

## 4. PRD 规格检视

与 P2 PRD 对齐：

- Chatbox-first、本地优先、Agent Tool-first 不变；
- P2 不默认触发真实外部 provider；
- 本次真实 provider 验收使用 examples 匿名真实感数据；
- 验收目标仍是可信、可确认、可导出的求职结果；
- 不新增 MCP、CLI、ASR、会议平台、自动投递或 SaaS。

无重大规格偏差。

## 5. 目标架构检视

与 P2 目标架构对齐：

- Provider Runtime 仍是 Domain Tools 的结构化生成边界；
- Provider 输出必须 schema validation 后才能写库；
- Workflow / Chatbox 不直接拼业务 prompt；
- Artifact、Export 和 Workspace 边界不变；
- MiniMax 只是 OpenAI-compatible provider 的一个 preset，不是独立业务架构分支。

无重大架构偏差。

## 6. 打回条件

出现以下任一情况，本子阶段不得通过：

- MiniMax 真实调用返回额度、鉴权或网络错误；
- provider 输出无法通过 schema validation；
- provider 失败后写入半成品业务记录；
- provider_invocation 或报告中泄露 API Key；
- 导出写出 workspace；
- 把真实 provider 验收失败写成通过；
- 自动开始 P3 范围。

## 7. 审计意见

当前可以进入 WP6.1/WP6.2 实质开发和验收。  
本子阶段不需要用户继续介入，除非出现 API 额度、鉴权、真实个人资料使用、不可逆迁移或 P3 范围扩张。

## 8. 执行记录

### 第一次真实 E2E

结果：未通过。

失败点：

```text
extract_facts → MiniMax provider read timeout
```

处理：

- 不声明真实 provider E2E 通过；
- 补强 provider timeout 错误映射，`socket.timeout` 统一归类为 `LLM_TIMEOUT`；
- 本地 MiniMax timeout 从 30 秒调整为 90 秒；
- 重新执行受控 E2E。

### 第二次真实 E2E

结果：未通过。

进展：

- `profile_extract_facts` 通过；
- `job_parse_jd` 通过；
- `job_match_profile` 通过。

失败点：

```text
application_create_package → VALIDATION_FAILED
```

处理：

- 不声明真实 provider E2E 通过；
- `application_create_package` 的 provider 输入补充 `candidate_output` schema-valid 草稿；
- `_validate_output` 输出字段级 validation 摘要，避免只看到笼统失败。

### 第三次真实 E2E

结果：业务链路通过，但审计未通过。

进展：

- 申请包生成通过；
- Markdown / DOCX 导出通过；
- API Key 未泄露。

失败点：

```text
provider_invocation input_summary 过长，存在记录过多输入摘要的审计风险。
```

处理：

- 收紧 provider invocation 摘要策略；
- 对 `candidate_output`、facts、projects、job 等大对象只记录计数、ID、标题和字段名；
- 增加摘要长度和脱敏回归测试。

### 最终 clean E2E

结果：通过。

证据文件：

```text
docs/reports/P2_M6_MINIMAX_PROVIDER_ACCEPTANCE_RESULT.json
```

验收结果：

```text
workspace_init: completed
import_examples: completed
extract_facts: completed
create_project_card: completed
parse_jd: completed
match_profile: completed
create_application_package: completed
export_package: completed
```

真实 provider invocation：

```text
profile_extract_facts: success
job_parse_jd: success
job_match_profile: success
application_create_package: success
```

导出：

```text
markdown: generated
docx: generated
```

安全检查：

```text
api_key_leaked_in_provider_invocation: false
full_payload_summary_risk: false
```

冻结回归：

```text
python3 -m pytest: 52 passed
npm --prefix apps/chatbox run build: passed
active Markdown docs: 19
drawio XML: parsed, 5 pages
```

## 9. P2-M6 最终审计结论

通过。

可以声明：

- MiniMax 作为 opt-in OpenAI-compatible provider 已完成 examples 受控 E2E；
- provider 输出已通过 schema validation 后写库；
- 申请包 Markdown / DOCX 导出可用；
- provider invocation 未记录 API Key，且输入摘要已收敛；
- mock provider 仍是默认可复现验收基线。

仍不能声明：

- 真实个人简历、真实私有 JD 或真实 transcript 已验收；
- 用户上传资料完整手动路径已验收；
- MiniMax 是默认 provider；
- P2 已支持 MCP、CLI、ASR、会议平台或自动投递。
