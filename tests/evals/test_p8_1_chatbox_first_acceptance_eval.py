from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P8_1_CHATBOX_FIRST_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_1_chatbox_first"


def test_p8_1_acceptance_report_has_required_sections_and_real_screenshots() -> None:
    assert REPORT.exists(), "P8.1 Chatbox-first acceptance report is missing."
    html = REPORT.read_text(encoding="utf-8")

    required = [
        "P8.1 Chatbox-first 工作台自动化验收报告",
        "目标架构",
        "当前实现",
        "PRD 规格检视",
        "截图证据",
        "未验证范围与审计意见",
        "P8.1 阶段聊天能力边界",
        "Conversation Plane",
        "ComposerWorkflowDock",
        "Workbench",
    ]
    for marker in required:
        assert marker in html

    image_refs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    assert len(image_refs) >= 6
    for ref in image_refs:
        image = (REPORT.parent / ref).resolve()
        assert image.exists(), f"Missing image reference: {ref}"
        assert image.stat().st_size > 1024, f"Image evidence is too small: {ref}"

    expected_files = [
        "p8_1_chatbox_first_1920.png",
        "p8_1_jd_intake_workbench_1920.png",
        "p8_1_chatbox_first_1440.png",
        "p8_1_chatbox_first_1200.png",
        "p8_1_chatbox_first_720.png",
        "p8_1_chatbox_first_390.png",
    ]
    for filename in expected_files:
        assert (EVIDENCE_DIR / filename).exists()


def test_p8_1_acceptance_report_does_not_claim_false_green_scope() -> None:
    html = REPORT.read_text(encoding="utf-8")
    forbidden_claims = [
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "自动投递已实现",
        "SaaS 已实现",
        "ASR 已实现",
        "会议平台已实现",
        "Scenario did not define multi-turn dialogue evidence",
    ]
    for claim in forbidden_claims:
        assert claim not in html


def test_p8_1_chatbox_first_static_guard() -> None:
    main = (ROOT / "apps/chatbox/src/main.tsx").read_text(encoding="utf-8")
    css = (ROOT / "apps/chatbox/src/styles.css").read_text(encoding="utf-8")

    legacy_order = re.search(r'<section className="p8-workflow-strip"[\s\S]+?<div className="timeline"', main)
    assert legacy_order is None
    assert "function ComposerWorkflowDock" in main
    assert "JobTargetList jobs={jobs}" in main
    assert ".composer-tool-rail" in css
    assert ".composer-workflow-panel" in css
