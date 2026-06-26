# 目标架构与当前实现

## P4 目标 UX 架构

```text
用户任务意图
→ Experience Shell
  → Workspace / Mode / Provider Strip
  → Conversation Plane
    → Empty State Suggested Prompts
    → Free Local Dialogue
    → Clarification / Status / Next-step Replies
    → Loading / Thinking Steps
    → Error Recovery Actions
  → Composer and Upload Dock
  → Full-size Desktop Workbench Controller
  → Workbench Plane / Mobile Drawer
  → Artifact Review Cards
  → Confirmation and Export Bar
  → Responsive Layout Controller
→ Evidence Layer
```

## 模块职责

| 模块 | 应负责 | 不应负责 |
| --- | --- | --- |
| Experience Shell | 建立工作台语境，展示 workspace、mode、provider 状态 | 做营销首页，隐藏外呼状态 |
| Conversation Plane | 展示自由对话、计划、处理中、错误、结果和下一步 | 只显示裸 JSON，静默失败 |
| Empty State Suggested Prompts | 把导入资料、粘贴 JD、准备面试放入 Chatbox 空态 | 作为割裂任务卡区域 |
| Chat Intent Router | 区分自由追问、状态查询、下一步、明确工具意图 | 默认外呼 provider，误写 artifact |
| Workbench Plane | 展示当前阶段、产物、确认项、版本、导出 | 承担聊天输入或业务生成逻辑 |
| Artifact Review Cards | 用求职语义展示产物价值、风险和操作 | 用内部 id 或裸 JSON 做主视觉 |
| Mobile Drawer | 390px 下折叠 Workbench，不压缩 Chatbox | 遮挡输入区或造成横向滚动 |

## 当前实现

- FastAPI 提供 workspace、files、profile、job、application、interview、realtime、artifact、chat、provider、workflow API。
- React/Vite Chatbox 初始化本地 workspace，恢复 chat session，展示 mode/provider/privacy 状态。
- 默认 `KeywordChatCore` 本地/mock 路由支持自由对话、状态查询、下一步建议和显式工具执行。
- SQLite workspace 持久化 documents、artifacts、artifact versions、chat sessions、tool logs、exports。
- 真实外部 provider 为 opt-in，高风险路径需要用户明确确认。

## 当前已发现的体验问题

- 页面视觉仍偏工程验收，不够像用户愿意长期使用的工作台。
- 建议任务和 Workbench 需要更强的信息层级。
- 显式生成 `career_facts` 后，系统计数和移动端入口显示 1 个产物，但桌面 Workbench 主体仍可能显示空状态。
- 移动端可以访问推进台，但信息密度和操作顺序仍可优化。
