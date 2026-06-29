from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.workspace import init_workspace


def test_long_context_manager_returns_bounded_redacted_context(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "mock")
    workspace = init_workspace("p6-long-context", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    client = TestClient(app)
    session = client.post("/api/chat/sessions", json={"workspace_id": workspace_id, "title": "P6 long context"}).json()["data"]
    session_id = session["session_id"]

    for index in range(24):
        response = client.post(
            "/api/chat/message",
            json={
                "workspace_id": workspace_id,
                "session_id": session_id,
                "message": f"第 {index} 轮：我想继续讨论前端求职方向和项目表达，不要生成材料。",
            },
        )
        assert response.status_code == 200

    context = client.get(f"/api/chat/session/{session_id}/context?workspace_id={workspace_id}")

    assert context.status_code == 200
    data = context.json()["data"]
    assert data["total_message_count"] >= 48
    assert data["recent_count"] == 12
    assert data["rolling_summary"]["covered_message_count"] >= 36
    assert data["workspace_snapshot"]["artifact_count"] == 0
    assert data["privacy_boundary"]["contains_api_key"] is False
    assert data["privacy_boundary"]["raw_provider_response_included"] is False
    assert data["privacy_boundary"]["full_history_included"] is False
    joined_recent = "\n".join(item["content"] for item in data["recent_messages"])
    assert "sk-" not in joined_recent
