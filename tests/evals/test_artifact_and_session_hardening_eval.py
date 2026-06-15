from pathlib import Path

from services.storage.db import loads, rows_to_dicts
from services.storage.workspace import init_workspace, workspace_conn
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _build_workspace(tmp_path):
    workspace = init_workspace("artifact-hardening", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    project = jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    job = jobpilot.parse_jd(workspace_id, (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8"))
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    return workspace, project, package, exported


def test_artifact_rows_are_recoverable_and_export_stays_in_workspace(tmp_path):
    workspace, project, package, exported = _build_workspace(tmp_path)
    workspace_id = workspace["workspace_id"]
    conn, stored = workspace_conn(workspace_id)
    root = Path(stored["root_path"])

    artifacts = jobpilot.list_artifacts(workspace_id)
    assert artifacts

    application_artifact = next(item for item in artifacts if item["artifact_type"] == "application_package")
    content = loads(application_artifact["content_json"], {})
    assert content["package_id"] == package["package_id"]
    assert application_artifact["source_table"] == "application_package"
    assert application_artifact["source_id"] == package["package_id"]

    project_artifact = next(item for item in artifacts if item["source_id"] == project["project_id"])
    assert loads(project_artifact["questions_to_confirm"], [])
    assert loads(project_artifact["source_refs"], [])

    export_path = Path(exported["exports"][0]["path"])
    assert export_path.exists()
    assert root in export_path.resolve().parents
    assert export_path.parent.name == "exports"

    rows = rows_to_dicts(conn.execute("SELECT * FROM tool_invocation WHERE workspace_id=?", (workspace_id,)).fetchall())
    assert rows
    joined_summaries = "\n".join(row["input_summary"] or "" for row in rows)
    assert "Former operations specialist transitioning into frontend development" not in joined_summaries
    assert "TodoPlus is a small task management web app" not in joined_summaries


def test_chat_session_recovers_messages_and_artifact_refs(tmp_path):
    workspace, project, _, _ = _build_workspace(tmp_path)
    workspace_id = workspace["workspace_id"]
    conn, _ = workspace_conn(workspace_id)
    session = jobpilot.create_chat_session(workspace_id, "P0 maintenance session")
    artifact_ref = project["artifact_ref"]

    jobpilot.append_chat_message(conn, session["session_id"], "assistant", "项目卡已生成。", [artifact_ref])
    recovered = jobpilot.get_chat_session(workspace_id, session["session_id"])

    assert recovered["session"]["title"] == "P0 maintenance session"
    assert recovered["messages"][0]["role"] == "assistant"
    assert loads(recovered["messages"][0]["artifact_refs"], [])[0]["artifact_id"] == artifact_ref["artifact_id"]
    assert any(item["id"] == artifact_ref["artifact_id"] for item in recovered["artifacts"])
