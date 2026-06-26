# JobPilot AI P5 真实资料本地闭环架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。P4 已作为本地/mock Chatbox 体验冻结基线保留；本轮图示主线是 P5 真实资料本地闭环。

P5 不把真实外部 provider、SaaS、ASR、会议平台、自动投递、MCP Server 或 CLI 放入出门条件。任何真实个人资料、真实外部调用、API Key、workspace 删除或不可逆迁移都必须先获得用户确认。

## 图示页结构

P5 drawio 保持 6 页，不超过 8 页：

1. P5 目标体验与当前差距；
2. 当前架构与 P5 目标架构；
3. 代码实体、分层结构与交互关系；
4. P5 开发及验收计划；
5. P5 项目里程碑、验收门槛与出门条件；
6. 安全边界、状态标记、证据和后续阶段。

颜色含义：

- 绿色：已实现并冻结，包括 P0/P1/P2/P3/P4 本地/mock 基线；
- 黄色：P5 本阶段自动化候选已通过、但仍待真实资料或人工体验冻结的能力；
- 橙色：P5 中需要人工确认的高敏流程，例如真实资料授权、报告脱敏、导出确认、不可逆操作；
- 灰色：P6/P7/P8+ 后续开发能力；
- 红色：禁止路径、打回条件或必须审批的风险项；
- 蓝色：用户动作、验收数据、截图证据或说明性节点。

## 第 1 页 - P5 目标体验与当前差距

目标体验主链路：

```text
User
→ 本地 Chatbox
→ 上传/粘贴真实资料
→ 粘贴/导入目标 JD
→ 资料解析 + JD 解析
→ questions_to_confirm 事实确认
→ 申请包生成
→ 编辑 / 重新生成
→ 导出 Markdown/DOCX
→ 围绕当前资料和 JD 多轮追问
```

当前差距：

- P4 已完成示例路径和本地/mock Chatbox 体验冻结，P5 本地/mock + 脱敏 fixture 自动化候选已通过；
- 当前仍缺少用户明确授权的真实资料路径、允许展示字段、人工体验记录和 final closure audit；
- 本地连续对话已扩展到当前资料/JD/申请包上下文，但不代表 provider-backed 自由智能聊天；
- provider opt-in 基础存在，但 P5 默认不得外呼真实 provider；
- 报告必须脱敏，不能把真实个人资料或 API Key 写入证据。

## 第 2 页 - 当前架构与 P5 目标架构

当前已实现基线：

```text
React Chatbox
→ FastAPI Agent Service
→ ChatCore / PiAgent Adapter
→ Domain Tools
→ Artifact Versioning
→ Export Service
→ SQLite Workspace
→ P4 Evidence
```

P5 目标新增或改造的当前状态：

```text
Real Data Intake Controller（脱敏 fixture 自动化候选通过，真实资料待复核）
→ JD Intake and Gap Recovery（自动化候选通过，真实 JD 片段待复核）
→ Fact Confirmation Loop（blocking/warning/optional 自动化通过，人工文案待复核）
→ Application Package Edit/Regenerate Loop（核心链路通过，版本 UI 待人工复核）
→ Export Preflight（自动化硬门槛通过，真实资料导出待脱敏复核）
→ Local Context Snapshot（本地多轮追问通过，不代表 provider-backed 聊天）
→ P5 Redacted Evidence（P5 HTML 报告已生成，final closure audit 待补）
```

架构关系：

- Chatbox 只做输入、展示、确认、编辑和导出触发；
- FastAPI 负责请求边界、错误语义和 API 编排；
- ChatCore 负责意图区分和上下文摘要；
- Domain Tools 负责资料解析、JD 解析、匹配和申请包生成；
- Artifact/Export/Storage 负责版本、确认项、导出和本地持久化；
- Provider Policy Gate 负责保持 P5 默认不外呼。

## 第 3 页 - 代码实体、分层结构与交互关系

必须在图中出现的具体代码实体：

- `apps/chatbox/src/main.tsx`：Experience Shell、Conversation Plane、Workbench、Artifact/Export UI；P5 自动化候选通过，待人工体验冻结；
- `apps/chatbox/src/styles.css`：多视口布局、按钮对齐、文本溢出和移动端可达性；P5 多视口截图已覆盖 1200/1440/1600/1920/720/390；
- `services/api/main.py`：workspace、upload、chat、workflow、artifact、export API 边界；P5 本地/mock 候选通过，真实资料路径待复核；
- `services/chat/core.py`：自由追问、状态查询、资料导入、JD 解析、生成/导出意图区分；普通追问不写 artifact 已自动化覆盖；
- `services/workflows/p2_demo.py` 和 P5 本地闭环路径：从 examples flow 扩展到真实资料本地 flow；不得伪造真实资料通过；
- `services/tools/`：Profile、Project、Job、Match、Application、Interview 等 Domain Tools；脱敏 fixture 通过，真实资料质量待复核；
- Artifact/version/export/storage 相关服务：source refs、`questions_to_confirm`、版本和导出 preflight；blocking 导出门槛已自动化覆盖；
- Provider runtime/policy：mock 默认，external provider 需 P6 opt-in；
- `docs/reports/` 与截图脚本：P5 脱敏自动化验收证据。

