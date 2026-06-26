# P4C External Provider Desensitized Acceptance Plan

Date: 2026-06-24
Status: gated; no external call has been approved in this plan

## 1. Purpose

This plan defines how to run a later controlled acceptance check with an existing `.env` OpenAI-compatible provider and user-confirmed desensitized personal data. It exists to prevent false claims and accidental leakage.

## 2. Human Confirmation Required Before Execution

Before any real external provider call, the agent must pause and obtain explicit confirmation for:

- exact desensitized input file paths;
- which fields may be sent to the provider;
- provider name and model family;
- exact tool or API path to call;
- maximum number of calls;
- whether the result may be saved in the local workspace;
- whether screenshots or reports may include redacted summaries.

The agent must not read, print, copy, or report the API key.

## 3. Allowed Preflight Without External Call

The agent may run local-only checks:

- inspect provider status without revealing secrets;
- run provider redaction tests;
- confirm `.env` presence and configured/unconfigured status without printing values;
- verify that `provider_invocation` logs use redacted summaries;
- verify that reports do not contain raw key, token, email, full resume, full JD, or transcript text.

## 4. Acceptance Criteria

The external-provider path passes only if:

- the user-confirmed desensitized data is the only external input;
- the provider call requires explicit confirmation and does not run by default;
- schema validation passes;
- timeout/error behavior is reported honestly;
- invocation logs contain only redacted summaries;
- screenshots and reports avoid raw personal data and secrets;
- the final report clearly says this is a controlled desensitized provider acceptance, not default product behavior.

## 5. Failure and Stop Conditions

The acceptance is failed or blocked if:

- `.env` is missing or provider is unconfigured;
- the user has not confirmed the exact desensitized data and allowed fields;
- provider call fails, times out, or returns invalid structured output;
- any secret or raw personal data appears in logs, reports, screenshots, or fixtures;
- the result would be used to claim full P6 provider-backed free chat.

## 6. Current Audit Opinion

No real external call is authorized yet. This plan is ready for a later high-risk confirmation checkpoint, but it is outside the low-risk P4C-FC local/mock implementation loop.
