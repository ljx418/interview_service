# JobPilot AI 产品化后续开发路线图

日期：2026-06-25
状态：P4 本地/mock examples 路径已冻结；P5 真实资料本地闭环已进入当前阶段规划；真实外部 provider 路径仍待 P6 单独确认
用途：把当前到产品化 Beta / SaaS 之前的开发目标落盘，并作为 P5 真实资料本地闭环的阶段规划入口。

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

P4 冻结证据：

```text
2026-06-25 人工体验评分：26/26
.venv/bin/python -m pytest：71 passed, 1 warning
npm --prefix apps/chatbox run build：通过
drawio XML parse：5 diagrams
```

## 2. 产品化差距评估

当前成熟度只能按分层判断：

| 目标层级 | 当前估计 | 说明 |
| --- | ---: | --- |
| 本地可验收 MVP / 工程原型 | 约 70% | 示例路径、截图验收、测试门禁和报告已具备。 |
| 真实用户闭环 Beta | 约 40%-50% | 真实资料导入、确认、编辑、导出和体验顺滑度仍需打通。 |
| 可产品化发布 | 约 25%-35% | 账户、部署、监控、数据安全、provider 管控、合规和运营能力未完成。 |

这些百分比是开发规划估算，不是验收结论。

## 3. P4 冻结后当前主线

P4 已完成本地/mock examples 路径冻结。当前主线已选择为 P5：真实资料本地闭环。P6/P7/P8+ 仍作为后续阶段，不能混入 P5 出门条件：

```text
P5：真实资料本地闭环（当前阶段）
P6：真实外部 provider opt-in
P7：产品化 Beta
P8+：SaaS / ASR / 会议平台 / 自动投递等高风险能力
```

入口文档：

```text
docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md
docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md
docs/active/stage-reviews/P4C_EXTERNAL_PROVIDER_DESENSITIZED_ACCEPTANCE_PLAN.md
```

P5 实质开发前必须先完成 P5 PRD、目标架构、验收门槛、风险确认和 drawio gap 文档。P6/P7/P8+ 仍必须在各自启动前单独制定规划和验收边界。

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

## 5. P5 当前阶段：真实资料本地闭环

目标：把当前示例路径推进到真实用户资料的受控本地闭环。P5 默认仍是本地 workspace 和 mock/local provider 路径；真实外部 provider 不属于 P5 默认验收。

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

当前工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P5-M0 | 制定 P5 PRD、目标架构、验收门槛和风险确认 | P5 active docs、drawio、文本镜像 |
| P5-M1 | 真实资料导入和解析 UX | 上传/粘贴/解析截图和 eval |
| P5-M2 | 真实 JD 导入、解析和缺失项提示 | JD 解析截图、错误恢复测试 |
| P5-M3 | 事实确认与待补充信息闭环 | questions_to_confirm UI 和 tests |
| P5-M4 | 真实资料申请包生成和编辑 | 本地真实感资料验收报告 |
| P5-M5 | 导出路径人工审查 | Markdown/DOCX 文件和截图 |
| P5-FC | 围绕真实资料的本地多轮追问 | 会话恢复、上下文追问、非执行型对话测试 |

P5 非目标：

- 不默认启用真实外部 provider；
- 不做 SaaS、多租户、Billing；
- 不做自动投递；
- 不做 ASR/会议平台。
- 不做 provider-backed 自由智能聊天默认路径。

## 6. P6 候选：外部 provider 受控接入

目标：在用户明确确认后，验证真实外部模型调用的产品路径。

必须具备：

- `.env` 本地配置和 API Key 不入库、不入报告；
- 外部调用前明确确认；
- provider 状态、费用/隐私提示和失败降级；
- timeout、retry、schema validation、redaction；
- provider invocation 记录脱敏；
- mock provider 仍可作为默认离线基线。

建议工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P6-M0 | 制定 provider 风险确认和验收门槛 | P6 PRD/acceptance gates |
| P6-M1 | 外部调用确认 UX | 调用前确认截图 |
| P6-M2 | 真实 provider 路径最小 E2E | 用户授权后的受控验收记录 |
| P6-M3 | provider 失败/超时/结构错误恢复 | 自动化和人工截图 |
| P6-M4 | 日志脱敏和密钥边界复查 | eval gates 和审计记录 |
| P6-FC | provider-backed 自由智能聊天 opt-in | 调用前确认、脱敏日志、失败降级、本地基线对照 |

P6 出门条件：

- 用户授权后才可验收真实 provider；
- 不在仓库、报告、日志里写入真实 API Key；
- 真实 provider 的成功和失败路径都要有证据。

## 7. P7 候选：产品化 Beta

目标：从本地工具走向可被真实用户持续使用的 Beta。

建议能力：

- workspace 管理和历史恢复；
- 用户数据安全边界和本地/远端存储策略；
- 错误追踪、日志脱敏、诊断报告；
- 备份、导出、清理和迁移策略；
- 发布脚本、部署说明和回滚计划；
- Beta 使用说明和支持流程。

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

## 9. 回到当前主线

当前 P4 已冻结，P5 已被确认为当前阶段目标。执行顺序是先完成 P5 文档、drawio、验收门槛和风险确认，再进入 P5 实质开发：

1. P5-M0：完成真实资料本地闭环 PRD、目标架构、验收门槛、脱敏策略、drawio 和人工确认点；
2. P5-M1 到 P5-FC：按 P5 文档逐步实现资料导入、JD 解析、事实确认、申请包、导出和本地多轮追问；
3. P5-Freeze：通过自动化验收、脱敏截图报告、PRD 规格检视和人工体验记录后冻结；
4. 若进入 P6，重新制定真实外部 provider opt-in 方案、调用前确认、API Key 边界、日志脱敏和失败降级验收；
5. 若进入 P7，重新制定发布、部署、数据生命周期、备份/迁移、监控和隐私审计计划；
6. 任何真实个人资料、真实外部 provider、自动投递、会议平台或不可逆迁移操作，都必须先暂停并获得用户确认。
