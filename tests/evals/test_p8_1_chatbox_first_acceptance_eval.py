from __future__ import annotations

import re
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P8_1_CHATBOX_FIRST_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_1_chatbox_first"
FINAL_EVIDENCE = EVIDENCE_DIR / "p8_1_final_acceptance_evidence.json"


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
        "审计总览",
        "人类审计步骤",
        "最终命令门槛",
        "截图审计索引",
        "追踪矩阵",
        "残余风险与打回条件",
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


def test_p8_1_final_acceptance_evidence_is_complete() -> None:
    assert FINAL_EVIDENCE.exists(), "P8.1 final acceptance evidence JSON is missing."
    evidence = json.loads(FINAL_EVIDENCE.read_text(encoding="utf-8"))
    labels = {item["label"]: item for item in evidence["results"]}
    expected = ["全量 pytest（排除报告自举 eval）", "Chatbox production build", "git diff whitespace check"]
    if not os.environ.get("JOBPILOT_P8_1_REPORT_EVAL_BOOTSTRAP"):
        expected.append("P8.1 报告 eval")
    if not os.environ.get("JOBPILOT_P8_1_REPORT_EVAL_BOOTSTRAP") and not os.environ.get("JOBPILOT_P8_1_REPORT_EVAL_FINALIZING"):
        expected.append("P8.1 报告 eval（final）")
    for label in expected:
        assert label in labels
        assert labels[label]["status"] == "passed"

    html = REPORT.read_text(encoding="utf-8")
    assert "passed" in labels["全量 pytest（排除报告自举 eval）"]["summary"]
    assert "git diff --check" in html
