# P9-M0 开发前启动审计

日期：2026-07-03

结论：通过。允许进入 P9-M1 到 P9-M9 自动化开发，但实现范围必须严格限定为 Chatbox-first UI 信息架构重构、求职情报可视化层和现有能力重新组织。

## 1. 输入文档

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md`
- `docs/active/stage-reviews/P9_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/active/stage-reviews/P9_EXTERNAL_REVIEW_REVISION_AUDIT.md`

## 2. 开发准入判断

P9 文档已明确当前开发目标：

1. 顶部服务中心展示 provider、ASR、MCP、Skill、外部搜索和安全边界状态。
2. 左侧求职态势图展示岗位市场态势、目标机会与匹配态势、投递流程态势。
3. 中央 Chatbox 始终作为第一交互路径。
4. 右侧产物台展示简历、事实摘要、申请包、source refs、pending confirmations 和导出预检。
5. Chatbox 可发起 JD 汇总、资料补全、申请包生成和流程更新。

这些目标已被 PRD、目标架构、里程碑、验收门槛和追踪矩阵共同支撑，可以进入自动化开发。

## 3. 边界确认

本轮实现不得进入以下范围：

- 不登录或抓取 BOSS、猎聘、拉勾、LinkedIn 等招聘平台。
- 不建设真实全网 JD 搜索系统。
- 不默认调用 MiniMax、DeepSeek 或其他真实外部 provider。
- 不采集麦克风，不调用真实 ASR。
- 不建设 MCP / Skill 平台。
- 不自动投递，不自动对外沟通。
- 不读取未授权真实个人资料。
- 不执行 workspace 删除、migration apply 或不可逆操作。

## 4. 子阶段验收计划

| 子阶段 | 开发内容 | 验收要求 |
| --- | --- | --- |
| P9-M1 | Chatbox-native 三栏信息架构 | 中央 Chatbox 首屏优先，向导卡片不抢占主路径 |
| P9-M2 | 顶部服务中心 | 未配置服务不显示为已连通，设置入口不触发真实外呼 |
| P9-M3 | 左侧求职态势图 | 三页签、地图/图钉、缩放拖动和 Chatbox 联动可见 |
| P9-M4 | JD 信息源与 search run | 只使用用户粘贴、fixture、已有本地示例或合规公开样例 |
| P9-M5 | Chatbox 引导式资料补全 | 资料、项目故事、事实证据和 ASR opt-in 边界可见 |
| P9-M6 | 多 JD 申请包 | 不同 JD 的简历/申请包草稿有 source refs 和待确认项 |
| P9-M7 | Chatbox 更新产物与流程 | 对话可更新投递流程和产物状态，不对外发送 |
| P9-M8 | 响应式视觉质量 | 1920/1440/1200/720/390 多视口无核心入口不可达 |
| P9-M9 | 中文 HTML 验收报告 | 真实截图、测试结果、PRD 规格检视和未验证范围完整 |

## 5. 打回条件

任一子阶段出现以下情况必须打回计划阶段：

- 把合成示例或本地 fixture 写成真实全网搜索。
- 把 provider configured 写成真实 provider 质量通过。
- 把 ASR 状态入口写成真实语音采集已通过。
- 把 Chatbox UI 重构写成自动投递、自动沟通或平台接入完成。
- 验收报告缺少真实界面截图或截图无法证明核心路径。

## 6. 审计意见闭环

未发现致命或重大规格偏差。剩余风险主要是前端实现可能过度 dashboard 化，导致 Chatbox 主路径再次被削弱。实现阶段需要用多视口截图验证：中央 Chatbox 在所有视口下仍是默认主视图。
