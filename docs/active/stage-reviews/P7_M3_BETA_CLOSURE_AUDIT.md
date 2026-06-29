# P7-M3 Beta Closure 审计

日期：2026-06-29  
阶段：P7-M3 Beta 使用说明、支持流程、隐私审计和最终报告  
状态：自动化候选通过；产品化 Beta 基线可演示，非 SaaS GA。

## 1. 当前 Beta 最小使用路径

1. 启动 API：`.venv/bin/python -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000`
2. 启动 Chatbox：`npm --prefix apps/chatbox run dev -- --host 127.0.0.1 --port 5173`
3. 打开 `http://127.0.0.1:5173/`
4. 使用默认本地/mock 路径或在模型设置中保存 provider 偏好；
5. 授权本会话外呼后，可在 fake provider 验收模式下体验 provider-backed free chat；
6. 左侧 Long context 查看上下文摘要；
7. 左侧 Workspace ops 执行备份清单、清理预演、迁移预演和脱敏诊断；
8. 推进台继续查看产物、确认项和导出。

## 2. 支持与故障排查

| 问题 | 判断方式 | 恢复动作 |
| --- | --- | --- |
| API 未启动 | Chatbox 请求失败或初始化卡住 | 重新启动 uvicorn，确认 8000 端口可访问 |
| provider 未授权 | 状态显示已配置但待授权 | 打开模型设置并授权本会话外呼 |
| provider 失败 | 状态显示 failed/fallback | 继续使用本地 fallback；检查 provider 配置或保持 fake 验收 |
| workspace 操作风险 | cleanup/migration 显示 warning | 当前只允许 dry-run，不执行 apply |
| 报告截图不可见 | HTML 中图片路径失效 | 检查 `docs/reports/evidence/p6p7_acceptance/` 是否存在 |

## 3. 隐私审计结论

- API Key 不进入前端 bundle、报告、截图说明或测试 fixture；
- provider chat 日志只记录脱敏摘要、状态和错误类型；
- diagnostics report 是 metadata-only；
- backup 当前是 manifest-only，不复制完整资料内容；
- cleanup/migration 当前只 dry-run，不删除、不修改数据库；
- 真实个人资料路径仍未执行。

## 4. 出门条件对照

| P7 Gate | 当前结果 |
| --- | --- |
| workspace 生命周期可用 | backup manifest、cleanup dry-run、migration dry-run、diagnostics 已有 UI 和 API |
| 诊断与回滚可复现 | 本文记录启动、故障恢复、dry-run 边界；迁移 apply 未实现 |
| Beta 使用说明和支持流程 | 本文提供最小路径和支持表 |
| 可视化验收报告 | `docs/reports/P6P7_AUTOMATED_ACCEPTANCE_REPORT.html` |

## 5. 不得声明

- 不得声明 SaaS、多租户、Billing 或云端生产发布通过；
- 不得声明 workspace 删除或迁移 apply 已通过；
- 不得声明真实个人资料验收完成；
- 不得声明真实 provider 质量通过。

结论：P7 本地产品化 Beta 自动化候选可以进入人工审查；P7-post P5-REAL/P5-Freeze 仍需用户单独授权资料路径。
