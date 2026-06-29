# P5.5-M1 CandidateProfile 聚合审计

日期：2026-06-30  
状态：通过自动化候选。

## 开发内容

- 新增 `services/profile/candidate.py` 和 `services/profile/__init__.py`。
- 新增 `GET /api/profile/candidate` 和 `POST /api/profile/candidate/refresh`。
- 新增 `CandidateProfileRefreshRequest` schema。
- 刷新画像时更新或创建 `candidate_profile` 行，并写入 `artifact_type=candidate_profile` 的 artifact/version。

## 验收证据

- `tests/evals/test_p5_5_candidate_profile_eval.py` 覆盖空态、有数据态、API contract、profile row、artifact 和 artifact_version。

## PRD 检视

- 专业背景画像来自 `career_fact`、`skill_evidence`、`tech_project`、`job`、`match_report` 和 artifact source refs。
- 未新增数据库表，符合 P5.5 v1 最小可逆路线。

## 未验证范围

- 未读取用户真实个人资料。
- 未调用真实外部 provider。
