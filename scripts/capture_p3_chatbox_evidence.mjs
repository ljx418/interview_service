import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const DEBUG_PORT = process.env.CHROME_DEBUG_PORT || "9223";
const APP_URL = process.env.CHATBOX_URL || "http://127.0.0.1:5174/";
const OUT_DIR = resolve("docs/reports/evidence");
const WORKSPACE_ROOT = process.env.P3_EVIDENCE_WORKSPACE_ROOT || `/private/tmp/jobpilot-p3-evidence-${Date.now()}`;

const jdText = `# Junior Frontend Developer

Company: Example Labs

We are looking for a Junior Frontend Developer to build responsive product features with React, JavaScript, HTML/CSS, and REST APIs.

## Responsibilities
- Build reusable UI components
- Work with backend APIs
- Fix bugs and improve user experience

## Must Have
- React
- JavaScript
- HTML/CSS
- Git

## Nice To Have
- TypeScript
- Testing experience`;

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

async function getJson(path) {
  const response = await fetch(`http://127.0.0.1:${DEBUG_PORT}${path}`);
  if (!response.ok) {
    throw new Error(`Chrome debug endpoint failed: ${response.status} ${path}`);
  }
  return response.json();
}

class CdpClient {
  constructor(wsUrl) {
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
      const listeners = this.events.get(payload.method) || [];
      listeners.forEach((listener) => listener(payload.params));
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
      const listeners = this.events.get(method) || [];
      const wrapped = (params) => {
        this.events.set(
          method,
          (this.events.get(method) || []).filter((listener) => listener !== wrapped),
        );
        resolveEvent(params);
      };
      listeners.push(wrapped);
      this.events.set(method, listeners);
    });
  }

  close() {
    this.ws.close();
  }
}

async function createPage() {
  const targets = await getJson("/json/list");
  const page = targets.find((target) => target.type === "page") || targets[0];
  if (!page?.webSocketDebuggerUrl) {
    throw new Error("No Chrome page target found. Start Chrome with --remote-debugging-port first.");
  }
  const client = new CdpClient(page.webSocketDebuggerUrl);
  await client.open();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  return client;
}

async function setViewport(client, width, height) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width < 520,
  });
}

async function navigate(client, width, height) {
  await setViewport(client, width, height);
  const load = client.once("Page.loadEventFired");
  const url = `${APP_URL}?workspace_root=${encodeURIComponent(WORKSPACE_ROOT)}`;
  await client.send("Page.navigate", { url });
  await load;
  await waitForText(client, "Session ready", 10000);
}

async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || "Runtime.evaluate failed");
  }
  return result.result?.value;
}

async function waitForText(client, text, timeoutMs = 8000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const found = await evaluate(client, `document.body.innerText.includes(${JSON.stringify(text)})`);
    if (found) return;
    await delay(250);
  }
  throw new Error(`Timed out waiting for text: ${text}`);
}

async function sendChat(client, text) {
  await evaluate(
    client,
    `(() => {
      const textarea = document.querySelector('textarea');
      const button = document.querySelector('button.send');
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      setter.call(textarea, ${JSON.stringify(text)});
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      button.click();
      return true;
    })()`,
  );
}

async function screenshot(client, fileName, width, height) {
  await setViewport(client, width, height);
  await delay(500);
  const result = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
  });
  await writeFile(resolve(OUT_DIR, fileName), Buffer.from(result.data, "base64"));
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  const client = await createPage();
  try {
    await navigate(client, 1280, 900);
    await screenshot(client, "p3_chatbox_initial_1280.png", 1280, 900);

    await sendChat(client, "生成申请包");
    await waitForText(client, "请先粘贴一个 JD");
    await screenshot(client, "p3_chatbox_error_state_1280.png", 1280, 900);

    await sendChat(client, jdText);
    await waitForText(client, "我已解析岗位并生成适合度分析");
    await screenshot(client, "p3_chatbox_response_1280.png", 1280, 900);
    await screenshot(client, "p3_chatbox_narrow_720.png", 720, 900);
    await screenshot(client, "p3_chatbox_mobile_390.png", 390, 900);
  } finally {
    client.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
