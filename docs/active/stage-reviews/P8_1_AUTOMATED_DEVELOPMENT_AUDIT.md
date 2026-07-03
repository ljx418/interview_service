# P8.1 Chatbox-first 自动化开发审计记录

## 1. 阶段目标

P8.1 的目标是修正 P8 已实现能力在前端工作台中的主次关系。当前阶段只允许调整 Chatbox 信息架构、布局、入口位置、Agent 状态展示、工作台分工和响应式质量。

目标体验：

```text
用户指导 - Chatbox - 工作台
```

中央 Chatbox 必须是首屏第一优先路径。资料准备、JD 导入、岗位选择和简历生成能力必须保留，但入口不得继续以大块表单形式压在聊天时间线之前。

## 2. M0 开发前启动审计

审计结论：通过，允许进入 P8.1-M1。

审计依据：

- `docs/active/01_STAGE_PRD.md` 明确 P8.1 要解决 `p8-workflow-strip` 抢占中央首屏的问题；
- `docs/active/02_TARGET_ARCHITECTURE.md` 明确 P8.1 不改变 API、Domain Tool、SQLite 或 Artifact 业务语义；
- `docs/active/22_P8_1_CHATBOX_FIRST_WORKSPACE_PLAN.md` 明确 M1-M5 的开发顺序和出门条件；
- 当前代码中 `apps/chatbox/src/main.tsx` 的 `p8-workflow-strip` 位于 `ConversationHeader` 和 `.timeline` 之间，确认为本阶段主要 UI 偏差。

风险闭环：

- 不进入招聘平台接入；
- 不默认调用真实 provider；
- 不读取未授权真实个人资料；
- 不执行 workspace 删除、迁移 apply 或不可逆操作；
- 不重写后端业务语义。

## 3. M1 Chatbox-first 布局重构

开发计划：

- 移除中央栏中位于聊天时间线之前的大块 P8 workflow strip；
- 保持 `ConversationHeader` 作为紧凑 Agent 状态区；
- 保证 `.timeline` 在中央首屏优先出现；
- 保证输入框和工具入口稳定可达。

实现结论：

- `apps/chatbox/src/main.tsx` 已将 `MaterialIntakeWizard`、`JDIntakeCenter`、`JobTargetList`、`ResumeGenerationPlane` 从 timeline 前移走；
- 中央渲染顺序调整为 `ConversationHeader -> timeline -> composer`；
- P8 入口改由输入区工具坞触发。

PRD 检视：符合 Chatbox-first 主路径要求。

## 4. M2 资料/JD/简历入口迁移

开发计划：

- 在输入框上方新增紧邻工具入口；
- 入口包括上传资料、粘贴 JD、选择岗位、生成简历；
- 点击入口时展开轻量面板，不再永久占用聊天首屏；
- 保留原 P8 上传、JD intake、job list、resume generate 处理函数。

实现结论：

- 新增 `ComposerWorkflowDock`，作为输入框上方工具坞；
- 工具坞包含四类主入口；
- 资料、JD、岗位、简历面板按需展开；
- JD 导入后自动切到岗位面板，简历生成后自动切到简历面板。

PRD 检视：符合“上传资料、粘贴 JD、选择目标岗位、生成简历入口紧贴输入框”的要求。

## 5. M3 状态机与工作台分工

开发计划：

- 中央只展示 Agent 状态、聊天和输入；
- 右侧工作台展示岗位、画像、简历草稿、source refs、pending confirmations 和 export preflight；
- 左侧仍作为用户指导，不承担大型表单。

实现结论：

- `Workbench` 接入 `JobTargetList` 和 `ResumeGenerationPlane`；
- 中央 `ConversationHeader` 继续展示 Agent 状态机；
- 左侧 `DesktopContextPanel` 保持资料清单、下一步和安全边界说明；
- 产物与确认路径继续通过右侧工作台承载。

PRD 检视：符合三栏职责稳定要求。

## 6. M4 响应式和视觉质量修复

开发计划：

- 桌面视口保持三栏；
- 1024px 以下隐藏左侧用户指导，中央 Chatbox 仍为主路径；
- 768px 以下工作台抽屉化，输入区固定底部；
- 工具坞在小屏下变为两列，避免按钮重叠。

实现结论：

- `apps/chatbox/src/styles.css` 新增 `composer-workflow-dock`、`composer-tool-rail`、`composer-workflow-panel`；
- 展开面板设定最大高度和滚动，避免永久挤压聊天；
- 小屏下工具入口和输入框使用固定底部布局；
- 已通过前端 production build。

PRD 检视：需要 M5 通过真实多视口截图最终确认。

## 7. M5 自动化验收计划

计划：

- 启动本地 FastAPI 和 Chatbox；
- 使用 Headless Chrome 执行真实界面截图；
- 视口覆盖 1920、1440、1200、720、390；
- 生成中文 HTML 报告；
- 报告必须列出目标架构、当前实现、用户体验路径、截图证据、PRD 规格检视、未验证范围。

不允许的结论：

- 不声明招聘平台自动接入通过；
- 不声明真实 provider 质量通过；
- 不声明真实个人资料路径通过；
- 不声明自动投递、SaaS、ASR、会议平台通过。

## 8. 自动化开发停止条件

停止原因必须归类为：

- 完成：P8.1-M0 至 M5 全部通过；
- 暂停：触发真实 provider、真实资料、平台接入、删除 workspace、不可逆迁移等高风险确认；
- 打回：出现重大 PRD 偏差或虚假验收风险；
- 阻塞：自动化验收失败，需要回到开发计划阶段。

