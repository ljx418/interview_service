# P5.5-M3 项目可信度审计

日期：2026-06-30  
状态：通过自动化候选。

## 开发内容

- 基于 `tech_project` 生成项目可信度。
- 项目可信度标签固定为 `verified`、`plausible`、`needs_evidence`、`risky`。
- 本人贡献、技术难点、可验证材料缺口和待确认项分开展示。

## 验收证据

- `tests/evals/test_p5_5_project_credibility_eval.py` 覆盖未确认贡献不得标记 verified、缺可验证链接必须保留 evidence gap。

## PRD 检视

- 未确认本人贡献不写成事实。
- 项目可信度只评价证据状态，不做背景调查或敏感属性分析。
