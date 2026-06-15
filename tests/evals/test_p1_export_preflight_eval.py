from pathlib import Path
import zipfile

import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.db import dumps, loads
from services.storage.workspace import init_workspace, workspace_conn
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _build_package(tmp_path):
    workspace = init_workspace("p1-export", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    job = jobpilot.parse_jd(workspace_id, (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8"))
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    return workspace_id, package


def test_export_writes_markdown_and_formal_docx_with_warning_notes(tmp_path):
    workspace_id, package = _build_package(tmp_path)

    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown", "docx"])

    markdown_path = Path(next(item["path"] for item in exported["exports"] if item["format"] == "markdown"))
    docx_path = Path(next(item["path"] for item in exported["exports"] if item["format"] == "docx"))
    assert markdown_path.exists()
    assert docx_path.exists()
    assert "导出前仍需注意" in markdown_path.read_text(encoding="utf-8")
    with zipfile.ZipFile(docx_path) as docx:
        names = set(docx.namelist())
        assert "[Content_Types].xml" in names
        assert "word/document.xml" in names
        document_xml = docx.read("word/document.xml").decode("utf-8")
        assert "导出前仍需注意" in document_xml


def test_export_uses_current_artifact_version(tmp_path):
    workspace_id, package = _build_package(tmp_path)
    artifact_id = package["artifact_ref"]["artifact_id"]
    edited = dict(package)
    edited["resume_markdown"] = "# Current Version Resume\n\n这是当前版本。"
    edited.pop("artifact_ref", None)
    edited.pop("source_fact_refs", None)
    jobpilot.update_artifact(workspace_id, artifact_id, edited)

    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])

    markdown_path = Path(exported["exports"][0]["path"])
    assert "Current Version Resume" in markdown_path.read_text(encoding="utf-8")


def test_blocking_confirmation_prevents_export(tmp_path):
    workspace_id, package = _build_package(tmp_path)
    artifact_id = package["artifact_ref"]["artifact_id"]
    conn, _ = workspace_conn(workspace_id)
    artifact = conn.execute("SELECT * FROM artifact WHERE id=?", (artifact_id,)).fetchone()
    blocking = [
        {
            "question": "必须确认本人贡献范围。",
            "confirmation_level": "blocking",
            "reason": "阻塞导出",
            "source_refs": [],
        }
    ]
    conn.execute("UPDATE artifact SET questions_to_confirm=? WHERE id=?", (dumps(blocking), artifact_id))
    conn.execute("UPDATE artifact_version SET questions_to_confirm=? WHERE id=?", (dumps(blocking), artifact["current_version_id"]))
    conn.commit()

    with pytest.raises(ValueError, match="EXPORT_PRECHECK_FAILED"):
        jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])

    client = TestClient(app)
    response = client.post(
        "/api/application/export-package",
        json={"workspace_id": workspace_id, "package_id": package["package_id"], "formats": ["markdown"]},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "EXPORT_PRECHECK_FAILED"


def test_download_still_rejects_non_exports_paths(tmp_path):
    workspace_id, package = _build_package(tmp_path)
    jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    client = TestClient(app)

    outside = client.get("/api/application/download", params={"workspace_id": workspace_id, "path": "files/todoplus_README.md"})

    assert outside.status_code == 400
