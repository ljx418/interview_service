from pathlib import Path

from services.storage.workspace import init_workspace
from services.workflows.p2_demo import run_p2_demo_flow


def test_p2_guided_demo_flow_returns_complete_user_path(tmp_path):
    workspace = init_workspace("p2-guided-demo-test", str(tmp_path / "workspace"))
    result = run_p2_demo_flow(workspace["workspace_id"])

    step_keys = [step["key"] for step in result["steps"]]
    assert step_keys == [
        "import_materials",
        "build_profile",
        "create_project_card",
        "analyze_job",
        "create_application_package",
        "export_package",
        "prepare_interview",
        "realtime_hint",
        "review_and_training",
    ]
    assert all(step["status"] == "completed" for step in result["steps"])
    assert result["summary"]["facts"] >= 5
    assert result["summary"]["fit_label"] in {"比较适合", "可以尝试", "先补强再投"}
    assert result["summary"]["package_id"]
    assert result["summary"]["training_tasks"] >= 3

    export_paths = [Path(item["path"]) for item in result["exports"]]
    assert len(export_paths) == 2
    assert {path.suffix for path in export_paths} == {".md", ".docx"}
    assert all(path.exists() for path in export_paths)

    key_outputs = result["key_outputs"]
    assert key_outputs["application_package"]["questions_to_confirm"]
    assert key_outputs["realtime_hint"]["structure"]
    assert key_outputs["review"]["training_tasks"]
