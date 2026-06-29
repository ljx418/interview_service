from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.workspace import init_workspace, workspace_conn


def _count_provider_invocations(workspace_id: str) -> int:
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute("SELECT COUNT(*) AS count FROM provider_invocation WHERE workspace_id=?", (workspace_id,)).fetchone()
    return int(row["count"])


def test_provider_preferences_do_not_count_as_external_call(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "mock")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "test-key-never-called")
    monkeypatch.setenv("JOBPILOT_OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("JOBPILOT_OPENAI_MODEL", "test-model")
    workspace = init_workspace("p6-opt-in", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    client = TestClient(app)

    preference = client.post(
        "/api/provider/preferences",
        json={
            "provider": "openai_compatible",
            "preset": "deepseek",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "mode": "provider_opt_in",
        },
    )

    assert preference.status_code == 200
    data = preference.json()["data"]
    assert data["provider"] == "openai_compatible"
    assert data["configured"] is True
    assert data["configured_is_called"] is False
    assert data["called_in_workspace"] is False
    assert data["consented"] is False
    assert _count_provider_invocations(workspace_id) == 0


def test_provider_consent_requires_explicit_confirmation_and_does_not_call(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "test-key-never-called")
    monkeypatch.setenv("JOBPILOT_OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("JOBPILOT_OPENAI_MODEL", "test-model")
    workspace = init_workspace("p6-consent", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    client = TestClient(app)
    session = client.post("/api/chat/sessions", json={"workspace_id": workspace_id, "title": "P6 consent"}).json()["data"]
    session_id = session["session_id"]

    denied = client.post(
        "/api/provider/consent",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "scope": "chat_session",
            "allowed_data_classes": ["recent_messages", "workspace_summary"],
            "confirm_external_call": False,
        },
    )
    assert denied.status_code == 200
    denied_data = denied.json()["data"]
    assert denied_data["consent_required"] is True
    assert denied_data["consented"] is False

    granted = client.post(
        "/api/provider/consent",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "scope": "chat_session",
            "ttl_seconds": 120,
            "allowed_data_classes": ["recent_messages", "workspace_summary"],
            "confirm_external_call": True,
        },
    )
    assert granted.status_code == 200
    granted_data = granted.json()["data"]
    assert granted_data["p6_state"] == "consented"
    assert granted_data["consented"] is True
    assert granted_data["configured_is_called"] is False
    assert granted_data["called_in_session"] is False
    assert granted_data["consent"]["allowed_data_classes"] == ["recent_messages", "workspace_summary"]
    assert _count_provider_invocations(workspace_id) == 0

    status = client.get(f"/api/provider/status?workspace_id={workspace_id}&session_id={session_id}")
    assert status.status_code == 200
    status_data = status.json()["data"]
    assert status_data["p6_state"] == "consented"
    assert status_data["called_in_session"] is False
