# P3-M4 响应式 UX 与可访问性冒烟验收记录

日期：2026-06-16  
阶段：P3-M4  
状态：已通过自动化验收

## 1. 本子阶段目标

P3-M4 目标是验证 Chatbox 工作台在桌面、窄屏和移动宽度下都可阅读、可操作，不再出现严重横向滚动、控件遮挡、板块截断或输入区不可见。

截图是可见体验证据，不替代后端 eval、业务测试或 PRD 规格检视。

## 2. 验收标准

- 1280px：对话区和推进台双栏可读；
- 720px：布局降为单栏，模块顺序清楚；
- 390px：对话区优先，输入区可见，快捷任务换行，产物卡不严重横向裁切；
- 上传、发送、一键体验、模式切换按钮可见；
- 不出现明显横向页面溢出；
- `python3 -m pytest` 和 `npm --prefix apps/chatbox run build` 通过。

## 3. 证据路径

```text
docs/reports/evidence/p3_chatbox_initial_1280.png
docs/reports/evidence/p3_chatbox_response_1280.png
docs/reports/evidence/p3_chatbox_error_state_1280.png
docs/reports/evidence/p3_chatbox_narrow_720.png
docs/reports/evidence/p3_chatbox_mobile_390.png
```

## 4. 启动前审计意见

未发现新增致命或重大规格偏差，可以进入 P3-M4 验收固化。

主要风险及控制：

| 风险 | 判断 | 控制 |
| --- | --- | --- |
| 用截图替代业务测试 | 中风险 | 必须同时跑 pytest 和 build |
| 移动端内部滚动截断被忽略 | 中风险 | 抽查 390px 截图，补 PNG 尺寸 eval |
| 把 headless 截图说成人工体验通过 | 中风险 | 报告只写自动化可见截图通过 |

## 5. 完成后验收记录

### 5.1 实现与证据摘要

- 已修复 390px 下 artifact toolbar / version 区域横向裁切；
- 已将桌面布局调整为对话区 / 推进台双栏；
- 移动端顺序为对话区、推进台、运行边界；
- 已使用 Chrome CDP 重新采集 1280px、720px、390px 截图；
- 已增加 PNG 尺寸和文件有效性 eval。

### 5.2 测试命令和结果

```bash
python3 -m pytest tests/evals/test_p3_chatbox_response_eval.py tests/evals/test_p3_mode_boundary_eval.py tests/evals/test_p3_artifact_workbench_eval.py tests/evals/test_p3_responsive_evidence_eval.py tests/evals/test_p2_guided_demo_flow_eval.py
```

结果：9 passed。

```bash
npm --prefix apps/chatbox run build
```

结果：通过，Vite build 成功。

```bash
python3 -m pytest
```

结果：60 passed。

### 5.3 截图证据

```text
docs/reports/evidence/p3_chatbox_initial_1280.png
docs/reports/evidence/p3_chatbox_response_1280.png
docs/reports/evidence/p3_chatbox_error_state_1280.png
docs/reports/evidence/p3_chatbox_narrow_720.png
docs/reports/evidence/p3_chatbox_mobile_390.png
```

`tests/evals/test_p3_responsive_evidence_eval.py` 验证截图存在、PNG 格式有效、宽度分别为 1280 / 720 / 390，且文件大小不是空白截图。

### 5.4 PRD 规格检视

| 检视项 | 结果 |
| --- | --- |
| 1280px 双栏可读 | 通过 |
| 720px 单栏可读 | 通过 |
| 390px 输入区可见 | 通过 |
| 快捷任务和模式切换可见 | 通过 |
| 是否存在明显横向页面溢出 | 未发现严重问题 |
| 是否用截图替代业务测试 | 未替代，已跑全量 pytest 和 build |

### 5.5 打回判断

未发现需要打回开发计划阶段的问题。

剩余风险：

- 截图为自动化 Chrome 截图，不等于人工主观体验完全通过；
- P3-M5 需要制作 HTML 报告，把截图证据、目标架构、当前实现和未验证范围清楚呈现给人工审查。
