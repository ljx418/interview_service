from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.db import loads, row_to_dict
from services.storage.workspace import init_workspace, workspace_conn
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _build_application_workspace(tmp_path):
    workspace = init_workspace("p0-maintenance", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    job = jobpilot.parse_jd(workspace_id, (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8"))
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    return workspace, package


def test_realtime_end_updates_session_in_non_default_workspace(tmp_path):
    workspace = init_workspace("non-default-realtime", str(tmp_path / "custom_workspace"))
    workspace_id = workspace["workspace_id"]
    session = jobpilot.start_realtime_session(workspace_id, mode="formal_assist")

    ended = jobpilot.end_realtime_session(session["session_id"])

    conn, _ = workspace_conn(workspace_id)
    stored = row_to_dict(conn.execute("SELECT * FROM realtime_session WHERE id=?", (session["session_id"],)).fetchone())
    assert ended["ended"] is True
    assert ended["workspace_id"] == workspace_id
    assert stored and stored["ended_at"]


def test_application_download_rejects_non_exports_paths(tmp_path):
    workspace, package = _build_application_workspace(tmp_path)
    workspace_id = workspace["workspace_id"]
    jobpilot.confirm_artifact(workspace_id, package["artifact_ref"]["artifact_id"])
    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    export_file = Path(exported["exports"][0]["path"]).name
    client = TestClient(app)

    ok = client.get("/api/application/download", params={"workspace_id": workspace_id, "path": f"exports/{export_file}"})
    assert ok.status_code == 200

    outside = client.get("/api/application/download", params={"workspace_id": workspace_id, "path": "files/todoplus_README.md"})
    assert outside.status_code == 400


def test_confirm_artifact_persists_status_for_ui_refresh(tmp_path):
    workspace, package = _build_application_workspace(tmp_path)
    workspace_id = workspace["workspace_id"]
    artifact_id = package["artifact_ref"]["artifact_id"]

    confirmed = jobpilot.confirm_artifact(workspace_id, artifact_id)

    assert confirmed["status"] == "confirmed"
    artifacts = jobpilot.list_artifacts(workspace_id)
    assert next(item for item in artifacts if item["id"] == artifact_id)["status"] == "confirmed"
    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    assert Path(exported["exports"][0]["path"]).exists()


def test_chat_session_api_recovers_messages_and_artifact_content_for_chatbox(tmp_path):
    workspace = init_workspace("chatbox-recovery", str(tmp_path / "chatbox_workspace"))
    workspace_id = workspace["workspace_id"]
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    project = jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    client = TestClient(app)

    created = client.post("/api/chat/sessions", json={"workspace_id": workspace_id, "title": "P0 recovery"}).json()["data"]
    conn, _ = workspace_conn(workspace_id)
    jobpilot.append_chat_message(conn, created["session_id"], "assistant", "项目卡已生成。", [project["artifact_ref"]])

    listed = client.get("/api/chat/sessions", params={"workspace_id": workspace_id})
    recovered = client.get(f"/api/chat/sessions/{created['session_id']}", params={"workspace_id": workspace_id})

    assert listed.status_code == 200
    assert listed.json()["data"][0]["id"] == created["session_id"]
    assert recovered.status_code == 200
    data = recovered.json()["data"]
    refs = loads(data["messages"][0]["artifact_refs"], [])
    assert refs[0]["artifact_id"] == project["artifact_ref"]["artifact_id"]
    stored_artifact = next(item for item in data["artifacts"] if item["id"] == refs[0]["artifact_id"])
    assert stored_artifact["artifact_type"] == "tech_project"
    assert loads(stored_artifact["content_json"], {})["project_id"] == project["project_id"]
