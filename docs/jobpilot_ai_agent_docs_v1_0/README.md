# JobPilot AI 文档包 v1.0

本压缩包整理了 JobPilot AI 当前版本的核心产品和开发文档。

## 项目方向

JobPilot AI 是一个 **面向转行程序员的免费开源 AI 求职 Agent 服务**。

核心特点：

- Agent-first；
- Chatbox-first；
- 本地优先；
- 无需注册登录；
- 面向转行程序员；
- 聚焦用户实际得到的申请包、面试准备包、实时提示和复盘；
- 不做复杂控制台；
- 不做自动海投；
- 不做隐蔽式面试作弊工具。

## 文件说明

```text
docs/
├── 01_PRD_JobPilot_AI_Agent_Service_v1.0.md
├── 02_BASIC_CAPABILITY_SET.md
├── 03_DEVELOPMENT_PLAN.md
├── 04_ACCEPTANCE_CHECKLIST.md
└── 05_AGENT_MCP_TOOLS_DRAFT.md

prompts/
└── CODEX_TERMINAL_PROMPT.txt

assets/
└── interaction_acceptance_path.png
```

## 建议审阅顺序

1. 先看 `01_PRD_JobPilot_AI_Agent_Service_v1.0.md`，确认产品方向；
2. 再看 `02_BASIC_CAPABILITY_SET.md`，确认 P0 能力；
3. 再看 `03_DEVELOPMENT_PLAN.md`，确认开发节奏；
4. 用 `04_ACCEPTANCE_CHECKLIST.md` 做 MVP 验收；
5. 把 `prompts/CODEX_TERMINAL_PROMPT.txt` 复制到 Codex 终端，让它一起做工程评审和实现计划。

## 当前最重要的产品判断

本项目不是“AI 求职 Dashboard”，而是：

> 开源求职 Agent 服务 + 极简 Chatbox 入口。

第一版验收不看页面数量，而看用户是否真的拿到：

- 技能证据卡；
- 项目卡；
- 岗位适合度分析；
- 申请包；
- 面试准备包；
- 实时问题结构提示；
- 面试复盘；
- 下一步训练计划。

