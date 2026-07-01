#!/usr/bin/env node
import { spawn } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, relative, resolve } from "node:path";

const args = parseArgs(process.argv.slice(2));
if (args.has("help") || args.has("h")) {
  printHelp();
  process.exit(0);
}
const port = String(args.get("port") || process.env.CHROME_DEBUG_PORT || "9223");
const outputDir = resolve(args.get("output-dir") || args.get("out-dir") || "docs/reports/browser-acceptance");
const scenarioPath = args.get("scenario");
const reportPath = resolve(args.get("report") || `${outputDir}/BROWSER_ACCEPTANCE_REPORT.html`);
const shouldStartChrome = args.has("start-chrome");
const chromePath = process.env.CHROME_PATH || "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe";
const userDataDir = process.env.CHROME_USER_DATA_DIR || `/tmp/browser-acceptance-chrome-${port}`;

function parseArgs(argv) {
  const parsed = new Map();
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (!item.startsWith("--")) continue;
    const [key, inlineValue] = item.slice(2).split("=", 2);
    if (inlineValue !== undefined) parsed.set(key, inlineValue);
    else if (argv[index + 1] && !argv[index + 1].startsWith("--")) parsed.set(key, argv[++index]);
    else parsed.set(key, true);
  }
  return parsed;
}

function printHelp() {
  console.log(`browser-acceptance

Run a Chrome/CDP browser scenario and generate an HTML evidence report.

Usage:
  browser-acceptance --start-chrome --scenario <file.json> --output-dir <dir> --report <file.html>

Options:
  --scenario <file>     JSON scenario file. If omitted, a basic screenshot scenario is used.
  --url <url>           Target URL for the default scenario.
  --start-chrome        Start local Chrome with a DevTools debug port.
  --port <port>         Chrome DevTools port. Default: CHROME_DEBUG_PORT or 9223.
  --output-dir <dir>    Directory for screenshots and default report.
  --report <file>       HTML report path.
  --width <px>          Default scenario viewport width. Default: 1280.
  --height <px>         Default scenario viewport height. Default: 900.
  --help, -h            Show this help.

Scenario actions:
  goto, waitText, clickText, fill, evaluate, wait, screenshot
`);
}

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

function html(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function posixPath(path) {
  return path.replaceAll("\\", "/");
}

async function requestJson(path, init) {
  const response = await fetch(`http://127.0.0.1:${port}${path}`, init);
  if (!response.ok) throw new Error(`Chrome DevTools request failed: ${response.status} ${path}`);
  return response.json();
}

async function waitForChrome(timeoutMs = 10_000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return response.json();
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await delay(200);
  }
  throw lastError || new Error(`Chrome did not become ready on port ${port}`);
}

class CdpClient {
  constructor(wsUrl, targetId) {
    this.targetId = targetId;
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.events = new Map();
  }

  async open() {
    await new Promise((resolveOpen, rejectOpen) => {
      this.ws.addEventListener("open", resolveOpen, { once: true });
      this.ws.addEventListener("error", rejectOpen, { once: true });
    });
    this.ws.addEventListener("message", (event) => {
      const payload = JSON.parse(event.data);
      if (payload.id && this.pending.has(payload.id)) {
        const { resolveCommand, rejectCommand } = this.pending.get(payload.id);
        this.pending.delete(payload.id);
        if (payload.error) rejectCommand(new Error(payload.error.message));
        else resolveCommand(payload.result);
        return;
      }
      for (const listener of this.events.get(payload.method) || []) listener(payload.params);
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolveCommand, rejectCommand) => {
      this.pending.set(id, { resolveCommand, rejectCommand });
    });
  }

  once(method) {
    return new Promise((resolveEvent) => {
      const wrapped = (params) => {
        this.events.set(method, (this.events.get(method) || []).filter((listener) => listener !== wrapped));
        resolveEvent(params);
      };
      this.events.set(method, [...(this.events.get(method) || []), wrapped]);
    });
  }

  close() {
    this.ws.close();
  }
}

