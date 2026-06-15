# M3 面试与实时提示安全计划与审计

## 关联规格

- PRD 路径：生成 Interview Prep 和 StoryCard、模拟面试或输入当前面试问题、获得结构化实时提示、生成面试复盘和 TrainingTask。
- 目标架构：interview、realtime、training 工具域和正式面试安全边界。
- 验收门槛：面试准备与实时提示、复盘与训练。

## 开发计划

- StoryCard 必须引用 TechProject 或 CareerFact。
- realtime formal_assist 仅允许 minimal/outline hint。
- realtime hint 不包含 full_answer、逐字代答、隐蔽辅助字段。
- review 基于 transcript 生成问题清单、优点、改进点、thank-you draft 和至少 3 个 TrainingTask。
- transcript save policy 在 API 输出中可见，P0 不保存音视频。

## 验收标准

- 输入“讲一个你解决技术难题的经历”时，推荐真实项目并给出回答结构。
- formal_assist 输出不包含完整逐字答案。
- review 生成至少 3 个训练任务并写入 SQLite。
- 所有面试建议可追溯到项目、事实或 transcript。

## 审计意见

- 致命风险：实时提示变成正式面试逐字代答。处理：schema 和测试禁止 `full_answer`，formal_assist 禁止 `draft`。
- 重大风险：P0 被扩大为 ASR 或会议平台集成。处理：本阶段只实现 text question -> structured hint。
- 中等风险：复盘泛泛而谈。处理：必须生成可执行 TrainingTask。

## 当前结论

审计意见已闭环，M3 已完成。

## 完成记录

- StoryCard、interview prep、realtime hint 和 review 均带 source refs。
- formal_assist 只允许 minimal/outline，draft 会被拒绝。
- realtime hint schema 不包含 full_answer，并有安全 eval。
- review 至少生成 3 个 TrainingTask。

## PRD 规格检视

P0 realtime 严格保持 text question -> structured hint，不引入 ASR、会议平台或隐蔽式辅助。实现符合 PRD 非目标和目标架构安全边界。
