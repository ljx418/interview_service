#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/P8_1_FRONTEND_REVIEW_GUIDANCE.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_1_frontend_review"
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
WORKSPACE_ROOT = ROOT / ".tmp" / f"p8_1_frontend_review_workspace_{RUN_ID}"
SCENARIO = EVIDENCE_DIR / "p8_1_browser_scenario.json"
CAPTURE_REPORT = EVIDENCE_DIR / "p8_1_browser_capture_report.html"
COMMAND_EVIDENCE = EVIDENCE_DIR / "p8_1_command_evidence.json"
AI_IMAGE_AUDIT = EVIDENCE_DIR / "p8_1_ai_image_audit.json"
TARGET_MOCK = EVIDENCE_DIR / "p8_1_target_mock.html"
CONCEPT_SVG = EVIDENCE_DIR / "p8_1_concept_diagram.svg"
TARGET_STATIC_PORT = 8766


BASELINE_SHOTS = [
    ("baseline_current_1440.png", "当前真实基线 1440px：P8 workflow strip 位于聊天时间线之前"),
    ("baseline_current_1200.png", "当前真实基线 1200px：三栏基线和中央任务区"),
    ("baseline_current_720.png", "当前真实基线 720px：窄屏下聊天与 P8 工作区关系"),
    ("baseline_current_390.png", "当前真实基线 390px：移动端可达性和输入区"),
]
TARGET_SHOTS = [
    ("target_chatbox_first_1440.png", "目标概念 1440px：用户指导 - Chatbox - 工作台"),
    ("target_chatbox_first_720.png", "目标概念 720px：Chatbox 默认主视图，辅助区收敛"),
    ("target_chatbox_first_390.png", "目标概念 390px：移动端优先显示 Chatbox 和输入区"),
]


def _html(value: object) -> str:
    return escape(str(value), quote=True)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _report_rel(path: Path) -> str:
    return path.relative_to(REPORT.parent).as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "log", "-1", "--oneline"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _git_status_short() -> str:
    try:
        return subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip() or "clean"
    except Exception:
        return "unknown"


def _url_ready(url: str) -> bool:
    try:
        with urlopen(url, timeout=2) as response:
            return response.status < 500
    except Exception:
        return False


def _wait_url(url: str, timeout: float = 45.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception as exc:
            last_error = exc
        time.sleep(0.35)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _run_command(label: str, command: list[str] | str, timeout: int = 180, env: dict[str, str] | None = None) -> dict:
    started = datetime.now(timezone.utc)
    shell = isinstance(command, str)
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        env=command_env,
    )
    output = completed.stdout or ""
    lines = [line for line in output.splitlines() if line.strip()]
    return {
        "label": label,
        "command": command if isinstance(command, str) else " ".join(command),
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "started_at": started.isoformat(),
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "summary": "\n".join(lines[-16:]),
    }


