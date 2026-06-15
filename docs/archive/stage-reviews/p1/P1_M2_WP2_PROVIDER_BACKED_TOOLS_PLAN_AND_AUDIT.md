# P1-M2 / WP2 Core Tools Provider-backed 开发计划与审计

## 1. 阶段目标

本阶段把核心求职工具接入 P1-M1 已完成的 Provider Runtime。目标不是提升模型质量评价，而是证明核心工具具备稳定的 provider-backed 结构化生成路径，并保持 P0 mock 基线不退化。

必须覆盖：

- `profile.extract_facts`
- `job.parse_jd`
- `job.match_profile`
- `application.create_package`
- `interview.prepare`

验收重点：

- JD 解析；
- 申请包生成；
- source refs；
- questions_to_confirm；
- provider 失败不写半成品业务数据；
- mock provider 默认路径继续通过。

## 2. 开发范围

代码范围：

- `services/llm/contracts.py`
- `services/tools/jobpilot.py`
- `tests/evals/test_p1_provider_tool_integration_eval.py`

本阶段不改 Chatbox UX，不引入 artifact_version，不做 regenerate，不做 PDF/DOCX。

## 3. 实现计划

1. 补齐 P1 contract：
   - `ProfileExtractFactsOutput`
   - `InterviewPrepOutput`
2. 在 Domain Tools 内增加 provider helper：
   - 根据 workspace `llm_provider` 选择 provider；
   - `mock` 继续走 P0 deterministic 路径；
   - `fixture` 使用 deterministic fixture output；
   - `openai_compatible` 使用结构化 input，失败不写业务表。
3. 接入五个核心工具：
   - provider 返回 schema validated output 后再写库；
   - source refs 和 questions_to_confirm 必须保留；
   - provider failure / validation failure 不写业务表、不写 artifact。
4. 增加 eval：
   - fixture provider 下 JD parse 写库；
   - fixture provider 下 application package 写库；
   - malformed provider output 不写 job；
   - source refs 和 questions_to_confirm 不缺失。

## 4. 验收标准

必须通过：

- `python3 -m pytest tests/evals/test_p1_provider_tool_integration_eval.py`
- `python3 -m pytest`
- `npm --prefix apps/chatbox run build`

最低断言：

- fixture provider 下 `job.parse_jd` 生成 job 和 artifact；
- fixture provider 下 `application.create_package` 生成 package 和 artifact；
- output schema mismatch 返回 `VALIDATION_FAILED`；
- validation failure 后 `job` 表不新增记录；
- P0 mock demo flow 继续通过。

## 5. PRD 规格检视

完成后必须证明：

- provider-backed 工具仍由 Python Domain Tools 负责业务写入；
- Pi Agent Core 没有直接写库；
- Chatbox 没有拼 prompt；
- provider 输出先 schema validate；
- source refs 和待确认项没有被省略；
- 不确定内容仍进入 questions_to_confirm。

## 6. 审计意见

当前计划没有新增致命或重大规格偏差。可以进入 P1-M2 / WP2 实质开发。

必须暂停找用户确认的情况：

- 使用真实 API Key 或真实外部 provider 调用；
- 使用真实个人简历、真实私有 JD 或真实 transcript；
- 试图把所有工具一次性替换为真实 provider 并删除 P0 heuristic/mock 基线。

## 7. 实现结果

已完成：

- 新增 `ProfileExtractFactsOutput`；
- 新增 `InterviewPrepOutput`；
- `profile.extract_facts` 支持非 mock provider-backed 路径；
- `job.parse_jd` 支持 provider-backed 路径，provider validate 成功后才写 `job`；
- `job.match_profile` 支持 provider-backed 路径；
- `application.create_package` 支持 provider-backed 路径，provider validate 成功后才写 `resume_version` / `application_package`；
- `interview.prepare` 支持 provider-backed 最小路径；
- 新增 `tests/evals/test_p1_provider_tool_integration_eval.py`。

未执行：

- 未使用真实 API Key；
- 未发起真实外部 provider 调用；
- 未删除 P0 heuristic/mock 基线；
- 未实现 artifact_version / regenerate / PDF-DOCX。

## 8. 验收结果

自动化测试：

```text
python3 -m pytest tests/evals/test_p1_provider_tool_integration_eval.py
结果：4 passed

python3 -m pytest
结果：35 passed

npm --prefix apps/chatbox run build
结果：通过
```

真实感数据：

- 使用 `examples/resumes/transition_frontend_resume.md`；
- 使用 `examples/projects/todoplus_README.md`；
- 使用 `examples/jds/junior_frontend_jd.md`；
- 使用本地 `fixture` provider，不访问外部网络。

## 9. PRD 规格检视

通过：

- 核心工具具备 provider-backed 结构化生成路径；
- mock provider 默认路径继续通过；
- provider 输出先 schema validate 再写业务表；
- JD 和申请包保留 source refs；
- JD 和申请包保留 questions_to_confirm；
- provider validation failure 不写半成品 `job`；
- Chatbox、Pi Agent Core 未承担业务写库职责。

未完成但不属于本阶段：

- artifact versioning；
- regenerate 新版本；
- export preflight 和 PDF/DOCX；
- Chatbox provider mode / version UX。

## 10. 目标架构检视

通过。P1-M2 已把目标架构中的 `Domain Tool Executor → Provider Runtime → Prompt Contract Layer` 主链路接通，同时保持：

- Domain Tools 是业务写入边界；
- Provider Runtime 不直接写业务表；
- Provider failure 不产生半成品核心业务记录；
- Pi Agent Core 仍只负责 intent/tool_plan。

## 11. 残留风险

- 真实 OpenAI-compatible provider 的输出质量和 prompt 质量尚未人工验收；
- 当前 fixture provider 证明的是 contract 和事务边界，不代表真实模型文案质量；
- `interview.prepare` provider-backed 路径为最小实现，后续如需深度故事卡生成应另行计划。

## 12. 是否允许进入下一阶段

允许进入 `P1-M3 / WP3+WP4: Artifact Versioning + Regenerate`。

当前没有新增致命或重大规格偏差，也没有虚假验收风险；本阶段结论仅代表核心工具 provider-backed contract 路径通过，不代表真实外部 provider 文案质量已验收。
