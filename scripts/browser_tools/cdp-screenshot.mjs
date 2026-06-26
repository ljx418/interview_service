#!/usr/bin/env node
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const args = new Map();
for (let index = 2; index < process.argv.length; index += 1) {
  const item = process.argv[index];
  if (!item.startsWith("--")) continue;
  const [key, inlineValue] = item.slice(2).split("=", 2);
  const value = inlineValue ?? process.argv[index + 1];
  args.set(key, value);
  if (inlineValue === undefined) index += 1;
}

const url = args.get("url") || process.argv[2] || "about:blank";
const output = resolve(args.get("output") || process.argv[3] || "/tmp/cdp-screenshot.png");
const port = args.get("port") || process.env.CHROME_DEBUG_PORT || "9223";
const width = Number(args.get("width") || process.env.SCREENSHOT_WIDTH || 1280);
const height = Number(args.get("height") || process.env.SCREENSHOT_HEIGHT || 900);

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

async function requestJson(path, init) {
  const response = await fetch(`http://127.0.0.1:${port}${path}`, init);
  if (!response.ok) throw new Error(`Chrome DevTools request failed: ${response.status} ${path}`);
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
      const listeners = this.events.get(method) || [];
      const wrapped = (params) => {
        this.events.set(method, (this.events.get(method) || []).filter((listener) => listener !== wrapped));
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

const target = await requestJson(`/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
if (!target.webSocketDebuggerUrl) throw new Error("Chrome target did not expose a WebSocket debugger URL.");
const client = new CdpClient(target.webSocketDebuggerUrl);
await client.open();

try {
  await client.send("Page.enable");
  await client.send("Runtime.enable");
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width < 520,
  });
  const load = client.once("Page.loadEventFired");
  await client.send("Page.navigate", { url });
  await load;
  await delay(Number(args.get("delay") || 700));
  const screenshot = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
  });
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, Buffer.from(screenshot.data, "base64"));
  console.log(output);
} finally {
  await client.send("Emulation.clearDeviceMetricsOverride").catch(() => undefined);
  await client.send("Emulation.setTouchEmulationEnabled", { enabled: false }).catch(() => undefined);
  client.close();
  await fetch(`http://127.0.0.1:${port}/json/close/${target.id}`).catch(() => undefined);
}
