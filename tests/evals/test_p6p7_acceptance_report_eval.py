from pathlib import Path


def test_p6p7_acceptance_report_has_visible_evidence_and_boundaries():
    report = Path("docs/reports/P6P7_AUTOMATED_ACCEPTANCE_REPORT.html")
    assert report.exists()
    html = report.read_text(encoding="utf-8")

    assert "P6+P7 自动化验收报告" in html
    assert "目标架构" in html
    assert "当前实现" in html
    assert "PRD 规格检视" in html
    assert "Fake provider" in html
    assert "未执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼" in html
    assert "未读取或验收用户真实个人资料" in html
    assert "不执行删除或迁移 apply" in html

    required_images = [
        "p6p7-desktop-initial.png",
        "p6p7-provider-settings.png",
        "p6p7-provider-consented.png",
        "p6p7-fake-provider-chat.png",
        "p6p7-workspace-backup.png",
        "p6p7-diagnostics.png",
        "p6p7-mobile-initial.png",
    ]
    for image in required_images:
        assert image in html
        assert (Path("docs/reports/evidence/p6p7_acceptance") / image).exists()


def test_p6p7_stage_audits_do_not_overclaim_real_provider_or_real_profile():
    audit_paths = [
        Path("docs/active/stage-reviews/P6_M2_PROVIDER_BACKED_CHAT_ACCEPTANCE_AUDIT.md"),
        Path("docs/active/stage-reviews/P6_M4_M5_TOOL_SAFETY_PRIVACY_AUDIT.md"),
        Path("docs/active/stage-reviews/P6P7_AUTOMATED_ACCEPTANCE_AND_PRD_REVIEW.md"),
        Path("docs/active/stage-reviews/P7_M3_BETA_CLOSURE_AUDIT.md"),
    ]
    for path in audit_paths:
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "真实 provider" in text or "真实外部 provider" in text
        assert "真实个人资料" in text
        assert "不得声明" in text or "未验证范围" in text
        assert "真实个人资料路径已通过" not in text
        assert "真实外部 provider 默认路径已通过" not in text


def test_p6p7_stage_acceptance_report_has_visible_evidence_and_audit_sections():
    report = Path("docs/reports/P6P7_STAGE_ACCEPTANCE_AUDIT_REPORT.html")
    assert report.exists()
    html = report.read_text(encoding="utf-8")

    assert "P6+P7 阶段性审计与自动化验收报告" in html
    assert "目标架构" in html
    assert "当前实现" in html
    assert "PRD 规格检视" in html
    assert "代码检视" in html
    assert "文档审计" in html
    assert "截图证据" in html
    assert "未执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼" in html
    assert "未读取或验收用户真实个人资料" in html
    assert "不执行删除或迁移 apply" in html
    assert "不是 production/SaaS ready" in html

    required_images = [
        "stage-desktop-initial.png",
        "stage-provider-settings.png",
        "stage-provider-consented.png",
        "stage-fake-provider-chat.png",
        "stage-workspace-backup.png",
        "stage-cleanup-dry-run.png",
        "stage-migration-dry-run.png",
        "stage-diagnostics.png",
        "stage-wide-1920.png",
        "stage-mobile-390.png",
    ]
    for image in required_images:
        assert image in html
        assert (Path("docs/reports/evidence/p6p7_stage_acceptance") / image).exists()
