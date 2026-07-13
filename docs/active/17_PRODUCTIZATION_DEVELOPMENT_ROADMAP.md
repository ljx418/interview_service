# JobPilot AI 产品化后续开发路线图

日期：2026-06-25
状态：P4 本地/mock examples 路径已冻结；P5 本地/mock + 脱敏 fixture 自动化候选已完成；P5.5 Candidate Profile 自动化候选已完成；P6+P7 本地 Beta 自动化候选已完成；P6-REAL / P7-post 审计报告已完成；P8-JD Intake 与简历生成体验强化自动化候选已完成；P8.1 Chatbox-first 自动化候选已完成；P9 Chatbox-native 求职情报与申请包工作台本地自动化候选已完成；P9.1 行政区划下钻式地图与 Socratic Intake 本地自动化候选已完成；P10-CLI 本地命令入口自动化候选已完成；当前主线进入 P11 真实市场数据 Provider Opt-in Level1 阶段性验收收口。
用途：把当前到产品化 Beta / SaaS 之前的开发目标落盘，并作为 P11 真实市场数据 opt-in provider、P10-CLI 本地命令入口、P9.1 行政区划下钻式市场地图、Socratic Intake、P9 Chatbox-native、P8.1 Chatbox-first、P8 资料准备向导、JD 手动导入中心、JD 定制简历、招聘平台合规接入和 P9+ 高风险能力拆分的规划入口。

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

P5.5 / P6+P7 / P6-REAL / P7-post / P8 当前口径：

- P5.5 Candidate Profile 自动化候选已完成；
- P6+P7 本地 Beta 自动化候选已完成；
- P6 fake provider opt-in、20 轮连续对话和脱敏日志可作为自动化候选证据，但不代表真实 LLM 质量通过；
- P6-REAL / P7-post 阶段审计报告已完成，但真实 provider 质量和真实个人资料路径仍未执行；
- P8-JD Intake 自动化候选已完成，覆盖资料准备、JD 手动导入、多 JD 当前目标和 JD 定制简历体验；
- P8.1 Chatbox-first 自动化候选已完成并作为当前前端基线保留；
- P9 Chatbox-native 已完成本地自动化候选，目标体验为“顶部服务中心 - 左侧求职态势图 - 中央 Chatbox 主控台 - 右侧产物台”，覆盖本地 JD 汇总、Chatbox 资料补全、多 JD 申请包、投递流程可视化和地图/图钉式态势交互；
- P9.1 本地自动化候选已完成，目标是补齐行政区划下钻式市场地图体验、真实市场数据 opt-in provider 状态表达和 Socratic Intake 资料补全策略；
- P10-CLI 本地命令入口自动化候选已完成，覆盖本地 API、examples/fixture、workspace、artifact 和 report 能力；
- P11 当前为 Level1 自动化候选验收收口，已实现本地/fixture/recorded/manual/public market provider 边界、授权拒绝、安全门、数据契约、source refs、调用日志、CLI 状态、Chatbox 联动和 evidence；Level2 真实 provider opt-in 仍待用户提供合法凭据和外呼确认；
- 不读取真实个人资料；
- 不声明真实个人资料路径通过；
- 不声明真实外部 provider 默认路径通过；
- 不声明 BOSS 或其他招聘平台已自动接入；
- 不声明自动沟通或自动投递已实现；
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

P4 已完成本地/mock examples 路径冻结。P5 已完成本地/mock + 脱敏 fixture 自动化候选。P5.5 已完成职业画像与能力评估自动化候选。P6+P7 已完成本地 Beta 自动化候选。P6-REAL 和 P7-post P5-REAL 已完成审计准备但尚未执行真实验收。P8-JD Intake 自动化候选已完成：资料准备向导、JD 手动导入中心、岗位列表、JD 定制简历和招聘平台合规边界已完成本地/mock + 受控真实感数据验收。P8.1 Chatbox-first 自动化候选已完成。P9 Chatbox-native 求职情报与申请包工作台已完成本地自动化候选。P9.1 行政区划市场地图与 Socratic Intake 本地自动化候选已完成，覆盖 ECharts 下钻地图、Market Provider 未配置状态、Socratic 一问一答、产物台联动和中文 HTML 证据。

