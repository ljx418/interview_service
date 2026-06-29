# P7-M1/M2 Workspace Lifecycle 与 Diagnostics 基线审计

日期：2026-06-29
阶段：P7-M1 Workspace Lifecycle / P7-M2 Diagnostics
状态：本地优先 Beta 基线实现；不包含删除、迁移 apply 或 SaaS 能力。

## 1. 本阶段目标

- 提供 workspace backup manifest；
- 提供 cleanup dry-run；
- 提供 migration dry-run；
- 提供脱敏 diagnostics report；
- 让后续 P7 HTML 报告可展示本地数据生命周期和诊断边界。

## 2. 安全边界

- backup 当前只生成 metadata manifest，不复制完整资料内容；
- cleanup 只生成 dry-run plan，不删除文件；
- migration 只生成 dry-run plan，不修改数据库或文件；
- diagnostics 只返回 metadata、计数、provider 脱敏状态和 workspace 健康摘要；
- 任何 delete、cleanup apply、migration apply 都必须另行高风险确认。

## 3. 验收口径

自动化测试必须证明：

- backup manifest 存在且 `contains_file_contents=false`；
- cleanup plan `dry_run=true` 且导出文件仍存在；
- migration plan `dry_run=true` 且含回滚说明；
- diagnostics report 不包含 API Key、完整个人资料或 provider raw response。

## 4. 不得声明

- 不得声明 workspace 删除已通过；
- 不得声明迁移 apply 已通过；
- 不得声明 SaaS、多租户、Billing 或远端同步已完成；
- 不得把 diagnostics report 写成隐私审计最终通过。
