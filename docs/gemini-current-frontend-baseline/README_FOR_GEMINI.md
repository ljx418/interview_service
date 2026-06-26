# JobPilot AI Chatbox Frontend Baseline

This folder is a clean copy of the current production-facing Chatbox frontend source from:

```text
apps/chatbox/
```

It is intended as the baseline package for Gemini to redesign or refactor the UI. It is not a generated mockup and not an acceptance report.

## Source Files

```text
CURRENT_FRONTEND_IMPLEMENTATION_MAP.md
GEMINI_FRONTEND_REDESIGN_PROMPT.md
README_FOR_GEMINI.md
package.json
package-lock.json
index.html
vite.config.ts
tsconfig.json
src/main.tsx
src/styles.css
```

## Runtime

- Framework: React 19 + Vite 7 + TypeScript
- Icon library: lucide-react
- Frontend dev server: `127.0.0.1:5173`
- Backend API expected by the current code: `http://127.0.0.1:8000`
- Main React entry: `src/main.tsx`
- Main stylesheet and design tokens: `src/styles.css`

## Read This First

Start with:

```text
CURRENT_FRONTEND_IMPLEMENTATION_MAP.md
```

That document aligns the current React implementation with the PRD and target architecture. It lists:

- what PRD requirements the current UI is trying to satisfy;
- the real current source structure;
- current types, state, API calls, and endpoints;
- every current in-file React component and what it does;
- implemented user scenarios;
- known gaps that must not be hidden;
- a proposed future component tree, clearly marked as a suggestion rather than current fact.

## How To Run

From this folder:

```bash
npm install
npm run build
npm run dev
```

Inside the original repository, the known working command is:

```bash
npm --prefix apps/chatbox run build
```

## Important Boundaries

- Do not claim P4 has human UX approval.
- Do not claim real personal data paths have passed acceptance.
- Do not claim real external provider or real API key paths have passed acceptance.
- Current acceptance evidence is based on local/demo/mock paths unless explicitly documented otherwise.
- ASR, meeting platform integration, auto-apply, SaaS, irreversible migration, real external model calls, and real personal data workflows require human confirmation before implementation or validation.

## Known UI / Product Issues To Preserve As Facts

- The current interface is a three-column desktop workbench with responsive narrow/mobile paths.
- The current visual quality is not final product quality.
- Free Chatbox and uninterrupted long multi-turn dialogue are still follow-up development goals, not fully productized capabilities.
- Career facts artifact generation has evidence in messages/backend refs, but the right-side Workbench display has a partial refresh/visibility inconsistency that must not be hidden in design claims.
- The current implementation is mostly a single-file React app in `src/main.tsx`; any multi-file component structure is a proposed refactor, not current reality.

## Expected Gemini Output

Gemini should produce either:

- an improved React/TypeScript implementation patch based on these files, or
- a redesigned component structure and CSS token system that can be applied back to these files.

The redesign should keep the first screen as the usable product workbench, not a marketing landing page.
