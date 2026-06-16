import pytest

from services.llm.provider import provider_status
from services.storage.workspace import init_workspace
from services.workflows.p2_demo import run_p2_demo_flow


def test_example_mode_demo_flow_is_explicitly_labeled(tmp_path):
    workspace = init_workspace("p3-example-mode", str(tmp_path / "workspace"))

    result = run_p2_demo_flow(workspace["workspace_id"], data_mode="example")

    assert result["data_mode"] == "example"
    assert result["data_source"] == "repository_examples"
    assert result["summary"]["facts"] >= 5
    assert result["exports"]


def test_my_data_mode_cannot_run_examples_demo(tmp_path):
    workspace = init_workspace("p3-my-data-mode", str(tmp_path / "workspace"))

    with pytest.raises(ValueError, match="EXAMPLE_WORKFLOW_MODE_REQUIRED"):
        run_p2_demo_flow(workspace["workspace_id"], data_mode="my_data")


def test_mock_provider_status_is_local_boundary():
    status = provider_status("mock")

    assert status["provider"] == "mock"
    assert status["configured"] is True
    assert status["external_calls_enabled"] is False
