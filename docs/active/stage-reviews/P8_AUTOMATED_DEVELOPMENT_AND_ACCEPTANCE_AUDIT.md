# P8-JD Intake 自动化开发与验收审计

状态：P8 自动化候选通过；不代表招聘平台自动接入、真实 provider、真实个人资料或自动投递通过。

生成时间：2026-07-01

## 1. 开发前启动审计

P8-M0 已按 `P8_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md` 执行。审计结论：

- P8 文档目标明确：资料准备向导、JD 手动导入、多 JD 目标选择、JD 定制简历、中文验收报告；
- 高风险边界明确：不登录招聘平台、不抓取 `source_url`、不自动投递、不默认调用真实 provider、不读取未授权真实个人资料；
- 当前实现路线可复用现有 `document`、`job`、`match_report`、`resume_version`、`application_package`、`artifact_version`；
- 未发现阻止 P8-M1 开发的重大规格偏差。

## 2. 子阶段实现与验收

| 子阶段 | 开发结果 | 验收证据 | 结论 |
| --- | --- | --- | --- |
| P8-M1 资料准备向导 | Chatbox 增加简历、项目经历、作品链接、目标 JD、求职偏好五类资料卡；上传支持 `kind` | `tests/evals/test_p8_jd_intake_resume_generation_eval.py`、截图 `p8_desktop_initial.png` | 通过 |
| P8-M2 JD 手动导入中心 | 新增 `POST /api/job/intake`，保存 JD 文本、`source_url`、平台来源和备注；不抓取 URL | API eval、`p8_api_evidence.json`、截图 `p8_desktop_job_intake.png` | 通过 |
| P8-M3 多 JD 与当前目标 | 新增 `GET /api/jobs`、`POST /api/jobs/{job_id}/select`；`job.is_current_target` 非破坏性迁移 | API eval 验证多 JD 切换和当前目标排序 | 通过 |
| P8-M4 JD 定制简历 | 新增 `POST /api/resume/generate`；复用申请包生成并返回 `resume_version_id`、source refs、pending confirmations、export preflight | API eval、ChatCore intent eval、截图 `p8_desktop_resume_generated.png` | 通过 |
| P8-M5 可视化报告 | 生成中文 HTML 自动化验收报告，包含目标架构、当前实现、PRD 检视、截图和未验证范围 | `docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html` | 通过 |

## 3. 代码检视

- API：新增 P8 路由复用 `run_tool` 错误处理，没有绕过 provider consent/policy；
- Storage：`job` 表仅新增 `platform`、`import_method`、`user_notes`、`parse_status`、`is_current_target`，属于非破坏性加列迁移；
- Domain：`job_intake` 复用 `parse_jd` 和 `match_profile`；`generate_resume` 复用 `create_application_package` 和 `resume_version`；
- ChatCore：只有明确“生成简历/定制简历”意图才写入简历产物；普通聊天或“不要生成”不会静默覆盖 `resume_version`；
- Frontend：P8 工作区位于对话状态机与输入区之间，保留现有三栏/移动抽屉结构，并补充响应式样式。

## 4. 文档审计

已同步 README、TODO、`docs/active/00_README.md` 和 `docs/active/01_STAGE_PRD.md` 的阶段口径：

- P8 不再是“仅文档开发阶段”；
- P8 当前为“本地/mock + 受控真实感数据自动化候选通过”；
- 仍不得写成真实 provider、真实个人资料、招聘平台自动化或自动投递通过。

## 5. 自动化证据

- `.venv/bin/python -m pytest tests/evals/test_p8_jd_intake_resume_generation_eval.py`：3 passed；
- `npm --prefix apps/chatbox run build`：通过；
- `docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html`：HTML 报告状态 passed；
- `docs/reports/evidence/p8_jd_intake/`：包含 API evidence JSON、browser scenario JSON 和 5 张 headless Chrome 截图。

## 6. PRD 规格检视

| PRD / Gate | 证据 | 结论 |
| --- | --- | --- |
| 用户知道需要提供什么资料 | 五类资料卡和上传 `kind` | 通过 |
| JD 手动导入，不抓取平台 | `source_url` 仅保存；API 证据写明未抓取 | 通过 |
| 多 JD 选择当前目标 | `GET /api/jobs` 和 select route | 通过 |
| JD 定制简历可追溯 | `resume_version_id`、source refs、pending confirmations、preflight | 通过 |
| 不做虚假验收 | 报告列出未验证范围 | 通过 |

## 7. 未验证范围

- 未接入 BOSS、猎聘、拉勾等平台登录、抓取、自动沟通或自动投递；
- 未调用真实 MiniMax、DeepSeek、OpenAI-compatible provider；
- 未读取用户真实个人资料；
- 未验证 SaaS、ASR、会议平台、多租户、Billing、MCP/CLI；
- 未执行 workspace 删除、cleanup apply 或 migration apply。

## 8. 审计结论

P8 自动化候选通过。当前项目已经能在本地/mock 和受控真实感数据下完成：

```text
资料准备向导
→ 手动导入 JD
→ 多 JD 选择当前目标岗位
→ JD 定制简历
→ source refs / pending confirmations / export preflight
→ 中文 HTML 验收报告
```

下一阶段建议进入 P8 人工体验复核或规划 P8+ 合规招聘平台接入、真实 provider 质量复验、真实个人资料复验。上述高风险路径必须另行授权。
