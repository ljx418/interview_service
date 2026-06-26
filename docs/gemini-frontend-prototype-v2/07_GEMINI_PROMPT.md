# 面向 Gemini 的原型生成提示词

```text
你是资深产品设计负责人、UX 架构师和前端设计工程师。请基于我提供的 docs/gemini-frontend-prototype-v2/ 文件夹，为 JobPilot AI 重新设计一个更好看的、可交互的前端网页原型。

请先阅读：
- 00_README.md
- 01_CONTEXT_AND_SCOPE.md
- 02_TARGET_ARCHITECTURE_AND_CURRENT_IMPLEMENTATION.md
- 03_USER_FLOWS_AND_ACCEPTANCE_GATES.md
- 04_VISUAL_SYSTEM_AND_COMPONENT_SPEC.md
- 05_EVIDENCE_CONTACT_SHEET.html
- prototype.html
- prototype.css
- prototype.js

项目背景：
JobPilot AI 面向转行程序员，默认入口是 Chatbox，核心目标是把简历、项目 README、JD 和面试 transcript 组织成可信、可确认、可导出的求职材料。当前后端和本地/mock 自动化路径已能跑通，但前端体验仍像工程验收控制台，视觉较丑，信息层级、产物卡语言、Workbench 刷新一致性和移动端体验需要明显改进。

你的任务：
1. 重新设计 prototype.html、prototype.css、prototype.js，生成一个可直接打开的单页交互原型。
2. 第一屏必须是实际可用的求职材料工作台，不要做 landing page，不要做营销 hero。
3. 桌面端应像完整工作台：左侧上下文/下一步，中间 Chatbox，对话和任务入口，右侧 Workbench/产物推进台。
4. 移动端 390px 下必须优先保留 Chatbox 输入和消息流，Workbench 收为底部抽屉或次级入口。
5. 任务入口必须并入 Chatbox empty state / suggested prompts，不要做割裂的任务卡区域。
6. Suggested prompt 点击后必须填入 composer 或触发对应原型状态。
7. provider 状态必须使用用户语言，例如“外部模型未调用（隐私安全）”，不要使用工程表达。
8. 对话必须包含 loading / thinking / executing 状态，说明系统正在读取资料、对比 JD、生成草稿。
9. 错误状态必须包含恢复动作，例如补充资料、粘贴 JD、运行示例路径。
10. 产物卡必须用求职语义表达，例如“职业事实”“岗位解析”“匹配报告”“申请包草稿”“面试故事卡”，不要把裸 JSON 或内部 id 作为主视觉。
11. 待确认项必须像求职辅导建议，而不是程序校验错误。
12. 按钮必须有清晰主次：主要动作只给最重要的下一步，secondary action 不要抢主按钮权重。
13. 必须展示并修复当前发现的问题：显式生成职业事实后，Workbench 计数为 1，但主体仍显示空状态。新原型应展示一致的产物卡和空状态消失逻辑。
14. 原型必须覆盖这些状态切换：空状态、两轮自由对话 0 产物、状态查询、处理中、示例路径完成 9/9 步、显式生成职业事实 1 个 artifact、错误恢复、移动端 Workbench 抽屉。
15. 请给出至少 3 个设计方向，可以通过 Tweaks 面板切换：稳健工具型、求职教练型、文档审查型。
16. 请使用现代 CSS Grid/Flexbox、CSS variables、清晰 typography scale、稳定 spacing scale。
17. 不要使用紫蓝粉渐变、装饰性 orb、过度 bokeh、营销式大 hero、伪造客户 logo、伪造指标、emoji 装饰。
18. 不要使用 scrollIntoView。
19. 不要外呼任何 API，不要读取真实文件，不要声明真实 provider 或真实个人资料验收通过。
20. 原型是设计方案，不是已实现产品，请在页面角落或说明区明确这一点。

硬约束：
- 只生成 prototype.html、prototype.css、prototype.js。
- 单页可点击原型，不需要构建工具。
- 不调用 API，不读取真实文件，不写数据库。
- 不使用 scrollIntoView。
- 不要把 JSON 或内部 id 作为产物主视觉。
- 不要让所有按钮同等权重。
- 不要把本地/mock 原型说成真实 provider 或真实资料验收。

请输出：
- 修改后的 prototype.html
- 修改后的 prototype.css
- 修改后的 prototype.js
- 简短说明：你选择的设计方向、核心交互改动、仍需产品确认的问题

评估标准：
- 一个转行程序员不读开发文档，5 秒内知道第一步。
- 能清楚区分示例模式、我的资料模式、本地处理、外部 provider 未调用。
- 能在对话区完成资料/JD/申请包相关任务。
- 能在 Workbench 理解当前阶段、产物、待确认项、版本和导出。
- 1200/1440/1600/1920 桌面、720 窄屏、390 移动端均能顺手使用。
- 不做虚假验收，不扩展 P4 范围。
```
