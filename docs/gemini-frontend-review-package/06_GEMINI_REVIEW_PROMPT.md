# 推荐 Gemini 审查提示词

请把本文件夹作为一个完整、独立的前端页面方案来审查。你不需要访问仓库其他文件。

注意：当前版本已经吸收第一轮 Gemini 审查意见，包括 Task Launcher 并入 Chatbox empty state / suggested prompts、provider 状态用户化、loading/thinking 状态、产物卡 primary/secondary action、移动端 Workbench 折叠和 ARIA 状态。请继续审查第二版是否真正解决了这些问题。

审查对象：

- `01_PRODUCT_AND_UX_BRIEF.md`
- `02_PAGE_INFORMATION_ARCHITECTURE.md`
- `03_COMPONENT_AND_STATE_SPEC.md`
- `04_VISUAL_DESIGN_DIRECTION.md`
- `05_INTERACTION_AND_ACCESSIBILITY_CHECKLIST.md`
- `prototype.html`
- `prototype.css`
- `prototype.js`

推荐提示词：

```text
你是资深产品设计负责人、UX 架构师和前端体验审查员。请审查这个本地优先求职 Agent 的 P4 前端页面方案，并在必要时继续给出可替换的 HTML/CSS/JS 原型实现。

产品背景：
JobPilot AI 面向转行程序员，默认入口是 Chatbox，核心目标是把简历、项目 README、JD 和面试 transcript 组织成可信、可确认、可导出的求职材料。当前 P0-P3 已经跑通本地 examples 路径和基础 Chatbox 工作台，但人工审查认为页面仍偏工程验收控制台，首屏任务入口、产物卡语言、provider 状态和移动端操作需要优化。

请重点审查：
1. 用户是否能在 5 秒内理解第一步。
2. 页面是否清楚区分对话区、任务启动、推进台和产物卡。
3. 产物卡是否能用求职语义表达价值、风险和下一步，而不是暴露工程字段。
4. provider、示例模式、我的资料模式和本地隐私边界是否有歧义。
5. 1280px、720px、390px 的信息架构是否合理。
6. 视觉设计是否足够专业、克制、有高级感，但不变成营销页或复杂 dashboard。
7. 交互状态是否覆盖空状态、处理中、缺资料、错误、完成、导出受阻。
8. 是否存在可访问性问题。
9. 是否存在过度计划、虚假验收或超出 P4 范围的建议。
10. 第一轮审查指出的问题是否已经被第二版方案有效修复：任务入口割裂、provider 语义、按钮层级、loading、Workbench 空状态、移动端压缩、错误恢复、ARIA、长内容折叠、待确认项语气。

输出格式：
- 总体结论：通过 / 有条件通过 / 不通过。
- 前 10 个最重要问题，按严重程度排序，每个问题说明影响、证据和建议。
- 信息架构评分：0-10。
- 视觉设计高级感评分：0-10。
- 交互易用性评分：0-10。
- 移动端体验评分：0-10。
- 可访问性评分：0-10。
- 必须在 P4 修复的问题。
- 可以推迟到 P5 的问题。
- 不建议纳入本阶段的过度范围。
- 你会如何修改首屏和产物卡。
- 如当前原型仍不足，请直接输出可替换的 `prototype.html`、`prototype.css`、`prototype.js`，或给出精确分文件 patch 建议。

注意：
- 不要建议把 MCP、CLI、ASR、会议平台、自动投递、SaaS 登录、多租户或 Billing 纳入 P4 hard gate。
- 不要把静态原型当成已实现代码。
- 不要把 examples 数据当成用户真实个人资料。
- 不要把外部 provider 已配置误判为本次已经外呼。
```
