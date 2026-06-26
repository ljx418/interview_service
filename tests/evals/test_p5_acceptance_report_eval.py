from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P5_LOCAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/p5-local-data-closure-evidence"
PRE_FREEZE_AUDIT = ROOT / "docs/active/stage-reviews/P5_PRE_FREEZE_AUTOMATED_CANDIDATE_AUDIT.md"
HUMAN_CHECKLIST = ROOT / "docs/active/stage-reviews/P5_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md"


def test_p5_local_data_closure_report_contains_required_evidence_and_boundaries():
    assert REPORT.exists()
    html = REPORT.read_text(encoding="utf-8")

    assert '<span class="badge">passed</span>' in html
    assert "P5 本地资料闭环自动化验收" in html
    assert "目标架构" in html
    assert "当前实现" in html
    assert "截图证据" in html
    assert "6 passed" in html
    assert "EXPORT_PRECHECK_FAILED" in html
    assert "NOT A HUMAN ACCEPTANCE" in html
    assert "未使用用户真实个人资料" in html
    assert "未配置或调用 MiniMax、DeepSeek、OpenAI-compatible" in html

    for screenshot in [
        "p5_initial_desktop.png",
        "p5_jd_match_desktop.png",
        "p5_package_needs_confirmation.png",
        "p5_export_blocked.png",
        "p5_package_confirmed.png",
        "p5_export_completed.png",
        "p5_export_completed_1200.png",
        "p5_export_completed_1600.png",
        "p5_export_completed_1920.png",
        "p5_export_completed_720.png",
        "p5_export_completed_mobile.png",
    ]:
        assert screenshot in html
        assert (EVIDENCE_DIR / screenshot).exists()


def test_p5_pre_freeze_docs_do_not_overclaim_real_data_or_productization():
    assert PRE_FREEZE_AUDIT.exists()
    assert HUMAN_CHECKLIST.exists()
    audit = PRE_FREEZE_AUDIT.read_text(encoding="utf-8")
    checklist = HUMAN_CHECKLIST.read_text(encoding="utf-8")

    assert "本地/mock + 脱敏 fixture 自动化候选通过" in audit
    assert "P5 尚未冻结" in audit
    assert "真实授权资料路径" in audit
    assert "不得声明 P5 已冻结" in audit
    assert "真实资料路径未填写前，不得标记通过" in checklist
    assert "默认不调用" in checklist
    assert "真实个人资料路径已通过" not in audit
    assert "最终产品化发布已通过" not in audit
