# P4C-FC Development Plan and Start Audit

Date: 2026-06-24
Status: approved for low-risk local/mock development; external-provider acceptance is gated

## 1. Stage Scope

This stage covers the P4C-FC local continuous Chatbox loop:

- free, multi-turn job-search conversation in the local/mock default path;
- workspace-aware status and next-step replies;
- explicit tool execution only when the user clearly asks for profile extraction, JD parsing, application package generation, or interview preparation;
- browser screenshot evidence and HTML acceptance reporting;
- PRD review before and after the implementation loop.

This stage does not deliver SaaS, ASR, meeting-platform capture, automatic job application, default external-model calls, or full provider-backed open-ended chat.

## 2. PRD Alignment

Relevant PRD requirements:

- `docs/active/01_STAGE_PRD.md`: P4C-FC requires at least two free follow-up turns without forced artifact generation.
- `docs/active/02_TARGET_ARCHITECTURE.md`: Chatbox remains a thin UI over session state, intent routing, local dialogue, and domain tools.
- `docs/active/04_ACCEPTANCE_GATES.md`: P4 Gate 2 adds continuous conversation, status query, and explicit tool-intent boundaries.
- `docs/active/18_FREE_CHATBOX_CONTINUOUS_DIALOGUE_PLAN.md`: current stage proves only the local/mock continuous dialogue baseline.

Audit result: the documentation is sufficient to guide P4C-FC local development. It is not sufficient to claim P6 provider-backed free chat, and it intentionally gates that path.

## 3. Development Plan

1. Tighten the chat intent router so "explain first / do not generate" stays in free dialogue.
2. Preserve explicit tool intents for "整理资料", JD parsing, application package generation, and interview preparation.
3. Add regression tests for free chat, status query, and non-execution requests.
4. Generate browser evidence for initial state, free-chat two-turn path, status query, explicit tool execution, session restore, and responsive layouts.
5. Produce a readable HTML report with screenshots, target architecture, current implementation, PRD review, unverified scope, and audit opinion.
6. Run full regression: `python3 -m pytest` and `npm --prefix apps/chatbox run build`.

## 4. Acceptance Criteria

P4C-FC passes only if all of the following are true:

- free chat accepts at least two turns without artifact writes;
- "我还没有 JD，先聊聊求职方向" is not treated as JD parsing;
- "先别生成 / 先解释" does not generate an application package;
- "当前进展如何 / 有哪些产物" returns a workspace summary and writes no artifact;
- explicit tool intents still generate the expected artifacts;
- browser screenshots prove the above user paths on a real Chatbox UI;
- the report does not claim real personal-data or real external-provider acceptance.

## 5. Stop Rules

Stop and ask the user before proceeding if any of these appear:

- the only way to pass requires sending real or desensitized personal data to an external provider;
- an API key, raw full resume, raw full JD, or transcript would enter logs, reports, or screenshots;
- browser evidence cannot be captured but the report would need to claim visual acceptance;
- P4C-FC work drifts into P5/P6, ASR, meeting platform, auto-apply, SaaS, or irreversible migration;
- a major PRD mismatch is found after implementation.

## 6. Start Audit Opinion

Low-risk local/mock implementation can proceed. The current documentation supports this stage after this audit record. Real external-provider acceptance remains blocked until the user confirms exact desensitized data paths, provider, allowed fields, purpose, and call count.
