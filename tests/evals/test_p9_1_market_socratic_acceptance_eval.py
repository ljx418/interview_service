from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/P9_1_MARKET_SOCRATIC_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p9_1_market_socratic"
COMMAND_EVIDENCE = EVIDENCE_DIR / "p9_1_command_evidence.json"
POST_REPORT_EVIDENCE = EVIDENCE_DIR / "p9_1_post_report_evidence.json"


def test_p9_1_static_implementation_entities_exist() -> None:
    main = (ROOT / "apps/chatbox/src/main.tsx").read_text(encoding="utf-8")
    css = (ROOT / "apps/chatbox/src/styles.css").read_text(encoding="utf-8")
    package_json = (ROOT / "apps/chatbox/package.json").read_text(encoding="utf-8")

    required_main = [
        "import * as echarts from \"echarts\"",
        "echarts.registerMap",
        "type AdministrativeRegionNode",
        "type RegionJobDistributionSnapshot",
        "type MarketMapLayerState",
        "type SocraticSession",
        "function MarketMapView",
        "Market Provider: not_configured",
        "Socratic Intake",
        "CandidateFactSummary",
        "PendingConfirmations",
        "DoNotClaimList",
    ]
    for marker in required_main:
        assert marker in main

    required_css = [
        ".echarts-drilldown-map",
        ".market-layer-tabs",
        ".map-breadcrumb",
        ".source-trust-legend",
        ".salary-histogram",
        ".socratic-artifact-panel",
    ]
    for marker in required_css:
        assert marker in css

    assert "\"echarts\"" in package_json


def test_p9_1_report_has_required_sections_and_images() -> None:
    assert REPORT.exists(), "P9.1 acceptance report is missing."
    html = REPORT.read_text(encoding="utf-8")
    required = [
        "P9.1 行政区划市场地图与 Socratic Intake 自动化验收报告",
        "目标架构",
        "当前实现",
        "自动化步骤",
        "验收标准",
        "命令结果",
        "PRD 规格检视",
        "代码检视",
        "文档审计",
        "多背景多轮对话补证",
        "截图证据",
        "未验证范围与审计意见",
        "ECharts",
        "行政区划下钻",
        "Socratic Intake",
        "Market Provider: not_configured",
    ]
    for marker in required:
        assert marker in html

    image_refs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    assert len(image_refs) >= 8
    for ref in image_refs:
        image = (REPORT.parent / ref).resolve()
        assert image.exists(), f"Missing image reference: {ref}"
        assert image.stat().st_size > 1024, f"Image evidence is too small: {ref}"


def test_p9_1_report_does_not_claim_high_risk_false_green() -> None:
    html = REPORT.read_text(encoding="utf-8")
    forbidden_claims = [
        "真实市场 provider 已接入",
        "全网 JD 搜索已完成",
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实 ASR 已实现",
        "自动投递已实现",
        "MCP/Skill 连通性已通过",
    ]
    for claim in forbidden_claims:
        assert claim not in html
    assert "未登录、抓取、自动沟通或自动投递" in html
    assert "未默认调用 MiniMax、DeepSeek" in html


def test_p9_1_structured_evidence_files_pass() -> None:
    assert COMMAND_EVIDENCE.exists()
    command_evidence = json.loads(COMMAND_EVIDENCE.read_text(encoding="utf-8"))
    for item in command_evidence["results"]:
        assert item["status"] == "passed", item

    assert POST_REPORT_EVIDENCE.exists()
    post = json.loads(POST_REPORT_EVIDENCE.read_text(encoding="utf-8"))
    assert post["status"] == "passed"
    assert post["image_count"] >= 8
    assert post["missing_images"] == []
    assert post["missing_text"] == []
    assert post["forbidden_hits"] == []
