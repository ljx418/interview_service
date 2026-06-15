# P1-M4 / WP5 Export Service 开发计划与审计

## 1. 阶段目标

本阶段强化 Export Service，让导出读取 current/selected artifact version，并完成 P1 hard gate：Markdown 继续稳定，PDF 或 DOCX 至少一种正式可打开。

本阶段选择优先实现 DOCX，避免引入 PDF 渲染依赖。

## 2. 开发范围

代码范围：

- `services/api/schemas.py`
- `services/tools/jobpilot.py`
- `tests/evals/test_p1_export_preflight_eval.py`

## 3. 实现计划

1. 扩展 export formats：
   - `markdown`
   - `pdf`
   - `docx`
2. Export preflight：
   - package 属于 workspace；
   - artifact/version 属于 workspace；
   - 默认读取 current version；
   - source_refs 非空；
   - blocking questions 阻止导出；
   - warning questions 写入导出文件；
   - export path 在 workspace `exports/` 内。
3. DOCX renderer：
   - 使用标准库生成可打开的 minimal OOXML `.docx`；
   - 不引入新依赖；
   - 保留 warning confirmations。
4. 保留 Markdown hard gate。

## 4. 验收标准

必须通过：

- Markdown 可打开；
- DOCX 可打开且是 zip/docx 结构；
- blocking confirmation 阻止导出；
- warning confirmation 保留在 Markdown/DOCX 文本；
- export 使用 current version；
- workspace 外路径下载被拒绝；
- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过。

## 5. PRD 规格检视

完成后必须证明：

- 用户导出的是当前确认/当前版本材料；
- 待确认边界没有在导出中消失；
- blocking 风险不会被导出绕过；
- 正式导出文件只写入 workspace `exports/`；
- P1 不把 PDF 和 DOCX 双格式都做作为 hard gate。

## 6. 审计意见

当前计划没有新增致命或重大规格偏差。可以进入 P1-M4 / WP5 实质开发。

必须暂停找用户确认的情况：

- 删除用户 exports；
- 导出 workspace 外路径；
- 引入外部渲染服务；
- 把 PDF 和 DOCX 双格式都完成作为 P1 hard gate。

## 7. 实现结果

已完成：

- `formats` 支持 `markdown` / `pdf` / `docx`；
- `artifact_version_id` 可选参数；
- 默认导出 artifact current version；
- export preflight 检查 source refs；
- blocking confirmation 阻止导出；
- warning / optional confirmation 写入导出内容；
- Markdown hard gate 保持；
- 使用标准库生成正式可打开的 minimal DOCX；
- workspace download guard 保持。

未执行：

- 未实现复杂 PDF 排版；
- 未把 PDF 和 DOCX 双格式都作为 hard gate；
- 未引入外部渲染服务；
- 未删除已有 exports。

## 8. 验收结果

自动化测试：

```text
python3 -m pytest tests/evals/test_p1_export_preflight_eval.py
结果：4 passed

python3 -m pytest
结果：45 passed

npm --prefix apps/chatbox run build
结果：通过
```

真实感数据：

- 使用 `examples/resumes/transition_frontend_resume.md`；
- 使用 `examples/projects/todoplus_README.md`；
- 使用 `examples/jds/junior_frontend_jd.md`；
- 生成 ApplicationPackage；
- 编辑 current version；
- 导出 Markdown + DOCX；
- 验证 DOCX zip 结构和 `word/document.xml`；
- 验证 blocking confirmation 阻止导出。

## 9. PRD 规格检视

通过：

- Markdown 继续稳定；
- DOCX 是 P1 至少一种正式可打开导出；
- export 使用 current version；
- blocking confirmation 不能绕过；
- warning confirmation 保留在导出文件；
- 导出文件只写 workspace `exports/`；
- workspace 外路径下载仍被拒绝。

未完成但不属于本阶段：

- Chatbox provider mode / version / regenerate / export current UX；
- release checklist。

## 10. 目标架构检视

通过。WP5 已补齐目标架构中的 `Export Service` 和 `Export Preflight`：

- Export 不直接生成业务内容；
- Export 读取 current/selected artifact version；
- Export 只写 workspace exports；
- Export preflight 在写文件前执行。

## 11. 残留风险

- DOCX 为 minimal OOXML，可打开但不是最终精排模板；
- PDF 仍是轻量文本 fallback，不作为 P1 正式 rich export；
- Chatbox 尚未展示 DOCX 导出入口和 version 选择。

## 12. 是否允许进入下一阶段

允许进入 `P1-M4 / WP6: Chatbox P1 UX`。

当前没有新增致命或重大规格偏差，也没有虚假验收风险；本阶段结论仅代表 Export Service 通过，不代表 Chatbox P1 UX 或 release readiness 已完成。
