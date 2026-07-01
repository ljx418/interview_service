# P6-REAL / P7-post Development and Acceptance Plan

日期：2026-06-30

## 1. 阶段定位

本文件是 P6-REAL 真实 provider 受控验收与 P7-post P5-REAL 真实资料复验的合并版开发及验收计划。它不替代 PRD、目标架构和验收门槛，而是把后续自动化开发或受控执行需要按顺序完成的事项收口到一份可执行清单。

当前阶段仍是文档开发阶段。本文件不授权真实外呼，不读取真实个人资料，不执行 workspace 删除、cleanup apply、migration apply，也不进入 SaaS、ASR、会议平台、自动投递或 MCP/CLI。

## 2. 多轮独立文档审计

### Round A - PRD 规格覆盖审计

审计输入：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`

结论：通过。

理由：

- PRD 已明确当前阶段是 P6-REAL / P7-post 准入，不是业务代码开发；
- PRD 已区分 P5.5 自动化候选、P6/P7 自动化候选、真实 provider 待验收、真实资料待复验；
- 验收门槛已覆盖 provider opt-in、真实资料授权、报告脱敏、虚假验收打回和 P8+ 边界；
- roadmap 已明确当前不能声明最终产品化、真实 provider 质量或真实个人资料路径通过。

残余风险：

- 真实 provider 质量必须等用户授权真实调用后才能验证；
- 真实资料多样性必须等用户提供指定路径后才能验证。

### Round B - 目标架构与代码实体审计

审计输入：

- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`

结论：通过。

理由：

- 目标架构列出了具体代码实体：`apps/chatbox/src/main.tsx`、`services/api/main.py`、`services/chat/core.py`、`services/chat/context.py`、`services/chat/provider_backed.py`、`services/llm/`、`services/profile/candidate.py`、`services/workspace_lifecycle.py`、`scripts/generate_p5_real_data_acceptance.py`；
- drawio 保持 6 页，不超过 8 页，覆盖目标体验、当前与目标架构、代码实体、开发计划、出门门槛、安全边界；
- 图和文本均使用同一状态分层：已实现自动化候选、待真实验收、后续独立阶段；
- 架构不引入不必要的新系统，不把 SaaS、ASR、会议平台、自动投递混入当前阶段。

残余风险：

- 后续若真实 provider 接口形态和现有 provider runtime 不兼容，需要在执行阶段追加 adapter 细化设计；
- 如果用户选择非 OpenAI-compatible provider，需要单独审查 provider SDK、base_url、鉴权方式和错误语义。

### Round C - 验收、证据和虚假验收审计

审计输入：

- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md`
- `docs/active/stage-reviews/P6_REAL_AND_P7POST_DOCUMENTATION_DEVELOPMENT_AUDIT.md`

结论：通过。

理由：

- 验收矩阵已明确 fake provider 记录已具备，受控真实 provider 记录待用户授权后生成；
- traceability matrix 已明确 synthetic personas、examples、脱敏 fixture 不替代真实个人资料路径；
- P6 计划已给出受控外呼执行单，包含 provider、model、API Key 本地配置、最大调用次数、预算、数据类别、timeout/retry/fallback 和报告字段；
- 文档审计已明确文档通过不等于实现通过，drawio 认可不等于功能验收通过。

残余风险：

- 真实外呼成本和隐私风险只能通过执行前用户确认和执行中调用次数限制控制；
- 自动化报告必须继续扫描 API Key、完整 prompt、完整真实资料和 provider raw response，不能只依赖人工自觉。

## 3. 文档支撑度总评

结论：当前文档已经完整支撑本阶段后续开发和受控验收准备。

本阶段开发完成后，可以达成的目标：

- 用户能清楚判断哪些能力已完成自动化候选，哪些仍待真实验收；
- 系统可在用户授权后执行 P6-REAL 小样本真实 provider 验收；
- 系统可在用户提供明确路径后执行 P7-post P5-REAL 真实资料复验；
- 验收报告能明确区分 fake provider、真实 provider、synthetic personas、真实资料、dry-run 和不可逆操作；
- 文档、drawio、报告、测试和审计能防止把未执行路径写成通过。

本阶段开发完成后，仍不能直接达成的目标：

- 不能声明真实 provider 质量通过，除非用户授权并完成真实调用；
- 不能声明真实个人资料路径通过，除非用户提供资料路径并完成脱敏复验；
- 不能声明 SaaS、ASR、会议平台、自动投递、MCP/CLI 或最终产品化通过；
- 不能执行 workspace 删除、cleanup apply 或 migration apply，除非用户单独高风险确认。

## 4. 剩余开发计划大纲

### P6-REAL-0 - 执行前准入审计

目标：确认是否允许进入真实 provider 小样本验收。

必须完成：

- 检查用户是否明确选择 provider 和 model；
- 检查 API Key 是否只存在本地 `.env` 或运行环境变量；
- 检查最大调用次数、预算、timeout、retry 和 fallback；
- 检查允许发送的数据类别和禁止发送的数据类别；
- 检查报告允许展示字段。

出门条件：

- 所有授权字段齐全；
- 未发现默认外呼风险；
- 未发现 API Key 入库、入日志、入报告风险。

### P6-REAL-1 - 真实 provider 小样本对话验收

目标：验证真实 provider opt-in 路径、调用状态、失败降级和报告脱敏。

最小验收路径：

```text
默认进入 Chatbox，不外呼
→ 配置 provider 偏好，不外呼
→ 用户确认本轮数据范围和调用次数
→ 执行 3-10 轮真实 provider 普通求职对话
→ 检查 called / failed / fallback / redaction evidence
→ 验证普通聊天不写 artifact
→ 验证导出和工具仍受 confirmation / preflight 约束
→ 生成中文脱敏 HTML 报告
```

必须生成证据：

- 默认不外呼截图或 headless 证据；
- 配置但未调用证据；
- 调用前确认证据；
- 真实 provider 成功或失败证据；
- fallback 证据；
- provider invocation 脱敏日志；
- 敏感信息扫描结果；
- PRD 规格检视。

打回条件：

- 未授权外呼；
- provider configured 被写成 provider called；
- API Key、完整 prompt、完整真实资料或完整 raw response 出现在报告、日志、截图说明或 fixture；
- provider 失败后会话丢失或无法 fallback；
- 报告把 fake provider transcript 写成真实 LLM 质量。

### P7POST-REALDATA-0 - 真实资料执行前准入审计

目标：确认是否允许进入真实资料复验。

必须完成：

- 用户提供简历/背景资料、项目资料或作品说明、目标 JD 的明确本地路径；
- 用户确认允许展示字段和禁止展示字段；
- 明确脱敏级别；
- 确认只读用户指定路径，不扫描个人目录；
- 确认报告保存位置和截图展示边界。

出门条件：

- 三类核心资料路径或等价最小资料集齐全；
- 报告脱敏策略明确；
- 未发现路径越界、个人目录扫描或长原文泄露风险。

### P7POST-REALDATA-1 - P5-REAL 真实资料复验

目标：用用户授权资料复验资料导入、画像、匹配、申请包、导出 preflight 和报告脱敏。

最小验收路径：

```text
读取用户指定资料路径
→ 导入或解析资料
→ 导入或解析目标 JD
→ 生成 career facts / skill evidence / tech project / match report
→ 刷新 CandidateProfile
→ 检查 source refs、证据强度、待确认项
→ 生成申请包草稿或等价材料
→ 检查 blocking / warning / optional preflight
→ 生成脱敏 P5-REAL HTML 报告
```

必须生成证据：

- 只读指定路径记录；
- 脱敏资料摘要；
- source refs 和待确认项；
- 画像、能力矩阵、项目可信度、岗位短板证据；
- 导出 preflight 证据；
- 敏感信息扫描；
- P5 closure audit。

打回条件：

- 使用 synthetic personas、examples 或脱敏 fixture 替代真实资料复验；
- 自动扫描用户个人目录；
- 报告暴露联系方式、账号、私密链接、完整长原文、API Key 或未授权字段；
- 缺少 source refs 却写成事实；
- 未确认资料被用于正式导出。

### FINAL-REVIEW - 阶段收口验收

目标：确认 P6-REAL 和 P7-post 是否可进入冻结或继续打回。

必须完成：

- 全量 pytest；
- 前端 build；
- drawio XML parse；
- PRD 规格检视；
- 中文 HTML 可视化验收报告；
- 真实 provider / 真实资料证据边界扫描；
- 阶段 final audit。

出门条件：

- P6-REAL 若执行，必须有真实 provider 小样本成功或失败/fallback 证据；
- P7-post 若执行，必须有用户指定真实资料路径和脱敏报告；
- 未执行路径必须明确保持未执行；
- 不得声明 SaaS、ASR、会议平台、自动投递、MCP/CLI 或最终产品化通过。

## 5. 详细验收计划

| 验收域 | 必须验证 | 自动化证据 | 人工确认点 |
| --- | --- | --- | --- |
| 文档一致性 | PRD、架构、门槛、追踪矩阵、drawio 口径一致 | `rg` 口径扫描、drawio parse | 无 |
| 本地基线 | P0-P5/P5.5/P6/P7 自动化候选不退化 | pytest、frontend build | 无 |
| Provider 默认安全 | 默认不外呼，configured 不等于 called | provider policy eval、截图 | 真实外呼前确认 |
| 真实 provider 调用 | 小样本调用、失败降级、脱敏日志 | invocation log、HTML 报告 | provider/model/API Key/预算/次数 |
| 长程连续对话 | 20-50 轮、rolling summary、refresh recovery | long conversation eval、截图 | 真实 provider 质量只在授权后评估 |
| Tool Safety | 普通聊天不写 artifact，工具意图才执行 | chat/artifact/export eval | 无 |
| 真实资料复验 | 只读指定路径、资料解析、画像、source refs、preflight | P5-REAL report、敏感扫描 | 真实资料路径和展示字段 |
| 报告脱敏 | 不出现 API Key、完整 prompt、完整真实资料、raw response | sensitive scan | 报告可展示范围 |
| 高风险边界 | 不执行删除、迁移 apply、SaaS、ASR、会议平台、自动投递 | 审计记录 | 任何高风险执行前确认 |

## 6. 待验收审查结论

需要后续验收时逐项确认：

1. 文档是否仍然明确当前能力边界；
2. P6-REAL 是否获得用户授权；
3. P6-REAL 是否真实发生 provider called，还是只停留在 configured；
4. provider 失败时是否 fallback 且不丢 session；
5. provider invocation log 是否脱敏；
6. P7-post 是否获得真实资料路径授权；
7. P7-post 是否只读指定路径；
8. P5-REAL 报告是否脱敏；
9. source refs 是否支撑画像和申请材料判断；
10. 未执行路径是否保持未执行；
11. 报告是否没有把 fake provider 或 synthetic personas 写成真实验收；
12. 最终出门结论是否没有扩大到 SaaS、ASR、会议平台、自动投递或最终产品化。

## 7. 是否需要 ChatGPT 外部审计

当前结论：不强制需要 ChatGPT 外部审计。

理由：

- 已完成三轮独立审计，且没有发现致命或重大规格偏差；
- 文档已经把真实 provider、真实资料、fake provider、synthetic personas、dry-run 和 P8+ 边界拆开；
- drawio 页数、架构实体、验收门槛和打回条件已经满足当前阶段开发准入；
- 剩余风险主要来自真实授权执行，不能通过更多文档审计完全消除。

如果后续仍希望让 ChatGPT 做外部审计，建议只提供以下 11 个路径，少于 20 个：

1. `docs/active/00_README.md`
2. `docs/active/01_STAGE_PRD.md`
3. `docs/active/02_TARGET_ARCHITECTURE.md`
4. `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
5. `docs/active/04_ACCEPTANCE_GATES.md`
6. `docs/active/06_TRACEABILITY_MATRIX.md`
7. `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
8. `docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md`
9. `docs/active/jobpilot-stage-gap-and-acceptance.md`
10. `docs/active/stage-reviews/P6_REAL_AND_P7POST_DOCUMENTATION_DEVELOPMENT_AUDIT.md`
11. `docs/active/stage-reviews/P6_REAL_P7POST_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`

建议外部审计问题：

```text
请审计 JobPilot AI 当前 P6-REAL / P7-post 文档阶段是否存在规格偏差、虚假验收风险、架构实体不清、验收门槛不足、过度承诺或遗漏的高风险确认点。请特别检查 fake provider 是否被误写成真实 provider，synthetic personas 是否被误写成真实个人资料，workspace dry-run 是否被误写成不可逆操作已执行。
```
