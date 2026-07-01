# P8-JD Intake 与简历生成体验强化文档开发审计

日期：2026-07-01

状态：文档开发阶段通过；不得进入代码实现结论。

## 1. 审计目标

本轮审计回应用户反馈：

```text
当前交互仍然不好；
希望能主动接入 BOSS 或其他应聘平台寻找 JD；
需要增强面向用户的简历生成；
当前上传资料按钮太难理解，用户不知道需要提供什么资料。
```

本轮只允许文档开发，不允许修改前端、后端、数据库、测试或报告生成脚本。

## 2. 产品决策

采用低风险第一版路线：

```text
资料准备向导
→ JD 手动导入中心
→ 岗位列表和当前目标岗位
→ JD 定制简历
→ 中文 HTML 自动化验收报告
```

暂不采用以下路线：

- BOSS/招聘平台账号登录；
- 绕反爬、验证码或平台风控；
- 自动抓取岗位列表；
- 自动开聊、自动沟通、自动投递；
- 默认调用真实 provider 生成简历；
- 扫描用户个人目录寻找简历或资料。

理由：当前项目是本地优先求职 Agent，且现有高风险边界明确要求真实外部 provider、真实资料、自动投递和平台集成必须单独确认。直接接入 BOSS 或执行浏览器自动化会引入账号、合规、隐私、风控和虚假验收风险。

## 3. 文档变更范围

本轮文档开发应覆盖：

- `docs/active/00_README.md`
- `docs/active/01_STAGE_PRD.md`
- `docs/active/02_TARGET_ARCHITECTURE.md`
- `docs/active/03_MILESTONES_AND_DELIVERY_PLAN.md`
- `docs/active/04_ACCEPTANCE_GATES.md`
- `docs/active/06_TRACEABILITY_MATRIX.md`
- `docs/active/17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md`
- `docs/active/21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.md`
- `docs/active/jobpilot-stage-gap-and-acceptance.drawio`
- `TODO.md`

## 4. 规格完整性结论

当前文档应能完整指导后续 P8 自动化开发，前提是实现阶段继续遵守以下约束：

- 资料输入必须拆成简历、项目经历、作品链接、目标 JD、求职偏好五类；
- 每类资料必须有用途、示例、可跳过条件和缺失影响；
- JD 第一版只允许用户粘贴文本并保存来源链接；
- `source_url` 不触发网页抓取；
- 多个 JD 必须能形成岗位列表并选择当前目标岗位；
- JD 定制简历必须包含 source refs 和 pending confirmations；
- 缺证据内容不能写成事实；
- 平台自动接入、自动投递、真实 provider 和真实资料路径均保持未验证。

## 5. 开发准入意见

文档完成后，可以进入后续 P8 自动化开发准备，但必须先完成 P8 子阶段启动审计。建议实施顺序：

1. P8-M1：资料准备向导；
2. P8-M2：JD 手动导入中心；
3. P8-M3：多 JD 列表和当前目标岗位；
4. P8-M4：JD 定制简历；
5. P8-M5：可视化验收报告。

每个子阶段完成后必须执行：

- 后端/API eval；
- 前端 build；
- 浏览器截图验收；
- PRD 规格检视；
- HTML 验收报告或阶段审计更新。

## 6. 打回条件

出现以下任一情况必须打回文档或开发计划：

- 文档或实现把 BOSS/招聘平台接入列为当前能力；
- 文档或实现触发平台登录、绕风控、自动抓取、自动沟通或自动投递；
- 仅保存来源的 JD URL 被用于联网读取网页；
- 简历草稿缺少 source refs；
- 生成内容编造学历、工作年限、项目贡献、量化结果或公司经历；
- 普通聊天静默覆盖 `resume_version`；
- 报告把真实 provider、真实个人资料、自动投递、SaaS、ASR 或会议平台列为验收结论。

## 7. 审计结论

P8-JD Intake 文档方向合理，优先解决用户资料输入和 JD 输入的真实体验断点。第一版不应主动接入 BOSS 平台账号或自动抓取岗位，而应提供合规、安全、可验收的手动 JD 导入和定制简历闭环。当前文档开发可以收口；后续代码开发仍需按子阶段重新制定启动审计、验收计划和截图证据要求。
