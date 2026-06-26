# JobPilot AI 当前前端实现与 PRD 对齐地图

本文档整理 `apps/chatbox` 当前真实前端实现，目标是让 Gemini、Claude Code、Codex 或开发者能基于同一个事实基线继续优化 UI。本文不是新设计稿，也不是验收通过声明。

## 1. PRD 对当前前端的核心要求

来源文档：

- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/16_P4_UX_EXPERIENCE_HARDENING_PLAN.md`
- `docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`

当前阶段的前端目标可以归纳为：

| PRD 要求 | 当前前端应呈现的用户体验 |
| --- | --- |
| P4 UX 强化 | 从“能演示的 Chatbox”提升为“可理解、可操作、可审查的求职材料工作台”。 |
| 全尺寸桌面工作台 | 1200/1440/1600/1920px 下必须是完整三栏工作台，不能像窄屏布局被放大后停在左侧。 |
| Chatbox 空状态任务入口 | 空状态内直接提供“导入资料 / 解析 JD / 面试准备 / 自由聊 / 示例路径”等 suggested prompts。 |
| 自由连续对话基线 | 普通追问、偏好补充、下一步问题不能误触发 artifact 写入；明确工具意图才执行工具。 |
| Workbench 推进台 | 右侧只承载当前任务、阶段、产物、确认项、版本和导出，不承担聊天输入。 |
| Artifact 可读化 | 产物卡要用求职语义展示摘要、待确认项、版本和主次操作，避免裸 JSON 成为主反馈。 |
| Provider / 隐私边界 | 默认本地/mock；真实外部 provider、真实 API Key、真实个人资料路径不能被写成已验收。 |
| 移动端可用性 | 390px 下对话优先，Workbench 作为底部抽屉或次级面板，不挤压 Chatbox。 |

非目标和高风险边界：

- 不新增 ASR、会议平台、自动投递、SaaS、真实外部模型默认调用。
- 不把 P4/P4B/P4C 描述为已经完成人工体验审查闭环。
- 不把本地/mock 连续对话写成完整 provider-backed 自由智能聊天。

## 2. 当前源码结构

当前 Chatbox 前端代码集中在一个 React 入口和一个 CSS 文件中：

```text
apps/chatbox/
  package.json
  package-lock.json
  index.html
  vite.config.ts
  tsconfig.json
  src/
    main.tsx
    styles.css
```

当前 baseline 包中的文件是上述目录的副本：

```text
docs/gemini-current-frontend-baseline/
```

重要事实：

- 当前没有 `src/components/`、`src/hooks/`、`src/api/` 等真实拆分目录。
- `src/main.tsx` 同时承担 API client、类型定义、状态管理、业务动作、组件渲染和应用入口。
- `src/styles.css` 同时承担 design tokens、全局布局、桌面三栏、Workbench、消息气泡、产物卡和响应式规则。
- 后续可以拆分组件，但 Gemini 输出必须说明这是“建议拆分”，不是当前事实。

## 3. 当前运行依赖

| 项 | 当前实现 |
| --- | --- |
| Framework | React 19 |
| Build | Vite 7 |
| Language | TypeScript |
| Icon | `lucide-react` |
| Dev server | `127.0.0.1:5173` |
| API base | `http://127.0.0.1:8000` |
| Build command | `npm --prefix apps/chatbox run build` |

## 4. 当前数据模型

这些类型定义在 `src/main.tsx` 内。

| 类型 | 用途 |
| --- | --- |
| `DataMode` | 当前数据模式：`example` 示例模式或 `my_data` 我的资料。 |
| `Message` | 前端消息模型，包含 role、content、tone 和 artifacts。 |
| `StoredChatMessage` | 后端恢复会话时返回的历史消息行。 |
| `StoredArtifact` | 后端恢复会话时返回的 artifact 行。 |
| `WorkflowStep` | 示例工作流中的单个步骤。 |
| `WorkflowResult` | 示例工作流整体结果，包括 steps、summary、key_outputs、exports。 |
| `ApiError` | 前端封装的 API 错误，携带 errorCode、suggestedAction、recoverable。 |

## 5. 当前 API 调用

