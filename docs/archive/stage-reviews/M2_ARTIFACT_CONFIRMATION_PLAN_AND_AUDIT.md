# M2 用户确认与产物闭环计划与审计

## 关联规格

- PRD 路径：用户确认或修改事实、生成申请包、导出 Markdown 和简单 PDF。
- 目标架构：Artifact Confirmation Layer、Chatbox Client、Storage Layer。
- 验收门槛：导入资料、申请包、开源可用性。

## 开发计划

- 新增 chat session、chat message、artifact、tool invocation 表。
- 所有关键工具生成 artifact，记录状态、source refs、questions_to_confirm 和恢复内容。
- 增加 artifact confirm/edit/regenerate 的最小 API。
- 申请包导出前检查 blocking confirmation，Markdown 是硬门槛，PDF 是软门槛。
- Chatbox 展示产物状态、待确认项和导出入口。

## 验收标准

- 重启或刷新后可恢复 session 和 artifact。
- blocking confirmation 未确认时不能静默导出。
- Markdown 文件保存在 workspace `exports/` 下，并可下载或直接打开。
- 修改事实后，后续生成申请包使用更新事实。

## 审计意见

- 致命风险：artifact 只保存元数据而无法恢复内容。处理：artifact 必须包含 `content_json` 或 `content_path`，并保留 `source_table + source_id`。
- 重大风险：导出绕过用户确认。处理：export 工具必须检查 artifact 状态和 blocking confirmation。
- 中等风险：前端做复杂 dashboard 导致偏离 Chatbox-first。处理：仅增加产物卡和确认/导出控件。

## 当前结论

审计意见已闭环，M2 已完成。

## 完成记录

- 新增 `chat_session`、`chat_message`、`artifact`、`tool_invocation` 表。
- 关键工具生成 artifact，记录状态、source refs、questions_to_confirm、content_json/content_path。
- 新增 artifact confirm/edit/regenerate API、chat session API、Markdown download API。
- Chatbox 支持产物卡、确认按钮和申请包 Markdown 导出按钮。

## PRD 规格检视

申请包 Markdown 导出为硬门槛并已通过；PDF 保持占位软门槛。Artifact 编辑 P0 采用 content_json 更新，复杂业务表 diff 留到 P1，没有偏离本阶段目标。
