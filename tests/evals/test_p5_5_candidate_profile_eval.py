from fastapi.testclient import TestClient

from services.api.main import app
from services.profile import get_candidate_profile, refresh_candidate_profile
from services.storage.db import loads
from services.storage.workspace import workspace_conn
from tests.evals.p5_5_helpers import build_p5_5_workspace


def test_p5_5_candidate_profile_refresh_writes_profile_row_and_artifact(tmp_path):
    scenario = build_p5_5_workspace(tmp_path)
    workspace_id = scenario["workspace_id"]
    job_id = scenario["job"]["job_id"]

    refreshed = refresh_candidate_profile(workspace_id, job_id, "Junior Frontend Developer")

    assert refreshed["empty"] is False
    assert refreshed["profile_summary"]["target_roles"] == ["Junior Frontend Developer"]
    assert refreshed["source_refs"]
    assert refreshed["artifact_ref"]["artifact_type"] == "candidate_profile"
    assert refreshed["capability_matrix"]
    assert refreshed["project_credibility"]
    assert refreshed["job_gaps"]

    conn, _ = workspace_conn(workspace_id)
    profile = conn.execute("SELECT * FROM candidate_profile WHERE workspace_id=?", (workspace_id,)).fetchone()
    artifact = conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND artifact_type='candidate_profile'", (workspace_id,)).fetchone()
    version = conn.execute("SELECT * FROM artifact_version WHERE artifact_id=?", (artifact["id"],)).fetchone()

    assert profile is not None
    assert artifact is not None
    assert version is not None
    assert loads(version["source_refs"], [])
    assert loads(version["content_json"], {})["profile_summary"]["current_level"] == "junior_candidate"


def test_p5_5_candidate_profile_get_empty_and_full_states(tmp_path):
    empty = build_p5_5_workspace(tmp_path / "empty")
    workspace_id = empty["workspace_id"]
    assert get_candidate_profile(workspace_id)["empty"] is True

    refreshed = refresh_candidate_profile(workspace_id, empty["job"]["job_id"], "Junior Frontend Developer")
    fetched = get_candidate_profile(workspace_id, empty["job"]["job_id"])

    assert fetched["empty"] is False
    assert fetched["artifact_ref"]["artifact_id"] == refreshed["artifact_ref"]["artifact_id"]
    assert fetched["profile_summary"]["target_roles"] == ["Junior Frontend Developer"]


def test_p5_5_candidate_profile_api_contract(tmp_path):
    scenario = build_p5_5_workspace(tmp_path)
    client = TestClient(app)

    get_empty = client.get("/api/profile/candidate", params={"workspace_id": scenario["workspace_id"]})
    assert get_empty.status_code == 200
    assert get_empty.json()["data"]["empty"] is True

    refresh = client.post(
        "/api/profile/candidate/refresh",
        json={"workspace_id": scenario["workspace_id"], "job_id": scenario["job"]["job_id"], "target_role": "Junior Frontend Developer"},
    )
    assert refresh.status_code == 200
    assert refresh.json()["data"]["artifact_ref"]["artifact_type"] == "candidate_profile"

    get_full = client.get("/api/profile/candidate", params={"workspace_id": scenario["workspace_id"], "job_id": scenario["job"]["job_id"]})
    assert get_full.status_code == 200
    assert get_full.json()["data"]["empty"] is False
