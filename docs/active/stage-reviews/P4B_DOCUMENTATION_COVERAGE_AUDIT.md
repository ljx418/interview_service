# P4B 开发文档覆盖度审计

日期：2026-06-23
阶段：P4B 自动化完成后 / 人工体验审查门槛

## 1. 结论

当前开发文档对 P4B 自动化开发、验收和下一步人工体验审查的支撑程度较高，整体覆盖度评估为 85%-90%。

覆盖充分的部分：

- 阶段口径：README、TODO、`docs/active/00_README.md` 明确 P0/P1/P2/P3/P4B 当前状态；
- 产品目标：`01_STAGE_PRD.md` 明确 P4/P4B 目标体验路径、非目标和防过度承诺边界；
- 架构设计：`02_TARGET_ARCHITECTURE.md` 明确 Experience Shell、Conversation Plane、Workbench、Artifact、Export、Evidence Plane 与后端 Agent Tool-first 架构关系；
- 开发计划：`03_MILESTONES_AND_DELIVERY_PLAN.md` 拆分 P4-M0 到 P4-M6，并补充 P4B 后置人工审查门槛；
- 验收门槛：`04_ACCEPTANCE_GATES.md` 覆盖回归、空状态、对话反馈、产物卡、provider、响应式、截图和报告；
- 追踪矩阵：`06_TRACEABILITY_MATRIX.md` 把目标、代码区域、证据和验收门槛连起来；
- 自动化边界：`09_AUTOMATED_DEVELOPMENT_SCOPE.md` 明确哪些可自动推进，哪些必须人工确认；
- 证据包：P4/P4B HTML 报告、截图证据、stage review 和 Gemini 审查包已存在。

## 2. 原有缺口与本轮补强

| 缺口 | 风险 | 本轮处理 |
| --- | --- | --- |
| TODO 中 P4-UX1 到 P4-UX7 与 stage review 状态不一致 | 新接手者误以为 P4 自动化开发仍未完成 | TODO 已更新为自动化完成、人工体验认可和 P4 冻结已完成 |
| 缺少人工体验审查表 | 主观反馈难以转成可执行 P4C backlog | 新增 `P4B_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md` |
| P4B 到 P4C / P4 冻结的判定规则不够集中 | 可能跳过人工审查直接进入 P5 | 在 P4 计划和里程碑中加入后置审查门槛 |
| 新电脑环境复验问题未集中说明 | 依赖或沙箱问题可能被误判为业务失败 | HANDOFF 增加 venv、TestClient、Rollup、PiAgent workspace link 注意事项 |
| P5+ 只有候选列表 | 可能直接开工高风险能力 | TODO 明确 P5-M0 必须先单独制定 PRD、架构和验收门槛 |

## 3. 仍需人工补齐的内容

以下内容不能由自动化文档替代：

- P4B 人工体验评分和结论；
- 人工审查发现的问题截图或复现步骤；
- P4C backlog 的优先级判定；
- 真实个人资料路径是否进入受控审查；
- 真实外部 provider 是否进入受控审查；
- 是否启动 P5+ 独立阶段规划。

## 4. 当前推荐开发顺序

```text
P4B 人工体验审查
→ 若认可：P4 冻结复验
→ 若需微调：P4C polish
→ 若不认可：P4C backlog 修正
→ P4 冻结后再启动 P5-M0 独立规划
```

P4C 不应扩大范围。允许项仅限体验微调、报告和审查反馈闭环；MCP、CLI、ASR、会议平台、自动投递、SaaS、默认真实外部 provider 必须留到 P5+ 独立阶段。

## 5. 2026-06-24 自由 Chatbox 目标补充审计

新增反馈指出：当前 Chatbox 仍偏任务控制台，缺少自由、不中断、连续多轮对话能力。

补充前覆盖度判断：

- P3/P4 文档能支撑“Chatbox 有响应、错误可恢复、任务入口自然”；
- 但没有完整支撑“自由对话、澄清、状态查询、上下文追问、明确意图才执行工具”的阶段目标；
- provider-backed 自由智能聊天和本地/mock 连续对话的边界也不够集中。

本轮补强：

- 新增 `docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`；
- TODO 增加 P4C-FC 后续任务；
- `17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md` 增加 P4C-FC / P5-FC / P6-FC 分层；
- `03_MILESTONES_AND_DELIVERY_PLAN.md` 增加 P4C-FC 触发条件、交付物和出门条件；
- `01_STAGE_PRD.md` 增加 P4C-FC 用户结果和非目标；
- `02_TARGET_ARCHITECTURE.md` 增加 Chat Intent Router、Free Local Dialogue 和 Context Snapshot；
- `04_ACCEPTANCE_GATES.md` 增加 P4C-FC 最低证据、出门条件和不通过条件；
- `06_TRACEABILITY_MATRIX.md` 增加自由连续多轮对话目标、实现区域、证据和门槛映射；
- drawio 文本镜像和 drawio 本体增加自由追问、P4C-FC 和 P6 opt-in 边界。

补强后结论：

- 对 P4C-FC 本地/mock 连续对话基线的文档支撑已基本完整，可以支撑后续开发和验收；
- 对 P5-FC 真实资料多轮闭环仍只是路线级支撑，进入前必须单独制定 P5 PRD、目标架构、API/schema 和验收门槛；
- 对 P6-FC provider-backed 自由智能聊天仍只是风险边界和候选目标，必须在用户确认真实外部调用后单独立项。
