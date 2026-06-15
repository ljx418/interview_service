from pathlib import Path

from services.storage.db import loads, row_to_dict
from services.storage.workspace import init_workspace, workspace_conn
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _build_package_artifact(tmp_path):
    workspace = init_workspace("p1-artifact-versioning", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    job = jobpilot.parse_jd(workspace_id, (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8"))
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    return workspace_id, package, package["artifact_ref"]["artifact_id"]


def test_new_artifact_has_current_version_and_v1(tmp_path):
    workspace_id, package, artifact_id = _build_package_artifact(tmp_path)
    conn, _ = workspace_conn(workspace_id)
    artifact = row_to_dict(conn.execute("SELECT * FROM artifact WHERE id=?", (artifact_id,)).fetchone())

    assert artifact["current_version_id"]
    versions = jobpilot.list_artifact_versions(workspace_id, artifact_id)
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1
    assert loads(versions[0]["content_json"], {})["package_id"] == package["package_id"]


def test_edit_creates_v2_and_restore_keeps_v1_readable(tmp_path):
    workspace_id, package, artifact_id = _build_package_artifact(tmp_path)
    original_versions = jobpilot.list_artifact_versions(workspace_id, artifact_id)
    v1 = original_versions[0]
    edited = dict(package)
    edited["resume_markdown"] = package["resume_markdown"] + "\n\n编辑后的版本。"
    edited.pop("artifact_ref", None)
    edited.pop("source_fact_refs", None)

    updated = jobpilot.update_artifact(workspace_id, artifact_id, edited)
    versions = jobpilot.list_artifact_versions(workspace_id, artifact_id)

    assert updated["current_version_id"] != v1["id"]
    assert len(versions) == 2
    assert versions[0]["id"] == v1["id"]
    assert versions[1]["parent_version_id"] == v1["id"]
    assert "编辑后的版本" in loads(versions[1]["content_json"], {})["resume_markdown"]

    restored = jobpilot.restore_artifact_version(workspace_id, artifact_id, v1["id"])
    assert restored["current_version_id"] == v1["id"]
