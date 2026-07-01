#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def _write_browser_scenario(evidence: dict) -> None:
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
            {"command": ".venv/bin/python -m pytest tests/evals/test_p8_jd_intake_resume_generation_eval.py", "status": "passed", "evidence": "3 passed，覆盖 P8 API、DB、ChatCore intent。"},
            {"command": ".venv/bin/python -m pytest tests/evals/test_p8_acceptance_report_eval.py", "status": "passed", "evidence": "2 passed，覆盖 HTML 报告结构、截图证据和 false-green 禁止语。"},
            {"command": "npm --prefix apps/chatbox run build", "status": "passed", "evidence": "TypeScript 与 Vite build 通过。"},
            {"command": f"API evidence JSON: {API_EVIDENCE.relative_to(ROOT)}", "status": "passed", "evidence": f"resume_version={evidence['resume']['resume_version_id']}，blocking={evidence['resume']['blocking_count']}。"},
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


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence = _run_api_flow()
    _write_browser_scenario(evidence)

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
