# JobPilot AI P3 真实用户 Chatbox 体验开发及验收计划

## 1. 阶段结论

当前可以进入 P3 文档锁定与后续开发准备，但不能声称 P3 已实现或已人工体验通过。

P2 已证明 examples-guided 端到端路径可以跑通，但最近截图暴露出真实用户体验问题：窄屏布局压缩、对话区和推进台混杂、空白区域过大、用户难以判断 Chatbox 是否响应。P3 必须把这些问题作为阶段目标处理。

审计意见：

- 当前方向与总 PRD 一致：Chatbox-first、本地优先、结果导向；
- 当前 P2 基线可以支撑 P3 开发；
- P3 不应跳到 MCP、CLI、ASR 或会议平台；
- P3 必须增加真实 Chrome 截图验收，不允许用“构建通过”替代体验验收；
- 真实个人资料、API Key 和外部模型调用仍是高风险流程，必须人工确认。

## 2. P3 目标体验路径

P3 完成后，用户应能完成以下路径：

```text
打开本地 Chatbox
→ 看到 workspace、provider、示例/真实资料模式
→ 在聊天区选择上传资料、粘贴 JD 或输入任务
→ Chatbox 返回可理解响应、计划、错误或下一步
→ 推进台显示阶段、产物、确认项、版本和导出
→ 用户生成申请包、面试准备、实时文本提示、复盘和训练任务
→ 用户确认 / 编辑 / regenerate / 导出当前版本
→ 桌面、窄屏、移动宽度下均可完成截图验收
```

P3 不承诺：

- 默认真实外部 provider；
- 真实个人资料自动验收；
- 自动海投；
- MCP / CLI；
- ASR / 会议平台；
- SaaS 化。

## 3. 当前架构与目标架构差异

当前 P2 架构已经具备：

- React Chatbox；
- FastAPI Agent Service；
- ChatCore Facade；
- PiAgentChatCore / KeywordChatCore；
- Python Domain Tools；
- Provider Runtime；
- Artifact Versioning；
- Export Service；
- P2 Workflow Orchestrator；
- P2 HTML 报告和截图证据。

P3 目标新增：

- Conversation Plane：稳定消息流、任务输入、上传入口、错误反馈；
- Workbench Plane：阶段、下一步、产物、版本、确认项、导出；
- Mode Boundary：示例模式 / 真实资料模式 / mock provider / external provider；
- Responsive Layout Controller：桌面、窄屏、移动宽度稳定布局；
- UX Evidence Gate：每个体验阶段必须有 Chrome 截图证据。

关键架构约束：

- 前端只展示和触发 API，不复制业务生成逻辑；
- Chatbox 和推进台职责分离；
- Provider 默认 mock；
- 外部 provider opt-in；
- workspace 文件和导出仍受路径沙箱限制；
- source refs、questions_to_confirm、artifact version 不得丢失。

## 4. 工作包

### 4.0 执行规则

每个工作包进入开发前必须完成三件事：

1. 对照 `01_STAGE_PRD.md` 确认该工作包是否直接服务 P3 目标体验路径；
2. 对照 `02_TARGET_ARCHITECTURE.md` 确认没有破坏模块职责、依赖方向和禁止关系；
3. 在本工作包完成后保存验收证据，并写入 stage review。

每个工作包完成后必须回答：

| 检查项 | 通过标准 |
| --- | --- |
| PRD 体验路径 | 用户是否更接近“只通过 Chatbox 和推进台完成求职材料体验” |
| 架构职责 | 前端是否仍只做展示和触发，业务逻辑是否仍在 Domain Tools |
| 数据边界 | source refs、questions_to_confirm、artifact version 是否保留 |
| 安全边界 | 是否没有默认外部 provider、没有敏感 raw data 入库或日志 |
| 可见证据 | 是否有测试、截图或报告证明，而不是口头说明 |
| 打回风险 | 是否出现无响应、窄屏不可用、伪造验收或 P0/P1/P2 退化 |

P3 标准证据路径：

```text
docs/reports/evidence/p3_chatbox_initial_1280.png
docs/reports/evidence/p3_chatbox_response_1280.png
docs/reports/evidence/p3_chatbox_error_state_1280.png
docs/reports/evidence/p3_chatbox_narrow_720.png
docs/reports/evidence/p3_chatbox_mobile_390.png
docs/reports/P3_REAL_USER_CHATBOX_ACCEPTANCE_REPORT.html
docs/active/stage-reviews/p3-m1-chatbox-response.md
docs/active/stage-reviews/p3-m2-mode-boundary.md
docs/active/stage-reviews/p3-m3-workbench-separation.md
docs/active/stage-reviews/p3-m4-responsive-ux.md
docs/active/stage-reviews/p3-m5-acceptance-report.md
docs/active/stage-reviews/p3-m6-freeze-audit.md
```

测试候选文件：

