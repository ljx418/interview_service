from services.profile import refresh_candidate_profile
from tests.evals.p5_5_helpers import build_p5_5_workspace


def test_p5_5_job_gap_analysis_aligns_must_and_nice_requirements(tmp_path):
    scenario = build_p5_5_workspace(tmp_path)
    profile = refresh_candidate_profile(scenario["workspace_id"], scenario["job"]["job_id"], "Junior Frontend Developer")

    gaps = {item["requirement"]: item for item in profile["job_gaps"]}

    assert "React" in gaps
    assert "TypeScript" in gaps
    assert "Testing" in gaps
    assert gaps["Testing"]["gap_level"] == "missing"
    assert "补充" in gaps["Testing"]["next_action"]
    assert gaps["Testing"]["source_refs"]
    assert gaps["React"]["requirement_type"] == "must"
