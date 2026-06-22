import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const DEBUG_PORT = process.env.CHROME_DEBUG_PORT || "9223";
const APP_URL = process.env.CHATBOX_URL || "http://127.0.0.1:5173/";
const OUT_DIR = resolve("docs/reports/evidence");
const WORKSPACE_ROOT = process.env.P4_EVIDENCE_WORKSPACE_ROOT || `/private/tmp/jobpilot-p4-evidence-${Date.now()}`;

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

async function getJson(path) {
  const response = await fetch(`http://127.0.0.1:${DEBUG_PORT}${path}`);
  if (!response.ok) throw new Error(`Chrome debug endpoint failed: ${response.status} ${path}`);
  return response.json();
}

async function putJson(path) {
  const response = await fetch(`http://127.0.0.1:${DEBUG_PORT}${path}`, { method: "PUT" });
  if (!response.ok) throw new Error(`Chrome debug endpoint failed: ${response.status} ${path}`);
  return response.json();
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
  const page = await putJson(`/json/new?${encodeURIComponent(APP_URL)}`);
  await delay(500);
  if (!page?.webSocketDebuggerUrl) throw new Error("No Chrome page target found. Start Chrome with --remote-debugging-port first.");
  const client = new CdpClient(page.webSocketDebuggerUrl, page.id);
  await client.open();
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  return client;
}

async function closeTarget(targetId) {
  if (!targetId) return;
  await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/close/${targetId}`).catch(() => undefined);
}

async function setViewport(client, width, height) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width < 520,
  });
}

async function clearViewportOverride(client) {
  await client.send("Emulation.clearDeviceMetricsOverride");
  await client.send("Emulation.setTouchEmulationEnabled", { enabled: false });
}

async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Runtime.evaluate failed");
  return result.result?.value;
}

async function waitForText(client, text, timeoutMs = 10000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const found = await evaluate(client, `document.body.innerText.includes(${JSON.stringify(text)})`);
    if (found) return;
    await delay(250);
  }
  throw new Error(`Timed out waiting for text: ${text}`);
}

async function navigate(client, width, height) {
  await setViewport(client, width, height);
  const load = client.once("Page.loadEventFired");
  const url = `${APP_URL}?workspace_root=${encodeURIComponent(WORKSPACE_ROOT)}`;
  await client.send("Page.navigate", { url });
  await load;
  await waitForText(client, "外部模型未调用", 10000);
}

async function screenshot(client, fileName, width, height) {
  await setViewport(client, width, height);
  await delay(700);
  const result = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
  });
  await writeFile(resolve(OUT_DIR, fileName), Buffer.from(result.data, "base64"));
}

async function runExample(client) {
  await evaluate(
    client,
    `(() => {
      const candidates = Array.from(document.querySelectorAll('.prompt-card, button'));
      const target = candidates.find((node) => node.innerText.includes('运行示例路径') || node.innerText.includes('跑示例路径'));
      target?.click();
      return Boolean(target);
    })()`,
  );
  await waitForText(client, "申请包草稿", 15000);
}

async function triggerRecoverableError(client) {
  await evaluate(
    client,
    `(() => {
      const input = document.querySelector('textarea[aria-label="对话输入框"]');
      const button = document.querySelector('button[aria-label="发送任务"]');
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      setter.call(input, '生成申请包');
      input.dispatchEvent(new Event('input', { bubbles: true }));
      button.click();
      return true;
    })()`,
  );
  await waitForText(client, "请先粘贴一个 JD", 10000);
  await waitForText(client, "补充 JD", 10000);
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  const client = await createPage();
  try {
    await navigate(client, 1600, 1000);
    await screenshot(client, "p4_workbench_initial_1200.png", 1200, 900);
    await screenshot(client, "p4_workbench_initial_1280.png", 1280, 900);
    await screenshot(client, "p4_workbench_initial_1440.png", 1440, 960);
    await screenshot(client, "p4_workbench_initial_1600.png", 1600, 1000);
    await screenshot(client, "p4_workbench_initial_1920.png", 1920, 1080);
    await triggerRecoverableError(client);
    await screenshot(client, "p4_workbench_error_recovery_1200.png", 1200, 900);
    await screenshot(client, "p4_workbench_error_recovery_1280.png", 1280, 900);
    await runExample(client);
    await screenshot(client, "p4_workbench_completed_1200.png", 1200, 900);
    await screenshot(client, "p4_workbench_completed_1280.png", 1280, 900);
    await screenshot(client, "p4_workbench_completed_1440.png", 1440, 960);
    await screenshot(client, "p4_workbench_completed_1600.png", 1600, 1000);
    await screenshot(client, "p4_workbench_completed_1920.png", 1920, 1080);
    await screenshot(client, "p4_workbench_narrow_720.png", 720, 900);
    await screenshot(client, "p4_workbench_mobile_390.png", 390, 900);
  } finally {
    await clearViewportOverride(client).catch(() => undefined);
    const targetId = client.targetId;
    client.close();
    await closeTarget(targetId);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