async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    const detail = result.exceptionDetails.exception?.description || result.exceptionDetails.text;
    throw new Error(detail || "Runtime.evaluate failed");
  }
  return result.result?.value;
}

async function createPage(url) {
  const target = await requestJson(`/json/new?${encodeURIComponent(url || "about:blank")}`, { method: "PUT" });
  if (!target.webSocketDebuggerUrl) throw new Error("Chrome target did not expose a WebSocket debugger URL.");
  const client = new CdpClient(target.webSocketDebuggerUrl, target.id);
  await client.open();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  return client;
}

async function setViewport(client, viewport) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width: viewport.width,
    height: viewport.height,
    deviceScaleFactor: viewport.deviceScaleFactor || 1,
    mobile: viewport.mobile ?? viewport.width < 520,
  });
}

async function navigate(client, url) {
  const load = client.once("Page.loadEventFired");
  await client.send("Page.navigate", { url });
  await load;
}

async function waitForText(client, text, timeoutMs = 10_000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const found = await evaluate(client, `document.body.innerText.includes(${JSON.stringify(text)})`);
    if (found) return true;
    await delay(250);
  }
  throw new Error(`Timed out waiting for text: ${text}`);
}

async function clickText(client, text) {
  const clicked = await evaluate(
    client,
    `(() => {
      const text = ${JSON.stringify(text)};
      const nodes = Array.from(document.querySelectorAll('button, a, [role="button"], input[type="button"], input[type="submit"], .prompt-card'));
      const target = nodes.find((node) => (node.innerText || node.value || '').includes(text));
      if (!target) return false;
      target.click();
      return true;
    })()`,
  );
  if (!clicked) throw new Error(`Clickable text not found: ${text}`);
}

async function fill(client, selector, value) {
  const filled = await evaluate(
    client,
    `(() => {
      const node = document.querySelector(${JSON.stringify(selector)});
      if (!node) return false;
      const proto = node instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
      if (setter) setter.call(node, ${JSON.stringify(value)});
      else node.value = ${JSON.stringify(value)};
      node.dispatchEvent(new Event('input', { bubbles: true }));
      node.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })()`,
  );
  if (!filled) throw new Error(`Input selector not found: ${selector}`);
}

async function screenshot(client, output, viewport) {
  await setViewport(client, viewport);
  await delay(300);
  const result = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
  });
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, Buffer.from(result.data, "base64"));
}

function defaultScenario() {
  const url = args.get("url") || "about:blank";
  return {
    name: "Browser automation smoke test",
    goal: "Verify that a CLI agent can drive a real browser and capture screenshot evidence.",
    targetArchitecture: ["Agent CLI", "browser-acceptance", "Chrome DevTools Protocol", "Chrome browser", "HTML evidence report"],
    currentImplementation: ["Node.js built-in fetch/WebSocket", "Chrome remote debugging endpoint", "PNG screenshot evidence", "Self-contained HTML report"],
    url,
    viewports: [{ name: "desktop", width: Number(args.get("width") || 1280), height: Number(args.get("height") || 900) }],
    steps: [
      { name: "Open target page", action: "goto", url },
      { name: "Capture initial page", action: "screenshot", file: "initial.png" },
    ],
  };
}

async function readScenario() {
  if (!scenarioPath) return defaultScenario();
  return JSON.parse(await readFile(resolve(scenarioPath), "utf8"));
}

async function runStep(client, scenario, step, activeViewport, artifacts) {
  const started = new Date();
  if (step.action === "goto") await navigate(client, step.url || scenario.url);
  else if (step.action === "waitText") await waitForText(client, step.text, step.timeoutMs);
  else if (step.action === "clickText") await clickText(client, step.text);
  else if (step.action === "fill") await fill(client, step.selector, step.value || "");
  else if (step.action === "wait") await delay(step.ms || 500);
  else if (step.action === "evaluate") await evaluate(client, step.expression);
  else if (step.action === "screenshot") {
    const file = step.file || `${step.name || "screenshot"}.png`;
    const output = resolve(outputDir, file);
    await screenshot(client, output, activeViewport);
    artifacts.push({ name: step.name || file, file: output });
  } else {
    throw new Error(`Unsupported action: ${step.action}`);
  }
  return { ...step, status: "passed", started: started.toISOString(), ended: new Date().toISOString() };
}

