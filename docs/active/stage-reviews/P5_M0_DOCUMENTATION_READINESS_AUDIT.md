# P5-M0 文档就绪审计与开发准入结论

日期：2026-06-25
阶段：P5-M0 文档开发收口
审计结论：有条件通过，可以进入 P5 自动化开发；不得跳过分阶段验收直接声明 P5 完成。

## 1. 审计范围

本审计只评估 P5 文档是否足够支撑后续自动化开发和出门验收，不评估 P5 功能是否已经实现。

审计文档：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `README.md`
- `TODO.md`

## 2. 结论

当前文档已经能完整支撑 P5 本阶段自动化开发，前提是后续实现严格保持以下边界：

- P5 只验收真实资料本地闭环，不验收默认真实外部 provider；
- P5 默认采用路线 A：复用现有本地工具链并逐步加固；
- P5 必须按 P5-M1、P5-M2、P5-M3、P5-M4、P5-FC、P5-M5、P5-Freeze 分阶段验收；
- P5 报告必须脱敏，不得把 examples 写成真实个人资料验收；
- P5 完成不代表 SaaS、ASR、会议平台、自动投递、MCP/CLI、provider-backed 自由智能聊天或最终产品化发布完成。

## 3. 覆盖度评估

| 维度 | 当前覆盖 | 结论 |
| --- | --- | --- |
| 目标体验 | `01_STAGE_PRD.md` 已定义导入资料、JD 解析、事实确认、申请包、导出和多轮追问 | 充分 |
| 目标架构 | `02_TARGET_ARCHITECTURE.md` 已映射 Chatbox、FastAPI、ChatCore、Domain Tools、Artifact/Export、Storage、Provider Gate | 充分 |
| 接口契约 | `02_TARGET_ARCHITECTURE.md` 已列出 P5 最小可执行接口契约 | 充分 |
| 开发计划 | `03_MILESTONES_AND_DELIVERY_PLAN.md` 已拆分 P5-M0 到 P5-Freeze | 充分 |
| 技术路线 | `03_MILESTONES_AND_DELIVERY_PLAN.md` 已给出路线 A/B/C 和取舍 | 充分 |
| 验收门槛 | `04_ACCEPTANCE_GATES.md` 已定义自动化矩阵、人工体验门槛和不通过条件 | 充分 |
| 测试映射 | `06_TRACEABILITY_MATRIX.md` 已映射开发任务、代码边界、建议测试和截图证据 | 充分 |
| drawio 审查 | drawio 6 页，未超过 8 页，覆盖架构、差距、计划、门槛、证据和后续阶段 | 充分 |
| 风险边界 | provider、真实资料、API Key、SaaS/ASR/会议/自动投递均已隔离 | 充分 |

## 4. 自动化开发准入条件

进入 P5 实质开发前必须确认：

- drawio XML parse 通过，分页不超过 8 页；
- `README.md`、`TODO.md`、active docs 均显示 P5 为当前阶段，P4 为冻结基线；
- 没有文档声称 P5 已实现或真实外部 provider 默认路径已通过；
- 开发任务默认不使用真实 API Key、真实外部 provider 或未授权真实个人资料；
- 后续每个子阶段都先写测试或验收断言，再实现功能，再生成证据。

## 5. 打回条件

出现以下任一情况，必须停止开发并回到文档阶段：

- 实现方案要求 P5 默认调用 MiniMax、DeepSeek 或其他真实外部 provider；
- 实现方案要求把真实简历、真实 JD 或 API Key 写入报告、日志、fixture 或提交内容；
- ChatCore 普通追问无法可靠避免 artifact 写入，且没有新的意图契约；
- `questions_to_confirm` 无法影响导出 preflight；
- 前端状态复杂度导致无法完成 P5-M1/M2 验收，且没有局部拆分计划；
- drawio、PRD、架构、验收门槛出现 P5/P6/P7/P8 口径冲突。

## 6. 残余风险

| 风险 | 等级 | 控制方式 |
| --- | --- | --- |
| 本地/mock 文本质量不足以代表真实 LLM 质量 | 中 | P5 只验收本地闭环，不声称 provider-backed 质量 |
| 真实资料格式差异大 | 中 | 自动化使用 examples 和脱敏授权样本，真实资料只做人工确认 |
| ChatCore 启发式意图误判 | 中 | P5-FC 必须增加普通追问不写 artifact 的 eval |
| 确认项与导出耦合不足 | 高 | P5-M3/M4 把 blocking confirmation 作为导出硬门槛 |
| 报告泄露隐私 | 高 | P5-M5 必须加入隐私脱敏 eval 和人工复核 |

## 7. 备选技术路线

| 路线 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- |
| A：复用现有本地工具链 | 风险最低；保持 P0-P4 回归稳定；适合自动化开发 | 生成质量有限，不代表真实 LLM 智能体验 | 当前采用 |
| B：P5 同步接入真实 provider | 文本质量可能更好；自由问答能力更强 | API Key、隐私、费用、失败降级和虚假验收风险高 | 不采用，转 P6 opt-in |
| C：大规模重构前端/状态架构 | 长期维护性更好 | 容易扩大范围并影响冻结基线 | 不采用，只允许局部拆分 |

## 8. 最终判断

P5-M0 文档开发可以收口。后续可以进入 P5-M1 自动化开发，但必须逐阶段完成端到端验收和 PRD 规格检视。当前不得声明 P5 已完成，不得声明真实个人资料或真实外部 provider 默认路径已通过。
