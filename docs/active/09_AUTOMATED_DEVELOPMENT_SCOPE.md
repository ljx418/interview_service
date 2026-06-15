# JobPilot AI P3 自动化开发范围与验收边界

## 0. P3 当前自动化范围

当前阶段口径：

- P0 已冻结；
- P1 已完成本地工程闭环；
- P2 已完成 examples-guided Chatbox E2E、HTML 报告、Chrome 截图和 MiniMax opt-in 受控验收；
- P3 当前目标是真实用户 Chatbox 体验、响应式 UX、对话/推进台分离和可截图验收；
- 真实 API Key、真实外部模型调用、真实个人资料、不可逆迁移仍必须暂停找用户确认。

P3 可以由自动化 Agent 直接推进的范围：

- Chatbox 对话响应、错误反馈和下一步提示；
- 示例模式 / 真实资料模式的文案和状态呈现；
- 对话区与推进台分离；
- responsive CSS、滚动体验、窄屏和移动布局修正；
- artifact 摘要、确认项、版本、导出入口的可读性修正；
- 使用 examples 真实感数据做端到端验收；
- Chrome 可见截图验收；
- P3 HTML 报告、PRD 规格检视、stage review；
- README、TODO、active docs、drawio 同步；
- eval 增量补强、pytest、frontend build。

P3 必须先写计划和审计意见的范围：

- 新增复杂结构化编辑表单；
- 新增多示例数据集或真实上传复杂清洗流程；
- 重大路由/API 重构；
- 数据库 schema 不可逆迁移；
- Provider 策略改变为默认外部调用；
- 大规模视觉设计系统替换。

P3 必须人类确认的高风险流程：

- 使用用户真实简历、真实私有 JD、真实 transcript 或其他个人敏感资料；
- 使用外部 API Key 发起真实 LLM 网络调用；
- 删除 workspace、覆盖导出文件或做不可逆数据迁移；
- 进入自动海投、隐蔽式面试辅助、逐字代答；
- 接入 ASR、系统音频、会议平台、屏幕解析或视频解析；
- 增加登录、多租户、Billing、SaaS 后台。

P3 最低验收命令：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

如果涉及浏览器体验，必须采集 Chrome 1280/720/390 截图，并在报告中说明已验证和未验证范围。

以下 P2 自动化范围作为已完成基线和历史背景保留；不代表当前 P3 执行口径。

## 1. 目的

本历史段落定义 P2 开发期间自动化 Agent 可以继续推进的范围、必须先审计的范围和必须交给人类确认的高风险流程。

P2 当时阶段口径：

- P0 已冻结；
- P1 已完成本地工程闭环；
- P2 当时目标是完整端到端 Chatbox 用户体验；
- P2 可以自动推进 guided workflow、HTML 验收报告、截图证据整理、小步 UX 可读性修正和冻结复验；
- 真实 API Key、真实外部模型调用、真实个人资料、不可逆迁移仍必须暂停找用户确认。

## 2. 当前状态判断

当前 P2 文档体系已经覆盖：

```text
P2 PRD
→ P2 目标架构
→ P2 里程碑
→ P2 验收门槛
→ P2 实现规格
→ P2 追踪矩阵
→ P2 端到端开发及审计计划
→ P2 drawio 图示和文本镜像
```

当前实现已经具备：

- P2 Workflow Orchestrator API；
- examples guided demo flow；
- Chatbox Guided Flow 面板；
- 一键体验完整路径按钮；
- `?autorun=1` 本地可见验收入口；
- 关键产物最小人类可读摘要；
- P2 guided flow eval；
- Chrome 初始/完成/总结截图。

当前剩余 P2 工作：

- P2 HTML 验收报告；
- 截图证据整理；
- 全量冻结复验；
- README/TODO/docs/drawio 最终同步；
- P2 冻结审计。

## 3. 可自动开发范围

以下工作可以由自动化 Agent 直接执行，但每次必须跑相应验收：

- P2 HTML 验收报告；
- 截图证据整理和引用修正；
- Chatbox workflow 面板小步 UX 修正；
- artifact 人类可读摘要增强；
- examples guided flow 的错误提示和恢复信息；
- README、TODO、active docs、drawio 同步；
- P2 stage review 和冻结审计；
- eval 增量补强；
- Chrome 可见截图验收；
- 全量 pytest 和前端 build。

最低验收命令：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

如果涉及浏览器体验，还必须采集 Chrome 可见截图。

## 4. 需先计划和审计的范围

以下工作不能直接实现，必须先写开发计划、验收标准和审计意见，并确认无致命或重大风险：

- 从 examples 一键路径扩展到复杂真实上传引导；
- 新增结构化 artifact 编辑表单；
- 复杂版本 diff UI；
- PDF 样式优化；
- 多岗位模板和更多示例数据；
- 长时间稳定性和并发测试；
- 任何会改变 workspace 数据模型的迁移。

## 5. 必须人类确认的高风险流程

以下工作必须暂停并找用户确认：

- 使用用户真实简历、真实私有 JD、真实 transcript 或其他个人敏感资料；
- 使用外部 API Key、生产凭据、真实 LLM 网络调用；
- 删除 workspace、覆盖导出文件或做不可逆数据迁移；
- 进入自动海投、隐蔽式面试辅助、逐字代答；
- 接入 ASR、系统音频、会议平台、屏幕解析或视频解析；
- 增加登录、多租户、Billing、SaaS 后台。

## 6. 历史 P2/P3 边界

以下能力曾作为 P2 之后的候选，但在当前 P3 中仍不进入出门条件；它们只能作为 P4+ 或独立阶段规划：

- MCP Server；
- CLI；
- 完整 ASR / Whisper；
- 会议平台助手；
- 默认真实外部 Provider；
- 真实个人资料自动验收；
- 向量数据库；
- 岗位数据源接入；
- Offer 分析；
- 自动申请和投递跟踪大屏。

## 7. P3 后续开发大纲

### P3-M1 Chatbox 对话响应闭环

- 有效输入返回计划或执行结果；
- 无效输入、缺少资料和后端错误有明确反馈；
- 采集 Chrome 消息响应和错误态截图。

### P3-M2 示例模式 / 真实资料模式

- 明确 examples 与真实资料模式；
- 明确 mock / external provider 状态；
- 未授权时不触发真实外部 provider。

### P3-M3 推进台与产物区重构

- 对话区和推进台分离；
- 推进台展示阶段、下一步、产物、版本、确认项和导出；
- 保留 source refs、questions_to_confirm、artifact version。

### P3-M4 响应式 UX 验收

- 修复窄屏卡片压缩、右侧空白、分区截断和输入区压迫；
- 采集 1280px、720px、390px Chrome 截图；
- 前端 build 通过。

### P3-M5/P3-M6 报告和冻结

- 制作 P3 HTML 验收报告；
- 运行 `python3 -m pytest`；
- 运行 `npm --prefix apps/chatbox run build`；
- 验证 drawio XML；
- 同步 README/TODO/active docs；
- 生成 P3 冻结审计。

## 8. 审计意见

当前文档经过 P3 PRD 增补、目标架构、里程碑、验收门槛、追踪矩阵、自动化范围、详细开发计划和 drawio 补齐后，可以支撑 P3 剩余自动化开发。关键限制是：真实个人数据、真实 API Key、真实外部模型调用、不可逆迁移、ASR/会议平台、MCP/CLI、自动投递和 SaaS 化能力都不能被自动越过。
