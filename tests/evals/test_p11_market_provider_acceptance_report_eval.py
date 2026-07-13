from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_p11_market_provider_acceptance_report_is_auditable() -> None:
    report = ROOT / "docs/reports/P11_MARKET_PROVIDER_OPTIN_ACCEPTANCE_REPORT.html"
    evidence = ROOT / "docs/reports/evidence/p11_market_provider/p11_market_provider_acceptance_evidence.json"
    screenshot = ROOT / "docs/reports/evidence/p11_market_provider/p11_chatbox_market_panel.png"

    assert report.exists(), "P11 HTML acceptance report must exist"
    assert evidence.exists(), "P11 structured evidence JSON must exist"
    assert screenshot.exists() and screenshot.stat().st_size > 0, "P11 real UI screenshot must exist"

    html = report.read_text(encoding="utf-8")
    data = json.loads(evidence.read_text(encoding="utf-8"))

    required_markers = [
        "P11 Market Provider Opt-in 自动化验收报告",
        "Level 1 通过",
        "目标架构与当前实现",
        "API 证据摘要",
        "命令证据",
        "未验证范围",
        "不能声明 Level 2",
        "不代表真实市场 provider",
        "p11_chatbox_market_panel.png",
    ]
    for marker in required_markers:
        assert marker in html

    assert all(command["exit_code"] == 0 for command in data["commands"])
    assert data["drawio"]["ok"] is True
    assert data["drawio"]["page_count"] <= 8
    assert data["api"]["provider_status"]["can_claim_real_market"] is False
    assert data["api"]["search_run"]["status"] == "fallback"
    assert data["api"]["opt_in_reject"]["error_code"] == "CONSENT_REQUIRED"
    assert data["screenshot"]["ok"] is True