```text
tests/evals/test_p3_chatbox_response_eval.py
tests/evals/test_p3_mode_boundary_eval.py
tests/evals/test_p3_artifact_workbench_eval.py
tests/evals/test_p3_responsive_evidence_eval.py
tests/evals/test_p3_full_flow_regression_eval.py
```

如果实现时发现现有 API 无法支撑这些测试，可以先补 API 或测试夹具，但不得把截图报告作为唯一后端验收。

### WP1 - Chatbox 对话响应闭环

目标：

- 修复“发送后似乎无反应”的体验；
- 对有效任务返回计划或执行结果；
- 对无效任务、缺少资料、API 失败返回可理解错误。

实现区域：

- `apps/chatbox/src/main.tsx`；
- `apps/chatbox/src/styles.css`；
- `services/api/main.py`；
- ChatCore / PiAgent adapter。

验收证据：

- 发送有效任务截图；
- 发送无效任务截图；
- 后端错误态截图或测试；
- frontend build。

详细开发清单：

- Conversation View 增加明确的用户消息、系统计划、执行结果、错误状态；
- Composer 对空输入给出本地提示，不发无意义请求；
- Chat API 失败时将错误码和可读错误返回 UI；
- 缺少资料时返回“下一步需要上传资料或选择 examples”，而不是空回复；
- 有效任务至少覆盖：上传资料引导、粘贴 JD、生成申请包、准备面试。

出门条件：

- Chrome 截图证明有效输入后有可见响应；
- Chrome 截图证明无效输入或缺资料时有可理解错误；
- 没有把前端 mock 文案冒充真实工具结果；
- `npm --prefix apps/chatbox run build` 通过。

### WP2 - 示例模式 / 真实资料模式边界

目标：

- 用户清楚知道当前在使用 examples 还是自己的资料；
- 用户清楚知道当前 provider 是 mock 还是 external；
- 真实资料模式不会默认发起外部调用。

实现区域：

- Chatbox 顶部状态和模式控件；
- provider status API；
- workflow request payload。

验收证据：

- 示例模式截图；
- 真实资料模式截图；
- provider 状态截图；
- 外部 provider 未授权时不会调用的测试或日志证据。

详细开发清单：

- Header 或模式控件显示 `Example mode` / `My data mode`；
- Provider 状态显示 `mock`、`external configured`、`external enabled/disabled` 的区别；
- 真实资料模式显示本地优先和外部调用确认边界；
- Workflow 请求必须携带 mode，后端据此决定是否加载 examples；
- 外部 provider 未授权时，任何真实资料路径不得自动调用外部模型。

出门条件：

- 示例模式可以继续跑 P2 examples E2E；
- 真实资料模式不会自动触发 MiniMax 或其他 external provider；
- 报告中只允许写“真实感示例数据验收”，除非用户明确授权真实个人资料。

### WP3 - 对话区与推进台分离

目标：

- 对话区负责输入和消息；
- 推进台负责阶段、下一步、产物、确认项、版本和导出；
- 空状态不出现无意义大空白。

实现区域：

- Chatbox layout；
- artifact card rendering；
- workflow panel rendering。

验收证据：

- 初始页截图；
- 运行中截图；
- 产物和导出截图；
- source refs / questions_to_confirm / version 可见。

详细开发清单：

- 页面主布局明确分为 Conversation Area 和 Workbench Area；
- Conversation Area 只包含消息流、输入、上传和快捷任务；
- Workbench Area 只包含阶段、下一步、产物、确认项、版本和导出；
- Artifact Cards 必须展示 artifact type、current version、status、source refs 或 artifact refs、questions_to_confirm；
- 空状态展示下一步，不留大面积无意义空白；
- Workbench 在窄屏下移动到对话区下方，不挤压输入区。

出门条件：

- 用户能从截图中清楚区分“我要输入什么”和“系统已经产出什么”；
- artifact version、confirm、regenerate、export 入口仍可见；
- source refs 和 questions_to_confirm 没有因 UI 简化被隐藏。

### WP4 - 响应式 UX 修正

目标：

- 修复窄屏卡片过窄、右侧空白、分区截断和输入区压迫；
- 保证桌面、720px、390px 可用。

实现区域：

- `apps/chatbox/src/styles.css`；
- 需要时微调 React DOM 结构。

验收证据：

- 1280px 截图；
- 720px 截图；
- 390px 截图；
- 无严重横向滚动；
- 输入区不遮挡消息。

详细开发清单：

- 1280px：对话区和推进台可并排或合理分栏；
- 720px：布局切换为单列或主次堆叠，不能出现半屏空洞；
- 390px：输入区、发送按钮、上传入口、状态标签不溢出；
- 消息列表和推进台有明确滚动区域；
- 任何固定高度都必须有响应式约束；
- 按钮和标签长文本不能撑破容器。

出门条件：