function renderReport({ scenario, results, artifacts, status, error, startedAt, endedAt }) {
  const artifactCards = artifacts
    .map((artifact) => {
      const rel = posixPath(relative(dirname(reportPath), artifact.file));
      return `<figure><img src="${html(rel)}" alt="${html(artifact.name)}"><figcaption>${html(artifact.name)}<br><code>${html(rel)}</code></figcaption></figure>`;
    })
    .join("\n");
  const steps = results
    .map((step, index) => `<tr><td>${index + 1}</td><td>${html(step.name || step.action)}</td><td><code>${html(step.action)}</code></td><td class="${step.status}">${html(step.status)}</td></tr>`)
    .join("\n");
  const target = (scenario.targetArchitecture || []).map((item) => `<li>${html(item)}</li>`).join("");
  const current = (scenario.currentImplementation || []).map((item) => `<li>${html(item)}</li>`).join("");
  const acceptanceCriteria = (scenario.acceptanceCriteria || []).map((item) => `<li>${html(item)}</li>`).join("");
  const commandResults = (scenario.commandResults || [])
    .map((item) => `<tr><td><code>${html(item.command)}</code></td><td class="${html(item.status || "")}">${html(item.status || "")}</td><td>${html(item.evidence || "")}</td></tr>`)
    .join("\n");
  const prdReview = (scenario.prdReview || [])
    .map((item) => {
      const resultClass = String(item.status || "").toLowerCase().includes("pass") ? "passed" : String(item.status || "").toLowerCase().includes("fail") ? "failed" : "";
      return `<tr><td>${html(item.requirement)}</td><td>${html(item.evidence)}</td><td class="${resultClass}">${html(item.status)}</td></tr>`;
    })
    .join("\n");
  const codeReview = (scenario.codeReview || [])
    .map((item) => `<tr><td>${html(item.area)}</td><td>${html(item.finding)}</td><td class="${html(item.severity || "")}">${html(item.severity || "")}</td></tr>`)
    .join("\n");
  const documentationAudit = (scenario.documentationAudit || [])
    .map((item) => `<tr><td>${html(item.area)}</td><td>${html(item.finding)}</td><td class="${html(item.status || "")}">${html(item.status || "")}</td></tr>`)
    .join("\n");
  const multiTurnDialogues = (scenario.multiTurnDialogues || [])
    .map((dialogue) => {
      const files = (dialogue.source_files || [])
        .map((file) => `<details><summary>${html(file.label)}：<code>${html(file.path)}</code></summary><p>${html(file.excerpt)}</p></details>`)
        .join("");
      const turns = (dialogue.turns || [])
        .map((turn) => `<tr><td>${html(turn.turn)}</td><td>${html(turn.user)}</td><td>${html(turn.assistant)}</td><td>${html(turn.provider_invocation_status)} / ${html(turn.chat_mode)}</td><td>${html(turn.artifacts_count)}</td></tr>`)
        .join("\n");
      return `<article class="dialogue-case">
        <h3>${html(dialogue.persona)} · ${html(dialogue.target_role)}</h3>
        <p class="meta">技术背景：${html(dialogue.technical_background)}；provider 路径：${html(dialogue.provider_path)}；真实 provider 调用：${dialogue.real_provider_called ? "是" : "否"}</p>
        <table><tbody>
          <tr><th>轮次</th><td>${html(dialogue.turn_count)} 轮用户消息 / ${html(dialogue.message_count)} 条会话消息</td></tr>
          <tr><th>provider 记录</th><td>${html(dialogue.provider_called_count)} 条 called 记录；recent window=${html(dialogue.recent_count)}；rolling summary covered=${html(dialogue.rolling_summary_covered)}</td></tr>
          <tr><th>隐私边界</th><td>API Key=${html(dialogue.privacy_boundary?.contains_api_key)}；raw provider response=${html(dialogue.privacy_boundary?.raw_provider_response_included)}；full history=${html(dialogue.privacy_boundary?.full_history_included)}</td></tr>
          <tr><th>关注点</th><td>${(dialogue.focus || []).map((item) => html(item)).join(" / ")}</td></tr>
        </tbody></table>
        <h4>虚拟资料</h4>
        ${files}
        <h4>20 轮对话 transcript</h4>
        <table><thead><tr><th>#</th><th>用户消息</th><th>助手回复</th><th>状态</th><th>产物数</th></tr></thead><tbody>${turns}</tbody></table>
      </article>`;
    })
    .join("\n");
  const unverifiedScope = (scenario.unverifiedScope || []).map((item) => `<li>${html(item)}</li>`).join("");
  const auditOpinion = scenario.auditOpinion ? `<p>${html(scenario.auditOpinion)}</p>` : "";
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${html(scenario.name)} - Browser Acceptance Report</title>
  <style>
    body { margin: 0; font: 15px/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1f2933; background: #f6f8fb; }
    header, main { max-width: 1120px; margin: 0 auto; padding: 28px; }
    header { padding-top: 36px; }
    h1 { margin: 0 0 10px; font-size: 30px; letter-spacing: 0; }
    h2 { margin: 28px 0 12px; font-size: 19px; }
    .meta { color: #52606d; }
    .badge { display: inline-block; padding: 5px 10px; border-radius: 6px; font-weight: 700; background: ${status === "passed" ? "#d9f9e6" : "#ffe3e3"}; color: ${status === "passed" ? "#0f6b3d" : "#a61b1b"}; }
    section { background: #fff; border: 1px solid #d9e2ec; border-radius: 8px; padding: 18px; margin: 18px 0; }
    table { width: 100%; border-collapse: collapse; background: #fff; }
    th, td { text-align: left; border-bottom: 1px solid #e4e7eb; padding: 10px; vertical-align: top; }
    th { color: #52606d; font-size: 13px; }
    code { background: #eef2f7; padding: 2px 5px; border-radius: 4px; }
    .passed { color: #0f6b3d; font-weight: 700; }
    .failed { color: #a61b1b; font-weight: 700; }
    .warning { color: #8a4b0f; font-weight: 700; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }
    figure { margin: 0; border: 1px solid #d9e2ec; border-radius: 8px; overflow: hidden; background: #fff; }
    img { display: block; width: 100%; height: auto; border-bottom: 1px solid #d9e2ec; }
    figcaption { padding: 10px 12px; color: #52606d; font-size: 13px; }
    h3 { margin: 18px 0 8px; font-size: 17px; }
    h4 { margin: 18px 0 8px; font-size: 15px; color: #334e68; }
    details { border: 1px solid #d9e2ec; border-radius: 6px; padding: 10px 12px; margin: 8px 0; background: #fbfdff; }
    details p { margin: 10px 0 0; color: #334e68; }
    .dialogue-case { border: 1px solid #bcccdc; border-radius: 8px; padding: 14px; margin: 14px 0; background: #fff; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #fff4f4; color: #7f1d1d; padding: 12px; border-radius: 6px; }
  </style>
</head>
<body>
  <header>
    <h1>${html(scenario.name)}</h1>
    <p><span class="badge">${html(status)}</span></p>
    <p class="meta">${html(scenario.goal || "")}</p>
    <p class="meta">Started: ${html(startedAt)} · Ended: ${html(endedAt)} · Report: <code>${html(reportPath)}</code></p>
  </header>
  <main>
    <section>
      <h2>目标架构</h2>
      <ul>${target}</ul>
      <h2>当前实现</h2>
      <ul>${current}</ul>
    </section>
    <section>
      <h2>自动化步骤</h2>
      <table><thead><tr><th>#</th><th>步骤</th><th>动作</th><th>结果</th></tr></thead><tbody>${steps}</tbody></table>
      ${error ? `<h2>失败信息</h2><pre>${html(error.stack || error.message || error)}</pre>` : ""}
    </section>
    <section>
      <h2>验收标准</h2>
      <ul>${acceptanceCriteria || "<li>Scenario did not define explicit acceptance criteria.</li>"}</ul>
    </section>
    <section>
      <h2>命令结果</h2>
      <table><thead><tr><th>命令</th><th>状态</th><th>证据</th></tr></thead><tbody>${commandResults || "<tr><td colspan=\"3\">Scenario did not define command results.</td></tr>"}</tbody></table>
    </section>
    <section>
      <h2>PRD 规格检视</h2>
      <table><thead><tr><th>PRD / Gate 要求</th><th>证据</th><th>结论</th></tr></thead><tbody>${prdReview || "<tr><td colspan=\"3\">Scenario did not define PRD review items.</td></tr>"}</tbody></table>
    </section>
    <section>
      <h2>代码检视</h2>
      <table><thead><tr><th>区域</th><th>结论</th><th>级别</th></tr></thead><tbody>${codeReview || "<tr><td colspan=\"3\">Scenario did not define code review items.</td></tr>"}</tbody></table>
    </section>
    <section>
      <h2>文档审计</h2>
      <table><thead><tr><th>区域</th><th>结论</th><th>状态</th></tr></thead><tbody>${documentationAudit || "<tr><td colspan=\"3\">Scenario did not define documentation audit items.</td></tr>"}</tbody></table>
    </section>
    <section>
      <h2>多背景多轮对话补证</h2>
      <p class="meta">以下 transcript 来自合成资料和 fake provider opt-in 自动化路径，用于证明长程对话、上下文边界、脱敏日志和不同背景覆盖；未覆盖真实 LLM/provider 的回复质量、成本、稳定性或可用性验收。</p>
      ${multiTurnDialogues || "<p>Scenario did not define multi-turn dialogue evidence.</p>"}
    </section>
    <section>
      <h2>截图证据</h2>
      <div class="grid">${artifactCards || "<p>No screenshots captured.</p>"}</div>
    </section>
    <section>
      <h2>未验证范围与审计意见</h2>
      <ul>${unverifiedScope || "<li>No unverified scope declared.</li>"}</ul>
      ${auditOpinion}
    </section>
  </main>
</body>
</html>`;
}

async function main() {
  const startedAt = new Date().toISOString();
  await mkdir(outputDir, { recursive: true });
  let chrome;
  if (shouldStartChrome) {
    chrome = spawn(chromePath, [
      "--headless=new",
      "--disable-gpu",
      "--remote-debugging-address=127.0.0.1",
      `--remote-debugging-port=${port}`,
      `--user-data-dir=${userDataDir}`,
      "--no-first-run",
      "--no-default-browser-check",
      "about:blank",
    ], { stdio: "ignore" });
  }
  const scenario = await readScenario();
  const artifacts = [];
  const results = [];
  let client;
  let status = "passed";
  let error;
  try {
    await waitForChrome();
    const viewports = scenario.viewports?.length ? scenario.viewports : [{ name: "desktop", width: 1280, height: 900 }];
    client = await createPage(scenario.url || "about:blank");
    for (const viewport of viewports) {
      await setViewport(client, viewport);
      for (const step of scenario.steps || []) {
        if (step.viewport && step.viewport !== viewport.name) continue;
        results.push(await runStep(client, scenario, step, viewport, artifacts));
      }
    }
  } catch (caught) {
    status = "failed";
    error = caught;
    results.push({ name: "Unhandled automation failure", action: "error", status: "failed" });
  } finally {
    if (client) {
      await client.send("Emulation.clearDeviceMetricsOverride").catch(() => undefined);
      client.close();
      await fetch(`http://127.0.0.1:${port}/json/close/${client.targetId}`).catch(() => undefined);
    }
    if (chrome) chrome.kill();
  }
  const endedAt = new Date().toISOString();
  const report = renderReport({ scenario, results, artifacts, status, error, startedAt, endedAt });
  await mkdir(dirname(reportPath), { recursive: true });
  await writeFile(reportPath, report);
  console.log(reportPath);
  if (status !== "passed") process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
