# JobPilot AI P1 Release Checklist

## Scope

- [x] P0 mock provider flow remains available without API key.
- [x] Provider Runtime supports mock, fixture and OpenAI-compatible opt-in.
- [x] Provider invocation logs store redacted summaries only.
- [x] Core tools have provider-backed contract paths.
- [x] Artifact edit creates new versions and keeps old versions readable.
- [x] Regenerate creates child versions and keeps current unchanged on failure.
- [x] Export preflight blocks unresolved blocking confirmations.
- [x] Markdown export remains available.
- [x] DOCX export is formally generated and openable.
- [x] Chatbox shows provider mode, artifact versions, edit, regenerate and export actions.
- [x] Chrome visible screenshot acceptance captured at `docs/active/evidence/p1_chrome_chatbox_visible_acceptance.png`.

## Required Checks

```bash
python3 -m pytest
npm --prefix apps/chatbox run build
```

## Manual High-Risk Checks

These are not run automatically:

- Real API key validation.
- Real external provider calls.
- Real personal resume / JD / transcript data.
- Irreversible migration against a user workspace.

## Non-Goals

- MCP Server.
- CLI.
- ASR / Whisper.
- Meeting platform integration.
- Auto apply / auto submit.
- SaaS login, multi-tenant backend or billing.
