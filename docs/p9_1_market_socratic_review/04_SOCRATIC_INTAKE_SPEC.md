# P9.1 Socratic Intake 对话设计

状态：文档设计，不代表代码实现。

## 1. 目标

让 Chatbox 像求职教练一样追问，而不是像表单一样收集资料。核心目标是把用户模糊经历转化为可追溯的简历事实、项目故事和申请包素材。

## 2. 对话状态

```text
idle
→ role_alignment
→ project_context
→ personal_contribution
→ technical_depth
→ impact_metrics
→ evidence_check
→ boundary_check
→ jd_mapping
→ story_draft
→ confirmation
```

## 3. 提问策略

- 一次只问一个问题；
- 优先追问会改变事实质量的问题；
- 不问用户已经明确回答过的问题；
- 每轮回答后更新事实摘要；
- 每 3-5 轮生成一次“已确认 / 待确认 / 不可写”总结；
- 不确定事实进入 pending confirmations；
- 没有证据的量化结果不得进入正式简历。

## 3.1 前端模块设计

`SocraticChatbox` 位于中央 `ConversationPlane`，它不是表单，也不是独立弹窗。目标设计如下：

```text
ConversationPlane
├─ JourneyStateStrip（当前：市场查询 / 补故事 / 证据检查 / 生成草稿）
├─ MessageTimeline
│  ├─ AgentQuestion（一轮一个主问题）
│  ├─ UserAnswer
│  └─ FactSummaryCheckpoint（每 3-5 轮）
├─ FactConfirmationStrip（已确认 / 待确认 / 不可写）
├─ ComposerToolRail（查市场 / 粘贴 JD / 补故事 / 生成申请包）
└─ Composer
```

视觉和交互要求：

- Agent 问题必须短、聚焦、可回答，不得一次展示 5 个问题；
- 每轮回答后，右侧产物台应能看到事实摘要或待确认项变化；
- `FactConfirmationStrip` 使用稳定三态：已确认、待确认、不可写；
- 用户可随时通过 Chatbox 修改上一轮事实，但修改必须产生可审查记录；
- 输入框上方工具入口是轻量操作，不得恢复成大块向导卡片。

## 3.2 与右侧产物台的联动

Socratic Intake 每推进一个关键状态，`ArtifactWorkbench` 应同步展示对应产物：

| 对话状态 | 右侧产物变化 |
| --- | --- |
| `role_alignment` | 更新目标岗位和 JD 关键词方向 |
| `project_context` | 更新项目背景事实摘要 |
| `personal_contribution` | 区分本人职责和团队贡献 |
| `technical_depth` | 记录技术难点和行动过程 |
| `impact_metrics` | 将指标放入待确认，直到有 source ref |
| `evidence_check` | 更新 source refs |
| `boundary_check` | 更新 DoNotClaimList |
| `story_draft` | 生成 STAR/CAR 草稿，但保留 pending confirmations |

## 4. 样例 A：前端 / LLM 应用

目标：把“智能客服控制台”整理成可投 LLM 应用前端岗位的项目故事。

| 轮次 | Agent 问题 | 用户回答示例 | 产物变化 |
| --- | --- | --- | --- |
| 1 | 你希望这段项目支持哪个目标岗位？ | LLM 应用前端 | 设置 target role |
| 2 | 这个项目解决了什么业务问题？ | 客服需要统一处理多渠道会话 | 记录项目背景 |
| 3 | 你本人负责哪一部分？ | 会话时间线、流式消息、错误重试 | 记录本人职责 |
| 4 | 最难的技术问题是什么？ | 流式消息乱序和失败恢复 | 记录技术难点 |
| 5 | 你采取了哪些具体动作？ | 做了状态机、幂等消息 ID、重试策略 | 记录 action |
| 6 | 有没有可确认指标？ | 首屏从 2.8s 降到 1.6s | 进入待确认指标 |
| 7 | 这个指标来源是什么？ | 内部性能面板截图 | 添加 source ref |
| 8 | 哪些内容不能写？ | 不写模型训练，只写应用前端 | 添加边界 |
| 9 | 这段经历映射 JD 哪些关键词？ | React、TypeScript、LLM 应用、流式体验 | 生成 JD 映射 |
| 10 | 我先生成 STAR 草稿，你确认哪些点？ | 确认职责和指标来源 | 生成故事草稿 |

## 5. 样例 B：后端 / AI 平台

目标：把“实时特征服务”整理成可投 AI 平台后端岗位的项目故事。

| 轮次 | Agent 问题 | 用户回答示例 | 产物变化 |
| --- | --- | --- | --- |
| 1 | 你想用这段经历支持哪个岗位？ | AI 平台后端 | 设置 target role |
| 2 | 项目服务什么业务？ | 推荐系统实时特征供给 | 记录项目背景 |
| 3 | 你本人负责哪些模块？ | Kafka 消费链路和特征缓存 | 记录本人职责 |
| 4 | 技术难点是什么？ | 峰值流量下延迟和一致性 | 记录技术难点 |
| 5 | 你做了哪些动作？ | 分区消费、缓存预热、降级策略 | 记录 action |
| 6 | 有量化结果吗？ | QPS 1.2 万，P99 80ms 内 | 进入待确认指标 |
| 7 | 数据来源能证明吗？ | 压测报告和监控截图 | 添加 source ref |
| 8 | 有哪些不能写？ | 没做 Kubernetes，不写 K8s 实操 | 添加边界 |
| 9 | 匹配 JD 哪些关键词？ | Kafka、缓存、稳定性、性能优化 | 生成 JD 映射 |
| 10 | 是否生成面试故事和简历 bullet？ | 先生成草稿，保留待确认 | 生成草稿 |

## 6. 输出结构

```text
CandidateFactSummary
ProjectStoryDraft
JDKeywordMapping
PendingConfirmations
SourceRefs
DoNotClaimList
```

## 7. 验收

- 每个样例至少 10 轮；
- 每轮只能问一个主问题；
- 每个草稿必须含 source refs 和 pending confirmations；
- 不得编造学历、年限、公司、项目贡献、指标或外部平台动作；
- 与 mock interview coach 的区别要写清：P9.1 先做事实采集，不先做模拟面试评分。
