# M4 Eval Gates 与开源发布计划与审计

## 关联规格

- PRD 成功标准：新贡献者能本地启动；转行程序员能用示例数据跑完整路径并拿到可确认、可修改、可导出的结果。
- 目标架构：Chatbox-first、Agent Tool-first、本地优先、artifact 可追溯、安全边界明确。
- 验收门槛：本地启动、资料导入、JD 分析、申请包、面试、复盘、开源可用性。

## 开发计划

- 新增 eval tests：JD 解析、事实安全、实时提示安全、workspace 隐私、完整 demo flow。
- README/TODO 与 active docs、实际命令保持一致。
- drawio 文档仅在架构或里程碑发生实质变化时更新。
- 最终执行后端测试、前端 build、真实数据端到端验收。

## 验收标准

- `python3 -m pytest` 通过。
- `npm --prefix apps/chatbox run build` 通过。
- 示例数据完整路径到达 application package、Markdown export、realtime hint、review 和 training tasks。
- PRD 规格检视无致命或重大偏差。

## 审计意见

- 致命风险：只跑单元测试但没有端到端证据。处理：保留 full demo flow eval。
- 重大风险：README/TODO 写法与真实命令不一致。处理：验收阶段同步检查。
- 中等风险：drawio 与实际实现漂移。处理：若本阶段改变架构边界，更新 drawio 镜像。

## 当前结论

审计意见已闭环，M4 已完成。

## 完成记录

- 新增 eval tests：JD 解析、事实安全、实时提示安全、workspace 隐私、完整 demo flow。
- `python3 -m pytest` 通过，8 个测试全部通过。
- `npm --prefix apps/chatbox run build` 通过。
- 使用匿名真实感示例数据完成 HTTP 端到端验收，覆盖导入、事实、项目卡、JD、匹配、申请包、Markdown 导出、面试准备、实时提示、复盘训练任务。

## PRD 规格检视

当前实现可支撑 PRD P0 目标体验路径。未发现致命或重大规格偏差；残留风险为 OpenAI-compatible provider 未启用真实调用、PDF 仍为占位、artifact 复杂编辑留到 P1，均不阻塞 P0。
