# P9 详细开发及验收计划

状态：文档开发阶段计划。本文档不进入代码实现，不授权真实 provider、ASR、招聘平台登录、自动投递、MCP/Skill 真实连通或读取真实个人资料。

## 1. 开发前总原则

P9 的目标是把 JobPilot AI 从向导卡片式工作台推进为 Chatbox-native 求职情报与申请包工作台。后续自动化开发必须按阶段推进，每个阶段完成后都要做端到端验收和 PRD 规格检视。

P9 的实施范围必须锁定为：

```text
Chatbox-first UI 与信息结构重构
+ 求职情报可视化层
+ 现有 API / Domain / Artifact 能力重新组织
```

后续开发不得把 P9 扩张为新系统平台。禁止范围：

- 不新增真实数据源系统；
- 不新增外部平台接入；
- 不新增长期运行任务系统；
- 不新增独立业务服务；
- 不建设真实 JD 搜索系统；
- 不建设真实 ASR 系统；
- 不建设 MCP/Skill 平台；
- 不建设招聘平台自动化或自动投递能力。

开发顺序：

```text
P9-M0 启动审计
→ P9-M1 Chatbox-native 信息架构
→ P9-M2 顶部服务中心
→ P9-M3 左侧求职态势图
→ P9-M4 JD 信息源与 search run
→ P9-M5 Chatbox/ASR 引导式资料补全
→ P9-M6 多 JD 申请包生成
→ P9-M7 Chatbox 驱动产物与流程更新
→ P9-M8 响应式与视觉质量
→ P9-M9 中文自动化验收报告与出门审计
```

任何阶段出现以下情况必须打回计划阶段：

- 实现结果与 P9 PRD 目标体验明显偏离；
- 自动化报告使用概念图、目标图或合成图替代真实界面截图；
- 报告把全网 JD 搜索、招聘平台自动接入、真实 provider、ASR、MCP/Skill 或自动投递写成已通过；
- 默认读取真实个人资料、默认采集麦克风、默认外呼外部 provider 或默认访问招聘平台账号；
- 右侧产物没有 source refs、pending confirmations 或版本边界。

## 2. P9-M0 开发前启动审计

目标：确认文档足以进入实质开发，且没有重大规格偏差。

