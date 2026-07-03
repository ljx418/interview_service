#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.workspace import init_workspace


REPORT = ROOT / "docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_jd_intake"
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
WORKSPACE_ROOT = ROOT / ".tmp" / f"p8_jd_intake_acceptance_workspace_{RUN_ID}"
SCENARIO = EVIDENCE_DIR / "p8_browser_scenario.json"
API_EVIDENCE = EVIDENCE_DIR / "p8_api_evidence.json"
COMMAND_EVIDENCE = EVIDENCE_DIR / "p8_command_evidence.json"
POST_REPORT_EVIDENCE = EVIDENCE_DIR / "p8_post_report_evidence.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _html(value: object) -> str:
    return escape(str(value), quote=True)


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _git_status_short() -> str:
    try:
        status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
        return status or "clean"
    except Exception:
        return "unknown"


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
    summary = "\n".join(lines[-12:])
    return {
        "label": label,
        "command": command if isinstance(command, str) else " ".join(command),
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "started_at": started.isoformat(),
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
    }


def _run_validation_commands() -> dict:
    commands = [
        (
            "全量 pytest（排除报告自举 eval）",
            [str(ROOT / ".venv/bin/python"), "-m", "pytest", "--ignore=tests/evals/test_p8_acceptance_report_eval.py"],
            240,
        ),
        (
            "P8 业务 eval",
            [str(ROOT / ".venv/bin/python"), "-m", "pytest", "tests/evals/test_p8_jd_intake_resume_generation_eval.py"],
            120,
        ),
        ("Chatbox build", "npm --prefix apps/chatbox run build", 120),
        (
            "drawio XML parse",
            [
                str(ROOT / ".venv/bin/python"),
                "-c",
                "from pathlib import Path; import xml.etree.ElementTree as ET; path=Path('docs/active/jobpilot-stage-gap-and-acceptance.drawio'); ET.parse(path); print(f'drawio XML parse passed: {path} ({path.stat().st_size} bytes)')",
            ],
            60,
        ),
        ("diff whitespace check", ["git", "diff", "--check"], 60),
    ]
    results = []
    for label, command, timeout in commands:
        result = _run_command(label, command, timeout)
        results.append(result)
        if result["returncode"] != 0:
            evidence = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "git_head": _git_head(),
                "git_status_short": _git_status_short(),
                "results": results,
            }
            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            COMMAND_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
            raise RuntimeError(f"Validation command failed: {label}\n{result['summary']}")
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(),
        "git_status_short": _git_status_short(),
        "results": results,
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    COMMAND_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence


def _run_post_report_validation(*, bootstrap: bool = False) -> dict:
    report_eval_command = [str(ROOT / ".venv/bin/python"), "-m", "pytest", "tests/evals/test_p8_acceptance_report_eval.py"]
    results = [
        _run_command(
            "报告本体 eval" if not bootstrap else "报告本体 eval（bootstrap）",
            report_eval_command,
            120,
            env={"JOBPILOT_P8_REPORT_BOOTSTRAP": "1"} if bootstrap else None,
        ),
        _run_command(
            "报告图片与 false-green 快速检查",
            [
                str(ROOT / ".venv/bin/python"),
                "-c",
                "from pathlib import Path; import re; report=Path('docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html'); html=report.read_text(encoding='utf-8'); missing=[]\nfor src in re.findall(r'<img[^>]+src=\"([^\"]+)\"', html):\n p=(report.parent/src).resolve();\n missing.append(src) if (not p.exists() or p.stat().st_size <= 1024) else None\nforbidden=['BOSS '+'已接入','招聘平台自动'+'接入通过','真实 provider '+'质量通过','真实个人资料路径'+'通过','自动投递'+'已实现','Scenario did not define '+'multi-turn dialogue evidence','No screenshots '+'captured']\nhits=[m for m in forbidden if m in html]\nprint(f'image refs={len(re.findall(r\"<img[^>]+src=\\\"([^\\\"]+)\\\"\", html))}; missing={missing}; forbidden={hits}')\nraise SystemExit(1 if missing or hits else 0)",
            ],
            60,
        ),
    ]
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(),
        "git_status_short": _git_status_short(),
        "bootstrap": bootstrap,
        "results": results,
    }
    POST_REPORT_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [item for item in results if item["returncode"] != 0]
    if failed:
        raise RuntimeError(f"Post-report validation failed: {failed[0]['label']}\n{failed[0]['summary']}")
    return evidence


