from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P8_JD_INTAKE_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_jd_intake"


def test_p8_acceptance_report_contains_required_evidence_and_boundaries():
    assert REPORT.exists()
    html = REPORT.read_text(encoding="utf-8")

    required = [
        '<span class="badge">passed</span>',
        "目标架构",
        "当前实现",
        "PRD 规格检视",
        "截图证据",
        "未验证范围",
        "POST /api/job/intake",
        "POST /api/resume/generate",
        "source refs",
        "pending confirmations",
        "未接入 BOSS",
        "未调用真实外部 LLM provider",
        "未使用用户真实个人资料",
    ]
    for marker in required:
        assert marker in html

    forbidden_claims = [
        "BOSS 已接入",
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "自动投递已实现",
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
