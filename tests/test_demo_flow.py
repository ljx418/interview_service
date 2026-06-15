from pathlib import Path

from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[1]


def test_demo_flow_runs_end_to_end(tmp_path):
    workspace = init_workspace("demo", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]

    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")

    facts = jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    assert len(facts["facts"]) >= 5
    assert facts["missing_info"]

    project = jobpilot.create_project_card(workspace_id, "TodoPlus", [readme["document_id"]], "Junior Frontend Developer")
    assert project["project_id"]
    assert "React" in project["tech_stack"]

    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")
    job = jobpilot.parse_jd(workspace_id, jd_text)
    assert job["job_id"]

    match = jobpilot.match_profile(workspace_id, job["job_id"])
    assert match["fit_label"] in {"比较适合", "可以尝试", "先补强再投"}
    assert match["next_actions"]

    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    assert "待确认" in package["resume_markdown"]
    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    assert Path(exported["exports"][0]["path"]).exists()

    prep = jobpilot.prepare_interview(workspace_id, job["job_id"], package["package_id"])
    assert prep["questions"]
    assert prep["story_cards"]

    session = jobpilot.start_realtime_session(workspace_id, job["job_id"])
    detected = jobpilot.detect_question(session["session_id"], "讲一个你解决技术难题的经历。")
    assert detected["question_detected"]
    hint = jobpilot.generate_hint(session["session_id"], detected["question_text"])
    assert hint["hint"]["structure"]

    transcript = (ROOT / "examples/transcripts/project_deep_dive.txt").read_text(encoding="utf-8")
    review = jobpilot.review_interview(workspace_id, session["session_id"], transcript)
    assert review["training_tasks"]

