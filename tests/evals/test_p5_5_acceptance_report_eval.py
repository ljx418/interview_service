from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p5_5_candidate_profile"


def test_p5_5_acceptance_report_has_screenshots_and_boundaries():
    html = REPORT.read_text(encoding="utf-8")

    assert "P5.5 Candidate Profile 自动化验收报告" in html
    assert "目标架构" in html
    assert "当前实现" in html
    assert "PRD 规格检视" in html
    assert "截图证据" in html
    assert "多背景多轮对话补证" in html
    assert "20 轮对话 transcript" in html
    assert "fake provider opt-in" in html
    assert "周亦然（合成）" in html
    assert "林澈（合成）" in html
    assert "陈若宁（合成）" in html
    assert "第 20 轮" in html
    assert "GET /api/profile/candidate" in html
    assert "POST /api/profile/candidate/refresh" in html
    assert "未使用用户真实个人资料" in html
    assert "未执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼" in html
    assert "未覆盖真实 LLM/provider 的回复质量、成本、稳定性或可用性验收" in html
    assert "不是人工体验认可" in html
    assert "真实个人资料路径已通过" not in html
    assert "真实 provider 默认路径已通过" not in html
    assert "真实 LLM 接入已通过" not in html
    assert "真实 LLM 或真实 provider 质量验收通过" not in html
    assert "真实 provider 质量验收通过。" not in html
    assert (EVIDENCE_DIR / "p5_5_multi_turn_dialogues.json").exists()

    for image in [
        "p5_5_initial_desktop.png",
        "p5_5_profile_overview.png",
        "p5_5_source_refs.png",
        "p5_5_profile_1200.png",
        "p5_5_profile_1600.png",
        "p5_5_profile_1920.png",
        "p5_5_profile_720.png",
        "p5_5_profile_mobile_390.png",
    ]:
        assert image in html
        assert (EVIDENCE_DIR / image).exists()
