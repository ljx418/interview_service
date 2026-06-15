from pathlib import Path

import pytest

from services.storage.db import loads
from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _build_package_artifact(tmp_path):
    workspace = init_workspace("p1-regenerate", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    job = jobpilot.parse_jd(workspace_id, (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8"))
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    return workspace_id, package["artifact_ref"]["artifact_id"]


def test_regenerate_creates_child_version_and_updates_current(tmp_path):
    workspace_id, artifact_id = _build_package_artifact(tmp_path)
    v1 = jobpilot.list_artifact_versions(workspace_id, artifact_id)[0]

    regenerated = jobpilot.regenerate_artifact(workspace_id, artifact_id)
    versions = jobpilot.list_artifact_versions(workspace_id, artifact_id)
    current = jobpilot.get_artifact_version(workspace_id, artifact_id, regenerated["current_version_id"])

    assert len(versions) == 2
    assert regenerated["current_version_id"] != v1["id"]
    assert current["parent_version_id"] == v1["id"]
    assert loads(current["content_json"], {})["regenerated"] is True


def test_regenerate_failure_keeps_current_version(tmp_path):
    workspace_id, artifact_id = _build_package_artifact(tmp_path)
    before = jobpilot.list_artifacts(workspace_id)[-1]["current_version_id"]

    with pytest.raises(ValueError):
        jobpilot.regenerate_artifact(workspace_id, artifact_id, fail_for_test=True)

    after = jobpilot.list_artifacts(workspace_id)[-1]["current_version_id"]
    versions = jobpilot.list_artifact_versions(workspace_id, artifact_id)
    assert after == before
    assert len(versions) == 1
