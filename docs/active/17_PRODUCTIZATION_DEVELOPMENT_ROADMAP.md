# JobPilot AI 产品化后续开发路线图

日期：2026-06-25
状态：P4 本地/mock examples 路径已冻结；P5 本地/mock + 脱敏 fixture 自动化候选已完成；P5.5 Candidate Profile 自动化候选已完成；P6+P7 本地 Beta 自动化候选已完成；当前主线为 P6-REAL 真实 provider 受控验收和 P7-post P5-REAL 真实资料复验准备。
用途：把当前到产品化 Beta / SaaS 之前的开发目标落盘，并作为 P6-REAL 真实 provider 受控验收、P7-post P5-REAL 真实资料复验和 P8+ 高风险能力拆分的规划入口。

## 1. 当前真实状态

当前项目已经具备本地可运行、可截图验收、可演示核心方向的求职 Agent 工作台：

```text
本地 mock / 示例路径
→ FastAPI 后端可运行
→ React Chatbox 可运行
→ 自动化 pytest / frontend build 通过
→ Chrome/CDP 多视口截图证据已生成
→ P4B HTML 自动化验收报告已完成
→ P4B/P4C 本地 Chatbox 人工体验认可
→ P4 冻结复验通过
```

但当前不得被描述为最终产品化，也不得声称以下路径已通过：

- 真实个人资料、真实简历、真实 JD 的默认路径已通过；
- 真实外部 provider / API Key / 外部模型调用已通过；
- ASR、会议平台、自动投递、SaaS、多租户、Billing 已进入验收范围。

P4/P5 基线证据：

```text
2026-06-25 人工体验评分：26/26
.venv/bin/python -m pytest：71 passed, 1 warning
npm --prefix apps/chatbox run build：通过
drawio XML parse：5 diagrams
P5 自动化候选：88 passed, 1 warning + P5 HTML 报告 + 三身份合成资料可视化验收
```

P5.5 / P6+P7 / P5-REAL 当前口径：

- P5.5 Candidate Profile 自动化候选已完成；
- P6+P7 本地 Beta 自动化候选已完成；
- P6 fake provider opt-in、20 轮连续对话和脱敏日志可作为自动化候选证据，但不代表真实 LLM 质量通过；
- 冻结延期到 P7 后复验；
- 不读取真实个人资料；
- 不声明真实个人资料路径通过；
- 不声明真实外部 provider 默认路径通过；
- synthetic personas、examples 和脱敏 fixture 只能作为候选和增强证据，不能替代 P5-REAL。

## 2. 产品化差距评估

当前成熟度只能按分层判断：

| 目标层级 | 当前估计 | 说明 |
| --- | ---: | --- |
| 本地可验收 MVP / 工程原型 | 约 70% | 示例路径、截图验收、测试门禁和报告已具备。 |
| 真实用户闭环 Beta | 约 40%-50% | 真实资料导入、确认、编辑、导出和体验顺滑度仍需打通。 |
| 可产品化发布 | 约 25%-35% | 账户、部署、监控、数据安全、provider 管控、合规和运营能力未完成。 |

这些百分比是开发规划估算，不是验收结论。

## 3. P4/P5/P5.5/P6/P7 基线后的当前主线

P4 已完成本地/mock examples 路径冻结。P5 已完成本地/mock + 脱敏 fixture 自动化候选。P5.5 已完成职业画像与能力评估自动化候选。P6+P7 已完成本地 Beta 自动化候选。当前主线不是继续扩大自动化候选，而是准备 P6-REAL 和 P7-post P5-REAL 的真实验收准入：

```text
P5：真实资料本地闭环自动化候选完成；P5-REAL/P5-Freeze 冻结延期复验
P5.5：职业画像、能力矩阵、项目可信度、岗位短板自动化候选完成
P6/P7：本地 Beta 自动化候选完成
P6-REAL：真实外部 provider 受控小样本验收准备（当前文档阶段）
P7-post：P5-REAL/P5-Freeze 真实资料复验准备（当前文档阶段）
P8+：SaaS / ASR / 会议平台 / 自动投递等高风险能力
```

入口文档：

```text
docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md
docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md
docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md
```

P6-REAL/P7-post 实质执行前必须先完成授权表、目标架构、验收门槛、风险确认和 drawio gap 文档。P8+ 仍必须在各自启动前单独制定规划和验收边界。

## 4. P4C 候选：人工体验微调

触发条件：P4B 人工审查结论为“需要微调”。