```text
P5：真实资料本地闭环自动化候选完成；P5-REAL/P5-Freeze 冻结延期复验
P5.5：职业画像、能力矩阵、项目可信度、岗位短板自动化候选完成
P6/P7：本地 Beta 自动化候选完成
P6-REAL：真实外部 provider 受控小样本验收准备（当前文档阶段）
P7-post：P5-REAL/P5-Freeze 真实资料复验准备（当前文档阶段）
P8：JD Intake / 资料准备向导 / JD 定制简历体验强化（自动化候选完成）
P8.1：Chatbox-first 工作台信息架构修正（自动化候选完成，作为 P9 基线）
P9：Chatbox-native 求职情报与申请包工作台（本地自动化候选完成）
P9.1：行政区划下钻式市场地图与 Socratic Intake（本地自动化候选完成；真实市场 provider 未接入）
P10-CLI：本地命令入口自动化候选完成
P11-MARKET-OPTIN：真实市场数据 Provider Opt-in Level1 自动化候选收口；Level2 真实外呼待后续授权
P12-MCP / P12-ASR / P12-PLATFORM：后续备选，必须单独文档开发和授权
P9+：合规招聘平台接入 / SaaS / ASR / 会议平台 / 自动投递等高风险能力
```

入口文档：

```text
docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md
docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md
docs/active/19_P6_PROVIDER_BACKED_LONG_CONTEXT_CHAT_PLAN.md
docs/active/21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md
docs/active/22_P8_1_CHATBOX_FIRST_WORKSPACE_PLAN.md
docs/active/23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md
docs/active/24_P9_1_MARKET_DATA_AND_SOCRATIC_PROTOTYPE_PLAN.md
docs/active/25_P10_CLI_LOCAL_COMMAND_ENTRY_PLAN.md
```

P6-REAL/P7-post 实质执行前必须再次确认授权表、目标架构、验收门槛、风险确认和脱敏报告边界。P9+ 高风险能力仍必须在各自启动前单独制定规划和验收边界。

## 3.0.3 P11 当前收口主线：真实市场数据 Provider Opt-in Level1

触发原因：P9.1 已把市场地图体验升级为 ECharts 行政区划下钻式招聘情报板，但数据仍以 fixture/manual/public/opt-in 状态表达为主。用户希望减少 mock/fixture，并让地图和 Chatbox 能基于真实市场数据形成可追溯的求职情报。P11 是低于招聘平台自动接入的下一步：先完成可审计的 market provider 边界、授权门、数据契约和 evidence。当前 P11 Level1 已完成本地/fixture/recorded/manual/public 自动化候选；指定真实 provider Level2 调用仍必须等待合法凭据和用户外呼确认。

P11 第一版产品边界：

- 做真实市场 provider 的 opt-in 状态、授权门、调用日志、source refs 和 evidence；Level1 已完成本地路径，Level2 待授权；
- 做 `JobMarketProviderRegistry`、`MarketProviderPolicyGate`、`MarketProviderClient`、`MarketProviderInvocationLog`；Level1 已实现 registry/policy/log，本阶段不真实调用外部 client；
- 做 `JobSearchRunService`、`MarketDataNormalizer`、`SourceRefBinder`、`ConfidenceScorer`、`NormalizedJobPost`、`JobMarketSnapshot`；Level1 已实现本地 search run、snapshot 和 source refs；
- 支持 Adzuna、TheirStack、JSearch、Jooble、公司官网公开 JD 和用户粘贴作为规划候选；
- 未配置或未授权时保持 not_configured / configured / consented / called / failed / fallback 的清晰状态；
- 不登录招聘平台、不绕风控、不长期爬虫、不默认调用真实 LLM provider、不做 ASR/MCP/自动投递/SaaS。