| 前端动作 | Endpoint | 调用位置 | 用户可见功能 |
| --- | --- | --- | --- |
| Provider 状态 | `GET /api/provider/status` | `App` 初始化 | 顶栏显示隐私/provider 状态。 |
| 初始化 workspace | `POST /api/workspace/init` | `App` 初始化 | 创建或恢复本地 workspace。 |
| 查询会话 | `GET /api/chat/sessions?workspace_id=...` | `App` 初始化 | 找到最新会话。 |
| 恢复会话详情 | `GET /api/chat/sessions/{id}?workspace_id=...` | `App` 初始化 | 恢复历史消息和 artifact refs。 |
| 创建会话 | `POST /api/chat/sessions` | `App` 初始化 | 没有历史会话时创建新会话。 |
| 发送聊天 | `POST /api/chat/message` | `sendText` | 自由追问、状态查询、明确工具意图。 |
| 上传资料 | `POST /api/files/upload?workspace_id=...` | `upload` | 上传简历、README 等本地文件。 |
| 跑示例路径 | `POST /api/workflows/p2-demo/run` | `runGuidedDemo` | 生成示例求职材料闭环。 |
| Artifact 版本 | `GET /api/artifacts/{id}/versions?workspace_id=...` | `ArtifactCard` | 展示 artifact 版本 pill。 |
| 确认 artifact | `POST /api/artifacts/{id}/confirm` | `ArtifactCard.confirm` | 把待确认产物标记为已确认。 |
| 重新生成 | `POST /api/artifacts/{id}/regenerate` | `ArtifactCard.regenerate` | 创建新版本并保留旧版本。 |
| 导出申请包 | `POST /api/application/export-package` | `ArtifactCard.exportPackage` | 导出 Markdown/DOCX。 |
| 下载导出文件 | `GET /api/application/download?...` | `window.open` | 打开下载链接。 |

## 6. 当前组件划分

当前这些组件都在 `src/main.tsx` 中，没有独立文件。

### 6.1 App Shell

| 组件/函数 | 职责 | 当前功能 |
| --- | --- | --- |
| `App` | 根组件和状态容器 | 初始化 workspace/session；恢复历史；管理输入、消息、busy、dataMode、providerStatus、workflowResult、drawerOpen；渲染顶栏、左侧上下文、中间对话、右侧 Workbench 和移动 FAB。 |
| `api<T>` | 统一 fetch wrapper | 处理 JSON、非 ok、后端 `ok: false` 和结构化错误。 |
| `formatError` | 错误转用户文案 | 展示错误码、错误消息和 suggestedAction。 |
| `notice` | 插入系统提示消息 | 用于确认、导出、上传等操作后的反馈。 |
| `updateArtifactStatus` | 前端同步 artifact 状态 | 确认或重新生成后更新消息内 artifact_ref.status。 |

### 6.2 顶栏与状态

| 组件/函数 | 职责 | 当前功能 |
| --- | --- | --- |
| `StatusBadge` | 顶栏状态 badge | 显示本地就绪、provider 隐私等状态。 |
| `providerLabel` | provider 状态文案 | 当前统一显示“外部模型未调用（隐私安全）”。 |
| `modeLabel` | data mode 文案 | 把 `example` / `my_data` 映射为“示例模式” / “我的资料”。 |
| 顶栏 JSX | 产品语境和模式切换 | 显示 JobPilot AI、工作台标题、workspace 状态、dataMode segmented toggle、provider 状态和模式说明。 |

### 6.3 对话区

| 组件/函数 | 职责 | 当前功能 |
| --- | --- | --- |
| `ConversationHeader` | 桌面对话区头部 | 展示当前进度、产物数量、安全状态和桌面快捷任务。移动端隐藏。 |
| `SuggestedPrompts` | 空状态任务入口 | 展示导入资料、解析 JD、面试准备、自由聊、运行示例路径；部分按钮填入 composer，`自由聊求职方向` 会自动发送。 |
| `CollapsibleText` | 长文本折叠 | 对长消息、长摘要进行折叠/展开。 |
| `ThinkingMessage` | 处理中状态 | 展示 Agent 正在规划、检查 workspace、准备调用本地工具、完成后推送到推进台。 |
| `ErrorRecovery` | 错误恢复 | 错误消息中展示“补充 JD”和“跑示例路径”恢复动作。 |
| `inferAssistantTone` | 消息 tone 推断 | 有 artifact 时标为 plan；包含失败/请输入等文本时标为 error；否则为 notice。 |
| composer JSX | 输入与上传 | 支持上传资料、textarea 输入、Enter 发送、按钮发送。 |
| `sendText` | 发送对话 | 调用 `/api/chat/message`，把用户消息和 assistant 响应写入 messages。 |
| `upload` | 上传资料 | 上传文件后切换到 `my_data`，并插入 document artifact 提示。 |

