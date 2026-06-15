from pathlib import Path

import pytest

from services.llm.provider import ProviderError
from services.storage.db import loads, row_to_dict
from services.storage.workspace import init_workspace, workspace_conn
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _build_fixture_workspace(tmp_path):
    workspace = init_workspace("p1-provider-tools", str(tmp_path / "workspace"), llm_provider="fixture")
    workspace_id = workspace["workspace_id"]
    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    facts = jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    project = jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    return workspace_id, facts, project


def test_fixture_provider_parse_jd_writes_job_artifact_and_provider_log(tmp_path):
    workspace_id, _, _ = _build_fixture_workspace(tmp_path)
    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")

    job = jobpilot.parse_jd(workspace_id, jd_text)

    assert job["job_id"]
    assert job["source_refs"]
    assert job["questions_to_confirm"]
    assert job["artifact_ref"]["artifact_type"] == "job_parse"

    conn, _ = workspace_conn(workspace_id)
    stored_job = row_to_dict(conn.execute("SELECT * FROM job WHERE workspace_id=? AND id=?", (workspace_id, job["job_id"])).fetchone())
    assert stored_job is not None
    artifact = row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND source_id=?", (workspace_id, job["job_id"])).fetchone())
    assert artifact is not None
    provider_log = row_to_dict(conn.execute("SELECT * FROM provider_invocation WHERE workspace_id=? AND prompt_name='job_parse_jd'", (workspace_id,)).fetchone())
    assert provider_log is not None
    assert provider_log["status"] == "success"


def test_fixture_provider_application_package_preserves_refs_and_confirmations(tmp_path):
    workspace_id, _, _ = _build_fixture_workspace(tmp_path)
    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")
    job = jobpilot.parse_jd(workspace_id, jd_text)

    package = jobpilot.create_application_package(workspace_id, job["job_id"])

    assert package["package_id"]
    assert package["resume_markdown"]
    assert package["source_refs"]
    assert package["questions_to_confirm"]
    assert package["artifact_ref"]["artifact_type"] == "application_package"

    conn, _ = workspace_conn(workspace_id)
    stored_package = row_to_dict(conn.execute("SELECT * FROM application_package WHERE workspace_id=? AND id=?", (workspace_id, package["package_id"])).fetchone())
    assert stored_package is not None
    assert loads(stored_package["questions_to_confirm"], [])
    provider_logs = conn.execute(
        "SELECT COUNT(*) AS count FROM provider_invocation WHERE workspace_id=? AND prompt_name='application_create_package'",
        (workspace_id,),
    ).fetchone()
    assert provider_logs["count"] == 1


def test_provider_backed_match_and_interview_prepare_have_valid_outputs(tmp_path):
    workspace_id, _, _ = _build_fixture_workspace(tmp_path)
    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")
    job = jobpilot.parse_jd(workspace_id, jd_text)

    match = jobpilot.match_profile(workspace_id, job["job_id"])
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    prep = jobpilot.prepare_interview(workspace_id, job["job_id"], package["package_id"])

    assert match["source_refs"]
    assert match["questions_to_confirm"]
    assert prep["questions"]
    assert prep["source_refs"]
    assert prep["artifact_ref"]["artifact_type"] == "interview_prep"


def test_provider_validation_failure_does_not_write_job(tmp_path, monkeypatch):
    workspace = init_workspace("p1-provider-failure", str(tmp_path / "workspace"), llm_provider="fixture")
    workspace_id = workspace["workspace_id"]

    class BadProvider:
        def generate_structured(self, *args, **kwargs):
            raise ProviderError("VALIDATION_FAILED", "bad provider output")

    monkeypatch.setattr(jobpilot, "get_provider", lambda provider_name: BadProvider())

    with pytest.raises(ProviderError):
        jobpilot.parse_jd(workspace_id, "Title: Junior Frontend Developer\nRequirements: React")

    conn, _ = workspace_conn(workspace_id)
    count = conn.execute("SELECT COUNT(*) AS count FROM job WHERE workspace_id=?", (workspace_id,)).fetchone()["count"]
    assert count == 0