P5 默认复用现有接口：

- workspace：`POST /api/workspace/init`、`GET /api/workspace/status`；
- file intake：`POST /api/files/upload`、`POST /api/files/ingest-local`；
- profile/project：`POST /api/profile/extract-facts`、`POST /api/project/create-card`；
- job/match：`POST /api/job/parse-jd`、`POST /api/job/match-profile`；
- application/export：`POST /api/application/create-package`、`POST /api/application/export-package`；
- artifact：confirm、update、versions、restore、regenerate；
- chat：chat sessions、`POST /api/chat/message`；
- provider policy：P5 默认 mock/local，external provider 需 P6 opt-in。

依赖方向：

```text
Chatbox UI
→ FastAPI Routes
→ ChatCore / Workflow Controller
→ Domain Tools
→ Artifact / Export / Storage
→ Evidence
```

禁止关系：

- Chatbox 直接调用 provider；
- Chatbox 直接写 SQLite；
- Provider raw output 未校验即写入 artifact；
- Export Service 绕过 blocking confirmation；
- Evidence 报告写入完整真实资料或 API Key。

## 第 4 页 - P5 开发及验收计划

执行顺序：

```text
P5-M0 文档 / drawio / 风险边界锁定
→ P5-M1 真实资料本地导入与解析 UX（自动化候选通过）
→ P5-M2 JD 导入、解析和缺失信息恢复（自动化候选通过）
→ P5-M3 事实确认与 questions_to_confirm 闭环（自动化候选通过）
→ P5-M4 申请包生成、编辑、再生成和导出 preflight（自动化候选通过）
→ P5-FC 围绕资料/JD/申请包的本地多轮追问（自动化候选通过）
→ P5-M5 脱敏自动化验收报告、截图证据和 PRD 规格检视（自动化候选通过）
→ P5-REAL 真实授权资料脱敏复核（待用户提供路径）
→ P5-Freeze 回归复验、人工体验记录、final closure audit 和阶段冻结（未完成）
```

当前最新候选证据为 P5 HTML 报告、多视口真实截图、`.venv/bin/python -m pytest` 88 passed, 1 warning、前端 build 通过、drawio parse 通过和三身份合成资料 Chrome/CDP 可视化验收通过。出现隐私泄露、默认外呼、虚假验收或 P0-P4 基线退化时必须打回计划。

P5 当前采用路线 A：复用现有本地工具链并逐步加固。路线 B“P5 直接引入真实外部 provider”转入 P6 opt-in；路线 C“大规模重构前端/状态架构”仅在现有结构阻塞 P5-M1/M2 后局部采用。

## 第 5 页 - P5 项目里程碑、验收门槛与出门条件

P5 门槛：

1. P0-P4 冻结基线不退化；
2. 真实资料本地导入可理解；
3. JD 解析与缺失信息恢复成立；
4. 事实确认闭环可执行；
5. 申请包生成、编辑、再生成和导出可信；
6. 本地多轮追问不误触发工具；
7. 隐私、provider 和报告不误导；
8. 多视口体验和证据完整。

自动化矩阵必须覆盖：

- P5 real data local flow；
- JD gap recovery；
- confirmation gate；
- application package edit/regenerate loop；
- export preflight；
- local dialogue；
- privacy redaction；
- HTML acceptance report；
- drawio/docs consistency。

最终出门条件：

```text
导入资料 → 解析资料 → 导入 JD → 解析岗位 → 确认事实
→ 生成申请包 → 编辑/重新生成 → 导出 → 围绕当前资料继续追问
```

P5 完成只代表真实资料本地闭环通过；不代表真实外部 provider 默认路径、SaaS、ASR、会议平台、自动投递或最终产品化发布已通过。

## 第 6 页 - 安全边界、状态标记、证据和后续阶段

P5 证据包：

- P5 HTML 自动化验收报告；
- 1200/1440/1600/1920/720/390 多视口真实界面截图；
- 资料导入、JD 解析、事实确认、申请包、编辑再生成、导出、多轮追问截图；
- pytest 88 passed, 1 warning、frontend build、drawio XML parse、三身份合成资料 Chrome/CDP 可视化验收；
- README/TODO/active docs 同步；
- PRD 规格检视和虚假验收风险清单。

高风险边界：

- 真实个人资料必须用户授权；
- 自动化报告必须脱敏；
- 真实外部 provider 必须进入 P6 opt-in；
- API Key 不得进入仓库、报告、日志或截图；
- ASR、会议平台、自动投递、SaaS、MCP/CLI 不是 P5 出门条件；
- 文档通过不等于实现通过，drawio 方向认可不等于功能验收通过。
