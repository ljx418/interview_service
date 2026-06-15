# M5 P0 维护加固计划与审计

## 关联规格

- PRD 路径：完整 P0 体验路径必须持续可回归。
- 目标架构：Chatbox-first、Agent Tool-first、本地优先、artifact 可追溯、formal_assist 安全边界。
- 自动化范围：以 `09_AUTOMATED_DEVELOPMENT_SCOPE.md` 的 P0 Maintenance 为准。
- 冻结基线：以 `10_P0_FREEZE_AUDIT_AND_ACCEPTANCE_REPORT.md` 为准。

## 开发计划

- 增加 artifact 持久化与恢复验收：确认 artifact row 可通过 `content_json`、`content_path` 或 `source_table + source_id` 恢复。
- 增加 tool invocation 脱敏验收：确认日志不保存完整简历或 transcript 原文。
- 增加 chat session 恢复验收：确认 session、message、artifact refs 可恢复。
- 增加 schema 口径验收：确认 SourceRef 支持文档中定义的 P0 source_type，RealtimeHint 禁止额外字段和逐字答案。
- 增加文档防漂移验收：确认 active docs 不再包含会误导自动化开发的旧“待完成缺口”措辞。

## 验收标准

- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过；
- 使用 `examples/` 匿名真实感数据完成 HTTP 端到端验收；
- PRD 规格检视确认没有把 P1/P2 能力纳入 P0；
- active 文档数量仍小于 20。

## 审计意见

- 致命风险：无。
- 重大风险：无。
- 中等风险：测试可能过度绑定文档措辞。处理：只检查明确会造成自动化误判的旧缺口短语。
- 范围风险：不实现 OpenAI-compatible provider、复杂 artifact 编辑、正式 PDF/DOCX、MCP/CLI、ASR 或会议平台。

## 当前结论

审计意见已闭环，可以进入 M5 P0 Maintenance 实质开发。

## 完成记录

- 新增 artifact 持久化与恢复 eval，确认 `content_json`、`source_table + source_id` 和导出路径可用于恢复和追溯。
- 新增 tool invocation 脱敏 eval，确认工具日志不保存完整简历或项目 README 原文。
- 新增 chat session 恢复 eval，确认 message 和 artifact refs 可恢复。
- 新增 schema 口径 eval，确认 SourceRef 支持 P0 文档定义的 source_type，RealtimeHint 禁止额外 `full_answer` 和逐字答案。
- 新增 active docs 防漂移 eval，防止旧“待完成缺口”措辞重新进入冻结文档。

## PRD 规格检视

M5 未新增 P1/P2 功能，只加固 P0 维护验收。实现仍保持本地优先、Chatbox-first、Agent Tool-first、Markdown hard gate、formal_assist 结构提示边界。未发现致命或重大规格偏差。