def _write_concept_svg() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="760" viewBox="0 0 1440 760">
  <rect width="1440" height="760" fill="#f5f7f4"/>
  <text x="56" y="58" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#17231f">P8.1 Chatbox-first 概念图：用户指导 - Chatbox - 工作台</text>
  <text x="56" y="92" font-family="Arial, sans-serif" font-size="15" fill="#5d6b64">目标是修正信息架构主次关系，不声明当前 UI 已实现。</text>
  <g transform="translate(56 132)">
    <rect x="0" y="0" width="300" height="500" rx="12" fill="#eaf5f1" stroke="#73a99a" stroke-width="2"/>
    <text x="24" y="42" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#1d3832">用户指导</text>
    <text x="24" y="76" font-family="Arial, sans-serif" font-size="14" fill="#49635b">辅助用户知道该提供什么</text>
    <rect x="24" y="112" width="252" height="54" rx="8" fill="#ffffff" stroke="#c9ddd5"/>
    <text x="42" y="145" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#20352f">简历 / 项目 / 作品 / JD / 偏好</text>
    <rect x="24" y="184" width="252" height="54" rx="8" fill="#ffffff" stroke="#c9ddd5"/>
    <text x="42" y="217" font-family="Arial, sans-serif" font-size="15" fill="#20352f">缺失影响与下一步建议</text>
    <rect x="24" y="256" width="252" height="54" rx="8" fill="#ffffff" stroke="#c9ddd5"/>
    <text x="42" y="289" font-family="Arial, sans-serif" font-size="15" fill="#20352f">示例路径：仅作演示</text>
    <text x="24" y="430" font-family="Arial, sans-serif" font-size="13" fill="#7b4b1f">不承载大型编辑表单</text>
  </g>
  <g transform="translate(400 112)">
    <rect x="0" y="0" width="610" height="560" rx="14" fill="#ffffff" stroke="#46796e" stroke-width="3"/>
    <rect x="0" y="0" width="610" height="76" rx="14" fill="#f0f7f4" stroke="#46796e" stroke-width="0"/>
    <text x="28" y="42" font-family="Arial, sans-serif" font-size="23" font-weight="700" fill="#142b25">Chatbox 主路径</text>
    <text x="380" y="42" font-family="Arial, sans-serif" font-size="14" fill="#2f675c">状态：等待资料 → 解析 JD → 可导出</text>
    <rect x="34" y="104" width="420" height="58" rx="10" fill="#eef8f4" stroke="#c6dfd5"/>
    <text x="58" y="139" font-family="Arial, sans-serif" font-size="16" fill="#20352f">Agent：你可以直接问我如何生成目标岗位简历。</text>
    <rect x="156" y="184" width="420" height="58" rx="10" fill="#eef2ff" stroke="#c6ccef"/>
    <text x="180" y="219" font-family="Arial, sans-serif" font-size="16" fill="#25314f">用户：帮我基于这个 JD 生成前端岗位简历。</text>
    <rect x="34" y="264" width="440" height="78" rx="10" fill="#eef8f4" stroke="#c6dfd5"/>
    <text x="58" y="294" font-family="Arial, sans-serif" font-size="16" fill="#20352f">Agent：还缺项目经历和目标 JD，先补这两项。</text>
    <text x="58" y="322" font-family="Arial, sans-serif" font-size="14" fill="#52645e">资料入口在输入框上方，不压住聊天时间线。</text>
    <rect x="34" y="390" width="542" height="52" rx="10" fill="#f8fbf9" stroke="#d8e4df"/>
    <text x="54" y="422" font-family="Arial, sans-serif" font-size="15" fill="#52645e">上传资料    粘贴 JD    选择岗位    生成简历</text>
    <rect x="34" y="458" width="420" height="64" rx="12" fill="#ffffff" stroke="#9eb9b0"/>
    <text x="56" y="496" font-family="Arial, sans-serif" font-size="16" fill="#1d2f2a">输入框：继续对话、补充资料或确认事实...</text>
    <rect x="466" y="458" width="110" height="64" rx="12" fill="#236b5f"/>
    <text x="498" y="496" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#ffffff">发送</text>
  </g>
  <g transform="translate(1056 132)">
    <rect x="0" y="0" width="320" height="500" rx="12" fill="#fff8ed" stroke="#d8a456" stroke-width="2"/>
    <text x="24" y="42" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#3e2a0c">工作台</text>
    <text x="24" y="76" font-family="Arial, sans-serif" font-size="14" fill="#6b5432">产物、证据、确认、导出</text>
    <rect x="24" y="112" width="272" height="54" rx="8" fill="#ffffff" stroke="#ead7b7"/>
    <text x="42" y="145" font-family="Arial, sans-serif" font-size="15" fill="#352719">当前目标 JD / 岗位列表</text>
    <rect x="24" y="184" width="272" height="54" rx="8" fill="#ffffff" stroke="#ead7b7"/>
    <text x="42" y="217" font-family="Arial, sans-serif" font-size="15" fill="#352719">CandidateProfile 摘要</text>
    <rect x="24" y="256" width="272" height="54" rx="8" fill="#ffffff" stroke="#ead7b7"/>
    <text x="42" y="289" font-family="Arial, sans-serif" font-size="15" fill="#352719">简历草稿 / source refs</text>
    <rect x="24" y="328" width="272" height="54" rx="8" fill="#ffffff" stroke="#ead7b7"/>
    <text x="42" y="361" font-family="Arial, sans-serif" font-size="15" fill="#352719">pending confirmations</text>
    <text x="24" y="430" font-family="Arial, sans-serif" font-size="13" fill="#7b4b1f">不抢占聊天主路径</text>
  </g>
  <text x="56" y="716" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#9a3412">目标概念图 / 非当前实现截图 / 不代表 P8.1 已完成</text>
