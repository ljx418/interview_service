# JobPilot AI 自由 Chatbox 与连续多轮对话开发计划

日期：2026-06-24
状态：后续开发目标已落盘；本地最小连续对话基线已实现，完整自由智能聊天未完成
适用阶段：P4C-FC / P5-FC / P6-FC 候选

## 1. 背景与真实状态

P4B 自动化工作台已经能跑示例路径、展示推进台、产物卡和导出状态，但用户反馈指出一个关键体验缺口：

```text
当前 Chatbox 仍偏任务控制台；
还不是一个自由、不中断、可连续多轮追问的求职对话界面。
```

已完成的最小修正：

- 默认本地 `KeywordChatCore` 已从“未知输入触发整理资料”改为“明确意图才执行工具”；
- 普通追问、补充偏好、问下一步、问当前状态会保留在本地自由对话路径；
- 前端首屏增加“自由聊求职方向”入口；
- 已增加针对性测试，证明普通连续追问不会误触发工具。

仍未完成：

- provider-backed 自由智能聊天；
- 长期 memory、用户画像、偏好和任务上下文的结构化维护；
- 多轮计划执行、澄清问题、工具调用确认和撤销；
- 真实个人资料路径上的自由聊天验收；
- 真实外部 provider 路径验收。

## 2. 目标分层

### P4C-FC：本地连续对话体验微调

目标：在不引入真实外部 provider 的前提下，让 Chatbox 不再打断用户，能连续承接求职方向、偏好、下一步和状态追问。

范围：

- 本地/mock 默认；
- 不调用真实外部模型；
- 不处理真实 API Key；
- 不新增 SaaS、ASR、会议平台或自动投递。

验收路径：

```text
打开 Chatbox
→ 输入“我还没有 JD，先聊聊求职方向”
→ 系统不触发 artifact 工具，只给出连续对话回复
→ 继续问“下一步我该补 React 还是项目经历”
→ 系统基于当前上下文给下一步建议
→ 明确输入“整理资料”后才生成职业事实 artifact
→ 明确输入“解析 JD / 生成申请包 / 准备面试”后才执行对应工具
```

出门条件：

- 普通自由追问不误触发工具；
- 明确工具意图仍能稳定执行；
- 会话恢复后能看到前序自由对话；
- 前端文案不暗示已接入真实自由大模型；
- 自动化测试和前端 build 通过；
- 截图或 HTML 报告说明这只是本地连续对话基线。

### P5-FC：真实资料本地多轮闭环

目标：在真实资料仍本地/mock 默认的前提下，让用户围绕自己的资料、JD 和申请包连续追问。

候选能力：

- 对话状态中保留当前目标岗位、最近申请包、待确认项和导出状态；
- 支持“刚才那个缺口是什么意思”“帮我把这个项目说得更强一点”等上下文追问；
- 支持澄清问题，而不是立即执行工具；
- 支持用户确认后再改写 artifact；
- 支持“不要生成，先解释”的非执行型对话。

验收证据：

- 真实感本地资料路径截图；
- chat session 恢复测试；
- artifact 不被无确认覆盖的测试；
- questions_to_confirm 不被自由聊天隐藏或绕过。

### P6-FC：provider-backed 自由智能聊天

目标：在用户明确确认外部调用后，使用真实 provider 改善自由对话能力。

必须先具备：

- 调用前确认；
- `.env` 本地配置，不提交 API Key；
- redaction、timeout、retry、schema validation；
- provider invocation 脱敏；
- mock provider 仍可离线复现；
- 失败降级到本地连续对话基线。

非目标：

- 不默认外呼；
- 不把 provider configured 写成 provider called；
- 不在报告、日志、fixture 中写真实 API Key；
- 不使用真实个人资料做未经确认的外部调用。

## 3. 目标架构增量

建议新增或强化以下边界：

```text
Chatbox UI
→ Chat Session State
→ Chat Intent Router
  → Free Local Dialogue
  → Clarification
  → Tool Intent
  → Provider-backed Dialogue（P6 opt-in）
→ Context Snapshot
  → latest job
  → latest package
  → artifacts
  → pending confirmations
→ Domain Tools
→ Artifact / Export / Evidence
```

职责划分：

- `Chatbox UI`：展示消息、输入、确认和产物，不生成求职内容；
- `Chat Intent Router`：判断自由对话、澄清、状态查询或工具执行；
- `Free Local Dialogue`：本地连续对话基线，不声称智能生成能力；
- `Context Snapshot`：提供当前 workspace 摘要，避免对话丢上下文；
- `Domain Tools`：只有明确意图或确认后才写入 artifact；
- `Provider-backed Dialogue`：P6 opt-in，不进入 P4C/P5 默认路径。

## 4. 风险与打回条件

必须打回的情况：

- 普通聊天误触发工具并写入 artifact；
- “还没准备好 JD”被误判为解析 JD；
- 用户说“先别生成”仍生成申请包；
- 自由聊天绕过待确认项或导出前检查；
- UI 暗示真实外部模型已默认启用；
- 真实资料或 API Key 被写入报告、日志或 fixture；
- P4C 文档把 P6 provider-backed 能力写成当前已完成。

## 5. 文档支撑评估

现有 P3/P4 文档能支撑“Chatbox 有响应、错误可恢复、任务入口自然”的体验优化，但不足以完整支撑“自由、连续、多轮、不中断”的后续目标。

