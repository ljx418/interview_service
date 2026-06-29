from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.db import loads, row_to_dict
from services.storage.workspace import init_workspace, workspace_conn


def _client_workspace(tmp_path):
    workspace = init_workspace("p6-provider-chat", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    client = TestClient(app)
    session = client.post("/api/chat/sessions", json={"workspace_id": workspace_id, "title": "P6 provider chat"}).json()["data"]
    return client, workspace_id, session["session_id"]


def _grant_consent(client, workspace_id, session_id):
    response = client.post(
        "/api/provider/consent",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "scope": "chat_session",
            "ttl_seconds": 120,
            "allowed_data_classes": ["recent_messages", "rolling_summary", "workspace_summary", "artifact_summary"],
            "confirm_external_call": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["consented"] is True


def _latest_chat_invocation(workspace_id):
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute("SELECT * FROM provider_chat_invocation WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
    return row_to_dict(row)


def test_provider_backed_fake_chat_requires_consent(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "fake-local-key-never-exposed")
    monkeypatch.setenv("JOBPILOT_OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("JOBPILOT_OPENAI_MODEL", "deepseek-chat")
    monkeypatch.setenv("JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT", "1")
    monkeypatch.delenv("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", raising=False)
    client, workspace_id, session_id = _client_workspace(tmp_path)

    denied = client.post(
        "/api/chat/message",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "message": "我想先聊聊转前端的求职方向，不要生成材料。",
            "provider_mode": "provider_opt_in",
        },
    )

    assert denied.status_code == 200
    denied_data = denied.json()["data"]
    assert denied_data["provider_invocation_status"] == "consent_required"
    assert denied_data["fallback_used"] is True
    assert denied_data["chat_mode"] == "free_local"
    assert "不会自动外呼真实 provider" in denied_data["message"]
    row = _latest_chat_invocation(workspace_id)
    assert row["status"] == "policy_denied"
    assert row["error_code"] == "CONSENT_REQUIRED"


def test_provider_backed_fake_chat_writes_redacted_invocation_log(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "fake-local-key-never-exposed")
    monkeypatch.setenv("JOBPILOT_OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("JOBPILOT_OPENAI_MODEL", "deepseek-chat")
    monkeypatch.setenv("JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT", "1")
    monkeypatch.delenv("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", raising=False)
    client, workspace_id, session_id = _client_workspace(tmp_path)
    _grant_consent(client, workspace_id, session_id)

    response = client.post(
        "/api/chat/message",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "message": "继续聊聊我的前端求职定位，不要生成材料。候选邮箱 candidate@example.com",
            "provider_mode": "provider_opt_in",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["chat_mode"] == "provider_fake"
    assert data["provider_invocation_status"] == "called"
    assert data["fallback_used"] is False
    assert data["artifacts"] == []
    assert "Fake provider" in data["message"]
    assert data["context_summary"]["privacy_boundary"]["contains_api_key"] is False
    row = _latest_chat_invocation(workspace_id)
    assert row["status"] == "called"
    assert row["fallback_used"] == 0
    summary = row["input_summary"]
    assert "fake-local-key-never-exposed" not in summary
    assert "candidate@example.com" not in summary
    redaction = loads(row["redaction_summary"], {})
    assert redaction["metadata_only"] is True

    status = client.get(f"/api/provider/status?workspace_id={workspace_id}&session_id={session_id}")
    assert status.json()["data"]["p6_state"] == "called"
    assert status.json()["data"]["called_in_session"] is True


def test_provider_backed_fake_failure_falls_back_to_local_chat(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "fake-local-key-never-exposed")
    monkeypatch.setenv("JOBPILOT_OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("JOBPILOT_OPENAI_MODEL", "deepseek-chat")
    monkeypatch.setenv("JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT", "1")
    monkeypatch.setenv("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", "timeout")
    client, workspace_id, session_id = _client_workspace(tmp_path)
    _grant_consent(client, workspace_id, session_id)

    response = client.post(
        "/api/chat/message",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "message": "继续帮我判断下一步学习 React 还是补项目。",
            "provider_mode": "provider_opt_in",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["provider_invocation_status"] == "failed"
    assert data["provider_error_code"] == "LLM_TIMEOUT"
    assert data["fallback_used"] is True
    assert data["chat_mode"] == "free_local"
    row = _latest_chat_invocation(workspace_id)
    assert row["status"] == "failed"
    assert row["error_code"] == "LLM_TIMEOUT"
    assert row["fallback_used"] == 1


def test_provider_mode_does_not_bypass_tool_intent_or_write_free_chat_artifact(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "fake-local-key-never-exposed")
    monkeypatch.setenv("JOBPILOT_OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("JOBPILOT_OPENAI_MODEL", "deepseek-chat")
    monkeypatch.setenv("JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT", "1")
    monkeypatch.delenv("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", raising=False)
    client, workspace_id, session_id = _client_workspace(tmp_path)
    _grant_consent(client, workspace_id, session_id)

    free = client.post(
        "/api/chat/message",
        json={"workspace_id": workspace_id, "session_id": session_id, "message": "先聊方向，不要生成任何材料。", "provider_mode": "provider_opt_in"},
    )
    assert free.status_code == 200
    assert free.json()["data"]["artifacts"] == []

    jd = client.post(
        "/api/chat/message",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "message": "帮我解析这个 JD：Responsibilities include React UI, TypeScript, testing. Requirements include collaboration.",
            "provider_mode": "provider_opt_in",
        },
    )
    assert jd.status_code == 200
    jd_data = jd.json()["data"]
    assert jd_data["provider_invocation_status"] == "skipped_tool_intent"
    assert len(jd_data["artifacts"]) >= 1


def test_provider_backed_fake_chat_supports_20_turn_bounded_context(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "fake-local-key-never-exposed")
    monkeypatch.setenv("JOBPILOT_OPENAI_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("JOBPILOT_OPENAI_MODEL", "deepseek-chat")
    monkeypatch.setenv("JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT", "1")
    monkeypatch.delenv("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", raising=False)
    client, workspace_id, session_id = _client_workspace(tmp_path)
    _grant_consent(client, workspace_id, session_id)

    for index in range(20):
        response = client.post(
            "/api/chat/message",
            json={
                "workspace_id": workspace_id,
                "session_id": session_id,
                "message": f"第 {index} 轮继续聊前端求职定位，不要生成材料。",
                "provider_mode": "provider_opt_in",
            },
        )
        assert response.status_code == 200
        assert response.json()["data"]["provider_invocation_status"] == "called"

    context = client.get(f"/api/chat/session/{session_id}/context?workspace_id={workspace_id}")
    assert context.status_code == 200
    data = context.json()["data"]
    assert data["total_message_count"] >= 40
    assert data["recent_count"] == 12
    assert data["rolling_summary"]["covered_message_count"] >= 28

    conn, _ = workspace_conn(workspace_id)
    row = conn.execute("SELECT COUNT(*) AS count FROM provider_chat_invocation WHERE workspace_id=? AND status='called'", (workspace_id,)).fetchone()
    assert row["count"] == 20
