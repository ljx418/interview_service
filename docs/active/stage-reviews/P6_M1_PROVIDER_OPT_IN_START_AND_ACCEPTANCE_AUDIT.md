# P6-M1 Provider Opt-in 启动与验收审计

日期：2026-06-29
阶段：P6-M1 Provider opt-in UX 与模型设置
状态：执行中；本文件记录本子阶段启动审计、实现边界和验收口径。

## 1. 本阶段目标

P6-M1 只解决 provider 默认安全和用户可理解状态：

- 用户能看到 mock/default、configured、consented、called、failed/fallback 等状态；
- 配置 provider 不等于调用 provider；
- 调用前 consent 必须显式确认；
- consent 只记录授权范围，不触发真实外呼；
- API Key 不进入前端持久化、报告或日志。

## 2. 本阶段不做

- 不实现 provider-backed 自由聊天；
- 不自动调用 MiniMax、DeepSeek 或 OpenAI-compatible provider；
- 不读取真实个人资料；
- 不执行 workspace 删除、迁移 apply、ASR、会议平台、自动投递或 SaaS 能力。

## 3. 实现边界

后端：

- 增加 provider preferences、provider consent 和增强 provider status；
- consent 使用当前后端进程内授权快照，包含 workspace、session、scope、ttl 和 allowed data classes；
- provider status 必须返回 configured、consented、called_in_session、called_in_workspace、configured_is_called 和 p6_state；
- preferences 只保存非敏感偏好；legacy runtime-config 保留当前能力但报告和状态必须脱敏。

前端：

- 模型设置弹窗显示配置、授权、调用是不同状态；
- 增加“授权本轮外呼”动作；
- 状态栏使用 P6 provider 状态展示；
- 普通聊天仍保持本地/mock 基线。

测试：

- 配置 provider 后 provider invocation 计数仍为 0；
- 未显式确认 consent 时只返回 consent_required；
- 显式确认 consent 后状态变为 consented，但 called_in_session 仍为 false；
- 不出现真实外呼。

## 4. 打回条件

出现任一情况，P6-M1 不得通过：

- 配置 provider 后自动外呼；
- configured 被写成 called；
- 未确认 consent 仍获得外呼授权；
- API Key 出现在截图说明、报告、日志或测试 fixture；
- 普通聊天被改成 provider-backed 路径。

## 5. 待验收结论

本阶段完成后只能声明：

```text
Provider opt-in 状态和调用前授权边界已落地；
配置 provider 不等于真实外呼；
provider-backed 自由聊天仍未实现，进入 P6-M2/P6-M3 后继续开发。
```

不得声明真实 provider 聊天质量、真实个人资料路径、P5-REAL 或 SaaS/Beta 出门通过。