### 6.4 左侧桌面上下文面板

| 组件 | 职责 | 当前功能 |
| --- | --- | --- |
| `DesktopContextPanel` | 1200px+ 桌面的任务上下文和安全边界 | 展示当前任务标题、下一步、进度条、流程/产物指标、导入资料/粘贴 JD/示例路径按钮和默认本地/mock 安全说明。 |

该面板在 `max-width: 1024px` 下隐藏。

### 6.5 Workbench / 推进台

| 组件/函数 | 职责 | 当前功能 |
| --- | --- | --- |
| `Workbench` | 右侧产物推进台容器 | 展示 header、产物数量、关闭按钮、`WorkflowPanel` 和 `ResultRail`；移动端作为底部抽屉。 |
| `WorkflowPanel` | 当前求职流程总览 | 无结果时展示空状态和运行示例路径；有结果时展示 headline、完成步数、统计、导出文件、步骤列表和验收边界说明。 |
| `WorkflowArtifactCards` | workflow result 转 artifact cards | 从 `key_outputs` 中抽取 job、match_report、application_package、interview_prep。 |
| `workflowStats` | workflow 统计 | 计算流程、事实、导出、训练任务数量。 |
| `ResultRail` | artifact 列表渲染 | 合并聊天消息中的 artifacts 和 workflow artifacts，然后渲染 `ArtifactCard`。 |
| `ArtifactCard` | 产物卡 | 展示求职语义标题、摘要、highlight、待确认项、版本、来源详情、确认、导出、重新生成。 |
| `artifactSummary` | 产物摘要 | 按 artifact 类型生成用户可读摘要。 |
| `artifactHighlights` | 摘要指标 | 按 artifact 类型生成岗位、公司、技术栈、匹配、优势、缺口、简历标题等 highlight。 |
| `readableType` | 类型中文映射 | 把 `job`、`match_report`、`application_package` 等转换为求职语义名称。 |
| `guidanceForConfirmation` | 待确认项转求职辅导文案 | 对性能指标、上线链接等问题给出更像求职辅导的提示。 |

### 6.6 移动端控制

| 组件/样式 | 职责 | 当前功能 |
| --- | --- | --- |
| `drawerOpen` state | 控制移动 Workbench 抽屉 | 点击 FAB 打开，点击 overlay 或关闭按钮关闭。 |
| `.mobile-fab` | 移动端推进台入口 | 390px/768px 下固定在右下角，显示“查看推进台”和数量 badge。 |
| `.drawer-overlay` | 移动抽屉遮罩 | Workbench 打开时显示半透明遮罩。 |
| `.workbench-plane.is-open` | 移动抽屉展开 | 通过 transform 从底部滑出。 |

## 7. 当前用户可完成的功能