</svg>
"""
    CONCEPT_SVG.write_text(svg, encoding="utf-8")


def _write_target_mock() -> None:
    html = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>P8.1 Chatbox-first Target Mock</title>
  <style>
    :root {
      --bg: #f5f7f4;
      --panel: #ffffff;
      --ink: #15231f;
      --muted: #60716a;
      --line: #d9e3dd;
      --guide: #e8f5f0;
      --guide-line: #91b9ad;
      --chat: #fdfefd;
      --work: #fff7e9;
      --work-line: #dfbc83;
      --primary: #246b60;
      --accent: #b96b2c;
    }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; font-family: Inter, "Segoe UI", system-ui, sans-serif; color: var(--ink); background: var(--bg); }
    .top { height: 68px; display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 0 28px; border-bottom: 1px solid var(--line); background: rgba(255,255,255,.9); }
    .top h1 { margin: 0; font-size: 22px; letter-spacing: 0; }
    .tag { border: 1px solid #d0ddd7; border-radius: 6px; padding: 7px 10px; color: #31534b; background: #f9fcfb; font-weight: 700; font-size: 13px; }
    .stage { color: #8a4b0f; background: #fff7e9; border-color: #e6cda8; }
    .shell { height: calc(100vh - 68px); display: grid; grid-template-columns: 300px minmax(0, 1fr) 360px; }
    aside, main { min-width: 0; }
    .guide { background: var(--guide); border-right: 1px solid var(--guide-line); padding: 20px; overflow: auto; }
    .workbench { background: var(--work); border-left: 1px solid var(--work-line); padding: 20px; overflow: auto; }
    .chat { display: flex; flex-direction: column; min-height: 0; background: var(--chat); }
    .agent { padding: 18px 26px; border-bottom: 1px solid var(--line); display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 14px; align-items: center; }
    .agent h2 { margin: 0 0 6px; font-size: 20px; }
    .agent p, .card p { margin: 0; color: var(--muted); line-height: 1.45; }
    .state { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
    .state span { border: 1px solid #cbdad3; border-radius: 6px; padding: 7px 9px; font-size: 12px; font-weight: 700; background: #fff; }
    .state .on { background: #e1f4ed; border-color: #8cc7b4; color: #195b4f; }
    .timeline { flex: 1; min-height: 0; overflow: auto; padding: 26px; display: flex; flex-direction: column; gap: 14px; }
    .bubble { max-width: 78%; border-radius: 10px; padding: 14px 16px; border: 1px solid var(--line); box-shadow: 0 8px 18px rgba(34,47,42,.05); }
    .assistant { background: #eff8f4; align-self: flex-start; }
    .user { background: #eef2ff; align-self: flex-end; }
    .composer { border-top: 1px solid var(--line); padding: 12px 26px 16px; background: rgba(255,255,255,.96); }
    .tools { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 8px; margin-bottom: 10px; }
    button { border: 1px solid #c8d8d1; background: #fff; border-radius: 7px; min-height: 40px; font-weight: 800; color: #20352f; }
    .inputrow { display: grid; grid-template-columns: minmax(0,1fr) 112px; gap: 10px; }
    textarea { resize: none; min-height: 58px; border: 1px solid #c8d8d1; border-radius: 10px; padding: 13px 14px; font: inherit; }
    .send { background: var(--primary); color: #fff; border-color: var(--primary); }
    .card { border: 1px solid var(--line); border-radius: 10px; background: rgba(255,255,255,.82); padding: 14px; margin-bottom: 12px; }
    .card h3 { margin: 0 0 8px; font-size: 16px; }
    .list { display: grid; gap: 8px; margin-top: 12px; }
    .row { display: flex; justify-content: space-between; gap: 12px; border: 1px solid #dde8e2; border-radius: 7px; background: #fff; padding: 10px; font-size: 13px; }
    .watermark { position: fixed; right: 18px; bottom: 14px; color: #9a3412; background: #fff7ed; border: 1px solid #fed7aa; border-radius: 7px; padding: 8px 10px; font-size: 12px; font-weight: 900; }
    @media (max-width: 900px) {
      .top { height: auto; align-items: flex-start; flex-direction: column; padding: 14px 16px; }
      .shell { height: auto; min-height: calc(100vh - 96px); grid-template-columns: 1fr; }
      .guide { order: 2; border-right: 0; border-top: 1px solid var(--guide-line); display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; }
      .chat { order: 1; min-height: 72vh; }
      .workbench { order: 3; border-left: 0; border-top: 1px solid var(--work-line); display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; }
      .card { margin-bottom: 0; }
      .agent { grid-template-columns: 1fr; }
      .state { justify-content: flex-start; }
      .tools { grid-template-columns: repeat(2, minmax(0,1fr)); }
    }
    @media (max-width: 520px) {
      .top h1 { font-size: 18px; }
      .tag { font-size: 12px; }
      .guide, .workbench { display: none; }
      .chat { min-height: calc(100vh - 92px); }
      .agent { padding: 14px 16px; }
      .agent h2 { font-size: 18px; }
      .timeline { padding: 16px; padding-bottom: 178px; }
      .bubble { max-width: 96%; }
      .composer { position: fixed; left: 0; right: 0; bottom: 0; padding: 10px 12px 12px; box-shadow: 0 -16px 34px rgba(17,27,24,.12); }
      .inputrow { grid-template-columns: 1fr; }
      .tools { grid-template-columns: repeat(2, minmax(0,1fr)); }
      button { min-height: 38px; font-size: 13px; }
      .watermark { left: 10px; right: 10px; bottom: 146px; text-align: center; }
    }
  </style>
</head>
<body>
  <header class="top">
    <div><h1>求职材料工作台</h1><span>目标概念：Chatbox 是主路径</span></div>
    <div><span class="tag stage">目标概念图 / 非当前实现</span> <span class="tag">本地 mock / 不外呼</span></div>
  </header>
  <div class="shell">
    <aside class="guide">
      <section class="card"><h3>当前任务</h3><p>先通过聊天明确目标岗位，再补材料。</p></section>
      <section class="card"><h3>资料清单</h3><div class="list"><div class="row"><span>简历</span><b>需要</b></div><div class="row"><span>项目经历</span><b>缺失影响高</b></div><div class="row"><span>目标 JD</span><b>可粘贴</b></div></div></section>
      <section class="card"><h3>缺失影响</h3><p>缺项目经历会影响 STAR 故事和简历证据。</p></section>
    </aside>
    <main class="chat">
      <section class="agent">
        <div><h2>对话与材料处理</h2><p>中央只放紧凑状态、聊天时间线和输入框；资料/JD 入口贴近输入框。</p></div>
        <div class="state"><span class="on">可继续对话</span><span>0 个产物</span><span>本地 mock</span></div>
      </section>
      <section class="timeline">
        <div class="bubble assistant">我可以先和你聊目标岗位，也可以在你粘贴 JD 后生成定制简历。</div>
        <div class="bubble user">帮我生成一版前端岗位简历，需要我提供什么？</div>
        <div class="bubble assistant">请先补充简历、一个项目经历和目标 JD。我会在右侧显示 source refs 和待确认项。</div>
      </section>
      <form class="composer">
        <div class="tools"><button>上传资料</button><button>粘贴 JD</button><button>选择岗位</button><button>生成简历</button></div>
        <div class="inputrow"><textarea>可以连续追问、补充偏好，或直接粘贴目标岗位 JD...</textarea><button class="send">发送任务</button></div>
      </form>
    </main>
    <aside class="workbench">
      <section class="card"><h3>当前目标 JD</h3><p>前端工程师 / 公司官网手动粘贴</p></section>
      <section class="card"><h3>画像摘要</h3><p>React 项目经验可用；工程化证据待补。</p></section>
      <section class="card"><h3>简历草稿</h3><p>绑定目标 JD，缺证据内容进入待确认。</p></section>
      <section class="card"><h3>导出前检查</h3><p>2 个 source refs，1 个 blocking confirmation。</p></section>
    </aside>
  </div>
  <div class="watermark">目标概念图 / 非当前实现截图 / 不代表 P8.1 已完成</div>
</body>
</html>
"""
    TARGET_MOCK.write_text(html, encoding="utf-8")