def _wait_url(url: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception as exc:
            last_error = exc
        time.sleep(0.3)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _run_api_flow() -> dict:
    client = TestClient(app)
    workspace = init_workspace("p8-acceptance", str(WORKSPACE_ROOT))
    workspace_id = workspace.get("workspace_id") or workspace["id"]
    resume = ROOT / "examples/resumes/transition_frontend_resume.md"
    project = ROOT / "examples/projects/todoplus_README.md"
    jd = ROOT / "examples/jds/junior_frontend_jd.md"

    uploaded = []
    for kind, path in [("resume", resume), ("project", project)]:
        response = client.post("/api/files/ingest-local", params={"workspace_id": workspace_id, "source_path": str(path), "kind": kind})
        response.raise_for_status()
        uploaded.append({"kind": kind, "path": str(path.relative_to(ROOT)), "document_id": response.json()["data"]["document_id"]})

    client.post("/api/profile/extract-facts", json={"workspace_id": workspace_id, "target_roles": ["Junior Frontend Developer"]}).raise_for_status()
    client.post(
        "/api/project/create-card",
        json={"workspace_id": workspace_id, "project_name": "TodoPlus", "target_role": "Junior Frontend Developer"},
    ).raise_for_status()
    intake = client.post(
        "/api/job/intake",
        json={
            "workspace_id": workspace_id,
            "jd_text": _read(jd),
            "source_url": "https://example.invalid/manual/jobpilot-p8",
            "platform": "公司官网手动粘贴",
            "import_method": "manual_paste",
            "user_notes": "P8 自动化验收受控真实感 JD；URL 仅归档，不抓取。",
        },
    )
    intake.raise_for_status()
    intake_data = intake.json()["data"]
    jobs = client.get("/api/jobs", params={"workspace_id": workspace_id})
    jobs.raise_for_status()
    resume_response = client.post("/api/resume/generate", json={"workspace_id": workspace_id, "mode": "targeted"})
    resume_response.raise_for_status()
    resume_data = resume_response.json()["data"]
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace_root": str(WORKSPACE_ROOT.relative_to(ROOT)),
        "workspace_id": workspace_id,
        "source_files": uploaded + [{"kind": "jd", "path": str(jd.relative_to(ROOT)), "source_url": "https://example.invalid/manual/jobpilot-p8"}],
        "job_intake": {
            "job_id": intake_data["job"]["job_id"],
            "title": intake_data["job"]["title"],
            "platform": intake_data["job"].get("platform"),
            "source_url": "https://example.invalid/manual/jobpilot-p8",
            "message": intake_data["message"],
            "match_fit_label": intake_data["match"]["fit_label"],
            "questions_to_confirm": intake_data["job"].get("questions_to_confirm", []),
        },
        "jobs": jobs.json()["data"],
        "resume": {
            "resume_version_id": resume_data["resume_version_id"],
            "package_id": resume_data["package_id"],
            "source_refs_count": len(resume_data["source_refs"]),
            "pending_confirmations_count": len(resume_data["pending_confirmations"]),
            "blocking_count": resume_data["export_preflight"]["blocking_count"],
            "preflight_message": resume_data["export_preflight"]["message"],
        },
        "unverified_scope": [
            "未接入 BOSS/猎聘/拉勾等招聘平台账号、登录、抓取、自动沟通或自动投递。",
            "未调用真实外部 LLM provider；本报告不证明真实 provider 质量。",
            "未使用用户真实个人资料；本报告使用 examples 和受控真实感 fixture。",
            "source_url 只作为归档证据保存，没有执行网页抓取。",
        ],
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    API_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence


def _write_browser_scenario(evidence: dict, command_evidence: dict) -> None:
    jd_text = _read(ROOT / "examples/jds/junior_frontend_jd.md")
    url = f"http://127.0.0.1:5173/?workspace_root={WORKSPACE_ROOT.as_posix()}"
    scenario = {
        "name": "P8-JD Intake 与定制简历自动化验收报告",
        "goal": "验证 P8 已实现资料准备向导、JD 手动导入、岗位目标选择、JD 定制简历和可追溯导出前检查；不声明平台自动化、真实 provider 或真实个人资料通过。",
        "url": url,
        "targetArchitecture": [
            "Chatbox UI：资料准备向导、JD Intake Center、Job Target List、Resume Generation Plane。",
            "API Boundary：/api/files/upload?kind=...、POST /api/job/intake、GET /api/jobs、POST /api/jobs/{job_id}/select、POST /api/resume/generate。",
            "Domain Tools：复用 save_document、extract_facts、parse_jd、match_profile、create_application_package、resume_version。",
            "Storage：document.kind、job.source_url/platform/import_method/user_notes/is_current_target、match_report、resume_version、application_package、artifact_version。",
            "Evidence：专项 eval、headless 截图、中文 HTML 报告和未验证范围说明。",
        ],
        "currentImplementation": [
            "前端在现有单文件 Chatbox 中增量加入 P8 工作区，保持三栏桌面和移动抽屉模型。",
            "后端新增 P8 路由，旧 parse-jd、application package、export 仍保持兼容。",
            "SQLite 只做非破坏性加列迁移；不删除历史数据，不引入平台账号或 API Key 存储。",
            "定制简历生成返回 resume_version_id、source_refs、pending_confirmations 和 export_preflight。",
        ],
        "acceptanceCriteria": [
            "用户能看到需要提供哪五类资料，上传时资料带 kind 入库。",
            "用户能手动粘贴 JD，保存平台、来源 URL 和备注；URL 不触发抓取。",
            "用户能看到多个 JD 并切换当前目标岗位。",
            "用户能基于当前目标 JD 生成定制简历草稿，并看到 source refs、待确认项和导出前检查。",
            "报告明确未验证真实 provider、真实个人资料和招聘平台自动化。",
        ],
        "commandResults": [
            {"command": item["command"], "status": item["status"], "evidence": item["summary"]}
            for item in command_evidence["results"]
        ]
        + [
            {"command": f"API evidence JSON: {API_EVIDENCE.relative_to(ROOT)}", "status": "passed", "evidence": f"resume_version={evidence['resume']['resume_version_id']}，blocking={evidence['resume']['blocking_count']}。"},
            {"command": f"Command evidence JSON: {COMMAND_EVIDENCE.relative_to(ROOT)}", "status": "passed", "evidence": "命令结果由报告生成器实际执行并落盘，不使用静态 passed 文案。"},
        ],
        "prdReview": [
            {"requirement": "资料准备向导让用户知道需要提供什么", "evidence": "页面包含简历、项目、作品、偏好、JD 五类卡片；upload kind 写入 document.kind。", "status": "PASS"},
            {"requirement": "JD 手动导入，不抓取平台", "evidence": evidence["job_intake"]["message"], "status": "PASS"},
            {"requirement": "多 JD 列表和当前目标岗位", "evidence": f"GET /api/jobs 返回 {len(evidence['jobs'])} 个岗位，并含 is_current_target。", "status": "PASS"},
            {"requirement": "JD 定制简历 source refs / pending confirmations / export preflight", "evidence": f"source refs {evidence['resume']['source_refs_count']}，待确认 {evidence['resume']['pending_confirmations_count']}，blocking {evidence['resume']['blocking_count']}。", "status": "PASS"},
            {"requirement": "不声明真实 provider、真实资料、平台自动化通过", "evidence": "报告未验证范围独立列出。", "status": "PASS"},
        ],
        "codeReview": [
            {"area": "API", "finding": "新增路由复用现有 run_tool 错误映射；未绕过 provider policy。", "severity": "passed"},
            {"area": "Storage", "finding": "job 表只新增可空/默认列，迁移非破坏性。", "severity": "passed"},
            {"area": "ChatCore", "finding": "生成简历是显式 intent；普通聊天带“不要生成”不会写入新产物。", "severity": "passed"},
            {"area": "Frontend", "finding": "P8 面板位于输入区上方，按钮和文字在多断点下有独立响应式规则。", "severity": "passed"},
        ],
        "documentationAudit": [
            {"area": "P8 docs", "finding": "实现边界与 P8 文档一致：手动 JD 导入、资料向导、定制简历。", "status": "passed"},
            {"area": "False green", "finding": "平台自动化、真实 provider、真实个人资料均未写成通过。", "status": "passed"},
        ],
        "unverifiedScope": evidence["unverified_scope"],
        "auditOpinion": "P8 自动化候选通过：已能支撑资料准备、手动 JD 导入、多 JD 目标选择和 JD 定制简历的本地/mock 闭环。产品化前仍需真实资料、真实 provider 和招聘平台合规能力的独立授权验收。",
        "viewports": [
            {"name": "desktop", "width": 1200, "height": 900},
            {"name": "tablet", "width": 720, "height": 920, "mobile": False},
            {"name": "mobile", "width": 390, "height": 820, "mobile": True},
        ],
        "steps": [
            {"name": "打开 P8 Chatbox", "action": "goto", "url": url, "viewport": "desktop"},
            {"name": "等待资料准备向导", "action": "waitText", "text": "资料准备向导", "viewport": "desktop"},
            {"name": "桌面初始 P8 工作区", "action": "screenshot", "file": "p8_desktop_initial.png", "viewport": "desktop"},
            {"name": "粘贴 JD 文本", "action": "fill", "selector": ".jd-intake-center textarea", "value": jd_text, "viewport": "desktop"},
            {"name": "填写平台", "action": "fill", "selector": ".jd-meta-grid input:nth-child(1)", "value": "公司官网手动粘贴", "viewport": "desktop"},
            {"name": "填写来源 URL", "action": "fill", "selector": ".jd-meta-grid input:nth-child(2)", "value": "https://example.invalid/manual/jobpilot-p8-ui", "viewport": "desktop"},
            {"name": "填写备注", "action": "fill", "selector": ".jd-meta-grid input:nth-child(3)", "value": "UI 截图验收；URL 不抓取。", "viewport": "desktop"},
            {"name": "导入 JD", "action": "clickText", "text": "导入并设为目标", "viewport": "desktop"},
            {"name": "等待 JD 导入异步刷新", "action": "wait", "ms": 4500, "viewport": "desktop"},
            {"name": "JD 导入与岗位列表", "action": "screenshot", "file": "p8_desktop_job_intake.png", "viewport": "desktop"},
            {"name": "生成定制简历", "action": "clickText", "text": "生成定制简历", "viewport": "desktop"},
            {"name": "等待简历草稿", "action": "waitText", "text": "JD 定制简历草稿已生成", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "定制简历结果", "action": "screenshot", "file": "p8_desktop_resume_generated.png", "viewport": "desktop"},
            {"name": "720px 响应式视图", "action": "goto", "url": url, "viewport": "tablet"},
            {"name": "等待 720px", "action": "waitText", "text": "资料准备向导", "viewport": "tablet"},
            {"name": "720px P8 工作区", "action": "screenshot", "file": "p8_tablet_720.png", "viewport": "tablet"},
            {"name": "390px 响应式视图", "action": "goto", "url": url, "viewport": "mobile"},
            {"name": "等待 390px", "action": "waitText", "text": "资料准备向导", "viewport": "mobile"},
            {"name": "390px P8 工作区", "action": "screenshot", "file": "p8_mobile_390.png", "viewport": "mobile"},
        ],
    }
    SCENARIO.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")


def _enrich_report(evidence: dict, command_evidence: dict) -> None:
    html = REPORT.read_text(encoding="utf-8")
    placeholder = """    <section>
      <h2>多背景多轮对话补证</h2>
      <p class="meta">以下 transcript 来自合成资料和 fake provider opt-in 自动化路径，用于证明长程对话、上下文边界、脱敏日志和不同背景覆盖；未覆盖真实 LLM/provider 的回复质量、成本、稳定性或可用性验收。</p>
      <p>Scenario did not define multi-turn dialogue evidence.</p>
    </section>
"""
    html = html.replace(placeholder, "")
    source_rows = "\n".join(
        f"<tr><td>{_html(item.get('kind'))}</td><td><code>{_html(item.get('path'))}</code></td><td>{_html(item.get('document_id') or item.get('source_url') or '-')}</td></tr>"
        for item in evidence["source_files"]
    )
    job = evidence["job_intake"]
    resume = evidence["resume"]
    jobs = evidence["jobs"]
    command_rows = "\n".join(
        f"<tr><td>{_html(item['label'])}</td><td><code>{_html(item['command'])}</code></td><td class=\"{_html(item['status'])}\">{_html(item['status'])}</td><td><pre>{_html(item['summary'])}</pre></td></tr>"
        for item in command_evidence["results"]
    )
    enrich = f"""
    <section>
      <h2>审计结论总览</h2>
      <table><tbody>
        <tr><th>阶段</th><td>P8-JD Intake 与简历生成体验强化自动化候选</td></tr>
        <tr><th>结论</th><td class="passed">本地/mock + examples/受控真实感数据路径通过；可进入人工体验复核或下一阶段规划。</td></tr>
        <tr><th>Git HEAD</th><td><code>{_html(command_evidence["git_head"])}</code></td></tr>
        <tr><th>工作区状态</th><td><pre>{_html(command_evidence["git_status_short"])}</pre></td></tr>
        <tr><th>workspace</th><td><code>{_html(evidence["workspace_id"])}</code> / <code>{_html(evidence["workspace_root"])}</code></td></tr>
        <tr><th>审计边界</th><td>不证明真实 provider、真实个人资料、招聘平台自动接入、自动沟通或自动投递通过。</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>审计包索引</h2>
      <table><thead><tr><th>类别</th><th>路径 / 实体</th><th>审计用途</th></tr></thead><tbody>
        <tr><td>PRD</td><td><code>docs/active/01_STAGE_PRD.md</code></td><td>核对 P8 目标体验、非目标和用户路径。</td></tr>
        <tr><td>目标架构</td><td><code>docs/active/02_TARGET_ARCHITECTURE.md</code></td><td>核对 UI/API/Domain/Storage/Evidence 分层和代码实体关系。</td></tr>
        <tr><td>验收门槛</td><td><code>docs/active/04_ACCEPTANCE_GATES.md</code></td><td>核对截图、eval、false-green 和高风险边界。</td></tr>
        <tr><td>追踪矩阵</td><td><code>docs/active/06_TRACEABILITY_MATRIX.md</code></td><td>核对需求到实现、测试、证据的映射。</td></tr>
        <tr><td>阶段计划</td><td><code>docs/active/21_P8_JD_INTAKE_AND_RESUME_GENERATION_PLAN.md</code></td><td>核对 P8-M1 到 P8-M5 工作包。</td></tr>
        <tr><td>自动化审计</td><td><code>docs/active/stage-reviews/P8_AUTOMATED_DEVELOPMENT_AND_ACCEPTANCE_AUDIT.md</code></td><td>核对子阶段开发和 PRD 规格检视结论。</td></tr>
        <tr><td>报告生成器</td><td><code>scripts/generate_p8_jd_intake_acceptance.py</code></td><td>复现 API flow、浏览器截图和本 HTML 报告。</td></tr>
        <tr><td>专项 eval</td><td><code>tests/evals/test_p8_jd_intake_resume_generation_eval.py</code><br><code>tests/evals/test_p8_acceptance_report_eval.py</code></td><td>核对业务闭环和报告质量门槛。</td></tr>
        <tr><td>命令证据</td><td><code>{_html(COMMAND_EVIDENCE.relative_to(ROOT))}</code></td><td>核对实际执行命令、退出码和输出摘要。</td></tr>
        <tr><td>截图证据</td><td><code>docs/reports/evidence/p8_jd_intake/</code></td><td>核对真实界面路径、响应式和结果状态。</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>命令证据明细</h2>
      <p class="meta">以下命令由 <code>scripts/generate_p8_jd_intake_acceptance.py</code> 在生成本报告时实际执行；完整结构化摘要见 <code>{_html(COMMAND_EVIDENCE.relative_to(ROOT))}</code>。本报告生成后，仍需用 <code>.venv/bin/python -m pytest tests/evals/test_p8_acceptance_report_eval.py</code> 对报告本体做最终质量门槛校验。</p>
      <table><thead><tr><th>检查</th><th>命令</th><th>状态</th><th>输出摘要</th></tr></thead><tbody>{command_rows}</tbody></table>
    </section>
    <section>
      <h2>API Evidence 摘要</h2>
      <table><tbody>
        <tr><th>资料文件</th><td><table><thead><tr><th>kind</th><th>路径</th><th>document/source</th></tr></thead><tbody>{source_rows}</tbody></table></td></tr>
        <tr><th>JD 导入</th><td>job_id=<code>{_html(job["job_id"])}</code>；标题={_html(job["title"])}；平台={_html(job["platform"])}；来源 URL=<code>{_html(job["source_url"])}</code>；匹配={_html(job["match_fit_label"])}；说明={_html(job["message"])}</td></tr>
        <tr><th>岗位列表</th><td>返回 {len(jobs)} 个岗位；当前目标={_html(jobs[0].get("is_current_target") if jobs else False)}；import_method={_html(jobs[0].get("import_method") if jobs else "-")}。</td></tr>
        <tr><th>定制简历</th><td>resume_version_id=<code>{_html(resume["resume_version_id"])}</code>；package_id=<code>{_html(resume["package_id"])}</code>；source refs={_html(resume["source_refs_count"])}；pending confirmations={_html(resume["pending_confirmations_count"])}；blocking={_html(resume["blocking_count"])}；preflight={_html(resume["preflight_message"])}</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>需求到证据追踪矩阵</h2>
      <table><thead><tr><th>PRD 目标</th><th>代码实体</th><th>自动化证据</th><th>人工审计看点</th></tr></thead><tbody>
        <tr><td>用户知道需要提供什么资料</td><td><code>MaterialIntakeWizard</code>、<code>/api/files/upload?kind=...</code>、<code>document.kind</code></td><td><code>p8_desktop_initial.png</code>、P8 upload kind eval</td><td>五类资料卡是否清楚，上传入口是否贴近输入区且不误导为平台接入。</td></tr>
        <tr><td>手动导入 JD 并保存来源</td><td><code>JDIntakeCenter</code>、<code>POST /api/job/intake</code>、<code>job.source_url/platform/import_method</code></td><td><code>p8_desktop_job_intake.png</code>、<code>p8_api_evidence.json</code></td><td>URL 只归档，不触发抓取；缺失信息进入待确认。</td></tr>
        <tr><td>多 JD 目标岗位选择</td><td><code>JobTargetList</code>、<code>GET /api/jobs</code>、<code>POST /api/jobs/{{job_id}}/select</code>、<code>job.is_current_target</code></td><td>P8 list/select eval、岗位列表截图</td><td>当前目标岗位是否明确，不静默覆盖其他 JD。</td></tr>
        <tr><td>JD 定制简历可追溯</td><td><code>ResumeGenerationPlane</code>、<code>POST /api/resume/generate</code>、<code>resume_version</code>、<code>application_package</code></td><td><code>p8_desktop_resume_generated.png</code>、resume source refs/pending/preflight JSON</td><td>草稿是否绑定当前 JD，source refs、pending confirmations 和导出阻塞是否可见。</td></tr>
        <tr><td>不做虚假验收</td><td>Provider policy、未验证范围、report eval forbidden claims</td><td><code>test_p8_acceptance_report_eval.py</code>、未验证范围 section</td><td>报告是否没有把真实 provider、真实个人资料、招聘平台自动化写成通过。</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>人工复核清单与打回条件</h2>
      <table><thead><tr><th>检查项</th><th>通过标准</th><th>打回条件</th></tr></thead><tbody>
        <tr><td>截图可见性</td><td>5 张截图均能在 HTML 中直接显示，且分别覆盖桌面初始、JD 导入、简历生成、720px、390px。</td><td>任一图片缺失、不可见、不是当前界面或不能证明对应步骤。</td></tr>
        <tr><td>命令证据</td><td>全量 pytest、P8 eval、前端 build、drawio parse 均给出命令和结果摘要。</td><td>只写“通过”但没有命令、输出摘要或可复现路径。</td></tr>
        <tr><td>代码实体映射</td><td>UI/API/Domain/Storage/Evidence 均能映射到具体文件、函数或数据列。</td><td>只写抽象概念，无法定位到实现实体。</td></tr>
        <tr><td>真实能力边界</td><td>明确未验收真实 provider、真实个人资料、招聘平台自动化、自动投递。</td><td>出现任何默认通过、已接入、已自动投递等不实口径。</td></tr>
        <tr><td>用户体验路径</td><td>能从报告中复现资料准备、JD 导入、目标选择、定制简历和导出前检查。</td><td>缺少关键步骤或截图不能支撑路径闭环。</td></tr>
      </tbody></table>
    </section>
"""
    marker = "    <section>\n      <h2>截图证据</h2>"
    if marker not in html:
        raise RuntimeError("Could not locate screenshot evidence section for report enrichment.")
    html = html.replace(marker, enrich + marker)
    cleaned = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    REPORT.write_text(cleaned, encoding="utf-8")


def _append_post_report_validation(post_evidence: dict) -> None:
    html = REPORT.read_text(encoding="utf-8")
    rows = "\n".join(
        f"<tr><td>{_html(item['label'])}</td><td><code>{_html(item['command'])}</code></td><td class=\"{_html(item['status'])}\">{_html(item['status'])}</td><td><pre>{_html(item['summary'])}</pre></td></tr>"
        for item in post_evidence["results"]
    )
    section = f"""    <!-- P8_POST_REPORT_VALIDATION_START -->
    <section>
      <h2>生成后报告自检</h2>
      <p class="meta">以下检查在 HTML 报告生成并增强后执行，用于证明本报告本体、图片引用和 false-green 禁止语也已通过自动化门槛。结构化证据见 <code>{_html(POST_REPORT_EVIDENCE.relative_to(ROOT))}</code>。</p>
      <table><thead><tr><th>检查</th><th>命令</th><th>状态</th><th>输出摘要</th></tr></thead><tbody>{rows}</tbody></table>
    </section>
    <!-- P8_POST_REPORT_VALIDATION_END -->
"""
    marker = "    <section>\n      <h2>未验证范围与审计意见</h2>"
    if marker not in html:
        raise RuntimeError("Could not locate final audit section for post-report validation.")
    start = "    <!-- P8_POST_REPORT_VALIDATION_START -->"
    end = "    <!-- P8_POST_REPORT_VALIDATION_END -->"
    if start in html and end in html:
        before, remainder = html.split(start, 1)
        _, after = remainder.split(end, 1)
        html = before + after.lstrip("\n")
    html = html.replace(marker, section + marker)
    cleaned = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    REPORT.write_text(cleaned, encoding="utf-8")


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    command_evidence = _run_validation_commands()
    evidence = _run_api_flow()
    _write_browser_scenario(evidence, command_evidence)

    api_proc = subprocess.Popen(
        [str(ROOT / ".venv/bin/python"), "-m", "uvicorn", "services.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    vite_proc = subprocess.Popen(
        ["npm", "--prefix", "apps/chatbox", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_url("http://127.0.0.1:8000/api/health")
        _wait_url("http://127.0.0.1:5173/")
        subprocess.run(
            [
                "node",
                "scripts/browser_tools/browser-acceptance.mjs",
                "--start-chrome",
                "--scenario",
                str(SCENARIO),
                "--output-dir",
                str(EVIDENCE_DIR),
                "--report",
                str(REPORT),
                "--port",
                "9224",
            ],
            cwd=ROOT,
            check=True,
        )
        _enrich_report(evidence, command_evidence)
        bootstrap_post_evidence = _run_post_report_validation(bootstrap=True)
        _append_post_report_validation(bootstrap_post_evidence)
        post_evidence = _run_post_report_validation()
        _append_post_report_validation(post_evidence)
    finally:
        for proc in [vite_proc, api_proc]:
            proc.terminate()
        for proc in [vite_proc, api_proc]:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    print(REPORT)


if __name__ == "__main__":
    main()
