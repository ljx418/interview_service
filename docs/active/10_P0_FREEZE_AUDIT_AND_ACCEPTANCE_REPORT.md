# JobPilot AI P0 冻结审计与验收报告

## 1. 审计结论

当前 active 文档体系达到“可以冻结为 P0 工程执行规格”的标准，可以支撑本阶段 P0 MVP 的自动化维护、验收回归和小步增强。

冻结判断：

- PRD 体验路径：通过；
- 目标架构 P0 版本：通过；
- 里程碑与工作包闭环：通过；
- schema、artifact、PDF、realtime、eval、README/TODO 同步：通过；
- 高风险流程边界：通过；
- 致命或重大规格偏差：未发现。

本文档不把 P1/P2 能力纳入 P0 出门条件。后续自动化开发范围以 `09_AUTOMATED_DEVELOPMENT_SCOPE.md` 为准。

## 2. PRD 体验路径验收

P0 冻结体验路径：

```text
创建 workspace
→ 导入简历和项目 README
→ 生成 CareerFact / SkillEvidence / TechProject
→ 粘贴 JD
→ 生成 JD 解析和 MatchReport
→ 生成 ApplicationPackage
→ 用户确认并导出 Markdown
→ 生成 Interview Prep 和 StoryCard
→ 输入实时问题并获得结构化提示
→ 输入 transcript 并生成复盘和 TrainingTask
```

验收要求：

- 至少 5 个职业事实或技能线索；
- 至少 1 个技术项目卡；
- JD parse 区分 must-have 和 nice-to-have；
- MatchReport 包含 fit label、strengths、gaps、next actions；
- ApplicationPackage 包含 source refs 和 questions_to_confirm；
- Markdown 导出写入 workspace `exports/`；
- StoryCard 和 realtime hint 引用真实项目或事实；
- formal_assist 不返回完整逐字答案；
- Review 至少生成 3 个 TrainingTask。

## 3. 目标架构验收

P0 目标架构验收检查项：

- Chatbox 只负责输入、展示、确认和导出，不承载核心业务生成逻辑；
- FastAPI API 调用后端 Domain Tools；
- P0 输出通过 schema validation；
- artifact row 记录状态、source refs、questions_to_confirm、content_json/content_path；
- tool invocation log 记录工具名、输入摘要、输出引用、错误码和时间；
- 导入文件只进入 workspace `files/`；
- 导出文件只进入 workspace `exports/`；
- formal_assist 只支持 text question → structured hint；
- P0 不实现 ASR、系统音频、会议平台、视频解析或隐蔽式面试辅助。

## 4. ChatGPT 审计建议闭环

| 建议 | 冻结状态 |
|---|---|
| 字段级 schema | 已由 `08_P0_PROMPT_AND_OUTPUT_SCHEMAS.md` 和 `services/llm/contracts.py` 覆盖 |
| artifact 模型 | 已统一 artifact row 与 ArtifactRef 口径 |
| PDF 口径 | Markdown 是 hard gate，PDF 是 soft gate |
| P0 realtime 口径 | text question → structured hint，不含 ASR/会议平台/音视频 |
| source_refs 标准格式 | 已定义 SourceRef |
| questions_to_confirm 分级 | 已定义 blocking/warning/optional 与导出规则 |
| eval fixtures 和断言 | 已落到 `tests/evals/` |
| root README/TODO 同步 | 已同步当前 P0 状态和剩余风险 |

## 5. 自动验收命令

每次 P0 自动化维护后必须执行：

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

涉及 HTTP API 或端到端路径时，还必须执行：

```bash
uvicorn services.api.main:app --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/api/health
```

并使用 `examples/` 的匿名真实感数据跑完整验收路径。

## 6. 残留风险

以下风险不阻塞 P0 冻结，但不能被误认为已经完成：

- OpenAI-compatible provider 仍是可选占位，默认验收基线是 mock provider；
- Artifact 编辑已支持 metadata/content_json 更新，复杂业务表回写、多版本 diff 和完整 regenerate 属于 P1；
- PDF 是软门槛，占位或轻量实现不阻塞 P0；
- 更大规模 hallucination checker 和 JD parser eval 属于后续增强；
- MCP Server、CLI、ASR、会议平台接入、DOCX、正式 PDF 均不属于 P0。
- M5 已增加 artifact/session 恢复、tool log 脱敏、schema/docs 防漂移 eval；
- M7 已修复 realtime end workspace 定位、导出下载边界和确认状态即时 UX；
- M8 已修复 Chatbox 最新本地会话与产物卡恢复；
- M9 已增加 ChatCore 接入层和 PiAgent adapter；实际 PiAgent 源码迁移仍需源码路径、许可证和依赖边界确认；
- P0 收口复验和下一阶段门禁已完成，不新增功能。

## 7. 后续开发大纲

### P0 Maintenance

- 修复 P0 真实 bug；
- 增加 eval fixture 覆盖边界输入；
- 保持 docs、README、TODO、drawio 文本镜像与实现一致；
- 确保 Chatbox 不承载核心业务逻辑。
- 每次维护后执行后端测试、前端构建和必要的 HTTP 端到端验收。

### P1 Provider 与编辑闭环

- 实现真实 OpenAI-compatible provider；
- 增加 timeout、retry、redaction 和错误回退；
- 完成 artifact 编辑写回业务表和多版本记录；
- 强化 regenerate，不覆盖旧产物。

### P1 Export 与发布体验

- 增加正式 PDF 或 DOCX；
- 完善 Docker、CI、release checklist；
- 增加 contributor quickstart 和本地 workspace 管理。

### P2 扩展入口

- 增加 CLI；
- 增加 MCP Server wrapper；
- 重新审计后再评估 ASR 或会议平台接入。

## 8. 审计意见

可以冻结 P0 工程执行规格。后续自动化开发应只围绕 P0 Maintenance 执行；任何涉及真实个人数据、外部模型调用、ASR/会议平台、MCP/CLI、复杂 artifact 编辑或正式导出能力的工作，都必须先进入新阶段计划、验收标准和审计。
