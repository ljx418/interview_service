from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P9_STAGE_CLOSURE_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p9_stage_closure"
COMMAND_EVIDENCE = EVIDENCE_DIR / "p9_stage_closure_command_evidence.json"
POST_REPORT_EVIDENCE = EVIDENCE_DIR / "p9_stage_closure_post_report_evidence.json"


def test_p9_stage_closure_report_has_required_human_audit_sections_and_images() -> None:
    if not REPORT.exists():
        pytest.skip("P9 stage closure report has not been generated yet.")
    html = REPORT.read_text(encoding="utf-8")
    required = [
        "P9 阶段收口：Chatbox-native 求职情报工作台自动化验收报告",
        "目标架构",
        "当前实现",
        "自动化步骤",
        "验收标准",
        "命令结果",
        "PRD 规格检视",
        "代码检视",
        "文档审计",
        "截图证据",
        "未验证范围与审计意见",
        "TopServiceCenter",
        "LeftIntelligencePanel",
        "ConversationPlane",
        "RightArtifactBench",
        "drawio",
        "阶段收口",
    ]
    for marker in required:
        assert marker in html

    image_refs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    assert len(image_refs) >= 7
    for ref in image_refs:
        image = (REPORT.parent / ref).resolve()
        assert image.exists(), f"Missing image reference: {ref}"
        assert image.stat().st_size > 1024, f"Image evidence is too small: {ref}"

    expected_files = [
        "p9_initial_1920.png",
        "p9_search_run_1920.png",
        "p9_pipeline_update_1920.png",
        "p9_1440.png",
        "p9_1200.png",
        "p9_720.png",
        "p9_390.png",
    ]
    for filename in expected_files:
        assert (EVIDENCE_DIR / filename).exists(), f"Missing P9 stage closure screenshot: {filename}"


def test_p9_stage_closure_report_does_not_claim_high_risk_false_green() -> None:
    if not REPORT.exists():
        pytest.skip("P9 stage closure report has not been generated yet.")
    html = REPORT.read_text(encoding="utf-8")
    forbidden_claims = [
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "自动投递已实现",
        "ASR 已实现",
        "全网搜索已完成",
        "BOSS 自动接入通过",
    ]
    for claim in forbidden_claims:
        assert claim not in html
    assert "未登录、抓取、自动沟通或自动投递" in html
    assert "未默认调用 MiniMax、DeepSeek" in html


def test_p9_stage_closure_static_implementation_entities_exist() -> None:
    main = (ROOT / "apps/chatbox/src/main.tsx").read_text(encoding="utf-8")
    css = (ROOT / "apps/chatbox/src/styles.css").read_text(encoding="utf-8")
    required_main = [
        "function TopServiceCenter",
        "function LeftIntelligencePanel",
        "function MarketMapView",
        "function OpportunityMatchPanel",
        "function ApplicationPipelineView",
        "function P9ArtifactOverview",
        "async function handleP9Command",
        "jobpilot:p9:pipeline",
    ]
    for marker in required_main:
        assert marker in main
    required_css = [
        ".top-service-center",
        ".left-intelligence-panel",
        ".market-map",
        ".pipeline-lane",
        ".p9-artifact-overview",
    ]
    for marker in required_css:
        assert marker in css


def test_p9_stage_closure_structured_evidence_files_pass() -> None:
    if not REPORT.exists():
        pytest.skip("P9 stage closure report has not been generated yet.")
    assert COMMAND_EVIDENCE.exists()
    command_evidence = json.loads(COMMAND_EVIDENCE.read_text(encoding="utf-8"))
    for item in command_evidence["results"]:
        assert item["status"] == "passed", item

    assert POST_REPORT_EVIDENCE.exists()
    post = json.loads(POST_REPORT_EVIDENCE.read_text(encoding="utf-8"))
    assert post["status"] == "passed"
    assert post["image_count"] >= 7
    assert post["missing_images"] == []
    assert post["missing_text"] == []
    assert post["forbidden_hits"] == []


def test_p9_stage_closure_drawio_text_mirror_is_synced() -> None:
    drawio = ROOT / "docs/active/jobpilot-stage-gap-and-acceptance.drawio"
    mirror = ROOT / "docs/active/jobpilot-stage-gap-and-acceptance.md"
    assert drawio.exists()
    assert mirror.exists()

    text = mirror.read_text(encoding="utf-8")
    required = [
        "P9 Chatbox-native 求职情报与申请包工作台自动化候选阶段收口审计",
        "P9-M0 到 P9-M9 本轮状态",
        "目标架构、当前实现、开发内容和出门门槛在本地自动化候选范围内全绿",
        "真实全网 JD 搜索已完成",
    ]
    for marker in required:
        assert marker in text

    import xml.etree.ElementTree as ET

    root = ET.parse(drawio).getroot()
    diagrams = root.findall("diagram")
    assert len(diagrams) == 8
    names = [diagram.attrib.get("name", "") for diagram in diagrams]
    assert "3 代码实体与分层" in names
    assert "7 里程碑门槛出门" in names
