# JobPilot AI P4 UX 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。

本轮图示主线是 P4 UX 体验强化：目标 UX 架构、当前架构差距、开发及验收计划、项目里程碑、验收门槛、出门条件和审查证据。它不把 MCP、CLI、ASR、会议平台、自动海投或 SaaS 放入 P4 出门条件。

## 图示页结构

P4 drawio 保持 5 页：

1. P4 目标 UX 架构与当前差距；
2. P4 前端页面功能角色与关联关系；
3. P4 开发及验收计划；
4. P4 项目里程碑、验收门槛与出门条件；
5. 安全边界、状态标记与审查证据。

颜色含义：

- 绿色：已完成 / P0+P1+P2+P3 基线；
- 黄色：P4 本阶段目标；
- 灰色：P5+ 后续能力；
- 红色：高风险人工确认或禁止路径；
- 蓝色：用户、证据或说明性节点。

## 第 1 页 - P4 目标 UX 架构与当前差距

目标架构主链路：

```text
User
→ Experience Shell
→ Conversation Plane
  → Empty State Suggested Prompts
  → Loading / Error Recovery
→ Full-size Desktop Workbench / Workbench Plane
→ Artifact Review Cards
→ P0-P3 后端基线
→ Evidence Plane
```

当前差距：

- 首屏仍偏工程状态，P4 目标是 Chatbox 空状态 suggested prompts 优先；
- Chatbox 可响应，但 P4 目标是反馈更自然，并包含 loading / error recovery；
- 推进台已分离，但 P4 目标是只管理结果、确认项、版本和导出，并在 1200px、1440px、1600px、1920px 形成完整桌面工作台；
- 产物卡仍有工程术语，P4 目标是求职语义优先，并区分 primary / secondary action；
- P4 不改变 FastAPI、ChatCore、PiAgent、Domain Tools、Artifact 和 Export 的后端主链路。
- 截图脚本必须隔离或清理 viewport emulation，避免污染人工审查浏览器。

禁止路径：

- 前端生成求职内容；
- 默认触发外部 provider；
- 隐藏待确认项；
- suggested prompts 与 composer 割裂；
- 1200px 以上桌面宽度出现布局错误造成的大面积空白；
- 截图脚本污染人工审查者浏览器 viewport；
- 用静态原型冒充已实现。

## 第 2 页 - P4 前端页面功能角色与关联关系

前端角色：

- Mode / Provider Strip：展示示例模式、我的资料模式、mock 默认和 external 需确认；
- Empty State Suggested Prompts：提供导入资料、粘贴 JD、生成申请包、准备面试等建议任务，点击后填入 composer 或触发对话；
- Chat Timeline：展示用户消息、系统计划、loading / thinking、错误恢复和完成摘要；
- Composer Dock：处理文本、上传和快捷任务；
- Current Task Panel：展示当前阶段、下一步和缺口提示；
- Artifact List / Artifact Card：展示岗位解析、匹配报告、申请包、面试准备，并突出 primary action；
- Confirm / Export Bar：执行导出前确认和导出触发；
- Responsive / Full-size Controller：约束 1200/1440/1600/1920/720/390 多档布局，390px 下 Workbench 不压缩 Chatbox，截图结束后清理 emulation。

页面规则：

- 不嵌套卡片；
- 不让工程字段成为主内容；
- 移动端不能用“可运行”替代“好用”；
- 全尺寸桌面不能用“左侧窄栏 + 右侧空白”冒充工作台。

## 第 3 页 - P4 开发及验收计划

执行顺序：

```text
P4-M0 文档 / drawio / Gemini 包锁定
→ P4-M1 Chatbox 空状态 suggested prompts
→ P4-M2 对话反馈、loading 与错误恢复
→ P4-M3 推进台与产物卡可读性、primary action
→ P4-M4 状态、错误恢复、provider 语义
→ P4-M5 响应式与可访问性冒烟
→ P4-M5A 全尺寸桌面工作台与截图脚本隔离
→ P4-M6 before/after 报告与冻结
```

每阶段都必须产生测试、截图或 PRD 规格检视证据；出现重大偏差必须打回计划。

## 第 4 页 - P4 项目里程碑、验收门槛与出门条件

P4 门槛：

1. P0-P3 回归不退化；
2. Chatbox 空状态任务入口清楚，suggested prompts 能进入 composer 或对话；
3. 对话反馈可理解，包含 loading 和错误恢复 action；
4. 推进台和产物卡可读，按钮主次清楚；
5. provider、隐私和外呼语义不误导；
6. 全尺寸响应式与基础可访问性，1200/1440/1600/1920 不留大面积空白，390px 下 Workbench 不压缩 Chatbox，截图脚本清理 emulation；
7. Gemini 审查包、HTML 报告和 PRD 规格检视。

最终出门条件：

一个转行程序员不读文档也能完成：

```text
导入资料 → 分析岗位 → 生成申请包 → 确认/编辑 → 导出
```

同时截图、测试、报告和人工体验记录齐全。

## 第 5 页 - 安全边界、状态标记与审查证据

P4 证据包：

- Chrome screenshots；
- 1200/1440/1600/1920/720/390 多档截图；
- P4 HTML report；
- Gemini review package；
- PRD review；
- drawio XML parse；
- README/TODO sync。

审计原则：

- 文档通过不等于实现通过；
- Gemini 建议不等于人工体验通过；
- 截图必须来自真实 Chrome；
- 截图脚本不能污染人工审查浏览器 viewport；
- 真实个人资料、真实外部调用、API Key、不可逆迁移和逐字代答必须人工确认。
