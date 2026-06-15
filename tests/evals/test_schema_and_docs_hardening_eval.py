from pathlib import Path

import pytest

from services.llm.contracts import SourceRef, validate_output


ROOT = Path(__file__).resolve().parents[2]


def test_source_ref_accepts_all_documented_p0_source_types():
    for source_type in [
        "career_fact",
        "skill_evidence",
        "tech_project",
        "document",
        "job",
        "story_card",
        "transcript",
        "artifact",
        "resume_version",
        "application_package",
        "interview",
        "realtime_session",
    ]:
        ref = SourceRef(source_type=source_type, source_id="source_1")
        assert ref.source_type == source_type


def test_realtime_hint_contract_rejects_extra_fields_and_verbatim_answer():
    base_payload = {
        "question_type": "project_deep_dive",
        "hint_level": "outline",
        "recommended_project": "TodoPlus",
        "structure": ["先复述问题", "说明项目背景", "讲你的实现"],
        "reminder": "只给结构提示。",
        "source_refs": [{"source_type": "tech_project", "source_id": "proj_1"}],
    }
    accepted = validate_output("realtime_generate_hint", base_payload)
    assert accepted["hint_level"] == "outline"

    with pytest.raises(ValueError):
        validate_output("realtime_generate_hint", {**base_payload, "full_answer": "照着念这段完整答案"})

    with pytest.raises(ValueError):
        validate_output("realtime_generate_hint", {**base_payload, "structure": ["完整答案：照着念"]})


def test_active_docs_do_not_contain_stale_pre_freeze_gap_language():
    stale_phrases = [
        "当前不足",
        "启发式输出需要替换",
        "事实和产物确认 UI 不完整",
        "导出下载还不是 Chatbox 的一等动作",
        "chat session 未持久化",
        "eval gates 需要覆盖",
    ]
    checked_files = [
        ROOT / "docs/active/02_TARGET_ARCHITECTURE.md",
        ROOT / "docs/active/06_TRACEABILITY_MATRIX.md",
        ROOT / "docs/active/07_REMAINING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md",
        ROOT / "docs/active/jobpilot-stage-gap-and-acceptance.md",
        ROOT / "docs/active/09_AUTOMATED_DEVELOPMENT_SCOPE.md",
        ROOT / "docs/active/10_P0_FREEZE_AUDIT_AND_ACCEPTANCE_REPORT.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)
    for phrase in stale_phrases:
        assert phrase not in combined
