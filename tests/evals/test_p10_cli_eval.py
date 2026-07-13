from __future__ import annotations

import json
from pathlib import Path

from services.cli import main as cli


class FakeClient:
    def __init__(self, api_url: str, timeout: float = 10.0) -> None:
        self.api_url = api_url

    def get(self, path: str, query=None, *, timeout=None):
        if path == "/api/health":
            return {"ok": True, "service": "jobpilot-ai"}
        if path == "/api/workspace/status":
            return {"workspace_id": "ws_test", "root_path": (query or {}).get("root_path")}
        if path == "/api/provider/status":
            return {"provider": "mock", "configured": False, "consented": False, "called": False}
        if path == "/api/provider/runtime-config":
            return {"api_key_configured": False}
        if path == "/api/market/providers/status":
            return {"level": "Level 1", "external_call_enabled": False, "can_claim_real_market": False, "providers": []}
        if path == "/api/jobs":
            return [{"id": "job_1", "title": "Frontend Engineer", "location": "Shanghai", "source_url": "https://example.invalid/jd"}]
        if path == "/api/artifacts":
            return [{"id": "art_1", "artifact_type": "resume", "status": "draft", "current_version_id": "v1"}]
        if path == "/api/artifacts/art_1/versions":
            return [{"version_id": "v1"}]
        if path == "/api/artifacts/art_1/versions/v1":
            return {
                "artifact_type": "resume",
                "status": "draft",
                "content_json": {
                    "source_refs": [{"document_id": "doc_1"}],
                    "pending_confirmations": ["确认指标"],
                    "body": "hidden full text",
                },
            }
        raise AssertionError(path)

    def post(self, path: str, body, *, timeout=None):
        if path == "/api/workflows/p2-demo/run":
            return {
                "workspace_id": body["workspace_id"],
                "provider_mode": "workspace_default",
                "summary": "demo completed",
                "steps": [{"key": "facts", "status": "passed"}],
            }
        raise AssertionError(path)


def make_workspace(tmp_path: Path) -> Path:
    root = tmp_path / ".jobpilot_workspace"
    root.mkdir()
    (root / "jobpilot.db").write_text("", encoding="utf-8")
    return root


def test_p10_cli_help_is_available(capsys):
    code = cli.main(["--help"])
    out = capsys.readouterr().out
    assert code == 0
    assert "workspace" in out
    assert "reports" in out


def test_p10_cli_workspace_status_json_uses_local_api(monkeypatch, tmp_path, capsys):
    workspace = make_workspace(tmp_path)
    monkeypatch.setattr(cli, "ApiClient", FakeClient)
    code = cli.main(["--json", "workspace", "status", "--workspace", str(workspace)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["workspace_id"] == "ws_test"
    assert payload["provider_state"]["called"] is False
    assert payload["meta"]["redacted"] is True


def test_p10_cli_reports_open_no_browser_only_locates_report(tmp_path, monkeypatch, capsys):
    report_dir = tmp_path / "docs" / "reports"
    report_dir.mkdir(parents=True)
    report = report_dir / "P10_FAKE_REPORT.html"
    report.write_text("<html>ok</html>", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    code = cli.main(["--json", "reports", "open", "--no-browser"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["data"]["no_browser"] is True
    assert payload["data"]["opened"] is False
    assert payload["data"]["report_path"].endswith("P10_FAKE_REPORT.html")
    assert payload["meta"]["redacted"] is True


def test_p10_cli_safety_gate_blocks_report_generation(capsys):
    code = cli.main(["reports", "open", "generate-report"])
    err = capsys.readouterr().err
    assert code == 1 or code == 4
    assert "error_code" in err or "unrecognized arguments" in err


def test_p10_cli_service_unavailable_exit_code(tmp_path, capsys):
    workspace = make_workspace(tmp_path)
    code = cli.main(["--api-url", "http://127.0.0.1:9", "workspace", "status", "--workspace", str(workspace)])
    err = capsys.readouterr().err
    assert code == 2
    assert "SERVICE_UNAVAILABLE" in err


def test_p10_cli_workspace_resolution_env(monkeypatch, tmp_path, capsys):
    workspace = make_workspace(tmp_path)
    monkeypatch.setenv("JOBPILOT_WORKSPACE", str(workspace))
    monkeypatch.setattr(cli, "ApiClient", FakeClient)
    code = cli.main(["--json", "jobs", "list"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["data"]["jobs"][0]["job_id"] == "job_1"


def test_p10_cli_artifact_show_redacts_to_summary(monkeypatch, tmp_path, capsys):
    workspace = make_workspace(tmp_path)
    monkeypatch.setattr(cli, "ApiClient", FakeClient)
    code = cli.main(["--json", "artifacts", "show", "art_1", "--workspace", str(workspace)])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    artifact = payload["data"]["artifact"]
    assert artifact["source_refs"] == [{"document_id": "doc_1"}]
    assert artifact["pending_confirmations"] == ["确认指标"]
    assert "body" in artifact["content_keys"]
