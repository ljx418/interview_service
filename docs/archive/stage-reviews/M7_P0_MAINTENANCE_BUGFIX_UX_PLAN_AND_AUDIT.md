# M7 P0 Maintenance Bugfix 与小步 UX 计划

## 关联规格

- PRD 路径：用户完成申请包、实时提示和复盘后，产物状态和本地 workspace 行为必须可信。
- 目标架构：本地优先、artifact 可追溯、Chatbox 负责确认和导出、realtime 为文本结构提示。
- 自动化边界：仅执行 `09_AUTOMATED_DEVELOPMENT_SCOPE.md` 允许的 P0 bugfix、eval 补强和小步 UX 修正。

## 开发计划

- 修复 `/api/realtime/end`：结束会话时必须定位 session 所属 workspace，不得只写默认 workspace。
- 强化 `/api/application/download`：下载路径必须严格位于当前 workspace 的 `exports/` 目录下。
- 小步 UX 修正：Chatbox 点击确认后立即把当前产物卡状态更新为 `confirmed`，避免用户误以为确认失败。
- 增加 eval：覆盖非默认 workspace realtime end、导出下载路径边界、artifact confirm 状态回写。

## 验收标准

- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过；
- 使用 `examples/` 匿名真实感数据完成 HTTP 端到端验收；
- PRD 规格检视确认未引入 P1/P2 能力。

## 审计意见

- 致命风险：无。
- 重大风险：无。
- 虚假验收风险：realtime end 必须用非默认 workspace 测试，避免默认 workspace 掩盖问题。
- 范围风险：不实现真实 LLM、复杂 artifact 编辑、正式 PDF/DOCX、MCP/CLI、ASR 或会议平台。

## 当前结论

审计意见已闭环，可以进入 M7 P0 Maintenance 实质开发。

## 完成记录

- 修复 `/api/realtime/end`：现在会定位 realtime session 所属 workspace 并写入对应 SQLite。
- 强化 `/api/application/download`：下载路径必须位于当前 workspace 的 `exports/` 目录。
- 修复 Chatbox 小步 UX：artifact 确认成功后当前卡片状态立即显示为 `confirmed`。
- 新增 `tests/evals/test_p0_maintenance_bugfix_eval.py` 覆盖非默认 workspace realtime end、下载路径边界和 artifact confirm 状态持久化。

## PRD 规格检视

M7 只修复 P0 维护范围内的真实 bug 和小步 UX，没有新增 P1/P2 能力。修正后仍保持本地优先、Chatbox-first、Agent Tool-first、Markdown hard gate、formal_assist 文本结构提示边界。未发现致命或重大规格偏差。

---

# M8 P0 Maintenance：Chatbox 会话恢复

本节记录下一次 P0 Maintenance 小阶段。为保持 `docs/active` 文档总数小于 20，本阶段计划、审计和完成记录并入本维护文档，不新增独立 active 文档。

## 关联规格

- PRD 路径：用户在本地 workspace 中持续推进求职任务，刷新或重开 Chatbox 后仍应能看到已生成的关键产物，而不是被迫从空会话开始。
- 目标架构：Chatbox 负责输入、确认、展示和导出；会话、消息和 artifact 状态由本地 SQLite 持久化。
- 自动化边界：仅修复 P0 可用性缺口，不新增账号、云同步、多会话管理页、复杂 dashboard 或 P1/P2 能力。

## 开发计划

- Chatbox 启动时先初始化默认 workspace，再读取 `/api/chat/sessions?workspace_id=...`。
- 若存在历史会话，则读取最新会话 `/api/chat/sessions/{session_id}`，恢复消息列表，并按 `artifact_refs` 从 artifact 表恢复产物卡。
- 若无历史会话或恢复失败，则回退到创建新会话，并保留清晰的本地提示。
- 增加 eval：覆盖 Chat Session API 可恢复带 artifact 引用的消息与 artifact 内容。

## 验收标准

- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过；
- 使用 `examples/` 匿名真实感数据完成 HTTP 端到端验收，包含会话写入后通过 API 恢复消息和 artifact；
- PRD 规格检视确认本阶段只补 P0 本地持续体验，没有扩大到 P1/P2。

## 审计意见

- 致命风险：无。
- 重大风险：无。
- 虚假验收风险：只检查 session list 不足以证明 Chatbox 可恢复产物，必须断言消息中的 `artifact_refs` 能映射到 artifact 内容。
- 范围风险：不实现多会话选择器、跨设备同步、账号系统、云端历史或复杂会话管理。

## 当前结论

审计意见已闭环，可以进入 M8 P0 Maintenance 实质开发。

## 完成记录

- 修复 Chatbox 启动逻辑：初始化 workspace 后优先读取最新本地 chat session；存在历史会话时恢复消息，不再无条件创建新会话。
- 增加前端恢复 helper：按 `chat_message.artifact_refs` 映射本地 artifact 表，并从 `content_json`、`source_refs`、`questions_to_confirm` 重建现有产物卡结构。
- 增加恢复失败回退：历史会话读取失败时创建新会话，并在 Chatbox 中给出本地提示。
- 新增 API 级 eval：`test_chat_session_api_recovers_messages_and_artifact_content_for_chatbox` 覆盖 session list、session get、消息 artifact 引用和 artifact 内容恢复。

## 验收结果

- `python3 -m pytest`：17 passed。
- `npm --prefix apps/chatbox run build`：通过。
- HTTP 端到端验收：通过。使用 `examples/` 匿名真实感数据完成 workspace 创建、资料导入、事实整理、JD 分析、申请包生成、artifact 确认、Markdown 导出、面试准备、会话恢复、formal_assist 实时提示、面试复盘。
- 端到端验收证据：恢复会话包含 8 条消息、7 个 artifact；Markdown 导出位于 `/private/tmp/jobpilot_m8_http_e2e/exports/pkg_4827381bf611_resume.md`；复盘生成 3 条训练任务。
- 临时验收服务已停止，未保留后台监听进程。

## PRD 规格检视

M8 修复的是 P0 本地持续体验缺口：用户刷新或重开 Chatbox 后能够回到已有求职进度并继续确认、导出和面试准备。该变更与 PRD 的“本地优先、Chatbox 默认入口、结果导向、artifact 可追溯”一致。未新增多会话管理页、账号、云同步、复杂 dashboard、MCP/CLI、ASR 或会议平台能力。未发现致命或重大规格偏差；主要虚假验收风险已通过 API 级 artifact 内容恢复断言闭环。