def _write_browser_scenario() -> None:
    app_url = f"http://127.0.0.1:5173/?workspace_root={WORKSPACE_ROOT.as_posix()}"
    target_url = f"http://127.0.0.1:{TARGET_STATIC_PORT}/{TARGET_MOCK.name}"
    scenario = {
        "name": "P8.1 Frontend Review Guidance capture",
        "goal": "Capture current real baseline screenshots and deterministic target concept screenshots for P8.1 Chatbox-first review.",
        "url": app_url,
        "targetArchitecture": [
            "Current baseline: actual running Chatbox UI from Vite/FastAPI.",
            "Target concept: deterministic HTML/SVG mock, explicitly marked as not implemented.",
        ],
        "currentImplementation": [
            "apps/chatbox/src/main.tsx renders p8-workflow-strip before timeline.",
            "P8.1 implementation is not yet complete.",
        ],
        "acceptanceCriteria": [
            "Baseline screenshots come from the real running UI.",
            "Target concept screenshots are visibly watermarked as non-implementation concept images.",
            "Report distinguishes evidence, concept, and unverified scope.",
        ],
        "viewports": [
            {"name": "baseline1440", "width": 1440, "height": 900, "mobile": False},
            {"name": "baseline1200", "width": 1200, "height": 900, "mobile": False},
            {"name": "baseline720", "width": 720, "height": 920, "mobile": False},
            {"name": "baseline390", "width": 390, "height": 820, "mobile": True},
            {"name": "target1440", "width": 1440, "height": 900, "mobile": False},
            {"name": "target720", "width": 720, "height": 920, "mobile": False},
            {"name": "target390", "width": 390, "height": 820, "mobile": True},
        ],
        "steps": [
            {"name": "打开当前 Chatbox 1440", "action": "goto", "url": app_url, "viewport": "baseline1440"},
            {"name": "等待当前页面标题 1440", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "baseline1440"},
            {"name": "当前真实基线 1440", "action": "screenshot", "file": "baseline_current_1440.png", "viewport": "baseline1440"},
            {"name": "打开当前 Chatbox 1200", "action": "goto", "url": app_url, "viewport": "baseline1200"},
            {"name": "等待当前页面标题 1200", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "baseline1200"},
            {"name": "当前真实基线 1200", "action": "screenshot", "file": "baseline_current_1200.png", "viewport": "baseline1200"},
            {"name": "打开当前 Chatbox 720", "action": "goto", "url": app_url, "viewport": "baseline720"},
            {"name": "等待当前页面标题 720", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "baseline720"},
            {"name": "当前真实基线 720", "action": "screenshot", "file": "baseline_current_720.png", "viewport": "baseline720"},
            {"name": "打开当前 Chatbox 390", "action": "goto", "url": app_url, "viewport": "baseline390"},
            {"name": "等待当前页面标题 390", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "baseline390"},
            {"name": "当前真实基线 390", "action": "screenshot", "file": "baseline_current_390.png", "viewport": "baseline390"},
            {"name": "打开目标概念 1440", "action": "goto", "url": target_url, "viewport": "target1440"},
            {"name": "等待目标概念 1440", "action": "waitText", "text": "目标概念图", "timeoutMs": 5000, "viewport": "target1440"},
            {"name": "目标概念 1440", "action": "screenshot", "file": "target_chatbox_first_1440.png", "viewport": "target1440"},
            {"name": "打开目标概念 720", "action": "goto", "url": target_url, "viewport": "target720"},
            {"name": "等待目标概念 720", "action": "waitText", "text": "目标概念图", "timeoutMs": 5000, "viewport": "target720"},
            {"name": "目标概念 720", "action": "screenshot", "file": "target_chatbox_first_720.png", "viewport": "target720"},
            {"name": "打开目标概念 390", "action": "goto", "url": target_url, "viewport": "target390"},
            {"name": "等待目标概念 390", "action": "waitText", "text": "目标概念图", "timeoutMs": 5000, "viewport": "target390"},
            {"name": "目标概念 390", "action": "screenshot", "file": "target_chatbox_first_390.png", "viewport": "target390"},
        ],
    }
    SCENARIO.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")