目标：

- 修正文案语气、任务入口和下一步引导；
- 强化自由 Chatbox 和无中断连续多轮追问，避免普通对话被误触发为工具执行；
- 优化 Workbench 信息密度；
- 强化产物详情的非 JSON 预览；
- 优化移动端抽屉/折叠路径；
- 降低“示例模式”和“我的资料模式”的理解成本；
- 继续保持真实外部 provider 默认关闭。

建议工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P4C-UX1 | 重新审视首屏 5 秒理解成本 | 人工审查记录、before/after 截图 |
| P4C-UX2 | 强化对话语气和错误恢复文案 | 缺资料、失败、恢复路径截图 |
| P4C-UX3 | 产物卡增加更清晰的正文预览 | 申请包/匹配报告完成态截图 |
| P4C-UX4 | 移动端工作台入口更顺手 | 390px/720px Chrome 截图和人工记录 |
| P4C-FC1 | 本地/mock 连续多轮对话基线 | 自由追问不触发工具的测试和截图 |
| P4C-UX5 | 报告和文档同步 | HTML 报告、TODO、active docs 更新 |

P4C 出门条件：

- 人工体验审查认可核心示例路径；
- pytest 和 frontend build 通过；
- Chrome 多视口截图和 HTML 报告更新；
- 未把真实个人资料或真实 provider 写成已通过。
- 未把 provider-backed 自由智能聊天写成当前已完成；该能力必须进入 P6 opt-in。

## 5. P5 冻结延期复验：真实资料本地闭环

状态：本地/mock + 脱敏 fixture 自动化候选已完成；P5-REAL/P5-Freeze 冻结延期到 P7 后复验。P5 默认仍是本地 workspace 和 mock/local provider 路径；真实外部 provider 不属于 P5 默认验收。

理想体验路径：

```text
导入或粘贴个人资料
→ 导入或粘贴 JD
→ 解析岗位和候选人经历
→ 匹配个人经历与岗位要求
→ 生成申请包草稿
→ 用户确认事实和待补充信息
→ 编辑 / 重新生成
→ 导出简历、cover letter、申请说明或面试准备
```

当前工作包状态：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P5-M0 | 制定 P5 PRD、目标架构、验收门槛和风险确认 | 已完成 |
| P5-M1 | 真实资料导入和解析 UX | 脱敏 fixture 自动化候选通过 |
| P5-M2 | 真实 JD 导入、解析和缺失项提示 | 自动化候选通过 |
| P5-M3 | 事实确认与待补充信息闭环 | 自动化候选通过 |
| P5-M4 | 真实资料申请包生成和编辑 | 自动化候选通过 |
| P5-M5 | 脱敏自动化报告和导出路径证据 | 自动化候选通过 |
| P5-FC | 围绕资料/JD/申请包的本地多轮追问 | 自动化候选通过 |
| P5-REAL | 真实资料路径复验 | 冻结延期到 P7-post |
| P5-Freeze | 人工体验记录和 final closure audit | 冻结延期到 P7-post |

P5 非目标：

- 不默认启用真实外部 provider；
- 不做 SaaS、多租户、Billing；
- 不做自动投递；
- 不做 ASR/会议平台。
- 不做 provider-backed 自由智能聊天默认路径。

## 6. P6-REAL 当前准备阶段：外部 provider 受控验收

目标：在不默认外呼的前提下，准备真实外部模型调用的受控验收路径，并把“长程连续对话”作为真实 provider 质量复验重点。P6 不承诺真正无限 token，而是通过会话持久化、滚动摘要、上下文快照和检索实现可验收的长程连续聊天。

必须具备：

- `.env` 本地配置和 API Key 不入库、不入报告；
- 外部调用前明确确认；
- provider 状态、费用/隐私提示和失败降级；
- timeout、retry、schema validation、redaction；
- provider invocation 记录脱敏；
- mock provider 仍可作为默认离线基线。
- 长对话上下文不能把全部历史逐字塞进 provider，必须有压缩和来源边界；
- provider-backed 回复不能绕过 artifact confirmation、questions_to_confirm 或 export preflight。

当前文档工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P6-REAL-DOC | 真实 provider 外呼执行单和报告模板 | provider/model、调用次数、预算、数据类别、脱敏字段 |
| P6-REAL-GATE | 真实 provider 小样本验收门槛 | configured/consented/called/failed/fallback 证据定义 |
| P6-REAL-AUDIT | 防止 fake provider 替代真实 LLM | 审计记录、虚假验收打回条件 |