| 用户功能 | 当前入口 | 当前实现状态 |
| --- | --- | --- |
| 打开本地 Chatbox | Vite 页面 | 可初始化 workspace/session。 |
| 查看本地/模式/provider 状态 | 顶栏 | 可见，但 provider 文案仍较保守，未区分更多 provider 细节。 |
| 切换示例模式/我的资料 | 顶栏 segmented toggle | 前端状态切换；上传后自动进入我的资料。 |
| 空状态启动任务 | `SuggestedPrompts` | 可填入或自动发送提示词。 |
| 自由聊求职方向 | `自由聊求职方向` prompt 或手动输入 | 本地/mock 连续对话基线已支持；不代表完整 provider-backed 智能聊天。 |
| 发送多轮消息 | composer | 支持连续消息和历史恢复。 |
| 上传资料 | composer 上传按钮 | 调用上传 API，展示 document artifact 提示。 |
| 运行示例路径 | prompt、左侧面板、Workbench 空状态 | 调用 P2 demo workflow，生成 workflowResult 和 workflow artifacts。 |
| 查看执行中状态 | `ThinkingMessage` | busy 时展示计划步骤。 |
| 错误恢复 | `ErrorRecovery` | 错误气泡提供补充 JD 和跑示例路径。 |
| 查看产物推进台 | 右侧 Workbench / 移动 FAB | 展示 workflow、产物、导出、确认和版本。 |
| 确认待确认项 | `ArtifactCard` | 调用 confirm API 并更新前端状态。 |
| 查看来源与详情 | `details` | 展示 JSON 详情；仍偏工程化，是后续 UI 优化点。 |
| 重新生成产物 | `ArtifactCard` | 调用 regenerate API，刷新版本列表。 |
| 导出申请包 | `ArtifactCard` | 对 application_package 调用 export-package 并打开下载。 |

## 8. 样式与布局实现

`src/styles.css` 当前承担所有视觉和响应式规则。

### 8.1 Design tokens

定义在 `:root`：

- 背景：`--bg`, `--surface`, `--surface-subtle`, `--surface-workbench`
- 文本：`--text-main`, `--text-muted`, `--text-soft`
- 边框：`--border`, `--border-strong`
- 品牌/状态：`--primary`, `--accent`, `--success`, `--warning`, `--danger`
- 圆角和阴影：`--radius`, `--radius-sm`, `--shadow-sm`, `--shadow-md`, `--shadow-drawer`

### 8.2 主要布局 class

| Class | 用途 |
| --- | --- |
| `.app-shell` | 全屏应用外壳。 |
| `.topbar` | 顶部品牌、状态、模式和 provider 条。 |
| `.layout-grid` | 主三栏布局：左侧上下文、中间对话、右侧 Workbench。 |
| `.desktop-context-panel` | 左侧上下文和安全说明。 |
| `.conversation-plane` | 中间对话容器。 |
| `.timeline` / `.timeline-content` | 消息滚动区域。 |
| `.composer` / `.composer-inner` | 底部输入区和上传/发送按钮。 |
| `.workbench` / `.workbench-plane` | 右侧推进台和移动抽屉容器。 |
| `.artifact-card` | 产物卡。 |
| `.mobile-fab` / `.drawer-overlay` | 移动端 Workbench 入口和遮罩。 |

### 8.3 响应式规则

| Breakpoint | 当前行为 |
| --- | --- |
| `min-width: 1441px` | app-shell 放宽到 1760px；三栏变为 300px / 1fr / 440px。 |
| `min-width: 1800px` | app-shell 放宽到 1840px；三栏变为 320px / 1fr / 460px。 |
| `max-width: 1024px` | 左侧 `DesktopContextPanel` 隐藏；布局变为对话 + 340px Workbench。 |
| `max-width: 768px` | 顶栏纵向；只保留对话主列；Workbench 变为底部抽屉；显示 mobile FAB。 |

## 9. 当前实现与 PRD 的对齐情况

| PRD 模块 | 当前实现组件 | 对齐程度 | 说明 |
| --- | --- | --- | --- |
| Experience Shell | `App`, `.app-shell`, `.topbar` | 部分完成 | 已有本地 workspace、mode、provider 状态，但视觉和信息层级仍可优化。 |
| Empty State Suggested Prompts | `SuggestedPrompts` | 已实现 | 已并入 Chatbox 空状态，包含自由聊和示例路径。 |
| Conversation Plane | `ConversationHeader`, timeline, messages, composer | 已实现但可优化 | 有消息、loading、错误恢复、折叠；整体观感仍偏工程化。 |
| Composer and Upload Dock | composer JSX, `upload`, `sendText` | 已实现 | 支持文件上传、文本输入、Enter 发送。 |
| Free Local Dialogue | `sendText` + 后端 `/api/chat/message` | 本地/mock 基线完成 | 不等于真实 provider-backed 智能聊天。 |
| Desktop Workbench Controller | `.layout-grid`, `DesktopContextPanel`, media queries | 已实现但需审美和密度优化 | 覆盖大屏列宽，仍需 Gemini 优化视觉统一性。 |
| Workbench Plane / Mobile Drawer | `Workbench`, `.workbench-plane`, `.mobile-fab` | 已实现 | 桌面右栏、移动底部抽屉均存在。 |
| Artifact Review Cards | `ArtifactCard` | 已实现但仍偏工程化 | 摘要、确认、版本、导出都有；“来源与详情”仍暴露 JSON。 |
| Confirmation and Export | `confirm`, `exportPackage`, version row | 部分完成 | 支持确认和导出，但导出前 preflight 的可视化还可加强。 |
| Evidence and Review | 报告脚本与 docs/reports | 非前端源码职责 | 不应由 Gemini 虚构验收结论。 |

