# JobPilot AI 前端页面审查包

本文件夹用于交给 Gemini 或其他外部审查者独立审查 JobPilot AI 当前 P4 UX 体验强化方案。审查重点是前端网页设计、交互易用性、视觉高级感、信息架构和响应式体验，不是后端 Agent 能力评测。

## 项目一句话

JobPilot AI 是面向转行程序员的本地优先、免费开源求职 Agent 服务。默认入口是 Chatbox，核心目标是帮助用户把简历、项目资料和 JD 变成可信、可确认、可导出的求职材料。

## 当前阶段

P4 UX 体验强化。P0-P3 已经证明本地 examples 路径、后端工具链、Chatbox 响应、推进台、截图报告可以跑通；但人工审查认为当前界面仍偏工程验收控制台，首屏任务入口、产物卡语言、provider 状态和移动端操作还需要明显优化。

## 本文件夹内容

1. `00_README.md`：审查包说明。
2. `01_PRODUCT_AND_UX_BRIEF.md`：产品背景、用户、目标体验路径和非目标。
3. `02_PAGE_INFORMATION_ARCHITECTURE.md`：页面信息架构和布局策略。
4. `03_COMPONENT_AND_STATE_SPEC.md`：关键组件、状态和交互规则。
5. `04_VISUAL_DESIGN_DIRECTION.md`：视觉设计方向、设计 token 和页面气质。
6. `05_INTERACTION_AND_ACCESSIBILITY_CHECKLIST.md`：交互、响应式和可访问性验收清单。
7. `06_GEMINI_REVIEW_PROMPT.md`：推荐给 Gemini 的完整提示词。
8. `prototype.html`：静态页面原型。
9. `prototype.css`：静态原型样式。
10. `prototype.js`：静态原型交互脚本。

文件数：10，小于 20。

## 审查注意

- 原型是 P4 UX 方案，不等于当前代码已经全部实现。
- 当前原型已吸收 Gemini 第一轮审查意见：任务入口并入 Chatbox 空状态 suggested prompts，增加 loading / thinking、primary/secondary 操作层级、provider 用户语言和移动端 Workbench 折叠策略。
- 默认验收数据是 examples 真实感数据，不是用户真实个人资料。
- 默认 provider 是 mock；外部 provider 只允许用户确认后调用。
- 不要把 MCP、CLI、ASR、会议平台、自动投递或 SaaS 化纳入 P4 必交付建议。
