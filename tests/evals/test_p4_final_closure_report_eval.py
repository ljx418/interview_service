from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P4_FINAL_CLOSURE_AUTOMATED_ACCEPTANCE_REPORT.html"
AUDIT = ROOT / "docs/active/stage-reviews/P4_FINAL_CLOSURE_AUDIT.md"
EVIDENCE_DIR = ROOT / "docs/reports/p4-final-closure-evidence"


def test_p4_final_closure_report_contains_prd_code_doc_audit_and_evidence():
    assert REPORT.exists()
    assert AUDIT.exists()
    html = REPORT.read_text(encoding="utf-8")

    assert '<span class="badge">passed</span>' in html
    assert "P4 Final Closure Automated Audit" in html
    assert "命令结果" in html
    assert "71 passed, 1 warning" in html
    assert "PRD 规格检视" in html
    assert "代码检视" in html
    assert "文档审计" in html
    assert "NOT A HUMAN ACCEPTANCE" in html
    assert "No real external provider call was made." in html
    assert "No real personal profile" in html

    for screenshot in [
        "p4_final_initial_1200.png",
        "p4_final_initial_1280.png",
        "p4_final_initial_1440.png",
        "p4_final_initial_1600.png",
        "p4_final_initial_1920.png",
        "p4_final_narrow_720.png",
        "p4_final_mobile_390.png",
        "p4_final_guided_completed_1440.png",
        "p4_final_fc_free_first.png",
        "p4_final_fc_free_second.png",
        "p4_final_fc_status.png",
        "p4_final_fc_artifact.png",
        "p4_final_fc_mobile_restore.png",
    ]:
        assert screenshot in html
        assert (EVIDENCE_DIR / screenshot).exists()


def test_p4_final_closure_audit_does_not_overclaim_human_or_real_provider_acceptance():
    text = AUDIT.read_text(encoding="utf-8")

    assert "P4 frozen for local/mock examples path" in text
    assert "real external provider calls" in text
    assert "P4 is not fully productized" in text
    assert "freeze only covers the local/mock examples path" in text
    assert "human experience approval recorded" in text
    assert "71 passed, 1 warning" in text
    assert "P4B/P4C 已被人工体验认可" not in text
    assert "真实外部 provider 默认路径已通过" not in text
