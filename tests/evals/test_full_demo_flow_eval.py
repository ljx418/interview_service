from pathlib import Path

from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def test_full_realistic_demo_flow_reaches_all_p0_outputs(tmp_path):
    workspace = init_workspace("full-demo-eval", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]

    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    facts = jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    project = jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    job = jobpilot.parse_jd(workspace_id, (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8"))
    match = jobpilot.match_profile(workspace_id, job["job_id"])
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    jobpilot.confirm_artifact(workspace_id, package["artifact_ref"]["artifact_id"])
    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    prep = jobpilot.prepare_interview(workspace_id, job["job_id"], package["package_id"])
    session = jobpilot.start_realtime_session(workspace_id, job["job_id"])
    hint = jobpilot.generate_hint(session["session_id"], "讲一个你解决技术难题的经历。")
    review = jobpilot.review_interview(workspace_id, session["session_id"], (ROOT / "examples/transcripts/project_deep_dive.txt").read_text(encoding="utf-8"))
    artifacts = jobpilot.list_artifacts(workspace_id)

    assert facts["artifact_ref"]["artifact_id"]
    assert project["artifact_ref"]["artifact_id"]
    assert match["artifact_ref"]["artifact_id"]
    assert Path(exported["exports"][0]["path"]).exists()
    assert prep["story_cards"]
    assert hint["hint"]["source_refs"]
    assert len(review["training_tasks"]) >= 3
    assert {item["artifact_type"] for item in artifacts} >= {"career_facts", "tech_project", "job_parse", "match_report", "application_package", "interview_prep", "interview_review"}
