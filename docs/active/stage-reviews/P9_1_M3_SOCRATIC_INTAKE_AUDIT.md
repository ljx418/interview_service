# P9.1-M3 Socratic Intake 审计

状态：实现候选已落地；最终通过状态以 P9.1-M5 全量自动化报告、截图和 eval 为准。

## 开发内容

- Chatbox 增加 Socratic Intake 本地状态机；
- 用户提出整理项目故事、资料补全或 ASR 引导诉求时，Agent 进入一问一答采集；
- 每轮只提一个问题，逐步采集目标岗位、项目背景、个人贡献、量化结果、技术难点、协作影响和不可声明边界；
- 右侧产物台展示事实摘要、故事草稿、source refs、pending confirmations 和 DoNotClaimList。

## PRD 规格检视

| PRD 要求 | 实现候选 |
| --- | --- |
| 使用苏格拉底启发式提问补资料 | Chatbox 一问一答追问，不展示大表单 |
| 不编造学历、年限、公司、项目贡献 | 没有证据的指标进入 pending confirmations |
| 用户能通过 Chatbox 更新中间产物 | 回答每一步后更新故事草稿和右侧产物台 |
| ASR 不默认启用 | ASR 只作为文本说明，不调用麦克风或外部语音服务 |

## 验收证据要求

- 截图展示 Socratic Intake 启动和至少一轮回答后的下一问题；
- 报告包含两个不同技术背景的多轮 transcript；
- 产物台展示 CandidateFactSummary、PendingConfirmations、DoNotClaimList。

## 打回条件

- Socratic Intake 退化为一次性长表单；
- 回答后没有更新右侧产物台；
- 报告把本地状态机写成真实外部 LLM provider 质量通过。

