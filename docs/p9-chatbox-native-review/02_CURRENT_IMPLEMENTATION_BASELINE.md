# P9 当前实现基线与差距

状态：文档审查阶段
基线来源：当前仓库、P8.1 自动化验收报告、真实 Chatbox 截图。

## 1. 当前已实现自动化候选

| 能力 | 当前状态 | 证据 |
| --- | --- | --- |
| Chatbox-first 三栏工作台 | 已实现自动化候选 | `docs/reports/P8_1_CHATBOX_FIRST_ACCEPTANCE_REPORT.html` |
| 手动 JD 导入 | 已实现 | `POST /api/job/intake` |
| 岗位列表与目标岗位 | 已实现 | `GET /api/jobs`, `POST /api/jobs/{job_id}/select` |
| JD 定制简历 | 已实现 | `POST /api/resume/generate` |
| 候选人画像 | 已实现自动化候选 | `/api/profile/candidate`, `/api/profile/candidate/refresh` |
| 右侧工作台 | 已实现候选 | `Workbench`, `JobTargetList`, `ResumeGenerationPlane` |
| provider opt-in 基线 | 已实现候选 | `/api/provider/status`, `/api/provider/consent` |
| 文本实时提示基线 | 已有接口 | `/api/realtime/start`, `/api/realtime/detect-question` |

## 2. 当前前端真实基线观察

真实截图：`evidence/baseline-current-chatbox.png`

可见事实：

- 页面已经是左中右三栏。
- 中央保留 Chatbox、状态机、时间线和输入框。
- 输入框上方已有上传资料、粘贴 JD、选择岗位、生成简历等工具。
- 中央仍存在较强任务卡片区，例如“导入简历与项目”“解析目标 JD”“模拟面试准备”等。
- 左侧仍以任务指导和安全边界为主，不是招聘态势图。
- 顶部只展示局部运行状态和模型设置，不是完整服务中心。
- 右侧已有产物台，但缺少 P9 所需的市场态势和招聘流程联动。

## 3. 当前未实现能力

| P9 目标 | 当前状态 |
| --- | --- |
| 自动搜索公开 JD 信息源 | 未实现 |
| JD 搜索任务、去重、标准化和可信度 | 未实现 |
| 城市薪资分布、技术栈热度、地图/图表态势 | 未实现 |
| 招聘流程图和公司状态可视化 | 未实现 |
| Chatbox 更新招聘流程状态 | 未实现 |
| ASR opt-in 资料采集 | 未实现完整链路 |
| 顶部 MCP / Skill / ASR / 搜索源服务中心 | 未实现 |
| 多 JD 申请包批量对比与版本化故事库 | 部分能力存在，P9 目标未实现 |

## 4. P9 设计约束

- 不继续增加大型向导卡片。
- 不把左侧做成静态任务列表。
- 不让右侧产物台空置或只展示内部 artifact。
- 不把目标图、概念图或 PRD 写成已实现。
- 不把真实 provider、ASR、MCP、Skill、招聘平台接入写成已通过。
