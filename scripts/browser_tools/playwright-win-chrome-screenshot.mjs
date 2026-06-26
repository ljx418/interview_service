#!/usr/bin/env node
import { createRequire } from "node:module";
import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { spawn } from "node:child_process";

const require = createRequire(import.meta.url);
const playwrightRoot = process.env.PLAYWRIGHT_GLOBAL_ROOT || "/home/administrator/.npm-global/lib/node_modules/playwright";
const { chromium } = require(playwrightRoot);

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
const output = resolve(args.get("output") || process.argv[3] || "/tmp/playwright-win-chrome-screenshot.png");
const width = Number(args.get("width") || 1280);
const height = Number(args.get("height") || 900);
const chromePath = process.env.CHROME_PATH || "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe";
const port = Number(args.get("port") || process.env.CHROME_DEBUG_PORT || 9231);
const userDataDir = process.env.CHROME_USER_DATA_DIR || `/tmp/jobpilot-playwright-win-chrome-${port}`;

const chrome = spawn(
  chromePath,
  [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-dev-shm-usage",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "about:blank",
  ],
  { stdio: "ignore" },
);

async function waitForChrome() {
  const deadline = Date.now() + 10_000;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return;
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 200));
  }
  throw lastError || new Error(`Chrome did not start on port ${port}`);
}

await waitForChrome();
const browser = await chromium.connectOverCDP(`http://127.0.0.1:${port}`);

try {
  const context = browser.contexts()[0] || (await browser.newContext());
  const page = await context.newPage();
  await page.setViewportSize({ width, height });
  await page.goto(url, { waitUntil: "networkidle" });
  await mkdir(dirname(output), { recursive: true });
  await page.screenshot({ path: output, fullPage: true });
  console.log(output);
} finally {
  await browser.close();
  chrome.kill();
}
