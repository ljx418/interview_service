from pathlib import Path

import pytest

from services.llm.contracts import validate_output
from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def test_formal_assist_realtime_hint_has_no_full_answer(tmp_path):
    workspace = init_workspace("realtime-eval", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]])
    jobpilot.create_story_cards(workspace_id)
    session = jobpilot.start_realtime_session(workspace_id, mode="formal_assist")

    hint = jobpilot.generate_hint(session["session_id"], "讲一个你解决技术难题的经历。", "outline")

    assert "full_answer" not in hint["hint"]
    assert hint["hint"]["hint_level"] in {"minimal", "outline"}
    assert hint["hint"]["source_refs"]


def test_formal_assist_rejects_draft_and_malformed_schema(tmp_path):
    workspace = init_workspace("realtime-bad-eval", str(tmp_path / "workspace"))
    session = jobpilot.start_realtime_session(workspace["workspace_id"], mode="formal_assist")

    with pytest.raises(ValueError):
        jobpilot.generate_hint(session["session_id"], "Tell me about your project.", "draft")

    with pytest.raises(ValueError):
        validate_output(
            "realtime_generate_hint",
            {
                "question_type": "project_deep_dive",
                "hint_level": "draft",
                "recommended_project": "TodoPlus",
                "structure": ["full_answer: read this line verbatim"],
                "reminder": "bad",
                "source_refs": [],
            },
        )
