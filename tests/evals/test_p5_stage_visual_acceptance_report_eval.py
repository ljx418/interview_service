from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_p5_stage_visual_report_has_visible_evidence_and_boundaries():
    report = ROOT / "docs/reports/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_REPORT.html"
    assert report.exists()
    html = report.read_text(encoding="utf-8")

    required_text = [
        "P5 阶段性合成资料可视化验收报告",
        "目标架构与当前实现",
        "本轮可完成的用户体验路径",
        "不代表 P5-REAL",
        "未使用用户真实个人资料",
        "未调用 MiniMax、DeepSeek、OpenAI-compatible 等真实外部 provider",
    ]
    for text in required_text:
        assert text in html

    required_images = [
        "p5-synthetic-realism-ops_to_frontend-evidence/p5_real_jd_match_redacted.png",
        "p5-synthetic-realism-ops_to_frontend-evidence/p5_real_export_blocked_redacted.png",
        "p5-synthetic-realism-teacher_to_edtech-evidence/p5_real_export_completed_mobile_redacted.png",
    ]
    for image in required_images:
        assert image in html
        image_path = report.parent / image
        assert image_path.exists()
        assert image_path.stat().st_size > 50_000


def test_p5_stage_audit_keeps_synthetic_scope_honest():
    audit = ROOT / "docs/active/stage-reviews/P5_STAGE_SYNTHETIC_VISUAL_ACCEPTANCE_AUDIT.md"
    assert audit.exists()
    text = audit.read_text(encoding="utf-8")

    assert "P5 合成资料增强自动化候选通过" in text
    assert "不得声明 P5-REAL" in text
    assert "真实个人资料路径" in text
    assert "未验证" in text
    assert "88 passed" in text