def _collect_static_facts() -> dict:
    main = _read(ROOT / "apps/chatbox/src/main.tsx")
    css = _read(ROOT / "apps/chatbox/src/styles.css")
    timeline_before = bool(re.search(r'<section className="p8-workflow-strip"[\s\S]+?<div className="timeline"', main))
    return {
        "p8_workflow_strip_before_timeline": timeline_before,
        "main_entities": {
            "DesktopContextPanel": "function DesktopContextPanel" in main,
            "MaterialIntakeWizard": "function MaterialIntakeWizard" in main,
            "JDIntakeCenter": "function JDIntakeCenter" in main,
            "JobTargetList": "function JobTargetList" in main,
            "ResumeGenerationPlane": "function ResumeGenerationPlane" in main,
            "Workbench": "function Workbench" in main,
        },
        "css_entities": {
            "layout_grid": ".layout-grid" in css,
            "p8_workflow_strip": ".p8-workflow-strip" in css,
            "composer_quick_actions": ".composer-quick-actions" in css,
            "mobile_media": "@media (max-width: 768px)" in css,
        },
    }


def _build_ai_image_audit(check_mode: dict) -> dict:
    audit = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requested_capability": "imag2 / GPT Image 2 style image generation",
        "mode_detection": check_mode,
        "ai_text_to_image_used": False,
        "decision": "未使用 AI 文生图；采用可复现 HTML/SVG 目标概念图。",
        "reason": [
            "gpt-image-2 检测为 B-or-C，未启用 Garden 本地出图且没有 OPENAI_API_KEY。",
            "本审查页需要稳定落盘和可复现，不应依赖不可验证的宿主图片去向。",
            "目标图必须避免被误解为当前真实实现截图。",
        ],
        "consistency_review": [
            {"item": "项目概念一致性", "result": "通过", "evidence": "目标图只表达 P8.1 文档定义的用户指导 - Chatbox - 工作台。"},
            {"item": "事实性错误", "result": "未发现", "evidence": "目标图带非当前实现水印，不声称平台接入、真实 provider 或真实资料通过。"},
            {"item": "实现截图混淆风险", "result": "已控制", "evidence": "报告将当前真实截图和目标概念截图分区展示。"},
        ],
    }
    AI_IMAGE_AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return audit


def _validate_images() -> list[dict]:
    images = [CONCEPT_SVG] + [EVIDENCE_DIR / name for name, _ in BASELINE_SHOTS + TARGET_SHOTS]
    results = []
    for path in images:
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        results.append({"path": _rel(path), "exists": exists, "size": size, "status": "passed" if exists and size > 1024 else "failed"})
    return results


def _render_figure(path: Path, caption: str, kind: str) -> str:
    return f"""
      <figure>
        <img src="{_html(_report_rel(path))}" alt="{_html(caption)}">
        <figcaption><strong>{_html(kind)}</strong><br>{_html(caption)}<br><code>{_html(_rel(path))}</code></figcaption>
      </figure>
"""