P11 计划工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P11-DOC | PRD、目标架构、里程碑、门槛、追踪矩阵、drawio 和审计同步 | 已完成；active docs 口径一致、drawio 解析通过、审计无重大规格偏差 |
| P11-M0 | 开发前启动审计 | 已完成；stage review 确认未混入平台抓取、真实 LLM provider、ASR、MCP、自动投递、长期爬虫或 SaaS |
| P11-M1 | market provider 状态 API | 已实现 Level1；not_configured/local/fallback 状态可见，不泄露 API Key |
| P11-M2 | provider check 授权门和调用日志 | 已实现 Level1；未确认真实 opt-in provider 拒绝外呼，本地路径有脱敏 evidence |
| P11-M3 | search run、normalization、snapshot | 已实现 Level1；`JobSearchRun`、`NormalizedJobPost`、`JobMarketSnapshot` 和 source refs 可验收 |
| P11-M4 | Chatbox / 地图 / 产物台联动 | 已实现 Level1；local/fallback source 映射到市场地图、Chatbox 回复、CLI status 和 Market Insight |
| P11-M5 | 中文自动化验收报告 | 已实现；provider opt-in eval、pytest、frontend build、PRD 规格检视和未验证范围 |

## 3.0.2 P10-CLI 自动化候选：本地命令入口

触发原因：P9+ 剩余开发准入审计显示，MCP Server wrapper、CLI 命令、本地 Whisper/ASR、会议平台、真实市场 provider、真实资料复验和真实 provider 复验都不能直接进入自动化开发。CLI 是其中最低风险入口，因为它可以只包装现有本地能力，不默认触发真实外呼或高风险平台行为。P10-CLI 当前已完成自动化候选。

P10-CLI 第一版产品边界：

- 做本地 CLI 命令入口，服务人类、Codex CLI、ClaudeCode CLI 和其他本地 Agent；
- 做 `jobpilot --help`、`workspace status`、`demo run --example`、`jobs list`、`artifacts list/show`、`reports open` 的命令契约；
- 做 `JobPilotCLI`、`CLICommandRouter`、`CLIConfigResolver`、`WorkspaceSelector`、`CommandSafetyGate`、`ApiClient`、`OutputRenderer`、`ExitCodePolicy`、`CommandAuditLog` 目标架构；
- 做中文输出、可选 JSON、stdout/stderr、exit code 和本地脱敏命令审计；
- 复用现有 FastAPI、Domain Tools、SQLite workspace、artifact 和 reports；
- P10-CLI v1 不自动启动 FastAPI，只在服务不可用时给 exit 2 和启动建议；
- `reports open` 只定位或打开已有报告，不生成、修复或重写验收报告；
- workspace 解析优先级固定为 `--workspace` > `JOBPILOT_WORKSPACE` > 当前目录 `.jobpilot_workspace` > 失败；
- 不做 MCP server，不默认真实 provider，不读取未授权真实资料，不抓取招聘平台，不做 ASR、会议平台、自动投递、SaaS 或不可逆 workspace 操作。

P10-CLI 计划工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P10-CLI-DOC | PRD、目标架构、里程碑、门槛、追踪矩阵、drawio 和审计同步 | active docs 口径一致、drawio 解析通过、审计无重大规格偏差 |
| P10-CLI-M0 | 开发前启动审计 | stage review 确认未混入 MCP、真实 provider、真实资料、平台抓取、ASR、自动投递；冻结 FastAPI 不自动启动、reports open 不生成报告、workspace 解析优先级 |
| P10-CLI-M1 | CLI 框架和帮助命令 | `jobpilot --help` 可运行，中文帮助和非目标清楚 |
| P10-CLI-M2 | workspace status 和 safety gate | provider/workspace/report 状态可见，高风险默认拒绝 |
| P10-CLI-M3 | demo/jobs/artifacts/reports 命令 | 本地 examples/fixture/workspace/report 路径可验收 |
| P10-CLI-M4 | Agent-friendly 输出 | `--json`、stdout/stderr、exit code 可被自动化脚本稳定判断 |
| P10-CLI-M5 | 中文自动化验收报告 | CLI eval、pytest、frontend build、PRD 规格检视和未验证范围 |

## 3.0.1 P9.1 本地自动化候选：市场地图、真实数据边界与 Socratic Intake

