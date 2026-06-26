from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P4B_REAL_USER_SCENARIO_AUTOMATED_ACCEPTANCE_REPORT.html"


def test_p4b_real_user_scenario_report_references_automated_evidence():
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

    assert "目标架构" in html
    assert "当前架构实现" in html
    assert "自动化用户场景路径" in html
    assert ".venv/bin/python -m pytest" in html
    assert "63 passed" in html
    assert "npm --prefix apps/chatbox run build" in html
    assert "Chrome CDP" in html


def test_p4b_real_user_scenario_report_does_not_overclaim():
    html = REPORT.read_text(encoding="utf-8")

    assert "人工体验认可" in html
    assert "未自动验收" in html
    assert "不等于真实个人简历" in html
    assert "没有默认触发真实外部 provider 调用" in html
    assert "不能写成“P4B 已被人工体验认可”" in html
    assert "真实个人资料验收通过" not in html
    assert "真实外部 provider 默认路径已通过" not in html
