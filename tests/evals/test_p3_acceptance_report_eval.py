from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P3_REAL_USER_CHATBOX_ACCEPTANCE_REPORT.html"


def test_p3_acceptance_report_exists_and_references_real_evidence():
    assert REPORT.exists()
    html = REPORT.read_text(encoding="utf-8")

    required_images = [
        "evidence/p3_chatbox_initial_1280.png",
        "evidence/p3_chatbox_error_state_1280.png",
        "evidence/p3_chatbox_response_1280.png",
        "evidence/p3_chatbox_narrow_720.png",
        "evidence/p3_chatbox_mobile_390.png",
    ]
    for image in required_images:
        assert image in html
        assert (REPORT.parent / image).exists()

    assert "未验证范围" in html
    assert "真实个人资料自动验收" in html
    assert "61 passed" in html
    assert "人工 UX 审查意见" in html
    assert "当前用户体验已被人工完全认可" in html
    assert "npm --prefix apps/chatbox run build" in html