触发原因：用户确认 P9 自动化候选后，仍认为市场模块地图样式粗糙、当前仍有较多 mock/fixture 数据、Chatbox 没有以苏格拉底式提问帮助用户补齐简历事实和项目故事。P9.1 已完成本地自动化候选；真实市场 provider、平台接入和 ASR 仍需后续单独授权。

P9.1 第一版产品边界：

- 做行政区划下钻式市场地图目标原型，不再用低保真装饰地图、静态 SVG、普通瓦片地图或暗色假大屏承载招聘情报；
- 做真实市场数据 provider 的 opt-in 规划，候选包括 Adzuna、TheirStack、JSearch、Jooble、用户粘贴和公司官网公开 JD；
- 做数据来源可信度表达，区分 fixture、manual、public、opt-in API；
- 做 Socratic Intake，一次只问一个高价值问题，逐步补齐目标岗位、项目背景、本人职责、技术难点、行动、指标、证据和边界；
- 做右侧产物台中的事实摘要、项目故事草稿、JD 映射、source refs 和 pending confirmations 规划；
- 不默认登录、抓取或绕过招聘平台风控；
- 不默认调用真实 provider，不默认开启 ASR，不默认自动投递。

P9.1 计划工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P9.1-DOC | PRD、架构、里程碑、门槛、追踪矩阵、drawio 和 HTML 审查页同步 | active docs 口径一致、drawio 解析通过、HTML 引用有效 |
| P9.1-M0 | 开发前启动审计 | stage review 确认无真实 provider、平台抓取、ASR、自动投递默认实现 |
| P9.1-M1 | 行政区划下钻式市场地图 | 多视口真实截图，行政区划颜色深浅、全国/省/市/区县下钻、城市气泡、visualMap、tooltip、toolbox、面包屑、薪资直方图、技术栈热度、来源可信度可见 |
| P9.1-M2 | opt-in 市场数据 provider 状态 | provider configured/connected/called/failed/fallback 状态可区分，未授权不外呼 |
| P9.1-M3 | Socratic Intake | 两类技术背景 10 轮以上一问一答样例，含事实摘要、故事草稿、待确认项 |
| P9.1-M4 | 地图、Chatbox、产物台联动 | 城市/技术栈点击后可追问，右侧产物台同步摘要和草稿 |
| P9.1-M5 | 中文自动化验收报告 | 报告区分真实截图、原型图、fixture、未验证 provider 和 PRD 规格检视 |

## 3.0 P9 当前文档主线：Chatbox-native 求职情报与申请包工作台

触发原因：用户明确反馈当前前端体验仍然很差，不希望存在很多向导卡片；期望通过 Chatbox 直接发起 JD、薪资、城市招聘信息汇总，通过 Chatbox 或 ASR 引导补全简历、项目故事和用户信息，自动生成不同 JD 的申请包，并在左侧看到地图/图钉式求职态势、在右侧看到简历和事实产物。

P9 第一版产品边界：

- 做 Chatbox-native 信息架构，不让向导卡片主导首屏；
- 做顶部服务中心，展示 provider、ASR、MCP、Skill、外部搜索和安全边界状态；
- 做左侧求职态势图，覆盖岗位市场、目标机会与匹配、投递流程三大板块；
- 做地图/图钉或等价地图可视化方案，支持缩放、拖动、折叠和 Chatbox 联动；
- 做 JD 搜索/汇总的合规架构，默认仅使用用户粘贴、fixture 或合规公开源；
- 做 Chatbox 引导式资料补全和多 JD 申请包生成；
- 做 Chatbox 驱动的产物、事实和投递流程更新；
- 不默认登录招聘平台、不绕风控、不自动沟通或自动投递；
- 不默认调用真实 provider，不默认开启 ASR，不默认声明 MCP/Skill 连通。

