from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from services.api.main import app
from services.cli import main as cli


client = TestClient(app)


def init_workspace(tmp_path: Path) -> str:
    root = tmp_path / ".jobpilot_workspace"
    response = client.post(
        "/api/workspace/init",
        json={"name": "p11-eval", "root_path": str(root), "llm_provider": "mock", "privacy_mode": "local_first"},
    )
    assert response.status_code == 200
    return response.json()["data"]["workspace_id"]


def test_p11_market_provider_status_is_redacted_and_level1(tmp_path):
    workspace_id = init_workspace(tmp_path)
    response = client.get("/api/market/providers/status", params={"workspace_id": workspace_id})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["level"] == "Level 1"
    assert payload["can_claim_real_market"] is False
    assert payload["external_call_enabled"] is False
    assert all("api_key" not in json.dumps(provider).lower() or provider.get("api_key_redacted") for provider in payload["providers"])
    assert {provider["provider_id"] for provider in payload["providers"]} >= {"fixture_local", "manual_paste", "adzuna_opt_in"}


def test_p11_fixture_provider_check_writes_redacted_invocation(tmp_path):
    workspace_id = init_workspace(tmp_path)
    response = client.post(
        "/api/market/providers/check",
        json={"workspace_id": workspace_id, "provider_id": "fixture_local", "confirm": False},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["checked"] is True
    assert payload["called"] is False
    assert payload["raw_provider_response_included"] is False
    status = client.get("/api/market/providers/status", params={"workspace_id": workspace_id}).json()["data"]
    assert status["recent_invocations"][0]["provider_id"] == "fixture_local"


def test_p11_opt_in_provider_without_consent_or_policy_is_not_called(tmp_path, monkeypatch):
    workspace_id = init_workspace(tmp_path)
    monkeypatch.setenv("JOBPILOT_ADZUNA_APP_ID", "fake-id-for-test")
    monkeypatch.setenv("JOBPILOT_ADZUNA_APP_KEY", "fake-key-for-test")
    response = client.post(
        "/api/market/providers/check",
        json={"workspace_id": workspace_id, "provider_id": "adzuna_opt_in", "confirm": False},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["checked"] is False
    assert payload["called"] is False
    assert payload["error_code"] == "CONSENT_REQUIRED"
    assert payload["raw_provider_response_included"] is False


def test_p11_search_run_snapshot_and_source_refs_are_traceable(tmp_path):
    workspace_id = init_workspace(tmp_path)
    response = client.post(
        "/api/market/search-runs",
        json={
            "workspace_id": workspace_id,
            "query": "北京 上海 LLM 前端岗位薪资",
            "city_filters": ["北京", "上海"],
            "salary_range": "20-40k",
            "tech_stack": ["React", "TypeScript", "LLM"],
            "provider_ids": ["fixture_local"],
            "source_policy": "fixture",
        },
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["status"] == "fallback"
    assert payload["raw_provider_response_included"] is False
    assert payload["result_count"] >= 1
    assert payload["source_refs"]
    assert "Level 1" in payload["boundary_note"]
    run_id = payload["run_id"]

    run = client.get(f"/api/market/search-runs/{run_id}", params={"workspace_id": workspace_id}).json()["data"]
    assert run["status"] == "fallback"
    assert run["error_code"] == "FALLBACK_ONLY"

    snapshot = client.get(f"/api/market/snapshots/{run_id}", params={"workspace_id": workspace_id}).json()["data"]
    assert snapshot["source_breakdown"]["fixture"] == payload["result_count"]
    assert snapshot["city_stats"]
    assert snapshot["low_confidence_notes"]
    assert snapshot["raw_provider_response_included"] is False

    source_ref = client.get(f"/api/market/source-refs/{payload['source_refs'][0]}", params={"workspace_id": workspace_id}).json()["data"]
    assert source_ref["confidence"] < 1
    assert source_ref["raw_provider_response_included"] is False
    assert source_ref["api_key_redacted"] is True


def test_p11_opt_in_search_rejects_without_consent(tmp_path):
    workspace_id = init_workspace(tmp_path)
    response = client.post(
        "/api/market/search-runs",
        json={
            "workspace_id": workspace_id,
            "query": "真实市场 provider 查询",
            "provider_ids": ["adzuna_opt_in"],
            "source_policy": "opt_in_api",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "CONSENT_REQUIRED"


def test_p11_frontend_and_cli_have_market_provider_hooks():
    frontend = Path("apps/chatbox/src/main.tsx").read_text(encoding="utf-8")
    cli_source = Path("services/cli/main.py").read_text(encoding="utf-8")
    assert "/api/market/providers/status" in frontend
    assert "/api/market/search-runs" in frontend
    assert "MarketProviderState" in frontend
    assert "marketProviderStatus" in frontend
    assert "/api/market/providers/status" in cli_source
    assert "market_can_claim_real_market" in cli_source


def test_p11_cli_workspace_status_reports_market_state(monkeypatch, tmp_path, capsys):
    workspace_root = tmp_path / ".jobpilot_workspace"
    workspace_root.mkdir()
    (workspace_root / "jobpilot.db").write_text("", encoding="utf-8")

    class FakeClient:
        def __init__(self, api_url: str, timeout: float = 10.0) -> None:
            self.api_url = api_url

        def get(self, path: str, query=None, *, timeout=None):
            if path == "/api/health":
                return {"ok": True}
            if path == "/api/workspace/status":
                return {"workspace_id": "ws_p11", "root_path": str(workspace_root)}
            if path == "/api/provider/status":
                return {"provider": "mock", "configured": False, "consented": False, "called": False}
            if path == "/api/provider/runtime-config":
                return {"api_key_configured": False}
            if path == "/api/market/providers/status":
                return {"level": "Level 1", "external_call_enabled": False, "can_claim_real_market": False, "providers": []}
            raise AssertionError(path)

    monkeypatch.setattr(cli, "ApiClient", FakeClient)
    code = cli.main(["--json", "workspace", "status", "--workspace", str(workspace_root)])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["provider_state"]["market_level"] == "Level 1"
    assert payload["provider_state"]["market_can_claim_real_market"] is False
    assert payload["data"]["market_provider_state"]["level"] == "Level 1"
