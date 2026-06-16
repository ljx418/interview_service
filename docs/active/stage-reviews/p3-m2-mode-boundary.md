# P3-M2 示例模式 / 我的资料模式边界开发、验收与审计记录

日期：2026-06-16  
阶段：P3-M2  
状态：已通过自动化验收

## 1. 本子阶段目标

P3-M2 目标是让用户和验收者清楚区分：

- 示例模式：使用仓库 `examples/` 中的真实感匿名数据，允许一键跑完整体验；
- 我的资料模式：只处理用户上传或输入的内容，不默认加载 examples，不默认触发外部 provider。

本阶段不承诺真实个人资料自动验收，也不默认调用 MiniMax 或其他 external provider。

## 2. 验收标准

- UI 明确显示当前模式；
- 一键体验请求必须携带 `data_mode=example`；
- 后端 workflow 对 `data_mode=my_data` 拒绝运行 examples demo；
- provider 状态可以显示 external configured，但不得被描述为已自动调用；
- P3 截图和报告只能把 examples 称为“真实感示例数据”，不能写成真实个人资料验收。

## 3. 开发计划

1. 后端 workflow mode 边界
   - `P2DemoWorkflowRequest` 增加 `data_mode`；
   - `run_p2_demo_flow` 只接受 `example`；
   - 返回结果包含 `data_mode`、`data_source` 和 provider 状态口径。

2. 前端模式说明
   - 对话区显示示例模式 / 我的资料模式说明；
   - 一键体验固定发送 `data_mode=example`；
   - 我的资料模式下继续允许聊天输入和上传，但不触发 examples demo。

3. 验收证据
   - P3-M2 eval 覆盖 example / my_data mode；
   - Chrome 截图复用 P3-M1 evidence，后续 P3-M5 汇总 HTML 报告。

## 4. 启动前审计意见

未发现新增致命或重大规格偏差，可以进入 P3-M2 实质开发。

主要风险及控制：

| 风险 | 判断 | 控制 |
| --- | --- | --- |
| examples 结果被误报为真实资料验收 | 重大虚假验收风险 | workflow 返回 `data_mode=example`，报告明确标注 |
| provider 已配置被误读为已调用 | 中风险 | UI 文案区分 configured 和 enabled/called |
| 真实资料模式偷跑 examples | 中风险 | 后端对 `my_data` demo workflow 直接拒绝 |

## 5. 完成后验收记录

### 5.1 实现摘要

- `P2DemoWorkflowRequest` 增加 `data_mode`；
- `run_p2_demo_flow` 只接受 `data_mode=example`，对 `my_data` 直接拒绝；
- workflow 返回 `data_mode=example` 和 `data_source=repository_examples`；
- Chatbox 一键体验固定发送 `data_mode: "example"`；
- Chatbox 模式控件下显示当前模式说明：
  - 示例模式：只使用仓库 examples 数据；
  - 我的资料模式：只处理上传或输入内容，外部 provider 不默认调用。

### 5.2 测试命令和结果

```bash
python3 -m pytest tests/evals/test_p3_chatbox_response_eval.py tests/evals/test_p3_mode_boundary_eval.py tests/evals/test_p2_guided_demo_flow_eval.py
```

结果：6 passed。

```bash
npm --prefix apps/chatbox run build
```

结果：通过，Vite build 成功。

```bash
python3 -m pytest
```

结果：57 passed。

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

初始态截图可见“示例模式只使用仓库 examples 数据，适合快速验收产品路径。”运行边界区也标注外部 provider 只在明确配置和确认后调用。

### 5.4 PRD 规格检视

| 检视项 | 结果 |
| --- | --- |
| 示例模式可继续跑 examples 完整路径 | 通过 |
| 我的资料模式不会运行 examples demo | 通过，后端直接拒绝 |
| provider configured 与真实调用是否区分 | 通过，UI 和测试均不声称已调用 |
| 是否把 examples 写成真实个人资料验收 | 未发现 |
| 是否默认触发 MiniMax 或 external provider | 未触发 |

### 5.5 打回判断

未发现需要打回开发计划阶段的问题。

剩余风险：

- P3-M3 仍需把推进台从“演示流程面板”进一步重构为产物和阶段管理区；
- P3-M5 HTML 报告必须继续明确 examples 与真实个人资料验收的区别。
