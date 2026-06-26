# Browser automation tools

This directory contains local browser automation helpers for JobPilot acceptance
evidence capture. They are intentionally small and use either Chrome DevTools
Protocol directly or a globally installed Playwright package.

## Installed commands

The following commands are linked into `/home/administrator/.local/bin`, which is
already on PATH for Codex terminals on this machine:

- `chrome-win-headless` starts Windows Chrome in headless mode with a DevTools
  debug port. Default port: `9223`.
- `cdp-screenshot` captures a full-page screenshot through an already running
  Chrome DevTools endpoint. It uses only Node built-ins.
- `playwright-win-chrome-screenshot` starts Windows Chrome with a DevTools port
  and connects with the globally installed Playwright package.
- `browser-acceptance` runs a JSON-defined browser scenario, captures screenshot
  evidence, and writes a readable HTML acceptance report.

Global npm packages installed on this machine:

- `playwright`
- `@playwright/test`
- `puppeteer-core`
- `chrome-remote-interface`

## Smoke-test examples

Start Chrome for CDP-based tools:

```bash
chrome-win-headless about:blank
```

Capture with the direct CDP helper:

```bash
cdp-screenshot \
  --url "http://127.0.0.1:5173/" \
  --output /tmp/jobpilot-chatbox.png \
  --width 1280 \
  --height 900
```

Capture with the Playwright helper:

```bash
playwright-win-chrome-screenshot \
  --url "http://127.0.0.1:5173/" \
  --output /tmp/jobpilot-chatbox-playwright.png \
  --width 1280 \
  --height 900
```

Run a reusable browser acceptance scenario:

```bash
browser-acceptance \
  --start-chrome \
  --scenario scripts/browser_tools/examples/smoke-scenario.json \
  --output-dir /tmp/jobpilot-browser-acceptance \
  --report /tmp/jobpilot-browser-acceptance/report.html
```

Scenario actions supported by `browser-acceptance`:

- `goto`: navigate to `step.url` or scenario `url`.
- `waitText`: wait until page body text contains `step.text`.
- `clickText`: click a button/link/role button whose visible text contains
  `step.text`.
- `fill`: set an input or textarea by CSS `step.selector`.
- `evaluate`: run JavaScript from `step.expression`.
- `wait`: wait for `step.ms`.
- `screenshot`: capture a full-page PNG at `step.file`.

This command is intended for Codex CLI, Claude Code CLI, and other agent
terminals. It makes browser use reproducible: the JSON scenario is the contract,
the screenshots are evidence, and the HTML report states what actually ran.

## Known limits

- The npm package named `chrome-cli` is macOS-only and cannot be installed on
  this WSL/Linux environment.
- `playwright install chromium` completed, but default Linux Playwright Chromium
  cannot launch yet because WSL system packages are missing. The failing missing
  library observed during setup was `libnspr4.so`.
- `playwright install-deps chromium` requires sudo/root package installation.
  It failed in this Codex session because sudo required an interactive password.
- The working no-sudo path on this machine is Windows Chrome plus CDP:
  `chrome-win-headless` + `cdp-screenshot`, or
  `playwright-win-chrome-screenshot`, or `browser-acceptance --start-chrome`.
- In Codex sandboxed commands, local debug-port access may be blocked. Run CDP
  screenshot commands with approval when they need to connect to
  `127.0.0.1:<debug-port>`.
- Browser automation reports do not prove real external-provider behavior,
  real personal data handling, or human UX acceptance unless those paths are
  explicitly run and reviewed.
