from __future__ import annotations

import html
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.api.main import app

REPORT = ROOT / "docs/reports/P11_MARKET_PROVIDER_OPTIN_ACCEPTANCE_REPORT.html"
EVIDENCE = ROOT / "docs/reports/evidence/p11_market_provider"
API_PORT = int(os.environ.get("JOBPILOT_P11_ACCEPTANCE_API_PORT", "18111"))
VITE_PORT = int(os.environ.get("JOBPILOT_P11_ACCEPTANCE_VITE_PORT", "5175"))
API_URL = f"http://127.0.0.1:{API_PORT}"
VITE_URL = f"http://127.0.0.1:{VITE_PORT}"


def run(command: list[str], *, timeout: int = 60) -> dict:
    started = time.time()
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return {
        "command": " ".join(command),
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "duration_ms": int((time.time() - started) * 1000),
    }


def html_escape(value: object) -> str:
    return html.escape(str(value or ""))


def wait_url(url: str, timeout_seconds: int = 20) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if 200 <= resp.status < 500:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def drawio_parse() -> dict:
    path = ROOT / "docs/active/jobpilot-p11-market-provider-optin-gap.drawio"
    try:
        root = ET.parse(path).getroot()
        pages = root.findall(".//diagram")
        return {"path": str(path.relative_to(ROOT)), "ok": True, "page_count": len(pages), "error": ""}
    except Exception as exc:
        return {"path": str(path.relative_to(ROOT)), "ok": False, "page_count": 0, "error": str(exc)}


def api_evidence() -> dict:
    client = TestClient(app)
    workspace_root = Path(tempfile.mkdtemp(prefix="jobpilot-p11-acceptance-"))
    init = client.post(
        "/api/workspace/init",
        json={"name": "p11-acceptance", "root_path": str(workspace_root), "llm_provider": "mock", "privacy_mode": "local_first"},
    )
    workspace_id = init.json()["data"]["workspace_id"]
    status = client.get("/api/market/providers/status", params={"workspace_id": workspace_id}).json()["data"]
    fixture_check = client.post(
        "/api/market/providers/check",
        json={"workspace_id": workspace_id, "provider_id": "fixture_local", "confirm": False},
    ).json()["data"]
    search = client.post(
        "/api/market/search-runs",
        json={
            "workspace_id": workspace_id,
            "query": "北京 上海 LLM 前端岗位薪资",
            "city_filters": ["北京", "上海"],
            "salary_range": "20-40k",
            "tech_stack": ["React", "TypeScript", "LLM"],
            "provider_ids": ["fixture_local"],
            "source_policy": "fixture",
        },
    ).json()["data"]
    run_id = search["run_id"]
    snapshot = client.get(f"/api/market/snapshots/{run_id}", params={"workspace_id": workspace_id}).json()["data"]
    source_ref = client.get(f"/api/market/source-refs/{search['source_refs'][0]}", params={"workspace_id": workspace_id}).json()["data"]
    opt_in_reject = client.post(
        "/api/market/search-runs",
        json={"workspace_id": workspace_id, "query": "真实 provider 查询", "provider_ids": ["adzuna_opt_in"], "source_policy": "opt_in_api"},
    )
    return {
        "workspace_id": workspace_id,
        "provider_status": status,
        "fixture_check": fixture_check,
        "search_run": search,
        "snapshot": snapshot,
        "source_ref": source_ref,
        "opt_in_reject_status_code": opt_in_reject.status_code,
        "opt_in_reject": opt_in_reject.json().get("detail", {}),
    }