输入文档：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`

执行项：

- 复核 P9 当前阶段仍是文档阶段，不把目标写成已实现。
- 复核 P8.1/P8/P5.5/P6/P7 只作为基线，不作为 P9 完成结论。
- 复核 P9 不默认启用高风险能力。
- 生成 `P9_M0_START_AUDIT.md`。

出门条件：

- 启动审计无致命或重大规格偏差；
- 后续每个阶段的验收标准已引用 PRD 与门槛；
- 允许进入 P9-M1。

## 3. P9-M1 Chatbox-native 信息架构

目标：让中央 Chatbox 成为首屏第一路径，消除向导卡片主导感。

开发范围：

- 调整 `apps/chatbox/src/main.tsx` 中的页面结构；
- 保留 P8.1 已有 Chatbox timeline、状态、输入框和工具入口；
- 让资料/JD/简历工具入口围绕输入框或辅助面板组织；
- 不新增真实 provider、ASR 或外部搜索调用。

验收标准：

- 1200px、1440px、1920px 下中央 Chatbox 时间线、历程状态和输入框首屏可见；
- 720px、390px 下 Chatbox 是默认主视图；
- 页面不再要求用户先处理大型向导卡片才能对话；
- 资料、JD、申请包入口仍可达。

证据：

- 真实界面截图；
- 前端 build；
- PRD 规格检视；
- 本阶段审计 `P9_M1_CHATBOX_NATIVE_AUDIT.md`。

## 4. P9-M2 顶部服务中心

目标：让用户快速了解当前服务配置和安全边界。

开发范围：

- 实现或复核 `TopServiceCenter`；
- 展示 provider、ASR、MCP、Skill、外部搜索、workspace、安全边界状态；
- 状态必须区分 `unavailable`、`not_configured`、`configured`、`connected`、`disabled`、`requires_confirmation`；
- 未验证服务不得显示为已连通。

验收标准：

- mock/provider 默认模式下显示本地/mock 或未配置状态；
- ASR、MCP、Skill、外部搜索如果未实现或未授权，必须显示为不可用、待配置或需确认；
- 点击设置入口不触发真实外呼；
- 不保存 API Key。

证据：

- 顶部服务中心截图；
- API/status 或本地状态 fixture 验收；
- false-green 文案扫描；
- 本阶段审计 `P9_M2_SERVICE_CENTER_AUDIT.md`。

## 5. P9-M3 左侧求职态势图

目标：实现岗位市场态势、目标机会与匹配态势、投递流程态势三大板块。

开发范围：

- 新增 `LeftIntelligencePanel`；
- 新增 `MarketMapView`、`OpportunityMatchPanel`、`ApplicationPipelineView` 或等价组件；
- 地图方案可先采用 SVG/ECharts/离线地图形态，后续再评估 MapLibre/Leaflet；
- 支持放大、缩小、拖动、重置、折叠和页签切换；
- 点击城市、岗位或流程节点后能把上下文带回 Chatbox。

验收标准：

- 三大板块均可见且职责不重叠；
- 地图/图钉或等价地图可视化可交互；
- 无真实外部搜索授权时，只展示 fixture、手动导入或合规公开源标记；
- 左侧面板不压住中央 Chatbox。

证据：

- 多视口左侧态势截图；
- 地图缩放/拖动自动化步骤记录；
- Chatbox 联动截图；
- 本阶段审计 `P9_M3_LEFT_INTELLIGENCE_AUDIT.md`。

## 6. P9-M4 JD 信息源与 search run

目标：用现有 API/Domain 边界表达 JD 信息源与 search run，不建设真实 JD 搜索系统，不默认接入招聘平台账号。

开发范围：

- 在现有 API/Domain 模块内新增轻量 `JobSourceConnector` 边界或等价函数，不新增独立业务服务；
- 支持用户粘贴、fixture、已有本地示例或合规公开样例数据；
- 记录 `search_run`、来源、query、城市、薪资、技术栈、结果数量、合规状态和 source refs；
- 不登录 BOSS、猎聘、拉勾、LinkedIn；
- 不绕验证码、反爬、账号权限或平台风控。
- 不新增长期运行任务、定时抓取、队列消费或平台 connector 后台服务。

验收标准：

- 用户可通过 Chatbox 发起“汇总北京 LLM 应用岗”等请求，并得到基于用户粘贴、fixture 或已有本地示例数据的可解释结果；
- 系统返回明确来源和限制；
- 搜索结果能进入左侧市场态势和右侧岗位/申请包路径；
- 报告不得写成全网搜索或平台接入已通过。

证据：

- API/eval；
- Chatbox 发起 search run 的真实截图；
- source refs 和合规状态截图；
- 本阶段审计 `P9_M4_JOB_SOURCE_SEARCH_AUDIT.md`。

## 7. P9-M5 Chatbox/ASR 引导式资料补全

目标：通过 Chatbox 引导用户补全简历模板、项目故事、能力证据和求职偏好。P9 不建设真实 ASR 系统；ASR 仅作为 opt-in 状态和后续独立阶段边界。

开发范围：

- 实现或复核 `handleP9Command` 的 Chatbox 命令解析与本地编排；
- 以本地故事草稿、既有 profile/resume/artifact 能力覆盖 P9 自动化候选；`StoryBank` / `CandidateFactGraph` 作为后续独立服务边界，不在 P9 新增；
- 通过对话收集事实、故事、证据、作品链接和偏好；
- 缺证据内容进入 pending confirmations；
- ASR 只展示入口状态、不可用/需确认说明或后续规划，不采集麦克风，不调用外部语音服务。

验收标准：

- 用户能说“帮我补全项目故事”并进入引导式问答；
- 系统能区分事实、待确认、建议表达；
- 右侧产物台能看到事实摘要和故事草稿；
- ASR 不触发真实麦克风采集或外部调用。

证据：

- 多轮对话 transcript；
- StoryBank/source refs/pending confirmations 证据；
- ASR 未启用状态截图；
- 本阶段审计 `P9_M5_GUIDED_INTAKE_AUDIT.md`。

## 8. P9-M6 多 JD 申请包生成

目标：基于不同 JD 生成可追溯的简历、面试故事、求职信或申请包草稿。

开发范围：

- 强化 `ResumePackageGenerator`；
- 引入 `ApplicationPackageVersion` 或等价版本边界；
- 支持每个 JD 绑定申请包版本；
- 输出必须包含 source refs、pending confirmations、导出预检。

验收标准：

- 至少两个不同 JD 能生成不同申请包草稿；
- 申请包能说明针对该 JD 做了哪些取舍；
- 缺证据内容不写成事实；
- 普通聊天不静默覆盖当前版本。

证据：

- 多 JD 申请包截图；
- source refs / pending confirmations / version eval；
- 导出预检证据；
- 本阶段审计 `P9_M6_APPLICATION_PACKAGE_AUDIT.md`。

## 9. P9-M7 Chatbox 驱动产物与流程更新

目标：用户能通过 Chatbox 修改申请包、项目事实、目标岗位和投递流程。

开发范围：

- 新增 `ApplicationPipelineService` 或等价 domain；
- 定义流程状态：待评估、待投递、已投递、HR 沟通、笔试、面试、Offer、拒绝、搁置；
- 支持 Chatbox 更新状态、备注、下一步动作和时间；
- 所有关键更新需要可回看，不静默覆盖历史。

验收标准：

- 用户可通过对话把某岗位状态改为“一面通过，下周三二面”；
- 左侧流程态势更新，右侧产物台记录相关备注；
- 不对外发送消息，不自动投递；
- 修改事实或申请包时保留版本/历史。

证据：

- 流程更新前后截图；
- domain/eval；
- 历史记录或版本证据；
- 本阶段审计 `P9_M7_PIPELINE_UPDATE_AUDIT.md`。

## 10. P9-M8 响应式与视觉质量

目标：确保 P9 在桌面、平板和移动端都有高可视度。

开发范围：

- 强化 `styles.css` 或等价样式系统；
- 覆盖 1920px、1440px、1200px、720px、390px；
- 左侧、中央、右侧在窄屏下应有清晰主次和折叠策略；
- 不能出现按钮错位、文字重叠、核心入口不可达。

验收标准：

- 1920/1440/1200 下四区域布局清晰；
- 720 下 Chatbox 默认主视图，态势图和产物台可作为次级面板；
- 390 下输入框、发送、关键工具入口可达；
- 地图可视化不会遮挡输入框。

证据：

- 多视口真实截图；
- accessibility/keyboard 基础检查；
- 视觉质量 PRD 检视；
- 本阶段审计 `P9_M8_RESPONSIVE_VISUAL_AUDIT.md`。

## 11. P9-M9 中文自动化验收报告与出门审计

目标：生成可供人类完整审计的中文 HTML 自动化验收报告。

报告必须包含：

- P9 目标架构；
- 当前架构实现；
- 用户场景路径；
- 多视口真实截图；
- 左侧态势图交互证据；
- Chatbox 发起 JD 汇总、资料补全、申请包生成、流程更新证据；
- source refs、pending confirmations、版本边界证据；
- 测试与构建结果；
- 未验证范围和高风险能力边界。

最低命令：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
drawio XML parse
```

出门条件：

- 报告可读性高，能让人类判断 P9 是否达到 PRD；
- 不使用概念图替代真实实现截图；
- 不虚假声明全网搜索、平台接入、ASR、真实 provider、MCP/Skill 或自动投递通过；
- 生成最终 stage review。

## 12. 本文档审计结论

P9 当前文档足以指导后续自动化开发。后续应先执行 P9-M0，而不是继续扩写主设计文档。除非 P9-M0 发现新增致命或重大规格偏差，否则可以进入 P9-M1。
