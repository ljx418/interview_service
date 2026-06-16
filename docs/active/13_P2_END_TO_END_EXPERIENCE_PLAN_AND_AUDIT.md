# JobPilot AI P2 端到端用户体验开发及验收计划

生成日期：2026-06-12  
阶段状态：P2-M1~M3 已完成最小闭环，P2-M4/P2-M5 待继续  
审计结论：可以进入 P2 实质开发；当前未发现致命或重大规格偏差。P2 必须聚焦“用户能通过 Chatbox 完成一条完整求职 Agent 体验路径”，不能把 MCP、CLI、ASR 或会议平台提前变成 P2 hard gate。

## 1. P2 阶段目标

P2 的目标不是继续扩底层工具数量，而是把 P0/P1 已完成的能力组织成一条人类可理解、可点击、可截图验收的完整端到端体验。

P2 完成时，一个用户应能在本地打开 Chatbox，并按引导完成：

```text
启动本地项目
→ 创建或恢复 workspace
→ 选择示例数据或上传自己的资料
→ 导入简历 / 项目 README
→ 生成职业事实、技能证据和项目卡
→ 粘贴或加载目标 JD
→ 生成 JD 解析和岗位匹配报告
→ 生成申请包
→ 用户确认 / 编辑 / regenerate
→ 导出 Markdown + DOCX
→ 生成面试准备和故事卡
→ 输入文本面试问题并获得结构提示
→ 输入 transcript 并生成复盘和训练任务
→ 看到本次求职推进摘要、产物列表和导出文件
```

P2 的验收核心仍是：用户是否拿到可信、可确认、可导出的结果，而不是页面数量或模型炫技。

## 2. P2 范围

### 2.1 必须实现

- Chatbox 端到端引导工作流；
- 一键加载 examples 真实感数据并跑通完整路径；
- 后端 workflow run API，返回每一步状态、产物、导出文件和错误；
- Chatbox 工作流面板，展示当前步骤、已完成步骤、下一步动作和失败恢复；
- 关键产物的人类可读摘要，不再只依赖 JSON textarea；
- 至少 3 张 Chrome 可见截图证据：初始页、工作流完成页、导出/总结页；
- P2 HTML 验收报告，引用截图、自动化测试和 PRD 规格检视；
- 保持 P0/P1 自动化测试不退化。

### 2.2 可做但不是 hard gate

- 更漂亮的 artifact 详情页；
- PDF 样式优化；
- 版本 diff 的可视化增强；
- 更多示例岗位模板；
- 移动端视觉优化。

### 2.3 非目标

P2 不把以下能力作为出门条件：

- MCP Server；
- CLI；
- ASR / Whisper；
- 会议平台接入；
- 屏幕解析或视频解析；
- 自动投递 / 自动申请；
- SaaS 登录、多租户或 Billing；
- 默认真实外部 Provider 调用；
- 使用真实个人资料做自动验收。

这些能力只能进入 P4+ 或独立阶段，并必须重新计划、审计和验收。P3 已重新定义为真实用户 Chatbox 体验和响应式 UX 阶段，不默认承诺这些能力。

## 3. 当前架构实现

P1 当前实现已经具备：

```text
React Chatbox
→ FastAPI Agent Service
→ ChatCore Facade
  → KeywordChatCore fallback
  → PiAgentChatCore optional
→ Python Domain Tools
→ Provider Runtime
  → MockProvider
  → FixtureProvider
  → OpenAI-compatible opt-in
→ Prompt Contract / Schema Validation
→ Artifact Versioning / Regenerate
→ Export Service
→ SQLite workspace / local exports
→ pytest eval gates / frontend build / Chrome screenshot evidence
```

P2 启动时的 P1 优势：

- mock/fixture 模式下可以无 API Key 本地验收；
- Pi Agent Core 已可接管基础业务编排；
- provider runtime、artifact version、regenerate、DOCX export 已有实现；
- Chatbox 可以展示产物卡、版本、编辑、重新生成和导出入口；
- 已有 P1 Chrome 可见截图报告。

P2 启动时的差距：

- 用户仍需要知道该输入什么 prompt；
- Chatbox 没有明确的“下一步”工作流状态；
- 没有一键跑通 examples 完整路径的后端 API；
- 产物主要以 JSON 展示，对非开发者可读性不足；
- 没有把完整体验路径拆成可截图验收的多个阶段；
- P1 HTML 报告证明“可见”，但还不能证明“完整用户体验路径可顺畅完成”。

## 4. P2 目标架构

P2 在 P1 架构上新增 Experience Flow 层：