def start_api() -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("JOBPILOT_LLM_PROVIDER", "mock")
    env.setdefault("JOBPILOT_ALLOW_MARKET_PROVIDER_CALL", "0")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "services.api.main:app", "--host", "127.0.0.1", "--port", str(API_PORT)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def start_vite() -> subprocess.Popen:
    env = os.environ.copy()
    env["VITE_API_BASE_URL"] = API_URL
    return subprocess.Popen(
        ["npm", "--prefix", "apps/chatbox", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(VITE_PORT), "--strictPort"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def windows_chrome_screenshot(url: str, screenshot_path: Path) -> dict:
    candidates = [
        Path("/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path("/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe"),
    ]
    browser = next((path for path in candidates if path.exists()), None)
    if not browser:
        return {"ok": False, "path": "", "error": "No Windows Chrome/Edge executable found"}
    try:
        win_screenshot = subprocess.run(["wslpath", "-w", str(screenshot_path)], cwd=ROOT, capture_output=True, text=True, timeout=5).stdout.strip()
        proc = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--window-size=1440,980",
                "--hide-scrollbars",
                "--virtual-time-budget=7000",
                f"--screenshot={win_screenshot}",
                url,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=35,
        )
        if proc.returncode == 0 and screenshot_path.exists() and screenshot_path.stat().st_size > 0:
            return {"ok": True, "path": str(screenshot_path.relative_to(ROOT)), "error": ""}
        return {"ok": False, "path": "", "error": (proc.stderr or proc.stdout or f"Chrome exited {proc.returncode}")[:1200]}
    except Exception as exc:
        return {"ok": False, "path": "", "error": str(exc)}


def screenshot_evidence() -> dict:
    screenshot_path = EVIDENCE / "p11_chatbox_market_panel.png"
    api_proc = start_api()
    vite_proc = None
    try:
        if not wait_url(f"{API_URL}/api/health"):
            return {"ok": False, "path": "", "error": "FastAPI server did not become healthy"}
        vite_proc = start_vite()
        if not wait_url(VITE_URL):
            return {"ok": False, "path": "", "error": "Vite server did not become healthy"}
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            return {"ok": False, "path": "", "error": f"Playwright unavailable: {exc}"}
        workspace_root = tempfile.mkdtemp(prefix="jobpilot-p11-browser-")
        url = f"{VITE_URL}/?workspace_root={urllib.parse.quote(workspace_root)}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 980}, device_scale_factor=1)
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.get_by_role("textbox").fill("帮我汇总北京和上海 LLM 前端岗位薪资和城市机会")
            page.get_by_role("button", name="发送任务").click()
            page.wait_for_timeout(1800)
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()
        return {"ok": True, "path": str(screenshot_path.relative_to(ROOT)), "error": ""}
    except Exception as exc:
        fallback_url = f"{VITE_URL}/?workspace_root={urllib.parse.quote(tempfile.mkdtemp(prefix='jobpilot-p11-browser-'))}"
        fallback = windows_chrome_screenshot(fallback_url, screenshot_path)
        if fallback["ok"]:
            fallback["fallback"] = "windows_chrome_headless"
            return fallback
        return {"ok": False, "path": "", "error": f"Playwright failed: {exc}; Windows Chrome fallback failed: {fallback['error']}"}
    finally:
        for proc in [vite_proc, api_proc]:
            if not proc:
                continue
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


def command_table(commands: list[dict]) -> str:
    return "\n".join(
        "<tr>"
        f"<td><code>{html_escape(item['command'])}</code></td>"
        f"<td>{item['exit_code']}</td>"
        f"<td><pre>{html_escape(item['stdout'][:1800])}</pre></td>"
        f"<td><pre>{html_escape(item['stderr'][:1800])}</pre></td>"
        "</tr>"
        for item in commands
    )


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    commands = [
        run([sys.executable, "-m", "pytest", "tests/evals/test_p11_market_provider_optin_eval.py", "-q"], timeout=90),
        run(["npm", "--prefix", "apps/chatbox", "run", "build"], timeout=120),
    ]
    drawio = drawio_parse()
    api = api_evidence()
    screenshot = screenshot_evidence()
    evidence = {"commands": commands, "drawio": drawio, "api": api, "screenshot": screenshot}
    evidence_path = EVIDENCE / "p11_market_provider_acceptance_evidence.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")

    expected = {
        "P11 eval": commands[0]["exit_code"] == 0,
        "Chatbox build": commands[1]["exit_code"] == 0,
        "drawio XML parse": drawio["ok"] and drawio["page_count"] <= 8,
        "provider status redacted": api["provider_status"]["can_claim_real_market"] is False,
        "fixture check no external call": api["fixture_check"]["called"] is False and api["fixture_check"]["raw_provider_response_included"] is False,
        "search run fallback is explicit": api["search_run"]["status"] == "fallback" and "Level 1" in api["search_run"]["boundary_note"],
        "snapshot has source refs": bool(api["snapshot"]["source_refs"]) and bool(api["snapshot"]["low_confidence_notes"]),
        "opt-in provider blocked without consent": api["opt_in_reject_status_code"] == 400 and api["opt_in_reject"].get("error_code") == "CONSENT_REQUIRED",
    }
    all_passed = all(expected.values())
    check_rows = "\n".join(f"<tr><td>{html_escape(key)}</td><td>{'通过' if value else '失败'}</td></tr>" for key, value in expected.items())
    screenshot_tool = "Windows Chrome headless fallback" if screenshot.get("fallback") else "Headless Playwright"
    screenshot_block = (
        f'<figure><img src="evidence/p11_market_provider/{html_escape(Path(screenshot["path"]).name)}" alt="P11 Chatbox 市场面板真实界面截图" /><figcaption>{html_escape(screenshot_tool)} 真实界面截图：{html_escape(screenshot["path"])}</figcaption></figure>'
        if screenshot["ok"]
        else f'<p class="warn">截图未生成：{html_escape(screenshot["error"])}</p>'
    )

    REPORT.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>P11 Market Provider Opt-in 自动化验收报告</title>
  <style>
    body {{ margin: 32px; background: #f6f8f4; color: #17201b; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    h1, h2 {{ color: #173b34; }}
    .card {{ background: #fff; border: 1px solid #d8ded6; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    .pass {{ color: #166534; font-weight: 800; }}
    .warn {{ color: #9a3412; font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; margin: 12px 0; }}
    th, td {{ border: 1px solid #d8ded6; padding: 10px; vertical-align: top; }}
    th {{ background: #edf3ee; text-align: left; }}
    code {{ background: #eef3ef; padding: 2px 5px; border-radius: 4px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; max-height: 260px; overflow: auto; }}
    img {{ max-width: 100%; border: 1px solid #d8ded6; border-radius: 8px; background: #fff; }}
    li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <h1>P11 Market Provider Opt-in 自动化验收报告</h1>
  <div class="card">
    <p><strong>验收结论：</strong><span class="{'pass' if all_passed else 'warn'}">{'Level 1 通过' if all_passed else '未通过'}</span></p>
    <p>本报告验证 P11 本地/记录数据市场 provider opt-in 边界。它不代表真实市场 provider、全网 JD 搜索、招聘平台接入、ASR、MCP、自动投递或 SaaS 已通过。</p>
  </div>
  <h2>目标架构与当前实现</h2>
  <div class="card">
    <p>目标架构：UI/CLI → FastAPI Market Provider Boundary → JobSearchRunService / Normalizer / SourceRefBinder → SQLite Workspace → Evidence Report。</p>
    <p>当前实现：<code>services/market/provider.py</code> 提供 provider registry、policy gate、fixture/manual/public Level1 search run、snapshot 和 source refs；<code>services/api/main.py</code> 暴露 P11 API；<code>apps/chatbox/src/main.tsx</code> 与 <code>services/cli/main.py</code> 已读取 market provider 状态。</p>
  </div>
  <h2>验收检查</h2>
  <table><tr><th>检查项</th><th>结果</th></tr>{check_rows}</table>
  <h2>真实界面截图证据</h2>
  <div class="card">{screenshot_block}</div>
  <h2>API 证据摘要</h2>
  <table>
    <tr><th>项目</th><th>证据</th></tr>
    <tr><td>Provider 状态</td><td><pre>{html_escape(json.dumps(api['provider_status'], ensure_ascii=False, indent=2)[:2200])}</pre></td></tr>
    <tr><td>Search Run</td><td><pre>{html_escape(json.dumps(api['search_run'], ensure_ascii=False, indent=2)[:2200])}</pre></td></tr>
    <tr><td>Snapshot</td><td><pre>{html_escape(json.dumps(api['snapshot'], ensure_ascii=False, indent=2)[:2200])}</pre></td></tr>
    <tr><td>Opt-in 拒绝</td><td><pre>{html_escape(json.dumps(api['opt_in_reject'], ensure_ascii=False, indent=2))}</pre></td></tr>
  </table>
  <h2>命令证据</h2>
  <table><tr><th>命令</th><th>exit code</th><th>stdout</th><th>stderr</th></tr>{command_table(commands)}</table>
  <h2>未验证范围</h2>
  <ul>
    <li>未执行真实市场 provider 调用；没有合法凭据和用户确认，因此不能声明 Level 2。</li>
    <li>未登录、抓取或联系 BOSS、猎聘、拉勾、LinkedIn 等招聘平台。</li>
    <li>未启动长期爬虫、队列、ASR、MCP server、自动投递、自动沟通或 SaaS。</li>
    <li>未存储 API Key、provider secret 或完整 raw provider response。</li>
  </ul>
  <p>完整结构化证据：<code>{html_escape(str(evidence_path.relative_to(ROOT)))}</code></p>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(REPORT)
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