## 10. 当前已知问题和 Gemini 应重点修复点

| 问题 | 影响 | 建议方向 |
| --- | --- | --- |
| 组件全部堆在 `main.tsx` | Gemini 和开发者难以局部修改，容易误伤业务逻辑。 | 可以建议拆为 `api.ts`, `types.ts`, `components/Conversation`, `components/Workbench`, `components/ArtifactCard` 等，但需保持功能一致。 |
| 视觉系统不够统一 | 看起来像工程验收页面，不像成熟求职生产力工具。 | 统一 spacing、panel hierarchy、button priority、type scale、surface color。 |
| 桌面信息层级仍偏重 | 左侧、header、prompt、Workbench 都在抢主次。 | 明确主任务区、辅助状态区、产物区的视觉权重。 |
| Prompt / action 入口重复 | 左侧、对话 header、空状态、Workbench 空状态均有示例路径入口。 | 保留必要入口，但减少视觉噪音和重复文案。 |
| Artifact 详情仍暴露 JSON | 用户需要理解内部结构才能审查详情。 | 设计非 JSON 详情视图；JSON 仅作为高级展开项。 |
| Provider 文案较单一 | 即便 providerStatus 不同，也主要显示同一句安全文案。 | 在不越界的前提下展示“当前未外呼 / 外呼需确认 / mock 验收路径”。 |
| Career facts Workbench 可见性有局部不一致 | artifact 已在消息/后端 refs 中存在，但右侧可能未稳定呈现。 | 设计和实现中要保留局部失败/刷新不一致状态，而不是写成完整通过。 |
| 自由聊天仍是本地/mock 基线 | 用户可能误以为已接入真实智能 provider。 | UI 文案要明确“本地连续对话基线”；真实 provider 进入 P6 opt-in。 |

## 11. 如果要拆分，建议目标组件树

以下是建议拆分，不是当前事实。

```text
src/
  api/
    client.ts
    endpoints.ts
  types/
    chat.ts
    workflow.ts
    artifacts.ts
  components/
    AppShell.tsx
    Topbar.tsx
    DesktopContextPanel.tsx
    Conversation/
      ConversationHeader.tsx
      SuggestedPrompts.tsx
      MessageBubble.tsx
      ThinkingMessage.tsx
      ErrorRecovery.tsx
      Composer.tsx
    Workbench/
      Workbench.tsx
      WorkflowPanel.tsx
      ResultRail.tsx
      ArtifactCard.tsx
      ArtifactDetails.tsx
    primitives/
      StatusBadge.tsx
      CollapsibleText.tsx
  styles/
    tokens.css
    layout.css
    conversation.css
    workbench.css
    responsive.css
  main.tsx
```

拆分原则：

- 先保持 API 和状态行为不变，再做视觉重构。
- 不在前端生成求职内容，不直连 provider，不写数据库。
- Artifact 的 `source_refs`、`questions_to_confirm`、`current_version_id` 不能因美化而丢失。
- 移动端 Workbench 抽屉、桌面三栏和空状态 prompts 都必须保留。

## 12. 给 Gemini 的最小任务边界

如果只做一轮可落地优化，应优先要求 Gemini：

1. 保持现有 `src/main.tsx` API 行为不变。
2. 优化 `src/styles.css` 的视觉系统和响应式布局。
3. 在必要时小幅调整 JSX 结构，但不要引入未确认业务能力。
4. 输出完整 patch 或完整替换文件。
5. 自带桌面 1440/1920、720、390 和关键路径验收清单。
