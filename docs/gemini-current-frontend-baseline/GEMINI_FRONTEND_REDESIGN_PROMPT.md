# 给 Gemini 的提示词

你正在基于 JobPilot AI 当前真实使用的 Chatbox 前端源码做 UI/UX 优化。请直接阅读并修改这个源码基线包，不要基于想象重写一个与项目脱节的展示页。

## 你收到的源码

```text
CURRENT_FRONTEND_IMPLEMENTATION_MAP.md
README_FOR_GEMINI.md
package.json
package-lock.json
index.html
vite.config.ts
tsconfig.json
src/main.tsx
src/styles.css
```

这是当前项目 `apps/chatbox` 的真实前端源码副本。

请先完整阅读 `CURRENT_FRONTEND_IMPLEMENTATION_MAP.md`。它已经把 PRD 要求、当前源码结构、组件划分、API 调用、已实现用户功能和已知缺陷做了对齐。你的输出必须以这份实现地图为事实基础。

## 项目背景

JobPilot AI 是一个求职 AI 工作台。目标体验是：用户通过连续 Chatbox 输入资料、职位目标和求职需求；系统在同一工作台中沉淀职业事实、职位解析、匹配报告、申请包、面试准备等产物；桌面端以三栏工作台承载“导航/状态 - 对话 - Workbench”，移动端以压缩布局或抽屉承载相同能力。

## 当前已知实现

1. React 19 + Vite 7 + TypeScript。
2. 入口是 `src/main.tsx`。
3. 主样式和设计 token 在 `src/styles.css`。
4. 当前 API base 是 `http://127.0.0.1:8000`。
5. 当前 UI 已有桌面三栏、窄屏和移动端响应式结构。
6. 当前 UI 视觉体验仍然粗糙，需要显著提升产品感、信息层级、布局比例、交互反馈和移动端可用性。
7. 当前没有真实拆分的 `components/` 目录；`main.tsx` 内部已有多个函数组件。你可以提出拆分，但必须说明这是建议重构，不是当前事实。

## 严格事实边界

1. 不要把 P4 描述为已经完成人工体验审查闭环。
2. 不要把真实个人资料路径、真实 API Key、真实外部 provider 默认路径描述为已完成验收。
3. 当前验收主要基于本地 mock/demo 路径。
4. 自由 Chatbox 和无中断连续多轮对话仍是后续开发目标，不能写成已完整产品化。
5. Career facts artifact 有消息和后端引用证据，但右侧 Workbench 展示存在局部刷新/可见性不一致，设计说明必须保留这个事实。
6. 不要新增 ASR、会议平台、自动投递、SaaS、真实外部模型调用等未确认能力。

## 请你完成

1. 基于现有 `src/main.tsx` 和 `src/styles.css`，提出并实现更专业的求职 AI 工作台界面。
2. 保留现有 API 交互和业务状态，不要破坏现有功能。
3. 优先改进：
   - 首屏信息层级
   - 对话区可读性
   - Workbench 产物区可扫描性
   - 阶段/任务状态表达
   - Artifact 生成、待确认、错误、局部失败状态表达
   - 桌面三栏比例
   - 720px 窄屏和 390px 移动端体验
4. 输出可以直接覆盖或合并回项目的代码，而不是只给视觉描述。
5. 如果需要拆分组件，请给出清晰的文件树，并保证所有现有功能、API 和状态仍能映射；如果不拆分，请直接给出修改后的 `src/main.tsx` 和 `src/styles.css`。
6. 不要做营销落地页，第一屏必须是可操作的产品工作台。
7. 不要使用虚假统计、虚假客户、虚假 logo、虚假验收结论或无法落地的装饰内容。

## 期望输出格式

请按以下结构输出：

1. 设计诊断：当前源码界面的主要问题。
2. 设计目标：这次改动要改善什么。
3. 当前组件理解：请引用 `CURRENT_FRONTEND_IMPLEMENTATION_MAP.md` 中的组件和功能边界，说明你将改哪些组件。
4. 修改后的文件树。
5. 完整代码或清晰 patch。
6. 验收清单：
   - 桌面 1440px
   - 桌面 1920px
   - 窄屏 720px
   - 移动端 390px
   - guided path
   - free chat
   - status query
   - career facts artifact 局部展示风险
7. 仍未完成或需要后端配合的事项。
