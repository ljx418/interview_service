from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P4_UX_EXPERIENCE_ACCEPTANCE_REPORT.html"


def test_p4_ux_report_exists_and_references_real_chrome_evidence():
    assert REPORT.exists()
    html = REPORT.read_text(encoding="utf-8")

    required_images = [
        "evidence/p4_workbench_initial_1200.png",
        "evidence/p4_workbench_initial_1280.png",
        "evidence/p4_workbench_initial_1440.png",
        "evidence/p4_workbench_initial_1600.png",
        "evidence/p4_workbench_initial_1920.png",
        "evidence/p4_workbench_error_recovery_1200.png",
        "evidence/p4_workbench_error_recovery_1280.png",
        "evidence/p4_workbench_completed_1200.png",
        "evidence/p4_workbench_completed_1280.png",
        "evidence/p4_workbench_completed_1440.png",
        "evidence/p4_workbench_completed_1600.png",
        "evidence/p4_workbench_completed_1920.png",
        "evidence/p4_workbench_narrow_720.png",
        "evidence/p4_workbench_mobile_390.png",
    ]
    for image in required_images:
        assert image in html
        assert (REPORT.parent / image).exists()

    assert "python3 -m pytest" in html
    assert "63 passed" in html
    assert "npm --prefix apps/chatbox run build" in html
    assert "外部模型未调用（隐私安全）" in html
    assert "1200px、1440px、1600px、1920px" in html
    assert "viewport emulation" in html
    assert "未验证范围与虚假验收风险" in html


def test_p4_ux_report_does_not_overclaim_human_or_real_data_acceptance():
    html = REPORT.read_text(encoding="utf-8")

    assert "人工主观体验认可仍需人类最终确认" in html
    assert "不等于真实个人资料自动验收" in html
    assert "没有默认触发真实外部 provider 调用" in html
    assert "人工体验已完全认可" not in html
    assert "真实个人资料自动验收通过" not in html