```text
Chatbox Client
  → Experience Flow Panel
    → step list
    → current state
    → next action
    → run demo flow
    → artifact summary
    → exports summary
  → Artifact Cards
    → human readable summary
    → source refs
    → confirmations
    → versions
    → edit / regenerate / export

FastAPI Agent Service
  → Workflow Routes
    → GET /api/workflows/p2-demo/status
    → POST /api/workflows/p2-demo/run
  → Existing Domain Routes

Workflow Orchestrator
  → load examples
  → save documents
  → extract facts
  → create project card
  → parse JD
  → match profile
  → create application package
  → export Markdown + DOCX
  → prepare interview
  → realtime text hint
  → review transcript
  → collect artifacts / exports / training tasks

Storage / Evidence
  → SQLite workspace
  → local exports
  → workflow run summary
  → Chrome screenshots
  → P2 HTML acceptance report
```

架构边界：

- Experience Flow 只编排已存在的 Domain Tools，不复制求职业务逻辑；
- Chatbox 只展示流程状态和触发动作，不直接写业务表；
- Demo flow 使用 `examples/` 匿名真实感数据，不使用真实个人资料；
- Provider 默认仍是 mock，本阶段不默认触发真实外部调用；
- 截图只能证明可见体验，业务正确性仍由 tests/evals 证明。

## 5. 工作包与里程碑

| 里程碑 | 工作包 | 目标 | 验收证据 |
| --- | --- | --- | --- |
| P2-M0 | 计划与审计 | 锁定 P2 端到端体验范围 | 本文档、README/TODO 同步 |
| P2-M1 | Workflow Orchestrator API | 后端一键跑 examples 完整路径 | 已完成，`test_p2_guided_demo_flow_eval.py` 通过 |
| P2-M2 | Chatbox Guided Flow | 前端显示步骤、下一步、运行 demo flow | 已完成，前端 build 通过并采集 Chrome 截图 |
| P2-M3 | Human-readable Artifact Summary | 关键产物不只展示 JSON | 已完成最小摘要，后续继续细化 |
| P2-M4 | P2 Acceptance Evidence | 生成截图和 HTML 验收报告 | P2 HTML 报告 + 截图路径 |
| P2-M5 | Freeze Regression | 全量 pytest、build、PRD 检视 | P2 冻结报告 |

## 6. P2 验收门槛

P2 通过必须满足：

- `python3 -m pytest` 通过；
- `npm --prefix apps/chatbox run build` 通过；
- 新增 P2 workflow eval，确认 examples 完整路径跑通；
- Chatbox 可以从 UI 触发 demo flow；
- UI 展示至少 7 个关键步骤的完成状态；
- 完成页展示申请包、面试准备、实时提示、复盘训练任务和导出文件；
- 导出文件仍只写入 workspace `exports/`；
- Chrome 可见截图覆盖初始、执行完成、总结/导出；
- P2 HTML 验收报告明确已验证和未验证范围；
- 不声称真实外部 Provider、真实 API Key 或真实个人资料验收已通过。

P2 不通过条件：

- P0/P1 回归测试失败；
- demo flow 需要真实 API Key 才能跑通；
- Chatbox 把业务生成逻辑写在前端；
- 导出写出 workspace 外；
- formal_assist 输出完整逐字代答；
- 截图或报告把未执行的真实外部调用写成已通过；
- P2 把 MCP/CLI/ASR/会议平台误列为必交付。

## 7. 第一批实现计划

P2-M1/M2 的第一批实现按最小闭环推进：

1. 新增 `WorkflowRunRequest` schema；
2. 新增 `services/workflows/p2_demo.py`；
3. 新增 `POST /api/workflows/p2-demo/run`；
4. 后端使用 examples 跑通完整路径并返回：
   - `steps`;
   - `artifacts`;
   - `exports`;
   - `job_id`;
   - `package_id`;
   - `realtime_hint`;
   - `training_tasks`;
5. 新增 `tests/evals/test_p2_guided_demo_flow_eval.py`；
6. Chatbox 增加 Workflow Panel 和“一键体验完整路径”按钮；
7. 前端展示 workflow summary 和关键产物摘要；
8. build 和 Chrome 截图验收。

## 8. 审计意见

当前审计结论：

- P2 方向与总 PRD 一致：优先把用户拿到结果的路径做完整；
- P2 不改变 P1 的本地优先、安全边界和 provider opt-in 原则；
- P2 第一批实现复用现有 Domain Tools，风险可控；
- 当前没有新增致命或重大规格偏差；
- 可以进入 P2-M1 实质开发。

残留风险：

- examples 数据只能代表真实感验收，不等于真实个人资料验收；
- UI 需要截图人工审查体验是否足够自然；
- 一键 demo flow 不能替代后续真实用户上传资料路径，但可以作为 P2 自动化验收基线。
