from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_p4c_fc_acceptance_report_contains_evidence_and_boundaries():
    report = ROOT / "docs/reports/P4C_FC_CONTINUOUS_DIALOGUE_ACCEPTANCE_REPORT.html"
    assert report.exists()
    html = report.read_text(encoding="utf-8")

    assert '<span class="badge">passed</span>' in html
    assert "P4C-FC Chatbox Continuous Dialogue Acceptance" in html
    assert "PRD 规格检视" in html
    assert "NOT A HUMAN ACCEPTANCE" in html
    assert "No real external provider call was made." in html
    assert "No real personal profile or raw private data was used." in html

    for screenshot in [
        "p4c_fc_desktop_initial.png",
        "p4c_fc_free_chat_first_turn.png",
        "p4c_fc_free_chat_second_turn.png",
        "p4c_fc_status_query.png",
        "p4c_fc_explicit_tool_artifact.png",
        "p4c_fc_session_restore.png",
        "p4c_fc_mobile_restored.png",
    ]:
        assert screenshot in html
        assert (ROOT / "docs/reports/p4c-fc-browser-acceptance" / screenshot).exists()
