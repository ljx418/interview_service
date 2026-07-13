from pathlib import Path


def test_p10_cli_acceptance_report_is_truthful_if_present():
    report = Path("docs/reports/P10_CLI_ACCEPTANCE_REPORT.html")
    if not report.exists():
        return
    text = report.read_text(encoding="utf-8")
    assert "P10-CLI 自动化验收报告" in text
    assert "未调用真实 provider" in text
    assert "未读取未授权真实个人资料目录" in text
    assert "未登录、抓取或联系招聘平台" in text
    assert "reports open" in text
    forbidden = [
        "真实 provider 已通过",
        "真实个人资料路径已通过",
        "招聘平台已接入",
        "ASR 已实现",
        "自动投递已实现",
        "MCP server 已实现",
    ]
    assert not any(item in text for item in forbidden)
