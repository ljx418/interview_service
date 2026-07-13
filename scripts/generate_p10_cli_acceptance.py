from __future__ import annotations

import html
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/P10_CLI_ACCEPTANCE_REPORT.html"
EVIDENCE = ROOT / "docs/reports/evidence/p10_cli"
PORT = int(os.environ.get("JOBPILOT_P10_ACCEPTANCE_PORT", "8765"))
API_URL = f"http://127.0.0.1:{PORT}"


def run(command: list[str], *, timeout: int = 30) -> dict:
    started = time.time()
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return {
        "command": " ".join(command),
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "duration_ms": int((time.time() - started) * 1000),
    }


def wait_health(timeout_seconds: int = 20) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{API_URL}/api/health", timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def start_api() -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("JOBPILOT_LLM_PROVIDER", "mock")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "services.api.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def html_escape(value: str) -> str:
    return html.escape(value or "")


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    workspace = ROOT / ".jobpilot_workspace"
    commands: list[dict] = []

    commands.append(run(["./jobpilot", "--help"]))
    commands.append(run(["./jobpilot", "--api-url", "http://127.0.0.1:9", "workspace", "status", "--workspace", str(workspace)]))

    server = start_api()
    try:
        if not wait_health():
            raise RuntimeError("FastAPI acceptance server did not become healthy")
        commands.extend(
            [
                run(["./jobpilot", "--api-url", API_URL, "--json", "workspace", "status", "--workspace", str(workspace)]),
                run(["./jobpilot", "--api-url", API_URL, "--json", "demo", "run", "--example", "--workspace", str(workspace)], timeout=90),
                run(["./jobpilot", "--api-url", API_URL, "--json", "jobs", "list", "--workspace", str(workspace)]),
                run(["./jobpilot", "--api-url", API_URL, "--json", "artifacts", "list", "--workspace", str(workspace)]),
                run(["./jobpilot", "--json", "reports", "open", "--no-browser"]),
                run(["./jobpilot", "reports", "open", "generate-report"]),
            ]
        )
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    evidence_json = EVIDENCE / "p10_cli_command_evidence.json"
    evidence_json.write_text(json.dumps(commands, ensure_ascii=False, indent=2), encoding="utf-8")

    expected = {
        "help": commands[0]["exit_code"] == 0,
        "service_unavailable": commands[1]["exit_code"] == 2,
        "workspace_status": any("workspace status" in item["command"] and item["exit_code"] == 0 and "--json" in item["command"] for item in commands),
        "demo": any("demo run" in item["command"] and item["exit_code"] == 0 for item in commands),
        "jobs": any("jobs list" in item["command"] and item["exit_code"] == 0 for item in commands),
        "artifacts": any("artifacts list" in item["command"] and item["exit_code"] == 0 for item in commands),
        "reports": any("reports open --no-browser" in item["command"] and item["exit_code"] == 0 for item in commands),
        "safety": commands[-1]["exit_code"] == 4,
    }
    all_passed = all(expected.values())

    rows = "\n".join(
        f"<tr><td><code>{html_escape(item['command'])}</code></td><td>{item['exit_code']}</td><td><pre>{html_escape(item['stdout'][:1600])}</pre></td><td><pre>{html_escape(item['stderr'][:1600])}</pre></td></tr>"
        for item in commands
    )
    checks = "\n".join(
        f"<tr><td>{html_escape(key)}</td><td>{'通过' if value else '失败'}</td></tr>"
        for key, value in expected.items()
    )

    REPORT.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>P10-CLI 自动化验收报告</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #17201b; background: #f7f8f5; }}
    h1, h2 {{ color: #173b34; }}
    .card {{ background: #fff; border: 1px solid #d8ded6; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #d8ded6; padding: 10px; vertical-align: top; }}
    th {{ background: #edf3ee; text-align: left; }}
    code {{ background: #eef3ef; padding: 2px 5px; border-radius: 4px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; max-height: 260px; overflow: auto; }}
    .pass {{ color: #166534; font-weight: 700; }}
    .warn {{ color: #9a3412; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>P10-CLI 自动化验收报告</h1>
  <div class="card">
    <p><strong>验收结论：</strong><span class="{'pass' if all_passed else 'warn'}">{'通过' if all_passed else '未通过'}</span></p>
    <p>本报告验证 P10-CLI 本地命令入口，不代表 MCP、真实 provider、真实个人资料、招聘平台抓取、ASR、自动投递或 SaaS 已通过。</p>
    <p>数据边界：当前仓库真实 <code>.jobpilot_workspace</code>、<code>docs/reports</code>、本地 FastAPI API、examples/fixture。</p>
  </div>
  <h2>目标架构与当前实现</h2>
  <div class="card">
    <p>目标架构：薄 CLI → 本地 FastAPI → Domain Tools → SQLite Workspace / Artifact / Evidence。</p>
    <p>当前实现：<code>services/cli/main.py</code> 提供 CLI presentation/application/adapter；根命令 <code>./jobpilot</code> 调用该模块；CLI 不自动启动 FastAPI。</p>
  </div>
  <h2>验收检查</h2>
  <table><tr><th>检查项</th><th>结果</th></tr>{checks}</table>
  <h2>命令证据</h2>
  <table><tr><th>命令</th><th>exit code</th><th>stdout</th><th>stderr</th></tr>{rows}</table>
  <h2>未验证范围</h2>
  <ul>
    <li>未调用真实 provider。</li>
    <li>未读取未授权真实个人资料目录。</li>
    <li>未登录、抓取或联系招聘平台。</li>
    <li>未实现 MCP server、ASR、会议平台、自动投递或 SaaS。</li>
    <li><code>reports open</code> 未生成报告，只定位已有报告。</li>
  </ul>
  <p>结构化证据：<code>{html_escape(str(evidence_json.relative_to(ROOT)))}</code></p>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(REPORT)
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
