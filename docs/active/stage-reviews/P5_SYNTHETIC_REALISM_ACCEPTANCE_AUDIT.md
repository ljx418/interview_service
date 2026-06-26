# P5 合成真实感资料验收审计

日期：2026-06-26
阶段：P5 自动化候选增强 / P5-SYNTHETIC-REALISM
状态：用户明确不提供真实个人资料后，改用多身份合成资料加强验收真实性。

## 1. 审计口径

本轮不执行 P5-REAL 真实个人资料验收，不读取用户个人文件，不调用真实外部 provider。

允许声明：

- 使用多身份合成资料加强 P5 本地/mock 自动化验收覆盖；
- 覆盖不同背景、目标岗位、项目材料和面试准备问题；
- 可用于发现资料解析、JD 匹配、申请包、确认项、导出和连续追问的结构性问题。

禁止声明：

- 不得声明真实个人资料路径已通过；
- 不得声明 P5-REAL 已通过；
- 不得声明 P5 已冻结；
- 不得声明真实外部 provider 默认路径已通过；
- 不得把合成资料写成真实背调材料或真实投递材料。

## 2. 合成资料覆盖

| Persona | 背景 | 目标岗位 | 验收价值 |
| --- | --- | --- | --- |
| `ops_to_frontend` | 运营数据分析转前端 | Junior Frontend Developer | 覆盖业务理解、前端工程、导出和本地隐私边界。 |
| `qa_to_fullstack` | 手工测试转自动化全栈 | QA Automation / Full-stack Assistant | 覆盖测试证据、截图报告、缺陷复现和全栈协作。 |
| `teacher_to_edtech` | 数学教师转教育科技前端 | EdTech Frontend Developer | 覆盖非技术背景转岗、教育场景、数据可视化和隐私边界。 |

资料路径：

- `examples/p5_synthetic_personas/ops_to_frontend/`
- `examples/p5_synthetic_personas/qa_to_fullstack/`
- `examples/p5_synthetic_personas/teacher_to_edtech/`

每个 persona 均包含：

- `resume.md`
- `project.md`
- `jd.md`
- `interview_brief.md`

## 3. 执行方式

生成全部合成验收场景：

```bash
JOBPILOT_LLM_PROVIDER=mock python3 scripts/generate_p5_synthetic_realism_acceptance.py
```

生成单个 persona：

```bash
JOBPILOT_LLM_PROVIDER=mock \
JOBPILOT_SYNTHETIC_PERSONA=qa_to_fullstack \
python3 scripts/generate_p5_synthetic_realism_acceptance.py
```

浏览器执行某个场景前必须提醒用户 Chrome 可能抢占焦点：

```bash
node scripts/browser_tools/browser-acceptance.mjs \
  --start-chrome \
  --scenario .tmp/p5-synthetic-realism-qa_to_fullstack.scenario.json \
  --output-dir docs/reports/p5-synthetic-realism-qa_to_fullstack-evidence \
  --report docs/reports/P5_SYNTHETIC_REALISM_ACCEPTANCE_qa_to_fullstack.html
```

## 4. 出门条件

合成真实感验收通过需要满足：

- 所有合成资料明确标注为合成；
- scenario 和报告不得出现真实个人资料通过的声明；
- provider 必须为 mock/local；
- 至少 3 个 persona 的 resume/project/JD 文本抽取质量合格；
- 每个 persona 可生成独立浏览器验收 scenario；
- P5 文档仍明确真实个人资料路径未通过、P5 未冻结。

## 5. 审计结论

该路线可以提高自动化验收真实性和覆盖面，尤其适合用户不愿提供真实资料的情况。

该路线不能替代 P5-REAL，也不能作为 P5-Freeze 的真实资料签收证据。若最终仍不提供真实资料，P5 可以保持“自动化候选增强通过”，但不能声称真实个人资料路径通过。
