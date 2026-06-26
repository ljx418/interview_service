# JobPilot AI Gemini 前端原型包 v2

本文件夹用于交给 Gemini 独立生成和审查 JobPilot AI 的 P4 前端网页设计原型。它只关注前端体验、信息架构、视觉系统和交互状态，不评估后端模型质量。

## 阅读顺序

1. `01_CONTEXT_AND_SCOPE.md`
2. `02_TARGET_ARCHITECTURE_AND_CURRENT_IMPLEMENTATION.md`
3. `03_USER_FLOWS_AND_ACCEPTANCE_GATES.md`
4. `04_VISUAL_SYSTEM_AND_COMPONENT_SPEC.md`
5. `05_EVIDENCE_CONTACT_SHEET.html`
7. `prototype.html`
8. `prototype.css`
9. `prototype.js`
10. `07_GEMINI_PROMPT.md`

文件数固定为 10 个。`07_GEMINI_PROMPT.md` 同时包含 Gemini 提示词和原型生成硬约束。

## 使用方式

- 打开 `05_EVIDENCE_CONTACT_SHEET.html` 查看当前真实界面截图和发现的问题。
- 打开 `prototype.html` 查看本包提供的可点击设计原型。
- 将 `07_GEMINI_PROMPT.md` 的提示词连同本文件夹内容交给 Gemini，让它继续生成更好的 `prototype.html`、`prototype.css`、`prototype.js`。

## 审查边界

- 原型是设计方案，不代表已进入生产代码。
- 本包只覆盖 P4/P4C-FC 本地/mock 前端体验。
- 不得声称 P4 已人工体验认可。
- 不得声称真实个人资料、真实外部 provider、ASR、会议平台、自动投递或 SaaS 已验收。
- 不得把 examples 数据写成真实用户资料验收。
