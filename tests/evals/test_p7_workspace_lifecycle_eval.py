from pathlib import Path

from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.workspace import init_workspace


def test_workspace_lifecycle_endpoints_are_dry_run_safe(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "mock")
    workspace = init_workspace("p7-lifecycle", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    root = Path(workspace["root_path"])
    exports = root / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    export_file = exports / "sample.md"
    export_file.write_text("# sample", encoding="utf-8")
    client = TestClient(app)

    backup = client.post("/api/workspace/backup", json={"workspace_id": workspace_id})
    assert backup.status_code == 200
    backup_data = backup.json()["data"]
    assert backup_data["backup_type"] == "manifest_only"
    assert backup_data["contains_file_contents"] is False
    assert Path(backup_data["manifest_path"]).exists()

    cleanup = client.post("/api/workspace/cleanup/plan", json={"workspace_id": workspace_id, "rules": {"include_exports": True}})
    assert cleanup.status_code == 200
    cleanup_data = cleanup.json()["data"]
    assert cleanup_data["dry_run"] is True
    assert cleanup_data["confirmation_required"] is True
    assert export_file.exists()

    migration = client.post("/api/workspace/migrate/plan", json={"workspace_id": workspace_id, "target_version": "p7-beta"})
    assert migration.status_code == 200
    migration_data = migration.json()["data"]
    assert migration_data["dry_run"] is True
    assert migration_data["confirmation_required"] is True
    assert "未修改数据库或文件" in migration_data["rollback_notes"]


def test_diagnostics_report_is_metadata_only(monkeypatch, tmp_path):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "mock")
    workspace = init_workspace("p7-diagnostics", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    client = TestClient(app)

    response = client.post("/api/diagnostics/report", json={"workspace_id": workspace_id, "include_provider": True})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["redaction_status"] == "metadata_only"
    assert data["contains_api_key"] is False
    assert data["contains_full_profile"] is False
    assert data["contains_provider_raw_response"] is False
    assert data["provider"]["api_key_redacted"] is True
