# P6+P7 文档覆盖度审计与开发准入结论

日期：2026-06-27
阶段：P6+P7 长程连续对话、真实 provider opt-in 与产品化 Beta
结论：通过，仍带高风险确认门。当前文档已经足以支撑进入 P6-M1/P7-M1 等后续自动化开发准备；本阶段开发完成后可以支撑预设目标和出门验收，前提是每个子阶段严格执行“先计划和审计、再开发、再端到端验收和 PRD 规格检视”的闭环，并且真实 provider、真实个人资料、workspace 删除、不可逆迁移等高风险动作继续由用户确认。2026-06-29 复审时发现 P6-M0/P7-M0 的执行细则分散在多个文档中，已补入 `docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md` 第 9 节。

## 1. 审计范围

本次审计覆盖以下文档和图：

- `README.md`
- `TODO.md`
- `docs/active/00_README.md`
- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`
- `docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`

代码结构只做只读匹配检查，不进入代码开发。已确认当前仓库存在这些关键基线实体：

- `apps/chatbox/src/main.tsx`
- `apps/chatbox/src/styles.css`
- `services/api/main.py`
- `services/chat/core.py`
- `services/llm/provider.py`
- `services/storage/workspace.py`
- `services/tools/jobpilot.py`
- `scripts/browser_tools/`
- `tests/evals/`

## 2. 文档覆盖结论

| 覆盖项 | 当前文档 | 结论 |
| --- | --- | --- |
| 阶段目标 | PRD、README、TODO、roadmap 已统一为 P6+P7；P5-REAL/P5-Freeze 为 P7-post 冻结延期复验 | 充分 |
| 用户目标体验 | PRD 已定义 provider opt-in、20-50 轮长程连续对话、失败降级、workspace lifecycle、diagnostics、P7-post 复验 | 充分 |
| 非目标和边界 | PRD、验收门槛、roadmap、drawio 明确不做 SaaS、ASR、会议平台、自动投递、MCP/CLI、默认外呼和真正无限上下文 | 充分 |
| 架构实体 | 目标架构和 drawio 已映射 Chatbox、FastAPI、ChatCore、Long Context Manager、Provider Policy Gate、Invocation Log、Workspace Lifecycle、Diagnostics | 充分 |
| 接口契约 | 目标架构已给 provider status/preferences/consent、chat context、diagnostics、backup、cleanup dry-run、migration dry-run 等最小契约；`19` 第 9 节补齐 provider 状态机、long context 持久化模型、invocation log schema 和 P7 lifecycle checklist | 充分 |
| 开发计划 | 里程碑已拆分 P6-M0 到 P6-Freeze、P7-M0 到 P7-Freeze、P7-post P5 revalidation | 充分 |
| 验收门槛 | 验收门槛覆盖 provider 默认安全、provider-backed chat、long context、tool safety、privacy、visual acceptance、workspace lifecycle、diagnostics、P5 复验 | 充分 |
| 测试策略 | 追踪矩阵和验收门槛已定义 provider policy eval、fake/real provider controlled eval、long conversation eval、tool safety、sensitive scan、lifecycle eval、diagnostics/report eval | 充分，具体测试文件名可在实现时按仓库命名 |
| drawio | 6 页，未超过 8 页；图中包含目标架构差异、代码实体、开发验收计划、里程碑、门槛和安全边界 | 充分 |
| 虚假验收防护 | 多处明确 configured 不等于 called、20-50 轮不等于真正无限、synthetic personas 不能替代 P5-REAL、文档通过不等于实现通过 | 充分 |

## 3. 能否支撑本阶段全部开发

结论：可以支撑，但必须按子阶段推进。

原因：

- P6 的关键不确定性已经被拆成可验收工作包：Provider opt-in UX、Provider-backed Chat Adapter、Long Context Manager、Tool Safety、Privacy/Redaction/Invocation Log、Visual Acceptance。
- P7 的产品化 Beta 能力已经被拆成 workspace lifecycle、diagnostics/release/rollback、support/privacy audit、P7-Freeze。
- 所有高风险能力都有明确确认门：真实 API Key、真实 provider、真实个人资料、workspace 删除、不可逆迁移、ASR/会议平台/自动投递/SaaS。
- 文档把“无限对话”修正为“20-50 轮长程连续对话”，并定义 rolling summary、context snapshot、refresh recovery、fallback 和来源边界。
- 文档明确 P5-REAL/P5-Freeze 是 P7-post 复验，不再阻塞 P6/P7，也不能被写成已通过。
- 2026-06-29 补齐的详细执行细则已经把 P6-M0/P7-M0 从“待细化文档动作”收敛为可执行 checklist；后续仍需为每个开发子阶段生成独立阶段审计记录，但不需要继续扩大主设计文档。

## 4. 能否达成预设目标并通过出门验收

结论：有条件可以。

可达成目标：

- 用户默认在本地/mock 模式下使用 Chatbox，不会因为配置 provider 就自动外呼。
- 用户可以 opt-in 使用真实 provider 聊天，并明确看到本轮是否外呼。
- Chatbox 支持可验收的长程连续对话：20-50 轮、滚动摘要、上下文快照、刷新恢复和失败降级。
- provider-backed chat 不绕过 artifact confirmation、`questions_to_confirm` 和 export preflight。
- P7 提供 workspace 生命周期、诊断报告、发布/部署/回滚、支持流程和隐私审计。
- P7 完成后可以进入 P7-post P5-REAL/P5-Freeze 复验。

不能由文档本身消除的条件：

- 没有用户确认和本地 `.env` 配置时，不能执行真实 provider 验收。
- 没有用户提供真实/脱敏资料路径时，P7-post P5-REAL 只能保持未执行。
- workspace 删除和迁移 apply 只能在用户明确确认后执行；默认开发和验收只做 dry-run。

## 5. 残余风险和控制

| 风险 | 级别 | 是否已被文档消减 | 控制方式 |
| --- | --- | --- | --- |
| 默认外呼真实 provider | 致命 | 已消减 | Provider Policy Gate、configured/called 状态、未确认不外呼 eval |
| API Key 泄露 | 致命 | 已消减 | 只读 `.env`，前端不保存，敏感扫描，报告脱敏 |
| 把 20-50 轮写成真正无限聊天 | 重大 | 已消减 | PRD、验收门槛和 drawio 均禁止真正无限上下文声明 |
| Long Context Manager 复杂度超出当前架构 | 中高 | 已消减到可控 | 默认复用 SQLite/chat session/artifact/source refs，不先引入复杂向量基础设施 |
| provider-backed chat 绕过工具确认 | 重大 | 已消减 | Tool Safety 和 Artifact/Export Guard 独立门槛 |
| workspace 删除或迁移造成数据损失 | 致命 | 已消减 | P7 默认 dry-run；apply/delete 必须高风险确认 |
| P7 Beta 范围膨胀成 SaaS | 重大 | 已消减 | 明确 P7 不做 SaaS、多租户、Billing |
| P5-REAL 被合成资料替代 | 重大 | 已消减 | P7-post 门槛明确 synthetic/examples/fixture 不能替代真实资料复验 |

## 6. 技术路线评估

| 路线 | 做法 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- | --- |
| A：增量模块化实现 | 在现有 FastAPI、ChatCore、services/llm、SQLite workspace 和 Chatbox 上增加 Provider Policy Gate、Long Context Manager、Invocation Log、Workspace Lifecycle、Diagnostics | 改动最小，保留 P0-P5 回归稳定；最适合当前单仓库和自动化验收 | 需要约束模块边界，避免 `main.tsx` 和 `core.py` 继续膨胀 | 推荐 |
| B：先引入向量库/复杂 memory 平台 | 长上下文直接接入向量检索、embedding、复杂记忆层 | 长期扩展性更强 | 引入新依赖和隐私面，当前 20-50 轮目标不需要，增加失败面 | 不推荐作为本阶段默认路线 |
| C：先做 SaaS 化 provider/账号/远端存储 | 直接面向云端 Beta 架构 | 更接近商业化 SaaS | 与当前本地优先、隐私确认和用户要求冲突，范围过大 | 不采用 |
| D：继续只做本地/mock，不接真实 provider | 避免 API Key 和外呼风险 | 风险最低 | 无法满足用户明确提出的真实 provider 聊天目标 | 不采用 |

最终建议采用路线 A。路线 A 的核心约束是：每个子阶段必须先写启动审计和详细验收标准，再开发；遇到真实 provider 或不可逆操作必须暂停确认。

## 7. 是否需要继续文档开发

当前无需继续扩大主文档范围。此前列为 P6-M0/P7-M0 前置输出的细则已经在 `docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md` 第 9 节补齐，包括：

- Provider Policy Gate 详细字段和状态机；
- Long Context Manager 具体持久化模型；
- Provider Invocation Log schema；
- 外呼确认 UX 和证据要求；
- P6 fake provider / controlled real provider 测试边界；
- P7 workspace lifecycle、diagnostics、release/rollback 和 Beta closure checklist。

后续进入实质代码开发前仍必须为具体子阶段输出短审计记录，例如 P6-M1 启动审计、P6-M2 启动审计和 P7-M1 启动审计。该类记录用于确认当次实现范围，没有必要再扩写主 PRD 或目标架构。

如果 P6-M0 审计发现以下情况，必须打回文档阶段：

- 任何默认外呼路径；
- API Key 可能进入前端、日志、报告或 fixture；
- Long Context Manager 需要未经确认发送完整个人资料；
- provider-backed chat 无法保持 Tool Safety；
- workspace lifecycle 需要默认执行删除或迁移 apply；
- P7 Beta 被扩大为 SaaS、多租户或 Billing。

## 8. 出门审查结论

当前文档水平可以完整支撑本阶段自动化开发的启动和逐阶段实施。若后续严格按 P6-M1 到 P7-post 的门槛推进，并在每个子阶段前后完成短审计、端到端验收和 PRD 规格检视，本阶段开发完成后可以达成预设目标并完成出门验收。

本结论不等于功能已实现，也不等于真实 provider、真实个人资料或 P5-REAL 已通过。功能验收仍必须依赖后续自动化测试、真实界面截图、HTML 报告、PRD 规格检视和必要的人类确认。
