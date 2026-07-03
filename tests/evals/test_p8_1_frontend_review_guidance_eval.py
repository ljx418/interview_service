from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P8_1_FRONTEND_REVIEW_GUIDANCE.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_1_frontend_review"


def test_p8_1_frontend_review_report_has_required_sections_and_boundaries() -> None:
    html = REPORT.read_text(encoding="utf-8")

    required = [
        "P8.1 前端优化审查与自动化实现指导",
        "概念图",
        "当前实际实现基线截图",
        "目标概念截图",
        "当前截图与目标截图对比",
        "用户操作 / 体验路线图",
        "自动化开发指导",
        "端到端验收门槛",
        "AI 文生图审计",
        "未验证范围",
        "用户指导 - Chatbox - 工作台",
        "p8-workflow-strip",
        "目标概念截图不是当前实现截图",
    ]
    for marker in required:
        assert marker in html

    forbidden = [
        "P8.1 已实现",
        "Chatbox-first UI 已验收通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "招聘平台自动接入通过",
        "自动投递已实现",
    ]
    for marker in forbidden:
        assert marker not in html


def test_p8_1_frontend_review_images_exist_and_are_nontrivial() -> None:
    html = REPORT.read_text(encoding="utf-8")
    refs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    assert len(refs) >= 8

    expected = {
        "evidence/p8_1_frontend_review/p8_1_concept_diagram.svg",
        "evidence/p8_1_frontend_review/baseline_current_1440.png",
        "evidence/p8_1_frontend_review/baseline_current_1200.png",
        "evidence/p8_1_frontend_review/baseline_current_720.png",
        "evidence/p8_1_frontend_review/baseline_current_390.png",
        "evidence/p8_1_frontend_review/target_chatbox_first_1440.png",
        "evidence/p8_1_frontend_review/target_chatbox_first_720.png",
        "evidence/p8_1_frontend_review/target_chatbox_first_390.png",
    }
    assert expected.issubset(set(refs))

    for ref in expected:
        path = REPORT.parent / ref
        assert path.exists(), ref
        assert path.stat().st_size > 1024, ref


def test_p8_1_frontend_review_evidence_json_records_current_state_and_ai_audit() -> None:
    command_evidence = json.loads((EVIDENCE_DIR / "p8_1_command_evidence.json").read_text(encoding="utf-8"))
    ai_audit = json.loads((EVIDENCE_DIR / "p8_1_ai_image_audit.json").read_text(encoding="utf-8"))

    assert command_evidence["static_facts"]["p8_workflow_strip_before_timeline"] is True
    assert command_evidence["static_facts"]["main_entities"]["DesktopContextPanel"] is True
    assert command_evidence["static_facts"]["main_entities"]["Workbench"] is True
    assert all(item["status"] == "passed" for item in command_evidence["images"])
    assert any(item["label"] == "headless Chrome screenshot capture" and item["status"] == "passed" for item in command_evidence["results"])

    assert ai_audit["ai_text_to_image_used"] is False
    assert "HTML/SVG" in ai_audit["decision"]
    assert ai_audit["mode_detection"]["mode"] in {"B-or-C", "unknown"}
