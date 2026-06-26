# 给 Gemini 的前端网页设计原型提示词

你正在基于 JobPilot AI 项目的事实基线源码生成前端网页设计原型。请先阅读本文件夹内所有文件，尤其是：

1. `01_STAGE_PRD.md`
2. `02_TARGET_ARCHITECTURE.md`
3. `03_P4_UX_EXPERIENCE_HARDENING_PLAN.md`
4. `04_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`
5. `05_CURRENT_FRONTEND_IMPLEMENTATION_MAP.md`
6. `06_CURRENT_CHATBOX_SOURCE_BASELINE.html`
7. `07_SOURCE_main.tsx`
8. `08_SOURCE_styles.css`

## 项目背景

JobPilot AI 是一个本地优先的 AI 求职材料工作台。目标体验不是营销落地页，而是一个可长期使用的生产力工具：用户通过 Chatbox 连续输入求职方向、简历资料、项目经历和 JD；系统在同一个工作台里沉淀职业事实、岗位解析、匹配报告、申请包、面试准备和导出状态。

## 当前真实前端

- React 19 + Vite + TypeScript。
- 入口是 `07_SOURCE_main.tsx`。
- 样式是 `08_SOURCE_styles.css`。
- 当前 UI 是桌面三栏工作台：左侧任务上下文，中间 Chatbox，右侧 Workbench 产物推进台。
- 390px 移动端通过底部 Workbench 抽屉访问产物。
- 当前实现仍集中在单个 `main.tsx` 中；如果你建议拆组件，请明确这是重构建议，不是当前事实。

## 严格事实边界

- 不要把 P4/P4B/P4C 描述为已经完成人工体验审查闭环。
- 不要把真实个人资料、真实 API Key、真实外部 provider 默认路径描述为已完成验收。
- 当前自由连续对话只是本地/mock 基线，不是完整 provider-backed 智能聊天。
- 不要新增 ASR、会议平台、自动投递、SaaS、多租户、Billing 或真实外部模型默认调用。
- Career facts artifact 在消息/后端引用中有证据，但右侧 Workbench 展示存在局部刷新/可见性不一致，不能被设计说明隐藏。

## 请完成

1. 基于当前源码和 PRD，生成一个更专业、更好看的前端网页设计原型。
2. 第一屏必须是可操作的 JobPilot AI 工作台，不要做宣传首页。
3. 覆盖桌面 1440/1920、窄屏 720、移动 390 的布局方案。
4. 优化 Chatbox 空状态、自由对话、任务入口、状态反馈、错误恢复、Workbench、Artifact 卡片、确认项、导出和移动抽屉体验。
5. 输出可落地的 HTML/CSS/JS 原型，或 React 组件结构 + 样式 token + 可合并 patch。
6. 每个设计决策都说明它解决了当前源码或 PRD 中的哪个问题。
7. 不要虚构功能、数据、用户、logo、验收结论或真实 provider 能力。

## 期望输出

- 设计诊断
- 目标体验原则
- 页面树和组件树
- 可运行原型代码
- 桌面/移动状态覆盖
- 和当前 `main.tsx` / `styles.css` 的迁移建议
- 仍需后端或后续阶段配合的事项