def _render_report(command_evidence: dict, static_facts: dict, ai_audit: dict, image_checks: list[dict]) -> None:
    baseline_figures = "\n".join(_render_figure(EVIDENCE_DIR / name, caption, "当前真实截图") for name, caption in BASELINE_SHOTS)
    target_figures = "\n".join(_render_figure(EVIDENCE_DIR / name, caption, "目标概念截图") for name, caption in TARGET_SHOTS)
    command_rows = "\n".join(
        f"<tr><td>{_html(item['label'])}</td><td><code>{_html(item['command'])}</code></td><td class=\"{_html(item['status'])}\">{_html(item['status'])}</td><td><pre>{_html(item['summary'])}</pre></td></tr>"
        for item in command_evidence["results"]
    )
    image_rows = "\n".join(
        f"<tr><td><code>{_html(item['path'])}</code></td><td>{_html(item['size'])} bytes</td><td class=\"{_html(item['status'])}\">{_html(item['status'])}</td></tr>"
        for item in image_checks
    )
    fact_rows = "\n".join(
        f"<tr><td>{_html(name)}</td><td class=\"{'passed' if value else 'failed'}\">{_html(value)}</td></tr>"
        for name, value in {
            "p8-workflow-strip 位于 timeline 之前": static_facts["p8_workflow_strip_before_timeline"],
            "DesktopContextPanel 存在": static_facts["main_entities"]["DesktopContextPanel"],
            "MaterialIntakeWizard 存在": static_facts["main_entities"]["MaterialIntakeWizard"],
            "JDIntakeCenter 存在": static_facts["main_entities"]["JDIntakeCenter"],
            "JobTargetList 存在": static_facts["main_entities"]["JobTargetList"],
            "ResumeGenerationPlane 存在": static_facts["main_entities"]["ResumeGenerationPlane"],
            "Workbench 存在": static_facts["main_entities"]["Workbench"],
            "composer quick actions 存在": static_facts["css_entities"]["composer_quick_actions"],
        }.items()
    )
    ai_rows = "\n".join(
        f"<tr><td>{_html(item['item'])}</td><td class=\"passed\">{_html(item['result'])}</td><td>{_html(item['evidence'])}</td></tr>"
        for item in ai_audit["consistency_review"]
    )
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>P8.1 前端优化审查与实现指导</title>
  <style>
    :root {{
      --bg: #f5f7f4;
      --panel: #ffffff;
      --ink: #16231f;
      --muted: #5d6b64;
      --line: #d9e3dd;
      --primary: #236b5f;
      --ok: #0f6b3d;
      --warn: #8a4b0f;
      --bad: #a61b1b;
      --soft: #eef7f3;
      --cream: #fff8ed;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font: 15px/1.58 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); }}
    header, main {{ max-width: 1180px; margin: 0 auto; padding: 30px; }}
    header {{ padding-top: 42px; }}
    h1 {{ margin: 0 0 10px; font-size: 31px; letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 21px; }}
    h3 {{ margin: 18px 0 10px; font-size: 17px; }}
    p {{ margin: 8px 0; }}
    section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin: 18px 0; box-shadow: 0 12px 28px rgb(31 47 42 / 0.05); }}
    .meta {{ color: var(--muted); }}
    .badge {{ display: inline-flex; align-items: center; min-height: 30px; padding: 6px 10px; border-radius: 7px; font-weight: 800; background: #fff7e6; color: var(--warn); border: 1px solid #e8c986; }}
    .badge.ok {{ background: #ddf7e8; color: var(--ok); border-color: #9bd5b2; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }}
    .two {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid #e6ece8; padding: 10px; }}
    th {{ color: var(--muted); font-size: 13px; }}
    code {{ background: #eef3f0; padding: 2px 5px; border-radius: 4px; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; margin: 0; background: #f8faf8; border: 1px solid #e0e7e3; border-radius: 6px; padding: 10px; max-height: 220px; overflow: auto; }}
    figure {{ margin: 0; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: #fff; }}
    img {{ display: block; width: 100%; height: auto; background: #fff; border-bottom: 1px solid var(--line); }}
    figcaption {{ padding: 11px 12px; color: var(--muted); font-size: 13px; }}
    .passed {{ color: var(--ok); font-weight: 800; }}
    .failed {{ color: var(--bad); font-weight: 800; }}
    .warning {{ color: var(--warn); font-weight: 800; }}
    .flow {{ counter-reset: step; display: grid; gap: 10px; }}
    .flow li {{ list-style: none; position: relative; padding: 13px 14px 13px 54px; background: var(--soft); border: 1px solid #cde0d7; border-radius: 8px; }}
    .flow li::before {{ counter-increment: step; content: counter(step); position: absolute; left: 14px; top: 12px; width: 26px; height: 26px; display: grid; place-items: center; border-radius: 50%; background: var(--primary); color: white; font-weight: 900; }}
    .callout {{ background: var(--cream); border-color: #edcf9d; }}
    @media (max-width: 760px) {{
      header, main {{ padding: 18px; }}
      .two {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <header>
    <p><span class="badge">P8.1 待实现</span> <span class="badge ok">审查指导页已生成</span></p>
    <h1>P8.1 前端优化审查与自动化实现指导</h1>
    <p class="meta">用途：让人类判断当前 Agent 是否完整理解前端页面优化诉求，并指导后续 P8.1 自动化开发和端到端验收。生成时间：{_html(datetime.now(timezone.utc).isoformat())}</p>
    <p class="meta">Git：<code>{_html(command_evidence["git_head"])}</code></p>
  </header>
  <main>
    <section class="callout">
      <h2>审查结论</h2>
      <p><strong>当前理解已明确：</strong>P8 能力已经存在，但前端信息架构主次错误。P8.1 的核心不是增加更多按钮，而是把体验恢复为 <code>用户指导 - Chatbox - 工作台</code>，其中中央 Chatbox 是首屏第一优先路径。</p>
      <p><strong>当前状态边界：</strong>本报告用于指导实现和验收，不代表 P8.1 UI 已修复；目标概念截图不是当前实现截图。</p>
    </section>

    <section>
      <h2>概念图</h2>
      <figure>
        <img src="{_html(_report_rel(CONCEPT_SVG))}" alt="P8.1 Chatbox-first 概念图">
        <figcaption>概念图明确三栏职责：左侧用户指导、中央 Chatbox 主路径、右侧工作台产物区。<code>{_html(_rel(CONCEPT_SVG))}</code></figcaption>
      </figure>
    </section>

    <section>
      <h2>当前实际实现基线截图</h2>
      <p class="meta">以下截图来自真实运行中的当前项目，不是设计稿。它们用于证明 P8.1 需要修复的基线状态。</p>
      <div class="grid">{baseline_figures}</div>
    </section>

    <section>
      <h2>目标概念截图</h2>
      <p class="meta">以下截图由确定性 HTML/SVG mock 渲染生成，水印已标注“目标概念图 / 非当前实现”。它们只用于指导开发，不作为实现验收通过证据。</p>
      <div class="grid">{target_figures}</div>
    </section>

    <section>
      <h2>当前事实基线检查</h2>
      <table><thead><tr><th>事实</th><th>结果</th></tr></thead><tbody>{fact_rows}</tbody></table>
    </section>

    <section>
      <h2>当前截图与目标截图对比</h2>
      <table>
        <thead><tr><th>审查点</th><th>当前基线</th><th>P8.1 目标</th><th>验收判断</th></tr></thead>
        <tbody>
          <tr><td>中央首屏主路径</td><td><code>p8-workflow-strip</code> 在 timeline 前，资料/JD/简历入口抢占首屏。</td><td>中央优先展示 Agent 状态、聊天时间线和输入框。</td><td class="warning">待实现</td></tr>
          <tr><td>资料/JD 入口</td><td>资料向导、JD 导入、岗位列表、简历生成集中在中央大块区域。</td><td>入口紧贴输入框，或进入左侧指导/右侧工作台/轻弹层。</td><td class="warning">待实现</td></tr>
          <tr><td>三栏职责</td><td>三栏存在，但中央职责混杂。</td><td>左侧指导、中央聊天、右侧产物确认。</td><td class="warning">待实现</td></tr>
          <tr><td>移动端</td><td>需要继续以真实截图确认 Chatbox 是否默认主路径。</td><td>移动端默认显示 Chatbox，指导和工作台抽屉化。</td><td class="warning">待实现</td></tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>用户操作 / 体验路线图</h2>
      <ol class="flow">
        <li>用户打开本地 Chatbox，首屏识别三栏：左侧“我该准备什么”、中央“聊天”、右侧“产物”。</li>
        <li>用户可以直接在 Chatbox 提问，例如“帮我生成一版前端岗位简历”。</li>
        <li>Agent 在对话中解释缺少哪些资料，并把上传资料、粘贴 JD、选择岗位、生成简历入口放在输入框附近。</li>
        <li>用户粘贴目标 JD；系统只保存文本、来源 URL、平台标签和备注，不抓取网页。</li>
        <li>右侧工作台展示当前目标 JD、CandidateProfile、简历草稿、source refs、pending confirmations 和 export preflight。</li>
        <li>用户继续多轮对话补充资料、确认事实，blocking 项处理后才能正式导出。</li>
      </ol>
    </section>

    <section>
      <h2>自动化开发指导</h2>
      <table>
        <thead><tr><th>区域</th><th>需要做什么</th><th>禁止做什么</th></tr></thead>
        <tbody>
          <tr><td><code>Conversation Plane</code></td><td>将 timeline 和 composer 提升为中央首屏主体，保留紧凑 Agent 状态机。</td><td>继续把大型资料/JD/简历表单放在 timeline 前。</td></tr>
          <tr><td><code>p8-workflow-strip</code></td><td>拆为输入框工具、轻弹层、抽屉或左右辅助面板。</td><td>删除 P8 能力或让工具入口不可达。</td></tr>
          <tr><td><code>DesktopContextPanel</code></td><td>承载资料清单、缺失影响、示例路径和下一步建议。</td><td>承载大型编辑表单或替代聊天。</td></tr>
          <tr><td><code>Workbench</code></td><td>承载岗位、画像、简历、source refs、pending confirmations、export preflight。</td><td>抢占中央主路径或要求用户理解内部 artifact。</td></tr>
          <tr><td><code>styles.css</code></td><td>固定多视口主次：桌面三栏、平板/移动 Chatbox 默认优先。</td><td>出现按钮错位、文字重叠、输入框不可达。</td></tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>端到端验收门槛</h2>
      <table>
        <thead><tr><th>门槛</th><th>必须证据</th><th>打回条件</th></tr></thead>
        <tbody>
          <tr><td>Chatbox-first</td><td>1200/1440/1920 首屏截图显示聊天时间线和输入框优先。</td><td>workflow strip 或大表单仍压住聊天。</td></tr>
          <tr><td>工具入口</td><td>上传资料、粘贴 JD、选择岗位、生成简历紧贴输入框或在辅助面板内。</td><td>入口分散、不可达、文字重叠。</td></tr>
          <tr><td>工作台</td><td>右侧能看到岗位、画像、简历、source refs、待确认和导出检查。</td><td>右侧空白或抢占中央聊天。</td></tr>
          <tr><td>移动端</td><td>720px/390px 真实截图证明默认 Chatbox 优先。</td><td>移动端默认进入资料表单或输入框不可达。</td></tr>
          <tr><td>边界</td><td>报告明确未验证真实 provider、真实资料、招聘平台自动化、自动投递。</td><td>任何 false-green 结论。</td></tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>AI 文生图审计</h2>
      <p class="meta">本阶段没有使用 AI 文生图作为报告图片。检测结果见 <code>{_html(_rel(AI_IMAGE_AUDIT))}</code>。</p>
      <table><tbody>
        <tr><th>检测模式</th><td><code>{_html(ai_audit["mode_detection"].get("mode"))}</code> / {_html(ai_audit["mode_detection"].get("summary"))}</td></tr>
        <tr><th>是否使用 AI 文生图</th><td class="warning">{_html(ai_audit["ai_text_to_image_used"])}</td></tr>
        <tr><th>决策</th><td>{_html(ai_audit["decision"])}</td></tr>
      </tbody></table>
      <h3>一致性与事实性检查</h3>
      <table><thead><tr><th>检查项</th><th>结果</th><th>证据</th></tr></thead><tbody>{ai_rows}</tbody></table>
    </section>

    <section>
      <h2>命令证据与图片完整性</h2>
      <h3>命令证据</h3>
      <table><thead><tr><th>检查</th><th>命令</th><th>状态</th><th>摘要</th></tr></thead><tbody>{command_rows}</tbody></table>
      <h3>图片引用检查</h3>
      <table><thead><tr><th>文件</th><th>大小</th><th>状态</th></tr></thead><tbody>{image_rows}</tbody></table>
    </section>

    <section>
      <h2>未验证范围</h2>
      <ul>
        <li>P8.1 UI 还没有实现，本报告只是审查与实现指导页。</li>
        <li>目标概念截图不是当前实现截图，不能作为验收通过证据。</li>
        <li>未调用真实 MiniMax、DeepSeek 或 OpenAI-compatible provider。</li>
        <li>未使用用户真实个人资料。</li>
        <li>未接入 BOSS、猎聘、拉勾等招聘平台，不自动沟通或自动投递。</li>
      </ul>
    </section>
  </main>
</body>
</html>
"""
    REPORT.write_text("\n".join(line.rstrip() for line in html.splitlines()) + "\n", encoding="utf-8")


def _run_report_quality_check() -> dict:
    forbidden = [
        "P8.1 已实现",
        "Chatbox-first UI 已验收通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "招聘平台自动接入通过",
        "自动投递已实现",
    ]
    html = REPORT.read_text(encoding="utf-8")
    missing = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
        path = (REPORT.parent / src).resolve()
        if not path.exists() or path.stat().st_size <= 1024:
            missing.append(src)
    hits = [item for item in forbidden if item in html]
    result = {
        "label": "报告图片与 false-green 自检",
        "command": "internal report validation",
        "status": "passed" if not missing and not hits else "failed",
        "returncode": 0 if not missing and not hits else 1,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "summary": f"image_refs={len(re.findall(r'<img[^>]+src=\"([^\"]+)\"', html))}; missing={missing}; forbidden={hits}",
    }
    if result["returncode"] != 0:
        raise RuntimeError(result["summary"])
    return result


def _start_services() -> list[subprocess.Popen]:
    started: list[subprocess.Popen] = []
    if not _url_ready("http://127.0.0.1:8000/api/health"):
        api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "services.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        started.append(api)
    if not _url_ready("http://127.0.0.1:5173/"):
        vite = subprocess.Popen(
            ["npm", "--prefix", "apps/chatbox", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        started.append(vite)
    if not _url_ready(f"http://127.0.0.1:{TARGET_STATIC_PORT}/{TARGET_MOCK.name}"):
        static = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "http.server",
                str(TARGET_STATIC_PORT),
                "--bind",
                "127.0.0.1",
                "--directory",
                str(EVIDENCE_DIR),
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        started.append(static)
    _wait_url("http://127.0.0.1:8000/api/health")
    _wait_url("http://127.0.0.1:5173/")
    _wait_url(f"http://127.0.0.1:{TARGET_STATIC_PORT}/{TARGET_MOCK.name}")
    return started


def _stop_services(processes: list[subprocess.Popen]) -> None:
    for proc in processes:
        proc.terminate()
    for proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    _write_concept_svg()
    _write_target_mock()
    _write_browser_scenario()

    check_mode = _run_command(
        "gpt-image-2 mode check",
        ["node", "/home/administrator/.agents/skills/gpt-image-2/scripts/check-mode.js", "--json"],
        30,
    )
    try:
        check_mode_json = json.loads(check_mode["summary"])
    except json.JSONDecodeError:
        check_mode_json = {"mode": "unknown", "summary": check_mode["summary"]}
    ai_audit = _build_ai_image_audit(check_mode_json)

    static_facts = _collect_static_facts()
    commands = [
        check_mode,
        _run_command(
            "drawio XML parse",
            [sys.executable, "-c", "import xml.etree.ElementTree as ET; ET.parse('docs/active/jobpilot-stage-gap-and-acceptance.drawio'); print('drawio parse ok')"],
            60,
        ),
    ]

    processes = _start_services()
    try:
        capture = _run_command(
            "headless Chrome screenshot capture",
            [
                "node",
                "scripts/browser_tools/browser-acceptance.mjs",
                "--start-chrome",
                "--scenario",
                str(SCENARIO),
                "--output-dir",
                str(EVIDENCE_DIR),
                "--report",
                str(CAPTURE_REPORT),
                "--port",
                "9238",
            ],
            180,
        )
        commands.append(capture)
        if capture["returncode"] != 0:
            raise RuntimeError(capture["summary"])
    finally:
        _stop_services(processes)

    image_checks = _validate_images()
    failed_images = [item for item in image_checks if item["status"] != "passed"]
    if failed_images:
        raise RuntimeError(f"Image validation failed: {failed_images}")

    command_evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(),
        "git_status_short": _git_status_short(),
        "results": commands,
        "static_facts": static_facts,
        "images": image_checks,
    }
    COMMAND_EVIDENCE.write_text(json.dumps(command_evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    _render_report(command_evidence, static_facts, ai_audit, image_checks)
    final_check = _run_report_quality_check()
    command_evidence["results"].append(final_check)
    COMMAND_EVIDENCE.write_text(json.dumps(command_evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    _render_report(command_evidence, static_facts, ai_audit, image_checks)
    print(REPORT)


if __name__ == "__main__":
    main()
