from pathlib import Path

from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def test_application_package_does_not_invent_credentials_or_metrics(tmp_path):
    workspace = init_workspace("factuality-eval", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]

    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]])
    jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]])
    jd = jobpilot.parse_jd(workspace_id, (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8"))

    package = jobpilot.create_application_package(workspace_id, jd["job_id"])
    content = package["resume_markdown"]
    confirmation_text = "\n".join(item["question"] for item in package["questions_to_confirm"])

    assert "AWS Certified" not in content
    assert "100万" not in content
    assert "可量化结果" in confirmation_text
    assert package["source_refs"]
