# P5.5-M2 能力矩阵审计

日期：2026-06-30  
状态：通过自动化候选。

## 开发内容

- 基于 `skill_evidence`、`career_fact` 和 JD requirements 生成能力矩阵。
- 证据等级固定为 `strong`、`usable`、`weak`、`missing`。
- 每项能力包含 source refs 或待确认项。

## 验收证据

- `tests/evals/test_p5_5_capability_matrix_eval.py` 覆盖强证据、可用证据、缺证据和敏感属性禁用口径。

## PRD 检视

- 能力等级解释为证据强弱和岗位相关性，不评价人格、潜力或敏感属性。
- 缺证据 JD 要求显示为 `missing`，不自动补全事实。
