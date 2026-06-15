# M1 结构化 Agent Tool 输出计划与审计

## 关联规格

- PRD 路径：导入资料、生成事实/技能证据/项目卡、解析 JD、生成 MatchReport、生成申请包。
- 目标架构：LLM Provider Adapter、Prompt Contract Layer、Domain Tools、统一错误结构。
- 验收门槛：资料导入、JD 分析、申请包、开源可用性。

## 开发计划

- 建立 `services/llm` provider 边界，P0 默认使用 mock provider。
- 用 Pydantic 定义 SourceRef、ConfirmationQuestion、ArtifactRecord 和 P0 核心输出模型。
- 工具层写库前执行结构化校验；provider 非法输出必须返回 `VALIDATION_FAILED` 或抛出可控错误。
- 工具输出补齐 source refs、questions_to_confirm、artifact refs 和 tool invocation log。

## 验收标准

- 示例简历、项目 README 和 JD 可跑通完整 demo flow。
- malformed provider output 有测试断言。
- 对外产物不得包含无来源的确定性证书、雇主、项目或指标。
- 工具错误不暴露内部堆栈。

## 审计意见

- 致命风险：无。
- 重大风险：如果只在文档中定义 schema，而工具不校验，验收会出现假通过。处理：本阶段必须把 schema validation 接入工具边界。
- 中等风险：mock provider 可能掩盖真实 LLM 输出波动。处理：P0 先保证 mock 可重复，OpenAI-compatible provider 仅作为可选配置。

## 当前结论

审计意见已闭环，M1 已完成。

## 完成记录

- 新增 `services/llm` provider 边界、P0 输出 schema 和 `validate_output`。
- JD、匹配、申请包、故事卡、实时提示、复盘输出已接入 schema validation。
- malformed realtime output 和 formal_assist draft 已有 eval 断言。

## PRD 规格检视

实现仍保持 Chatbox-first、Agent Tool-first、本地优先。OpenAI-compatible provider 未作为 P0 硬门槛启用，符合 P0 离线可验收原则。
