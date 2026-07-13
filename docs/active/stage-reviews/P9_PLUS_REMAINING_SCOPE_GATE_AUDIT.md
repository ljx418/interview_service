# P9+ 剩余开发范围准入审计

状态：准入审计完成。本文档用于判断“用户批准进入后，当前仓库是否存在可继续自动执行的、已被文档完整支撑的剩余开发计划”。

## 1. 审计结论

当前 P9.1-M0 到 M5 已完成本地自动化候选，证据为：

- `docs/reports/P9_1_MARKET_SOCRATIC_ACCEPTANCE_REPORT.html`
- `docs/reports/evidence/p9_1_market_socratic/`
- `tests/evals/test_p9_1_market_socratic_acceptance_eval.py`
- `scripts/generate_p9_1_market_socratic_acceptance.py`
- `docs/active/stage-reviews/P9_1_M0_START_AUDIT.md` 到 `P9_1_M5_ACCEPTANCE_REPORT_AUDIT.md`

剩余未完成项主要来自 `TODO.md`：

- P4C-EP：真实外部 provider + 脱敏个人资料验收；
- P7-POST-P5-REAL：真实资料路径复验；
- MCP Server wrapper；
- CLI 命令；
- 本地 Whisper / ASR adapter；
- 会议平台接入；
- 更完整岗位数据源、Offer 分析和申请跟踪。

其中，当前具备“可直接自动化实现”的文档支撑范围为 **无**。原因是这些剩余项要么属于高风险授权流程，要么只有 TODO 级条目，没有达到本项目进入实质开发前要求的 PRD、目标架构、里程碑、验收门槛、drawio、阶段审计和出门条件完整度。

## 2. 剩余项分类

| 剩余项 | 当前文档状态 | 风险级别 | 是否可直接自动化开发 | 需要补齐 |
| --- | --- | --- | --- | --- |
| P4C-EP 真实外部 provider + 脱敏个人资料 | 有历史计划，但需要具体数据路径、provider、调用次数、脱敏范围和 API Key 本地配置 | 高 | 否 | 用户逐项授权执行单、真实数据路径、预算和报告脱敏字段 |
| P7-POST-P5-REAL | 有复验方向，但用户此前明确不提供真实资料 | 高 | 否 | 真实资料路径、允许展示字段、脱敏级别、失败打回条件 |
| MCP Server wrapper | TODO 级条目；P9/P9.1 文档明确未验收 MCP/Skill 连通性 | 中高 | 否 | P10-MCP PRD、目标架构、工具清单、权限边界、stdio/http 模式、验收脚本 |
| CLI 命令 | TODO 级条目；缺少命令契约、输出格式和安全边界 | 中 | 否 | P10-CLI PRD、命令清单、workspace 参数、安全确认、验收脚本 |
| 本地 Whisper / ASR adapter | P9/P9.1 明确不默认启用真实 ASR | 高 | 否 | ASR 授权、麦克风/文件输入边界、隐私处理、离线模型下载与许可证 |
| 会议平台接入 | 明确为后续高风险能力 | 高 | 否 | 平台授权、账号边界、录音/转写合规、人工确认流程 |
| 更完整岗位数据源、Offer 分析和申请跟踪 | 只有方向性条目；真实市场 provider 未接入 | 中高 | 否 | 数据源选择、API Key、许可、source refs、真实/fixture 边界和验收门槛 |

## 3. 不允许直接声明或实施的内容

即使用户同意“进入下一阶段”，当前也不得默认执行：

- 真实 API Key 扫描、读取或提交；
- 未指定 provider 的真实 LLM 或真实市场 API 调用；
- BOSS、猎聘、拉勾、LinkedIn 等招聘平台登录、抓取、绕验证码或自动沟通；
- 真实个人资料目录读取；
- 麦克风采集、真实 ASR 外呼、会议平台接入；
- 自动投递、代表用户对外发送消息；
- workspace 删除、cleanup apply、migration apply 或不可逆迁移。

## 4. 建议下一阶段最小文档开发包

若要继续推进，建议先选择一个低风险入口，而不是同时做所有 P9+ 能力。推荐顺序：

1. **P10-CLI 本地命令入口**：只封装现有本地 API / fixture 能力，不新增真实 provider，不读取未授权资料。
2. **P10-MCP 本地 wrapper**：只暴露只读/本地 workspace 工具，不做外部平台和真实 provider 连通性验收。
3. **P10-MARKET-OPTIN**：真实市场 provider 的 opt-in 小样本验收，需要用户明确 provider、API Key、本地配置方式、预算和报告脱敏范围。

P10-CLI 或 P10-MCP 开发前至少需要落盘：

- PRD：用户体验路径、命令/工具清单、非目标；
- 目标架构：具体代码实体、调用关系、权限边界；
- 里程碑：M0 到 M5 子阶段；
- 验收门槛：命令输出、错误处理、隐私、回归测试；
- drawio：不超过 8 页，标注已实现、待新增、需修改、高风险；
- 阶段启动审计：确认无真实 provider、真实资料、平台自动化、ASR、自动投递混入默认路径。

## 5. 本轮停止条件

本轮可继续自动执行的工作仅限：

- 同步 P9.1 当前实现状态到文档；
- 修复 P9.1 文档与报告口径冲突；
- 运行现有测试和验收；
- 输出准入审计，说明下一阶段必须先补文档。

当前不应进入 MCP/CLI/ASR/真实市场 provider 的代码实现，因为现有文档不足以满足本项目一贯要求的“开发前计划、审计意见、验收门槛和高风险边界闭环”。

