# P9-M1 至 P9-M8 自动化开发审计

日期：2026-07-03

结论：P9-M1 至 P9-M8 自动化候选已完成第一轮实现。实现范围保持在 Chatbox-first UI 信息架构重构、求职情报可视化层和现有能力重新组织内；未新增真实平台接入、真实 ASR、真实 provider 默认外呼、自动投递或长期任务系统。

## 1. 子阶段实现记录

| 子阶段 | 实现内容 | 验收结论 |
| --- | --- | --- |
| P9-M1 | 中央 Chatbox 仍是首屏主路径；左侧改为求职态势，右侧改为产物台总览 | 通过 build；待 P9-M9 多视口截图复验 |
| P9-M2 | 顶部服务中心展示 LLM Provider、JD 信息源、ASR、MCP/Skill、Workspace 状态 | 通过；未配置能力不会显示为已连通 |
| P9-M3 | 左侧新增市场地图、机会匹配、投递流程三页签；地图支持缩放、拖动、重置和图钉选择 | 通过；数据来源标注为本地/fixture |
| P9-M4 | Chatbox 可发起 JD/城市/薪资汇总，生成本地 search run 状态 | 通过；只使用用户粘贴、已导入 JD、repo fixture 的表达 |
| P9-M5 | Chatbox 可引导项目故事、能力证据和简历模板补全；ASR 仅作为 opt-in 状态展示 | 通过；未采集麦克风、未调用语音服务 |
| P9-M6 | Chatbox 可触发现有 JD 定制简历生成，并同步故事包草稿到产物台 | 通过；复用现有 `/api/resume/generate` |
| P9-M7 | Chatbox 可更新本地投递流程状态，并同步左侧流程态势 | 通过；仅本地状态，不对外发送 |
| P9-M8 | 补充 1920/1440/1200/720/390 响应式样式，移动端保持 Chatbox 默认主视图 | build 通过；待截图报告确认视觉质量 |

## 2. PRD 规格检视

- Chatbox 是唯一主入口：通过。招聘汇总、资料补全、申请包生成和流程更新均可从输入框发起。
- 左侧求职态势：通过。包含岗位市场、目标机会与匹配、投递流程三大板块。
- 顶部服务状态：通过。展示 provider、JD 信息源、ASR、MCP/Skill、workspace 和安全边界。
- 右侧产物台：通过。展示 search run、故事草稿、流程摘要、岗位、简历和画像。
- 高风险边界：通过。实现未登录招聘平台、未联网抓取、未默认 provider 外呼、未采集 ASR。

## 3. 已运行验收

```bash
npm --prefix apps/chatbox run build
```

结果：通过。

## 4. 剩余复验

P9-M9 需要继续执行：

- `python3 -m pytest`
- `npm --prefix apps/chatbox run build`
- drawio XML parse
- Headless browser 多视口截图
- 中文 HTML 自动化验收报告

## 5. 打回风险

若 P9-M9 截图发现中央 Chatbox 在任一核心视口被左侧态势或右侧产物台压缩到不可用，必须打回 P9-M1/P9-M8。若报告把本地 search run 写成真实全网 JD 搜索或招聘平台接入通过，必须打回 P9-M4/P9-M9。
