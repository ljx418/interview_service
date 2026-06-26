# 合成项目资料：JobPilot Local Materials Workbench

> 本文件是 JobPilot P5 自动化验收使用的合成项目资料，不属于真实项目背调材料。

## 项目目标

把求职者的简历、项目说明和目标 JD 放入本地 workspace，生成可确认、可编辑、可导出的申请材料。

## 技术栈

- React、TypeScript、Vite
- FastAPI、SQLite
- pytest、Chrome/CDP、Markdown/DOCX export

## 个人贡献

- 设计 Conversation / Workbench / Artifact 三栏工作台。
- 实现申请包导出前 blocking confirmation 拦截。
- 编写多视口自动化截图场景和中文 HTML 验收报告。
- 处理导出失败后的恢复提示，让用户知道需要先确认事实。

## 可验证证据

- README、截图报告、pytest 输出、前端 build 输出。
- source refs 与 questions_to_confirm 保留在 artifact 中。

## 风险与缺口

- 文本质量默认使用本地 mock 规则，不代表真实外部模型生成质量。
- 若用于真实投递，需要人工确认本人贡献和量化指标。