- Chrome 1280 / 720 / 390 截图全部可读；
- 不存在严重横向滚动；
- 输入区不遮挡最后一条消息；
- `npm --prefix apps/chatbox run build` 通过。

### WP5 - P3 端到端体验验收报告

目标：

- 制作 P3 HTML 验收报告；
- 报告列出目标架构、当前实现、体验路径、截图证据、测试结果、未验证范围。

实现区域：

- `docs/reports/`；
- `docs/reports/evidence/`；
- `docs/active/stage-reviews/`。

验收证据：

- HTML 报告可打开；
- 截图路径有效；
- 不包含虚假验收；
- PRD 规格检视通过。

详细开发清单：

- 报告列出目标架构模块图和当前实现状态；
- 报告列出用户体验路径：启动、模式选择、输入、响应、推进台、产物、导出；
- 报告引用所有 P3 截图证据；
- 报告列出已运行测试命令和结果；
- 报告明确未验证范围：真实个人资料、默认外部 provider、ASR、会议平台、MCP、CLI；
- 报告包含 PRD 规格检视和目标架构符合性检查。

出门条件：

- 人类能在 3 分钟内理解当前实现了什么、没实现什么、风险在哪里；
- 报告不把未执行的真实外部调用或真实个人资料验收写成已通过。

### WP6 - 回归验收与阶段冻结

目标：

- P0/P1/P2 不退化；
- P3 文档、drawio、README、TODO 同步；
- 出具冻结审计。

验收命令：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

最低验收：

- examples 真实感数据端到端路径通过；
- Chrome 1280/720/390 截图存在；
- P3 HTML 报告存在；
- drawio XML 可解析；
- README/TODO/active docs 口径一致。

详细开发清单：

- 运行 P0/P1/P2/P3 相关 pytest；
- 运行前端 build；
- 验证 drawio XML；
- 检查 active Markdown 文档数小于 20；
- 检查 README、TODO、active README 当前阶段口径一致；
- 生成 P3 freeze audit；
- 列出残留风险和 P4+ 候选。

出门条件：

- 没有 P0/P1/P2 回归失败；
- 没有虚假验收风险；
- 没有把 P4+ 能力写入 P3 hard gate；
- 所有 P3 验收门槛都有证据。

## 4.7 架构模块验收矩阵

| 架构模块 | P3 必须完成的验收 | 主要证据 |
| --- | --- | --- |
| Chatbox Client | 只展示和触发 API，不生成求职内容 | 代码审查、Chatbox 截图 |
| Conversation View | 有效输入、无效输入、缺资料、错误态都有可见消息 | `p3_chatbox_response_1280.png`、`p3_chatbox_error_state_1280.png` |
| Composer / Upload Entry | 上传、粘贴 JD、快捷任务入口可用且响应式 | 1280/720/390 截图 |
| Workbench Panel | 阶段、下一步、产物、确认项、版本、导出可见 | 产物区截图 |
| Artifact Cards | source refs、questions_to_confirm、version 不丢失 | artifact 截图或 API 测试 |
| FastAPI Routes | chat/workflow/artifact/export/provider API 错误可理解 | API eval |
| ChatCore Facade | Keyword/PiAgent 编排不直接写业务数据 | 单元测试或代码审查 |
| Flow Controller | 缺资料返回下一步，失败不伪造完成 | workflow eval |
| Domain Tools | 继续生成事实、项目、JD、申请包、面试和训练任务 | examples E2E |
| Provider Policy Gate | mock 默认，external opt-in，敏感信息不落日志 | provider boundary eval |
| Artifact Service | edit/regenerate 新版本，旧版本保留 | artifact version eval |
| Export Service | preflight 和 workspace exports 边界不退化 | export eval |
| Evidence Layer | 测试、截图、HTML 报告可追溯 | P3 HTML 报告 |

## 5. 阶段打回规则

出现以下情况必须打回计划阶段重新思考：

- Chatbox 对有效输入无响应；
- 截图显示窄屏或移动端不可操作；
- examples 结果被写成真实个人资料验收；
- 真实外部 provider 被默认调用；
- 导出写出 workspace；
- artifact version / source refs / questions_to_confirm 丢失；
- P0/P1/P2 回归失败；
- 文档或报告承诺了未实现能力。

## 6. 需要人类处理的高风险流程

- 真实个人简历、真实私有 JD、真实 transcript；
- 真实外部 provider 调用；
- API Key 填写和授权；
- 不可逆数据库迁移；
- 删除 workspace 或覆盖用户导出；
- 判断最终视觉体验是否达到主观满意。

## 7. 启动审计结论

P3 文档目标与总 PRD、目标架构和当前 P2 基线一致。当前没有新增致命或重大规格偏差。可以进入 P3 实质开发，但每个工作包完成后必须执行对应截图验收、PRD 规格检视和阶段审计；如果验收不通过，必须打回当前工作包计划，不得用文字说明替代证据。
