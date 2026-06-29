from services.profile import refresh_candidate_profile
from services.storage.workspace import workspace_conn
from tests.evals.p5_5_helpers import build_p5_5_workspace


def test_p5_5_capability_matrix_explains_evidence_levels(tmp_path):
    scenario = build_p5_5_workspace(tmp_path)
    conn, _ = workspace_conn(scenario["workspace_id"])
    conn.execute("UPDATE skill_evidence SET user_verified=1, confidence=0.86 WHERE skill_name='React'")
    conn.commit()

    profile = refresh_candidate_profile(scenario["workspace_id"], scenario["job"]["job_id"], "Junior Frontend Developer")
    matrix = {item["skill"]: item for item in profile["capability_matrix"]}

    assert matrix["React"]["evidence_level"] == "strong"
    assert matrix["TypeScript"]["evidence_level"] in {"usable", "weak"}
    assert matrix["Python"]["evidence_level"] in {"usable", "weak"}
    assert matrix["Testing"]["evidence_level"] == "missing"
    assert matrix["React"]["source_refs"]
    assert matrix["Testing"]["questions_to_confirm"]
    serialized = str(profile["capability_matrix"])
    assert "人格" not in serialized
    assert "年龄" not in serialized
    assert "政治" not in serialized
