# P5.5-M4 JD 短板分析审计

日期：2026-06-30  
状态：通过自动化候选。

## 开发内容

- 基于 `job.requirements_json`、能力矩阵和 `match_report` 生成岗位短板。
- 每个短板包含 requirement、must/nice、gap_level、impact、next_action 和 source refs。

## 验收证据

- `tests/evals/test_p5_5_gap_analysis_eval.py` 覆盖 must requirement、缺证据项、补强行动和 source refs。

## PRD 检视

- 岗位短板可行动，不输出羞辱性或敏感属性相关评价。
- `missing` 不写成 `covered`。
