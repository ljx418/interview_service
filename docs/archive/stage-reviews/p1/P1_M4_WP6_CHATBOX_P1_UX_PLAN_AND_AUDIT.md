# P1-M4 / WP6 Chatbox P1 UX 开发计划与审计

## 1. 阶段目标

保持 Chatbox 极简入口，不做复杂 dashboard，只补齐 P1 必需操作：

- provider mode 显示；
- artifact current version 显示；
- version 列表；
- edit save new version；
- regenerate；
- export current version Markdown + DOCX；
- provider / export / regenerate 错误可理解提示。

## 2. 开发范围

代码范围：

- `apps/chatbox/src/main.tsx`
- `apps/chatbox/src/styles.css`

本阶段不改核心生成逻辑，不在前端拼 prompt，不保存 API Key。

## 3. 实现计划

1. Header 显示 provider status；
2. ArtifactCard 展示 current version；
3. ArtifactCard 加载 versions；
4. 支持 JSON 编辑 textarea；
5. 保存编辑调用 `PATCH /api/artifacts/{id}`；
6. regenerate 调用 `POST /api/artifacts/{id}/regenerate`；
7. export current version 调用 `POST /api/application/export-package`，默认导出 Markdown + DOCX。

## 4. 验收标准

必须通过：

- `npm --prefix apps/chatbox run build`；
- `python3 -m pytest`；
- UI 不出现复杂 dashboard；
- 前端不保存 API Key；
- 前端不拼 provider prompt；
- edit/regenerate/export 都走后端 API。

## 5. PRD 规格检视

完成后必须证明：

- Chatbox 仍是薄入口；
- 用户可以看到 provider mode 和 artifact version；
- 用户可以触发编辑保存新版本；
- 用户可以触发 regenerate；
- 用户可以导出当前版本；
- blocking/export 错误会显示给用户。

## 6. 审计意见

当前计划没有新增致命或重大规格偏差。可以进入 P1-M4 / WP6 实质开发。

必须暂停找用户确认的情况：

- 前端保存 API Key；
- 前端直接拼 prompt 或写业务内容绕过后端；
- UI 扩展成复杂 dashboard；
- 引入新的外部服务。

## 7. 实现结果

已完成：

- Header 显示 provider status；
- ArtifactCard 显示 current version；
- ArtifactCard 加载 version 列表；
- 支持 JSON 编辑并 `PATCH /api/artifacts/{artifact_id}` 保存新版本；
- 支持 regenerate；
- 支持导出 current version Markdown + DOCX；
- provider/export/regenerate 失败会进入聊天消息提示。

未执行：

- 未保存 API Key；
- 未在前端拼 provider prompt；
- 未让前端直接写业务表；
- 未做复杂 dashboard；
- 未做富版本 diff UI。

## 8. 验收结果

自动化测试：

```text
npm --prefix apps/chatbox run build
结果：通过

python3 -m pytest
结果：45 passed
```

Chrome 可见截图验收：

```text
截图文件：docs/active/evidence/p1_chrome_chatbox_visible_acceptance.png
结果：通过
```

截图确认了 Chatbox 首屏不是空白页，并展示 `Workspace ready`、`mock local` provider 状态、`application_package` 产物卡、current version、v1/v2/v3 版本列表、确认、导出、编辑、重新生成入口，以及 warning/optional 待确认项。

## 9. PRD 规格检视

通过：

- Chatbox 仍是薄入口；
- 用户可以看到 provider mode；
- 用户可以看到 artifact version；
- 用户可以编辑并保存新版本；
- 用户可以触发 regenerate；
- 用户可以导出 current version；
- 所有关键动作都走后端 API。

未完成但不属于本阶段：

- release checklist；
- P1 冻结审计；
- 真实外部 provider 人工验收。

## 10. 目标架构检视

通过。WP6 没有把 Chatbox 改成业务层：

- Chatbox 只触发动作和展示结果；
- artifact version、regenerate、export 均由后端执行；
- Chatbox 不保存 API Key；
- Chatbox 不拼 prompt。

## 11. 残留风险

- 编辑器是 JSON textarea，符合 P1 最小可用，但不是最终产品化编辑表单；
- version 列表只展示版本号，不提供复杂 diff。

## 12. 是否允许进入下一阶段

允许进入 `P1-M5 / WP7: Release Readiness + full regression`。

当前没有新增致命或重大规格偏差，也没有虚假验收风险；本阶段结论仅代表 Chatbox P1 必需控制通过，不代表发布冻结已完成。
