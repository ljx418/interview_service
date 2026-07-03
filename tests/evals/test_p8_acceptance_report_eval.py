import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_jd_intake"


def test_p8_acceptance_report_contains_required_evidence_and_boundaries():
    assert REPORT.exists()
    html = REPORT.read_text(encoding="utf-8")

    bootstrap = os.getenv("JOBPILOT_P8_REPORT_BOOTSTRAP") == "1"
    required = [
        '<span class="badge">passed</span>',
        "目标架构",
        "当前实现",
        "PRD 规格检视",
        "审计结论总览",
        "审计包索引",
        "命令证据明细",
        "工作区状态",
        "API Evidence 摘要",
        "需求到证据追踪矩阵",
        "人工复核清单与打回条件",
        "截图证据",
        "未验证范围",
        "POST /api/job/intake",
        "POST /api/resume/generate",
        "source refs",
        "pending confirmations",
        "MaterialIntakeWizard",
        "JDIntakeCenter",
        "JobTargetList",
        "ResumeGenerationPlane",
        "tests/evals/test_p8_jd_intake_resume_generation_eval.py",
        "scripts/generate_p8_jd_intake_acceptance.py",
        "p8_command_evidence.json",
        "未接入 BOSS",
        "未调用真实外部 LLM provider",
        "未使用用户真实个人资料",
    ]
    if not bootstrap:
        required.extend(["生成后报告自检", "p8_post_report_evidence.json"])
    for marker in required:
        assert marker in html

    forbidden_claims = [
        "BOSS 已接入",
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "自动投递已实现",
        "Scenario did not define multi-turn dialogue evidence",
        "No screenshots captured",
    ]
    for marker in forbidden_claims:
        assert marker not in html

    screenshots = [
        "p8_desktop_initial.png",
        "p8_desktop_job_intake.png",
        "p8_desktop_resume_generated.png",
        "p8_tablet_720.png",
        "p8_mobile_390.png",
    ]
    for name in screenshots:
        path = EVIDENCE_DIR / name
        assert path.exists()
        assert path.stat().st_size > 1024
        assert name in html


def test_p8_api_evidence_is_present_and_structured():
    path = EVIDENCE_DIR / "p8_api_evidence.json"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "workspace_id" in text
    assert "resume_version_id" in text
    assert "blocking_count" in text
    assert "source_url 只作为归档证据保存" in text


def test_p8_command_evidence_is_generated_from_real_commands():
    path = EVIDENCE_DIR / "p8_command_evidence.json"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    required = [
        '"git_head"',
        '"git_status_short"',
        ".venv/bin/python -m pytest --ignore=tests/evals/test_p8_acceptance_report_eval.py",
        "tests/evals/test_p8_jd_intake_resume_generation_eval.py",
        "npm --prefix apps/chatbox run build",
        "drawio XML parse",
        "git diff --check",
        '"returncode": 0',
    ]
    for marker in required:
        assert marker in text


def test_p8_post_report_evidence_closes_report_self_check():
    if os.getenv("JOBPILOT_P8_REPORT_BOOTSTRAP") == "1":
        return
    path = EVIDENCE_DIR / "p8_post_report_evidence.json"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    required = [
        '"git_head"',
        '"git_status_short"',
        "tests/evals/test_p8_acceptance_report_eval.py",
        "报告图片与 false-green 快速检查",
        "image refs=5",
        '"returncode": 0',
    ]
    for marker in required:
        assert marker in text
