# JobPilot AI Gemini UI Prototype Brief

这个文件夹用于交给 Gemini 生成 JobPilot AI 前端网页设计原型。它提供 PRD、目标架构、当前源码基线和当前实现说明，目标是让 Gemini 基于项目事实优化交互体验，而不是凭空设计一个脱离代码的展示页。

## 阅读顺序

1. `01_STAGE_PRD.md`
2. `02_TARGET_ARCHITECTURE.md`
3. `03_P4_UX_EXPERIENCE_HARDENING_PLAN.md`
4. `04_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`
5. `05_CURRENT_FRONTEND_IMPLEMENTATION_MAP.md`
6. `06_CURRENT_CHATBOX_SOURCE_BASELINE.html`
7. `07_SOURCE_main.tsx`
8. `08_SOURCE_styles.css`
9. `09_GEMINI_PROMPT.md`

## 每个文件的用途

| 文件 | 用途 |
| --- | --- |
| `01_STAGE_PRD.md` | 当前 P4 UX 阶段 PRD，定义目标体验、验收标准、非目标。 |
| `02_TARGET_ARCHITECTURE.md` | 当前目标架构，定义 Experience Shell、Conversation Plane、Workbench、Artifact Cards 等职责。 |
| `03_P4_UX_EXPERIENCE_HARDENING_PLAN.md` | P4 UX 强化计划，说明当前阶段要解决的体验问题。 |
| `04_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md` | 自由 Chatbox 与连续多轮对话计划，说明本地/mock 基线与 provider-backed 后续边界。 |
| `05_CURRENT_FRONTEND_IMPLEMENTATION_MAP.md` | 当前真实前端实现地图，列出组件、API、状态、功能路径和已知缺陷。 |
| `06_CURRENT_CHATBOX_SOURCE_BASELINE.html` | 当前 Chatbox 基线 HTML：静态还原当前首屏，并内嵌当前 `main.tsx` 与 `styles.css` 原文。不是报告页。 |
| `07_SOURCE_main.tsx` | 当前真实 React 源码副本。 |
| `08_SOURCE_styles.css` | 当前真实 CSS 源码副本。 |
| `09_GEMINI_PROMPT.md` | 可直接复制给 Gemini 的原型生成提示词。 |

## 事实边界

- 当前前端是 React 19 + Vite + TypeScript。
- 当前真实入口是 `apps/chatbox/src/main.tsx`，主样式是 `apps/chatbox/src/styles.css`。
- 当前前端仍主要是单文件 React 实现；如果拆分组件，应标注为后续重构建议。
- 当前验收默认是本地/mock/demo 路径。
- 不要把 P4/P4B/P4C 描述为已经完成人工体验审查闭环。
- 不要把真实个人资料、真实 API Key、真实外部 provider 默认路径描述为已完成验收。
- 当前自由连续对话只是本地/mock 基线，不是完整 provider-backed 智能聊天。
- 不要新增 ASR、会议平台、自动投递、SaaS、多租户、Billing 或真实外部模型默认调用。

## Gemini 应输出什么

Gemini 应基于这些文件输出一个更专业的前端网页设计原型，第一屏必须是可操作的 JobPilot AI 工作台，而不是营销落地页。输出可以是 HTML/CSS/JS 原型，也可以是 React 组件结构、样式 token 和可合并 patch。
