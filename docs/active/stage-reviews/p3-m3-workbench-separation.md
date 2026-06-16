# P3-M3 对话区与推进台分离开发、验收与审计记录

日期：2026-06-16  
阶段：P3-M3  
状态：已通过自动化验收

## 1. 本子阶段目标

P3-M3 目标是把当前“对话、workflow、结果摘要混在同一主列”的体验，整理成两个职责清楚的平面：

- 对话区：用户消息、系统响应、上传、快捷任务、错误和产物卡；
- 推进台：阶段进度、下一步、运行边界、结果摘要、确认项、版本和导出状态。

本阶段不新增复杂 Dashboard，不新增新的业务生成逻辑。

## 2. 验收标准

- 桌面宽度下，对话区和推进台在视觉上分栏；
- 移动宽度下，对话区优先，推进台在下方纵向展示；
- 对话区仍可发送 JD、生成申请包、显示错误和产物；
- 推进台不承载聊天输入；
- 前端仍只调用 API，不直接写 SQLite 或生成求职内容；
- source refs、questions_to_confirm、version 和导出入口不丢失。

## 3. 开发计划

1. 布局重构
   - `.workspace-grid` 改为 conversation / workbench 两列；
   - `WorkflowPanel` 与 `ResultRail` 合并到右侧 workbench；
   - 移动端顺序为对话区优先、推进台其次。

2. 文案与 ARIA
   - 对话区明确为 Conversation Area；
   - 推进台明确为 Workbench Area；
   - 避免继续使用“上方推进台”等过期文案。

3. 验收证据
   - 结构 eval；
   - 前端 build；
   - Chrome 截图覆盖 1280 / 720 / 390。

## 4. 启动前审计意见

未发现新增致命或重大规格偏差，可以进入 P3-M3 实质开发。

主要风险及控制：

| 风险 | 判断 | 控制 |
| --- | --- | --- |
| 变成复杂 Dashboard | 中风险 | 只重排已有模块，不新增页面 |
| 对话区产物卡丢失 | 中风险 | 保留 message artifact card 渲染 |
| 移动端顺序反直觉 | 中风险 | 移动端保持 Chatbox 优先 |

## 5. 完成后验收记录

### 5.1 实现摘要

- `workspace-grid` 重构为 conversation / workbench 两列；
- `WorkflowPanel` 与 `ResultRail` 移入右侧 `workbench`；
- `conversation-area` 只保留 Chatbox 对话、消息、上传、快捷任务和输入；
- 移动宽度下保持对话区优先，推进台和运行边界在下方纵向展示；
- 清理“上方推进台”等旧文案。

### 5.2 测试命令和结果

```bash
python3 -m pytest tests/evals/test_p3_chatbox_response_eval.py tests/evals/test_p3_mode_boundary_eval.py tests/evals/test_p3_artifact_workbench_eval.py tests/evals/test_p2_guided_demo_flow_eval.py
```

结果：8 passed。

```bash
npm --prefix apps/chatbox run build
```

结果：通过，Vite build 成功。

```bash
python3 -m pytest
```

结果：59 passed。

### 5.3 截图证据

重新采集：

```bash
node scripts/capture_p3_chatbox_evidence.mjs
```

截图路径：

```text
docs/reports/evidence/p3_chatbox_initial_1280.png
docs/reports/evidence/p3_chatbox_error_state_1280.png
docs/reports/evidence/p3_chatbox_response_1280.png
docs/reports/evidence/p3_chatbox_narrow_720.png
docs/reports/evidence/p3_chatbox_mobile_390.png
```

抽查结论：

- 1280px：左侧为对话区，右侧为推进台和运行边界；
- 390px：先显示对话区，再显示推进台和运行边界；
- 产物卡仍在对话消息中可见，未丢失确认、版本和操作按钮。

### 5.4 PRD 规格检视

| 检视项 | 结果 |
| --- | --- |
| 对话区负责输入和消息 | 通过 |
| 推进台负责阶段、结果、运行边界和导出摘要 | 通过 |
| 移动端对话优先 | 通过 |
| 前端是否新增业务生成逻辑 | 未发现 |
| source refs / questions / version 是否丢失 | 未发现，artifact card 保留 |

### 5.5 打回判断

未发现需要打回开发计划阶段的问题。

剩余风险：

- P3-M4 仍需继续做响应式细节验收和截图报告整理；
- P3-M5 需要把截图、架构、实现和未验证范围整理为 HTML 验收报告。
