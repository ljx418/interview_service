from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_chatbox_has_separate_conversation_and_workbench_regions():
    source = (ROOT / "apps/chatbox/src/main.tsx").read_text(encoding="utf-8")

    assert 'className="workstream conversation-area"' in source
    assert 'aria-label="对话区"' in source
    assert 'className="workbench"' in source
    assert 'aria-label="求职推进台"' in source
    assert source.index('className="workstream conversation-area"') < source.index('className="workbench"')


def test_workbench_keeps_stage_boundary_and_export_components():
    source = (ROOT / "apps/chatbox/src/main.tsx").read_text(encoding="utf-8")

    workbench_start = source.index('className="workbench"')
    workbench_source = source[workbench_start:]
    assert "WorkflowPanel" in workbench_source
    assert "ResultRail" in workbench_source
    assert "ArtifactCard" in source