P9 计划工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P9-DOC | PRD、架构、里程碑、门槛、追踪矩阵、drawio 同步 | active docs 口径一致、drawio 解析通过 |
| P9-M1 | Chatbox-native 信息架构 | 多视口真实截图，中央 Chatbox 首屏优先 |
| P9-M2 | 顶部服务中心 | provider/ASR/MCP/Skill/search 状态截图和未验证范围 |
| P9-M3 | 左侧求职态势图 | 三大页签、地图式可视化、缩放拖动截图 |
| P9-M4 | 合规 JD search run | fixture/手动/公开源验收，不声明平台自动接入 |
| P9-M5 | Chatbox/ASR 资料补全 | Chatbox 路径验收；ASR 真实路径单独授权 |
| P9-M6 | 多 JD 申请包 | 简历、故事、申请包版本、source refs、pending confirmations |
| P9-M7 | Chatbox 更新产物和流程 | 流程状态、事实修订、版本历史验收 |
| P9-M8/M9 | 响应式和中文报告 | 1920/1440/1200/720/390 截图和 HTML 报告 |

## 3.1 P8 当前自动化候选：JD Intake 与简历生成体验强化

触发原因：用户明确反馈当前交互仍不好，上传资料按钮过于抽象，用户不知道需要提供什么资料；同时希望系统能更主动地帮助寻找或导入 JD，并增强面向用户的简历生成。

P8 第一版产品边界：

- 做资料准备向导，不再只给“上传资料”按钮；
- 做 JD 手动导入中心，支持粘贴 JD、保存来源 URL、平台标签和备注；
- 做岗位列表和当前目标岗位选择；
- 做 JD 定制简历规划，输出 source refs、pending confirmations 和导出 preflight；
- 不做 BOSS/猎聘/拉勾等平台登录；
- 不做绕反爬、自动抓取、自动开聊、自动沟通或自动投递；
- 不默认调用真实 provider。

P8 已完成工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P8-DOC | PRD、架构、里程碑、门槛和追踪矩阵同步 | active docs 口径一致 |
| P8-DRAWIO | drawio 和文本镜像更新 | XML parse，页数不超过 8 |
| P8-AUDIT | 阶段审计记录 | 不含平台自动接入或自动投递虚假承诺 |
| P8-M1 | 资料准备向导 | 用户知道需要提供什么资料的真实界面截图 |
| P8-M2 | JD 导入中心 | 粘贴 JD、保存来源、岗位列表截图 |
| P8-M3 | JD 对比和当前目标 | 多 JD 匹配摘要和短板提示 |
| P8-M4 | JD 定制简历 | 简历草稿、source refs、待确认项和导出 preflight |
| P8-M5 | P8 自动化验收报告 | 中文 HTML 报告和 PRD 检视 |

P8 出门不能声称：

- BOSS 或任何招聘平台已真实接入；
- 平台职位列表已自动抓取；
- 不允许声明自动沟通或自动投递已实现；
- 真实 provider 或真实个人资料路径被列为验收结论。

## 3.2 P8.1 当前文档阶段：Chatbox-first 工作台信息架构修正

触发原因：用户人工体验反馈当前交互仍不好，感觉 Chatbox 被资料/JD/简历入口“干没了”。用户期望当前三栏栏目是“用户指导 - 聊天框 - 工作台”，聊天框始终是最优先展示。

P8.1 第一版产品边界：

- 保留 P8 已完成的资料准备、JD 导入、岗位选择和 JD 定制简历能力；
- 将中央首屏主路径恢复为 Chatbox 对话、Agent 状态和输入框；
- 将上传资料、粘贴 JD、选择目标岗位、生成简历入口迁移到输入框附近工具条、轻弹层、抽屉或左右辅助面板；
- 右侧工作台承载岗位列表、画像、简历草稿、source refs、pending confirmations 和导出前检查；
- 不新增招聘平台自动接入、真实 provider 默认调用、真实个人资料读取、自动投递、SaaS、ASR 或会议平台能力。

P8.1 后续工作包：

