# P5.5-M5 Profile Workbench 审计

日期：2026-06-30  
状态：通过自动化候选。

## 开发内容

- Chatbox Workbench 新增 Candidate Profile 面板。
- 面板展示画像概览、能力矩阵、项目可信度、岗位短板、source refs 和未验证范围。
- 输入区新增“生成画像”显式按钮，普通聊天不自动刷新画像。

## 验收证据

- `npm --prefix apps/chatbox run build` 通过。
- `tests/evals/test_p5_5_chat_boundary_eval.py` 覆盖普通聊天不写 `candidate_profile` artifact。

## PRD 检视

- Workbench 不是裸 JSON 展示。
- 画像刷新为显式用户动作，符合“普通追问不写 artifact”约束。
