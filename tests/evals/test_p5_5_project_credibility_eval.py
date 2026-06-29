from services.profile import refresh_candidate_profile
from tests.evals.p5_5_helpers import build_p5_5_workspace


def test_p5_5_project_credibility_keeps_unconfirmed_contribution_visible(tmp_path):
    scenario = build_p5_5_workspace(tmp_path)
    profile = refresh_candidate_profile(scenario["workspace_id"], scenario["job"]["job_id"], "Junior Frontend Developer")
    credibility = profile["project_credibility"][0]

    assert credibility["credibility_label"] in {"plausible", "needs_evidence", "risky"}
    assert credibility["credibility_label"] != "verified"
    assert credibility["source_refs"]
    assert credibility["questions_to_confirm"]
    assert any("贡献" in item["question"] or "负责" in item["question"] for item in credibility["questions_to_confirm"])
    assert "缺少可验证链接或材料" in credibility["evidence_gaps"]