| 工作包 | 目标 | 验收证据 |
| --- | --- | --- |
| P8.1-DOC | 文档、drawio、门槛、审计和外部意见收口 | active docs 口径一致，drawio 可解析，外部审计确认不建议继续扩写主设计文档 |
| P8.1-M0 | 开发前启动审计 | stage review 无重大 PRD 偏差 |
| P8.1-M1 | Chatbox-first 布局重构 | 桌面首屏聊天时间线和输入框可见 |
| P8.1-M2 | 资料/JD/简历入口迁移 | 输入框附近工具条或左右辅助面板截图 |
| P8.1-M3 | 状态机和工作台职责稳定 | Agent 状态、岗位、画像、简历、待确认项截图 |
| P8.1-M4 | 响应式和视觉质量修复 | 1200px/1440px/1920px/720px/390px 截图 |
| P8.1-M5 | 自动化验收报告 | 中文 HTML 报告和 PRD 检视 |

P8.1 结束后的用户可见状态必须是：用户打开 Chatbox 后先对话，再通过输入框附近入口补资料、粘贴 JD、选岗位和生成简历；右侧只负责产物和确认，不能继续用中央大块 workflow 区压低聊天优先级。

P8.1 文档收口判断：当前 PRD、目标架构、里程碑、验收门槛、追踪矩阵、专项计划、drawio 和文本镜像已能支撑 P8.1-M0 到 P8.1-M5 的后续自动化开发。后续不再扩写主设计文档，除非 P8.1-M0 启动审计发现新增致命或重大规格偏差。

P8.1 出门不能声称：

- P8.1 文档开发等于 UI 已修复；
- Chatbox-first 体验未经截图和人工复核即可冻结；
- BOSS 或任何招聘平台已真实接入；
- 真实 provider 或真实个人资料路径被列为验收结论。

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

## 9. P6+P7 历史主线和 P5.5 历史补充

本节前半部分记录 P6+P7 已完成自动化候选的历史主线。当前 P4 已冻结，P5-REAL/P5-Freeze 已冻结延期到 P7 后复验，P6+P7 已作为后续基线保留。以下执行顺序不再表示当前新增开发目标，而是用于说明 P6+P7 自动化候选和 P7-post 复验边界：

1. P5-M0：完成真实资料本地闭环 PRD、目标架构、验收门槛、脱敏策略、drawio 和人工确认点；
2. P5-M1 到 P5-FC：已按 P5 文档完成自动化候选；
3. P5-REAL/P5-Freeze：冻结延期到 P7-post，不作为当前阶段阻塞项，也不得写成通过；
4. P6-M0 到 P6-Freeze：真实外部 provider opt-in、调用前确认、API Key 边界、长程连续对话、日志脱敏、失败降级和可视化验收；
5. P7-M0 到 P7-Freeze：发布、部署、数据生命周期、备份/迁移 dry-run、诊断报告、回滚、支持流程和隐私审计；
6. P7-post：在用户提供真实资料路径后执行 P5-REAL/P5-Freeze 复验；
7. 任何真实个人资料、真实外部 provider、自动投递、会议平台、workspace 删除或不可逆迁移操作，都必须先暂停并获得用户确认。
## 9.1 P5.5 Candidate Profile 历史阶段补充

2026-06-29 起，文档主线曾切换为 P5.5 Candidate Profile。该阶段位于 P5 本地资料闭环之后、P6/P7 本地 Beta 自动化候选之后，目标是把用户资料、项目、技能证据和 JD 匹配结果组织成可审查的职业画像与能力评估。当前 P5.5 已完成自动化候选，作为 P8-JD Intake 的候选人画像和 source refs 基线保留。

P5.5 交付后，用户应能看到：

- 专业背景画像：目标岗位、转型路径、当前层级、主要经历线索；
- 能力矩阵：技能名称、类别、证据类型、证据强度、岗位相关性、待确认项；
- 项目可信度：本人贡献、技术难点、可验证材料、量化结果缺口、风险标签；
- 岗位短板：must-have 缺口、nice-to-have 缺口、表达风险和补强行动；
- source refs：每个判断都能追溯到资料、项目、JD 或 artifact。

P5.5 不替代 P5-REAL，不默认外呼真实 provider，不进入 SaaS/ASR/会议平台/自动投递/MCP/CLI。P5.5 后续只作为 P8 简历生成、岗位短板和 source refs 的历史能力基线；真实 provider 复验、P7-post P5-REAL 或 P8+ 高风险能力仍需单独确认。