本文件补齐：

- 分阶段目标；
- 默认本地连续对话与真实 provider-backed 聊天的边界；
- 目标架构增量；
- 验收路径；
- 风险和打回条件。

仍需后续在进入 P5/P6 前补齐：

- 独立 PRD；
- API / schema 设计；
- memory / context retention 规格；
- provider-backed 对话的确认和脱敏细则；
- 自动化浏览器验收报告模板。

## 6. P4C-FC 详细开发计划

P4C-FC 只处理本地/mock 连续对话体验，不扩大到真实 provider-backed 聊天。

| 工作包 | 目标 | 主要文件 | 验收证据 |
| --- | --- | --- | --- |
| FC-WP1 Intent Router 收紧 | 区分自由对话、状态查询、下一步、工具意图，减少误触发 | `services/chat/core.py` | pytest 覆盖“还没准备好 JD”不解析 JD |
| FC-WP2 Context Snapshot | 为“当前进展 / 下一步 / 有哪些产物”提供 workspace 摘要 | `services/chat/core.py`, `services/tools/jobpilot.py` | 状态查询返回 artifact/job/package/pending 摘要 |
| FC-WP3 Free Local Dialogue | 普通追问不写 artifact，仍保存 chat session | `services/chat/core.py`, chat session storage | 自由追问两轮后 artifact count 不变 |
| FC-WP4 Tool Intent Confirmation | 只有明确整理资料、解析 JD、生成申请包、准备面试才执行工具 | `services/chat/core.py`, tests | 明确工具意图仍生成对应 artifact |
| FC-WP5 Frontend Conversation UX | 首屏和输入框表达“可连续追问”，自由聊入口不遮蔽任务入口 | `apps/chatbox/src/main.tsx`, `styles.css` | 初始页截图、自由聊点击截图 |
| FC-WP6 Evidence Report | 生成本地连续对话 HTML 报告，明确不是 provider-backed 智能聊天 | browser acceptance scenario, `docs/reports/` | HTML 报告、桌面/移动截图 |
| FC-WP7 Docs Sync | 同步 README、TODO、active docs、drawio 文本镜像 | `README.md`, `TODO.md`, `docs/active/` | rg 检查、drawio XML parse |

## 7. P4C-FC 自动化验收计划

最低测试：

```bash
.venv/bin/python -m pytest tests/evals/test_p3_chatbox_response_eval.py
npm --prefix apps/chatbox run build
python3 - <<'PY'
import xml.etree.ElementTree as ET
root = ET.parse("docs/active/jobpilot-stage-gap-and-acceptance.drawio").getroot()
print(len(root.findall("diagram")))
PY
```

建议新增或保留的断言：

- 输入“我现在还没准备好 JD，想先聊聊转前端岗位的方向”：
  - 返回自由对话消息；
  - 不生成 `job`、`match_report` 或 `career_facts` artifact；
  - 不调用外部 provider。
- 输入“继续，我应该先补 React 还是项目经历”：
  - 返回下一步建议；
  - 不写 artifact。
- 输入“当前进展如何”：
  - 返回 workspace 状态摘要。
- 输入“请整理资料，生成职业事实”：
  - 生成 `career_facts` artifact。
- 输入有效 JD 文本：
  - 生成 `job` 和 `match_report` artifact。
- 刷新页面恢复 session：
  - 自由对话历史仍可见。

浏览器验收路径：

```text
打开 Chatbox
→ 点击“自由聊求职方向”
→ 等待自由对话回复
→ 输入“继续，我下一步应该做什么”
→ 截图：自由多轮对话仍在对话区，不强制打开推进台
→ 输入“请整理资料”
→ 截图：工具执行后推进台出现对应产物
→ 刷新页面
→ 截图：历史对话恢复
```

报告必须写明：

- 当前验收只证明本地/mock 连续对话基线；
- 不证明真实 provider-backed 自由智能聊天；
- 不证明真实个人资料路径；
- 不证明 ASR、会议平台、自动投递或 SaaS。

## 8. P4C-FC 人工验收表

每项 0-2 分：

| 项目 | 通过标准 | 分数 |
| --- | --- | --- |
| 自由开场自然 | 用户可先聊方向，不必立即提供 JD | 待填 |
| 连续追问不中断 | 至少两轮追问不误触发工具 | 待填 |
| 工具触发清楚 | 明确工具意图才生成 artifact | 待填 |
| 状态查询可理解 | “当前进展 / 下一步”能基于 workspace 回复 | 待填 |
| 会话恢复可信 | 刷新后历史自由对话仍可见 | 待填 |
| 隐私边界清楚 | UI 不暗示已默认外呼真实 provider | 待填 |

判定：

- 任一项为 0：不得冻结 P4C-FC；
- 总分低于 10：继续修；
- 总分 10-12 且无 0：可进入 P4 冻结复验。

## 9. P4C-FC 打回条件

出现任一情况必须打回：

- 普通自由聊天写入 artifact；
- “还没准备好 JD”触发 JD 解析；
- “先别生成 / 先解释”仍生成申请包；
- 自由对话隐藏或绕过 questions_to_confirm；
- 刷新后丢失自由对话历史；
- 报告暗示 provider-backed 自由聊天已完成；
- 真实资料或真实外部 provider 未经用户确认被纳入验收。
