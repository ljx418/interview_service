# P1-M3 / WP3+WP4 Artifact Versioning + Regenerate 开发计划与审计

## 1. 阶段目标

本阶段实现 artifact 当前版本、历史版本、编辑保存新版本和 regenerate 新版本闭环。目标是让 P1 后续导出只读取 current/selected version，并保证用户编辑或重新生成不会覆盖旧产物。

必须实现：

- `artifact.current_version_id`
- `artifact_version`
- 旧 artifact 自动迁移 v1；
- 新 artifact 自动创建 v1；
- `PATCH /api/artifacts/{artifact_id}` 创建新版本；
- `GET /api/artifacts/{artifact_id}/versions`
- `GET /api/artifacts/{artifact_id}/versions/{version_id}`
- `POST /api/artifacts/{artifact_id}/versions/{version_id}/restore`
- `POST /api/artifacts/{artifact_id}/regenerate` 创建新版本；
- regenerate 失败不改变 current version。

## 2. 开发范围

代码范围：

- `services/storage/db.py`
- `services/tools/jobpilot.py`
- `services/api/main.py`
- `tests/evals/test_p1_schema_migration_eval.py`
- `tests/evals/test_p1_artifact_versioning_eval.py`
- `tests/evals/test_p1_regenerate_eval.py`

本阶段不做 PDF/DOCX 正式导出，不做 Chatbox 复杂版本 diff UI。

## 3. 实现计划

1. 数据库迁移：
   - 给 `artifact` 增加 `current_version_id`；
   - 新增 `artifact_version`；
   - 对旧 artifact 创建 v1；
   - 幂等执行。

2. Artifact 写入：
   - `_write_artifact` 创建 artifact 后立即创建 v1；
   - `artifact.current_version_id` 指向 v1。

3. 编辑版本：
   - `update_artifact` 不覆盖旧版本；
   - 创建 v2；
   - 更新 current_version_id；
   - 对 `application_package` 做最小业务表写回。

4. 版本 API：
   - list versions；
   - get version；
   - restore version。

5. Regenerate：
   - 读取 current version；
   - mock/fixture 生成新 content；
   - 创建 child version；
   - parent_version_id 指向旧版本；
   - 成功后更新 current_version_id；
   - 失败不改变 current。

## 4. 验收标准

必须通过：

- 空库 init 后存在 `artifact_version`；
- 旧 artifact 可迁移 v1；
- 重复打开 workspace 不重复创建 v1；
- 新 artifact 有 current_version_id；
- 编辑 artifact 创建 v2，v1 仍可读；
- restore 能切回旧版本；
- regenerate 成功创建 child version；
- regenerate failure 不改变 current version；
- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过。

## 5. PRD 规格检视

完成后必须证明：

- 用户编辑不会覆盖旧产物；
- regenerate 不覆盖旧产物；
- artifact 版本可恢复；
- current version 是后续 export 的唯一默认读取对象；
- 业务写入仍由 Python Domain Tools 执行；
- Chatbox 和 Pi Agent Core 不直接写版本表。

## 6. 审计意见

当前计划没有新增致命或重大规格偏差。可以进入 P1-M3 / WP3+WP4 实质开发。

必须暂停找用户确认的情况：

- 删除旧 artifact 字段；
- 删除旧 artifact 内容；
- 执行不可逆迁移；
- regenerate 发起真实外部 provider 调用；
- regenerate 覆盖旧版本。

## 7. 实现结果

已完成：

- `artifact.current_version_id`；
- `artifact_version` 表；
- 旧 artifact 幂等迁移 v1；
- 新 artifact 自动创建 v1；
- `PATCH /api/artifacts/{artifact_id}` 创建新版本；
- `GET /api/artifacts/{artifact_id}/versions`；
- `GET /api/artifacts/{artifact_id}/versions/{version_id}`；
- `POST /api/artifacts/{artifact_id}/versions/{version_id}/restore`；
- `POST /api/artifacts/{artifact_id}/regenerate` 创建 child version；
- regenerate failure 不改变 current version；
- application_package artifact 的最小业务表写回。

未执行：

- 未删除旧 artifact 字段；
- 未做不可逆迁移；
- 未发起真实外部 provider regenerate；
- 未实现复杂版本 diff UI。

## 8. 验收结果

自动化测试：

```text
python3 -m pytest tests/evals/test_p1_schema_migration_eval.py tests/evals/test_p1_artifact_versioning_eval.py tests/evals/test_p1_regenerate_eval.py
结果：6 passed

python3 -m pytest
结果：41 passed

npm --prefix apps/chatbox run build
结果：通过
```

真实感数据：

- 使用 `examples/resumes/transition_frontend_resume.md`；
- 使用 `examples/projects/todoplus_README.md`；
- 使用 `examples/jds/junior_frontend_jd.md`；
- 生成 ApplicationPackage artifact；
- 编辑 artifact 创建 v2；
- restore 回 v1；
- regenerate 创建 child version。

## 9. PRD 规格检视

通过：

- 用户编辑不会覆盖旧 artifact version；
- regenerate 不覆盖旧产物；
- 旧版本仍可读；
- current version 可恢复；
- regenerate failure 不改变 current version；
- 业务写入仍在 Python Domain Tools；
- Chatbox 和 Pi Agent Core 未直接写版本表。

未完成但不属于本阶段：

- export preflight；
- PDF/DOCX 正式导出；
- Chatbox 版本选择和编辑抽屉 UX。

## 10. 目标架构检视

通过。P1-M3 已补齐目标架构中的 `Artifact Versioning Layer` 和 `Regenerate Transaction` 主边界：

- `artifact` 保存 current pointer；
- `artifact_version` 保存 lineage；
- edit / regenerate 创建新版本；
- restore 只切 current pointer，不删除旧版本；
- export 后续可以默认读取 current version。

## 11. 残留风险

- 当前 regenerate 是本地 mock/fixture 风格的确定性重生成，真实 provider regenerate 需要后续结合 P1-M2 provider prompt 质量继续增强；
- 当前版本恢复没有复杂 diff UI，P1 只要求可恢复和可追溯；
- Export Service 尚未改为强制读取 current/selected version。

## 12. 是否允许进入下一阶段

允许进入 `P1-M4 / WP5+WP6: Export Service + Chatbox P1 UX`，先做 WP5 Export Service。

当前没有新增致命或重大规格偏差，也没有虚假验收风险；本阶段结论仅代表 artifact versioning 和 regenerate 闭环通过，不代表 export 已满足 P1。
