# P4 UX 实现与验收阶段评审

日期：2026-06-17

## 1. 阶段结论

当前 P4 自动化开发项已完成一轮闭环：

- Chatbox 空状态任务入口已并入 suggested prompts；
- provider 状态改为用户可理解的隐私语义；
- 对话区增加 thinking / loading、业务阻塞恢复动作和长内容折叠；
- Workbench 继续保持桌面右栏、移动端底部抽屉；
- P4B 已增加全尺寸桌面任务上下文面板，使 1200px、1440px、1600px、1920px 下形成“任务上下文 / 对话 / 推进台”三栏工作台；
- 截图脚本已改为创建独立 Chrome target，并在结束时清理 viewport emulation / touch emulation；
- 产物卡以求职语义展示摘要、确认项、版本、导出和来源详情；
- P4 HTML 验收报告使用真实 Chrome 截图证据；
- 回归测试、前端构建和 drawio XML 解析通过。

审计口径：

```text
P4 自动化工程验收：通过
P4 人工主观体验验收：待用户确认
真实个人资料自动验收：未执行
真实外部 provider 默认调用验收：未执行
```

## 2. 对照 P4 工作包

| 工作包 | 状态 | 证据 |
| --- | --- | --- |
| P4-UX1 信息架构重排 | 已完成 | Chatbox 空状态 suggested prompts；桌面双栏；移动端抽屉 |
| P4-UX2 任务入口优化 | 已完成 | prompt 填入/触发；示例路径；缺 JD 恢复 |
| P4-UX3 产物卡可读性 | 已完成 | 岗位解析、匹配报告、申请包草稿、主次按钮 |
| P4-UX4 状态与反馈 | 已完成 | thinking spinner、执行步骤、recoverable error |
| P4-UX5 响应式精修 | 已完成自动化截图 | 1280 / 720 / 390 Chrome 截图 |
| P4-UX5A 全尺寸桌面工作台 | 已完成自动化截图，待人工体验确认 | 1200 / 1440 / 1600 / 1920 Chrome 截图 |
| P4-UX5B 截图脚本隔离 | 已完成 | 独立 Chrome target；finally 清理 emulation |
| P4-UX6 人工体验审查包 | 已完成报告文件 | `docs/reports/P4_UX_EXPERIENCE_ACCEPTANCE_REPORT.html` |
| P4-UX7 Gemini 前端审查包 | 已完成 | `docs/gemini-frontend-review-package/` |

## 3. PRD 规格检视

P4 PRD 要求用户打开本地 Chatbox 后，能清楚知道从哪里开始，输入或上传后知道系统正在做什么，能区分聊天、计划、产物、确认项和导出，并能在错误或缺资料时恢复。

当前实现覆盖：

- 首屏不再以工程状态或阶段表为主；
- 任务入口在 Chatbox 空状态内；
- 发送有效任务或运行示例路径后有可见响应；
- 缺少 JD 时不是静默失败，而是显示补充 JD / 跑示例路径；
- Workbench 展示当前目标、产物、确认项、版本和导出；
- 1200px、1440px、1600px、1920px 下不再是左侧窄栏加右侧空白，而是三栏工作台；
- 截图脚本不会复用人工正在审查的浏览器标签页作为截图 target；
- 390px 下 Workbench 不挤压 Chatbox。

未自动覆盖：

- 用户是否“愿意长期使用”的主观判断；
- 真实个人资料输入后的人工体验；
- 真实外部 provider 生产质量。

## 4. 验收证据

```text
docs/reports/evidence/p4_workbench_initial_1280.png
docs/reports/evidence/p4_workbench_initial_1200.png
docs/reports/evidence/p4_workbench_initial_1440.png
docs/reports/evidence/p4_workbench_initial_1600.png
docs/reports/evidence/p4_workbench_initial_1920.png
docs/reports/evidence/p4_workbench_error_recovery_1200.png
docs/reports/evidence/p4_workbench_error_recovery_1280.png
docs/reports/evidence/p4_workbench_completed_1200.png
docs/reports/evidence/p4_workbench_completed_1280.png
docs/reports/evidence/p4_workbench_completed_1440.png
docs/reports/evidence/p4_workbench_completed_1600.png
docs/reports/evidence/p4_workbench_completed_1920.png
docs/reports/evidence/p4_workbench_narrow_720.png
docs/reports/evidence/p4_workbench_mobile_390.png
docs/reports/P4_UX_EXPERIENCE_ACCEPTANCE_REPORT.html
```

最低命令：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
python3 -c 'import xml.etree.ElementTree as ET; ET.parse("docs/active/jobpilot-stage-gap-and-acceptance.drawio")'
```

本轮实际复验：

```text
python3 -m pytest tests/evals/test_p4_ux_acceptance_report_eval.py tests/evals/test_p3_artifact_workbench_eval.py
→ 4 passed

npm --prefix apps/chatbox run build
→ passed
```

## 5. 虚假验收风险控制

本轮不得声明：

- P4 已被人工完全认可；
- examples 数据等同于真实个人资料验收；
- 外部模型默认调用已完成生产验收；
- 静态原型等同于工程实现；
- P4 包含 MCP、CLI、ASR、会议平台、自动投递或 SaaS。

## 6. 下一步

如果人工体验审查仍不认可，应进入 P4 第二轮 UX 修正，优先处理：

- 对话文字节奏和语气；
- Workbench 信息密度；
- 产物详情的非 JSON 预览；
- 移动端抽屉操作路径；
- 真实资料模式的低风险引导。
