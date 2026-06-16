# P3-M1 Chatbox 对话响应闭环开发、验收与审计记录

日期：2026-06-16  
阶段：P3-M1  
状态：已通过自动化验收

## 1. 本子阶段目标

P3-M1 只解决一个核心问题：用户在 Chatbox 中输入任务、上传资料或触发错误时，必须看到明确、可理解、可恢复的响应。

本阶段不扩大产品范围，不引入 MCP、CLI、ASR、会议平台、自动海投、SaaS 登录或默认真实外部 provider 调用。

## 2. PRD 对齐口径

对应 P3 PRD 的体验路径：

```text
打开本地 Chatbox
→ 看到 workspace、provider、示例/真实资料模式
→ 在聊天区选择上传资料、粘贴 JD 或输入任务
→ Chatbox 返回可理解响应、计划、错误或下一步
→ 推进台显示阶段、产物、确认项、版本和导出
```

P3-M1 的验收重点是第三步和第四步：Chatbox 必须“有反应”，并且失败也要给出原因和下一步。

## 3. 开发计划

1. 前端 Chatbox 输入闭环
   - 空输入不再静默返回；
   - session / workspace 初始化中必须显示可见提示；
   - 后端错误显示 error code、message 和 suggested action；
   - 有效任务返回 assistant message 和 artifact card；
   - 增加常用任务入口，降低用户不知道如何开始的风险。

2. 模式边界的轻量呈现
   - 显示“示例模式 / 我的资料”；
   - 上传文件后切换为“我的资料”；
   - 一键体验明确为示例数据路径；
   - 不默认触发真实外部 provider。

3. 后端 ChatCore 会话完整性
   - 缺少 JD 时的申请包/面试准备提示写入 chat message；
   - 空输入返回可理解提示；
   - 不生成伪产物。

4. 验收证据
   - 新增 P3-M1 eval；
   - 运行相关回归；
   - 前端 build 通过；
   - Chrome 截图覆盖初始态、有效响应态和错误/缺资料态。

## 4. 验收标准

- 有效 JD 输入后，Chatbox 展示“已解析岗位”类响应，并出现 `job` / `match_report` 产物；
- 在没有 JD 的情况下输入“生成申请包”，Chatbox 显示“请先粘贴一个 JD”类恢复建议；
- 空输入、会话初始化、后端错误均有可见反馈；
- 示例模式和我的资料模式在 UI 上可区分；
- Chatbox 前端不生成求职内容，不直连 provider，不写 SQLite；
- P0/P1/P2 关键路径不退化。

## 5. 启动前审计意见

未发现新增致命或重大规格偏差，可以进入 P3-M1 实质开发。

主要风险及控制：

| 风险 | 判断 | 控制 |
| --- | --- | --- |
| 把 P3-M1 扩成复杂 Dashboard | 非阻塞风险 | 只增加对话反馈和任务入口，不新增复杂页面 |
| 把示例数据误说成真实个人资料验收 | 重大虚假验收风险 | 报告中明确 examples 真实感数据与真实个人资料区别 |
| 默认触发真实外部 provider | 高风险 | 本阶段保持 mock 默认，真实外部调用仍需人工确认 |
| 只截图不测试 | 中风险 | 必须运行 eval 和前端 build |

## 6. 完成后验收记录

### 6.1 实现摘要

- Chatbox 空输入、workspace/session 初始化中和后端错误不再静默失败；
- API 错误会展示 `error_code`、message 和 suggested action；
- 对话区增加示例模式 / 我的资料模式状态和常用任务按钮；
- 上传资料后切换为“我的资料”，一键体验明确为示例数据路径；
- ChatCore 能识别真实感 JD 文本结构，不再只依赖 `JD` / `岗位` 关键词；
- 缺少 JD 时的“生成申请包 / 准备面试”提示会写入 chat session；
- 390px 移动宽度下修复 artifact toolbar/version 区域横向裁切。

### 6.2 测试命令和结果

```bash
python3 -m pytest tests/evals/test_p3_chatbox_response_eval.py tests/evals/test_p2_guided_demo_flow_eval.py
```

结果：3 passed。

```bash
npm --prefix apps/chatbox run build
```

结果：通过，Vite build 成功。

```bash
python3 -m pytest
```

结果：54 passed。

### 6.3 截图证据

真实 Chrome CDP 截图脚本：

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

截图含义：

- 初始态：显示 workspace、provider、示例模式、对话区、推进台和运行边界；
- 缺资料态：在没有 JD 时输入“生成申请包”，Chatbox 明确提示“请先粘贴一个 JD”；
- 有效响应态：输入真实感 Junior Frontend JD 后，Chatbox 返回岗位解析和匹配报告产物；
- 窄屏 / 移动：对话区、快捷任务、推进台和运行边界可纵向阅读，没有严重横向截断。

### 6.4 PRD 规格检视

| 检视项 | 结果 |
| --- | --- |
| 用户能从 Chatbox 输入任务并看到响应 | 通过 |
| 用户缺前置资料时能看到失败原因和下一步 | 通过 |
| Chatbox 与推进台职责更清楚 | 基本通过，P3-M3 继续强化 |
| 示例模式和我的资料模式可见 | 基本通过，P3-M2 继续补完整模式工作流 |
| 前端是否生成求职内容 | 未发现，前端仍调用后端 API |
| 是否默认触发真实外部 provider | 未触发；截图只显示 provider 已配置状态 |
| 是否存在虚假验收风险 | 已标注截图使用临时 workspace 和真实感 JD，不代表真实个人资料自动验收 |

### 6.5 打回判断

未发现需要打回开发计划阶段的问题。

剩余风险：

- P3-M2 仍需把“示例模式 / 我的资料模式”做成更完整的工作流边界；
- P3-M3 仍需进一步强化推进台与产物区的信息组织；
- P3-M5 需要汇总 HTML 验收报告，当前只是阶段截图证据。
