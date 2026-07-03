# P9-M9 自动化验收与出门审计

日期：2026-07-03

结论：P9 Chatbox-native 求职情报与申请包工作台自动化候选通过。当前结论只覆盖本地 UI 信息架构、求职态势可视化层、Chatbox 本地命令路由、现有能力重新组织和多视口自动化截图证据。

## 1. 验收对象

- 顶部服务中心：LLM Provider、JD 信息源、ASR、MCP/Skill、Workspace 状态。
- 左侧求职态势：市场地图、机会匹配、投递流程三页签。
- 中央 Chatbox：首屏主路径、输入框、工具入口、JD/薪资/城市汇总、资料补全、流程更新。
- 右侧产物台：search run、故事草稿、流程摘要、岗位、简历、画像、source refs 和 pending confirmations。
- 响应式：1920px、1440px、1200px、720px、390px。

## 2. 已执行命令

```bash
python3 scripts/generate_p9_chatbox_native_acceptance.py
python3 -m pytest tests/evals/test_p9_chatbox_native_acceptance_eval.py
npm --prefix apps/chatbox run build
python3 -m pytest
git diff --check
```

结果：

- P9 报告脚本：通过，生成 7 张真实界面截图。
- P9 eval：4 passed。
- Chatbox build：通过。
- 全量 pytest：131 passed, 20 warnings。
- diff whitespace check：通过。

## 3. 证据路径

- 中文 HTML 验收报告：`docs/reports/P9_CHATBOX_NATIVE_ACCEPTANCE_REPORT.html`
- 截图证据：`docs/reports/evidence/p9_chatbox_native/`
- 结构化命令证据：`docs/reports/evidence/p9_chatbox_native/p9_command_evidence.json`
- 报告自检证据：`docs/reports/evidence/p9_chatbox_native/p9_post_report_evidence.json`
- P9 eval：`tests/evals/test_p9_chatbox_native_acceptance_eval.py`

## 4. PRD 规格检视

| 要求 | 结论 | 证据 |
| --- | --- | --- |
| Chatbox 是第一交互路径 | 通过 | 1920/1440/1200/720/390 截图显示中央 Chatbox 和输入区可见 |
| 顶部服务中心 | 通过 | P9 首屏截图显示 provider、JD 信息源、ASR、MCP/Skill、Workspace 状态 |
| 左侧求职态势三板块 | 通过 | 截图覆盖市场地图和流程态势，代码包含匹配态势页签 |
| Chatbox 发起 JD 汇总 | 通过 | `p9_search_run_1920.png` |
| Chatbox 更新投递流程 | 通过 | `p9_pipeline_update_1920.png` |
| 右侧产物台 | 通过 | 截图显示 search run、故事草稿、流程、岗位、简历入口和画像入口 |
| 高风险边界 | 通过 | 报告未把真实搜索、真实 provider、真实资料、ASR、自动投递写成已通过 |

## 5. 未验证范围

以下能力仍未通过 P9 验收，后续必须单独立项和授权：

- 真实全网 JD 搜索；
- BOSS、猎聘、拉勾、LinkedIn 等招聘平台登录、抓取、自动沟通或自动投递；
- MiniMax、DeepSeek、OpenAI-compatible provider 真实质量；
- 用户真实个人资料路径；
- 麦克风采集和真实 ASR；
- MCP/Skill 真实平台连通；
- SaaS、多租户、Billing、会议平台；
- workspace 删除、cleanup apply、migration apply 或其他不可逆操作。

## 6. 审计意见

P9 自动化候选可以进入人工体验审查或下一轮产品规划。若人工体验认为移动端全页截图顺序、左侧态势表达、地图精细度或 Chatbox 视觉权重仍不达标，应打回 P9-M1/P9-M3/P9-M8 继续优化。当前不建议把本结论写成最终产品化完成。

## 7. 阶段收口复验追加记录

日期：2026-07-04

为响应阶段性审计要求，已追加一轮 P9 阶段收口复验：

- drawio 已同步到最新实现状态，8 页分别覆盖目标体验、当前与目标差异、代码实体与分层、左侧态势图、用户体验路线、开发及验收计划、里程碑门槛、安全边界与证据；
- drawio 文本镜像已从“文档阶段”修订为“P9 自动化候选阶段收口审计”，明确 P9-M0 到 P9-M9 在本地自动化候选范围内完成；
- 追加最终 HTML 报告：`docs/reports/P9_STAGE_CLOSURE_ACCEPTANCE_REPORT.html`；
- 追加截图与结构化证据目录：`docs/reports/evidence/p9_stage_closure/`；
- 追加脚本：`scripts/generate_p9_stage_closure_acceptance.py`；
- 追加 eval：`tests/evals/test_p9_stage_closure_acceptance_eval.py`。

追加复验命令结果：

```bash
python3 scripts/generate_p9_stage_closure_acceptance.py
python3 -m pytest tests/evals/test_p9_stage_closure_acceptance_eval.py
python3 -m pytest
npm --prefix apps/chatbox run build
git diff --check
```

结果：

- P9 阶段收口报告脚本：通过，生成 7 张 headless 真实界面截图；
- P9 阶段收口 eval：5 passed；
- 全量 pytest：136 passed, 20 warnings；
- Chatbox build：通过；
- drawio XML parse：通过，8 页；
- diff whitespace check：通过。

追加复验结论仍保持边界：P9 阶段收口不代表真实全网 JD 搜索、招聘平台接入、真实 provider、真实个人资料、真实 ASR、MCP/Skill 连通、自动投递、SaaS 或会议平台能力通过。