P6 出门条件：

- 用户授权后才可验收真实 provider；
- 不在仓库、报告、日志里写入真实 API Key；
- 真实 provider 的成功和失败路径都要有证据。
- 报告不得把长程连续对话写成真正无限上下文；
- provider 失败时必须能降级到本地连续对话基线。

入口文档：

```text
docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md
```

## 7. P7-post 当前准备阶段：真实资料复验和 Beta 收口

目标：在 P6/P7 自动化候选基线上，准备 P7-post P5-REAL/P5-Freeze 真实资料复验和 Beta 收口，不默认读取真实资料、不执行不可逆 workspace 操作。

建议能力：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P7POST-DOC | 真实资料路径授权执行单 | 用户明确资料路径、允许展示字段、禁止展示字段 |
| P7POST-REDaction | 脱敏报告和截图边界 | 联系方式、账号、私密链接、长原文、密钥默认遮蔽 |
| P7POST-AUDIT | 防止 synthetic personas 替代真实资料 | P5-REAL 未授权时保持未执行 |
| P7POST-BETA | Beta 收口和不可逆操作边界 | workspace 删除/迁移 apply 仍需高风险确认 |

P7 出门条件：

- 有清晰的用户数据生命周期说明；
- 有可复现部署路径；
- 有监控和错误追踪；
- 有安全/隐私审计记录；
- 有端到端 Beta 验收报告。

## 8. P8+ 候选：SaaS 和高风险能力

这些能力必须单独立项，不得混入 P4/P5/P6：

- SaaS 登录、多租户、权限、Billing；
- ASR / Whisper / 系统音频；
- 会议平台接入；
- 自动投递；
- MCP Server wrapper；
- CLI 产品入口；
- 更完整岗位数据源、Offer 分析和申请跟踪。

任何涉及真实个人资料、外部模型调用、自动投递、会议平台或不可逆迁移的操作，都必须先暂停并获得用户确认。

## 9. P6+P7 历史主线和当前 P5.5 主线

本节前半部分记录 P6+P7 已完成自动化候选的历史主线。当前 P4 已冻结，P5-REAL/P5-Freeze 已冻结延期到 P7 后复验，P6+P7 已作为后续基线保留。以下执行顺序不再表示当前新增开发目标，而是用于说明 P6+P7 自动化候选和 P7-post 复验边界：

1. P5-M0：完成真实资料本地闭环 PRD、目标架构、验收门槛、脱敏策略、drawio 和人工确认点；
2. P5-M1 到 P5-FC：已按 P5 文档完成自动化候选；
3. P5-REAL/P5-Freeze：冻结延期到 P7-post，不作为当前阶段阻塞项，也不得写成通过；
4. P6-M0 到 P6-Freeze：真实外部 provider opt-in、调用前确认、API Key 边界、长程连续对话、日志脱敏、失败降级和可视化验收；
5. P7-M0 到 P7-Freeze：发布、部署、数据生命周期、备份/迁移 dry-run、诊断报告、回滚、支持流程和隐私审计；
6. P7-post：在用户提供真实资料路径后执行 P5-REAL/P5-Freeze 复验；
7. 任何真实个人资料、真实外部 provider、自动投递、会议平台、workspace 删除或不可逆迁移操作，都必须先暂停并获得用户确认。
# P5.5 Candidate Profile 当前阶段补充

2026-06-29 起，当前文档主线切换为 P5.5 Candidate Profile。该阶段位于 P5 本地资料闭环之后、P6/P7 本地 Beta 自动化候选之后，目标是把用户资料、项目、技能证据和 JD 匹配结果组织成可审查的职业画像与能力评估。

P5.5 交付后，用户应能看到：

- 专业背景画像：目标岗位、转型路径、当前层级、主要经历线索；
- 能力矩阵：技能名称、类别、证据类型、证据强度、岗位相关性、待确认项；
- 项目可信度：本人贡献、技术难点、可验证材料、量化结果缺口、风险标签；
- 岗位短板：must-have 缺口、nice-to-have 缺口、表达风险和补强行动；
- source refs：每个判断都能追溯到资料、项目、JD 或 artifact。

P5.5 不替代 P5-REAL，不默认外呼真实 provider，不进入 SaaS/ASR/会议平台/自动投递/MCP/CLI。P5.5 完成后，才考虑继续真实 provider 复验、P7-post P5-REAL 或 P8+ 高风险能力。
