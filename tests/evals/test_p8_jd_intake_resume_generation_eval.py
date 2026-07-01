from pathlib import Path

from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.db import loads
from services.storage.workspace import init_workspace, workspace_conn


ROOT = Path(__file__).resolve().parents[2]


def _workspace(tmp_path):
    workspace = init_workspace("p8-jd-intake", str(tmp_path / "workspace"))
    return workspace["workspace_id"]


def test_p8_material_upload_keeps_kind_and_legacy_compatibility(tmp_path):
    workspace_id = _workspace(tmp_path)
    client = TestClient(app)
    resume_path = ROOT / "examples/resumes/transition_frontend_resume.md"

    with resume_path.open("rb") as file_obj:
        response = client.post(
            "/api/files/upload",
            params={"workspace_id": workspace_id, "kind": "resume"},
            files={"file": ("transition_frontend_resume.md", file_obj, "text/markdown")},
        )

    assert response.status_code == 200
    document_id = response.json()["data"]["document_id"]
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute("SELECT kind FROM document WHERE workspace_id=? AND id=?", (workspace_id, document_id)).fetchone()
    assert row["kind"] == "resume"


def test_p8_job_intake_list_select_and_resume_generation(tmp_path):
    workspace_id = _workspace(tmp_path)
    client = TestClient(app)

    resume = ROOT / "examples/resumes/transition_frontend_resume.md"
    project = ROOT / "examples/projects/todoplus_README.md"
    client.post("/api/files/ingest-local", params={"workspace_id": workspace_id, "source_path": str(resume), "kind": "resume"}).raise_for_status()
    client.post("/api/files/ingest-local", params={"workspace_id": workspace_id, "source_path": str(project), "kind": "project"}).raise_for_status()
    client.post("/api/profile/extract-facts", json={"workspace_id": workspace_id, "target_roles": ["Junior Frontend Developer"]}).raise_for_status()
    client.post(
        "/api/project/create-card",
        json={"workspace_id": workspace_id, "project_name": "TodoPlus", "target_role": "Junior Frontend Developer"},
    ).raise_for_status()

    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")
    first = client.post(
        "/api/job/intake",
        json={
            "workspace_id": workspace_id,
            "jd_text": jd_text,
            "source_url": "https://example.invalid/boss/job/123",
            "platform": "BOSS 手动粘贴",
            "import_method": "manual_paste",
            "user_notes": "合成验收 JD，URL 仅归档。",
        },
    )
    assert first.status_code == 200
    data = first.json()["data"]
    assert data["job"]["source_refs"]
    assert data["job"]["platform"] == "BOSS 手动粘贴"
    assert data["message"].endswith("未触发网页抓取。")
    assert data["match"]["fit_label"] in {"比较适合", "可以尝试", "先补强再投"}

    second = client.post(
        "/api/job/intake",
        json={
            "workspace_id": workspace_id,
            "jd_text": "Title: Backend Developer\nCompany: Example Backend\nRequirements\nPython\nFastAPI\nSQL\nTesting",
            "source_url": "https://example.invalid/company/backend",
            "platform": "公司官网手动粘贴",
            "import_method": "manual_paste",
        },
    )
    second.raise_for_status()
    second_job_id = second.json()["data"]["job"]["job_id"]

    jobs = client.get("/api/jobs", params={"workspace_id": workspace_id})
    assert jobs.status_code == 200
    job_items = jobs.json()["data"]
    assert len(job_items) == 2
    assert job_items[0]["job_id"] == second_job_id
    assert job_items[0]["is_current_target"] is True
    assert job_items[0]["source_url"] == "https://example.invalid/company/backend"
    assert job_items[0]["match"]["fit_label"]

    first_job_id = data["job"]["job_id"]
    selected = client.post(f"/api/jobs/{first_job_id}/select", json={"workspace_id": workspace_id})
    assert selected.status_code == 200
    selected_jobs = selected.json()["data"]["jobs"]
    assert selected_jobs[0]["job_id"] == first_job_id
    assert selected_jobs[0]["is_current_target"] is True

    generated = client.post("/api/resume/generate", json={"workspace_id": workspace_id, "mode": "targeted"})
    assert generated.status_code == 200
    resume = generated.json()["data"]
    assert resume["job_id"] == first_job_id
    assert resume["resume_version_id"]
    assert "待确认" in resume["resume_markdown"]
    assert resume["source_refs"]
    assert resume["pending_confirmations"]
    assert resume["export_preflight"]["blocking_count"] >= 1

    conn, _ = workspace_conn(workspace_id)
    stored_job = conn.execute("SELECT platform, source_url, is_current_target FROM job WHERE workspace_id=? AND id=?", (workspace_id, first_job_id)).fetchone()
    assert stored_job["platform"] == "BOSS 手动粘贴"
    assert stored_job["source_url"] == "https://example.invalid/boss/job/123"
    assert stored_job["is_current_target"] == 1
    stored_resume = conn.execute("SELECT * FROM resume_version WHERE workspace_id=? AND id=?", (workspace_id, resume["resume_version_id"])).fetchone()
    assert loads(stored_resume["pending_confirmations"], [])


def test_p8_chatbox_resume_intent_uses_current_target_without_silent_overwrite(tmp_path):
    workspace_id = _workspace(tmp_path)
    client = TestClient(app)
    session = client.post("/api/chat/sessions", json={"workspace_id": workspace_id, "title": "P8 chat"}).json()["data"]

    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")
    client.post("/api/job/intake", json={"workspace_id": workspace_id, "jd_text": jd_text, "platform": "官网手动粘贴"}).raise_for_status()
    response = client.post(
        "/api/chat/message",
        json={"workspace_id": workspace_id, "session_id": session["session_id"], "message": "请基于当前目标 JD 生成定制简历草稿。"},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "定制简历" in payload["message"]
    assert payload["artifacts"][0]["type"] == "application_package"
    assert payload["artifacts"][0]["data"]["resume_version_id"]

    follow_up = client.post(
        "/api/chat/message",
        json={"workspace_id": workspace_id, "session_id": session["session_id"], "message": "我想先聊聊这个岗位的准备方向，不要生成。"},
    )
    assert follow_up.status_code == 200
    assert follow_up.json()["data"]["artifacts"] == []
