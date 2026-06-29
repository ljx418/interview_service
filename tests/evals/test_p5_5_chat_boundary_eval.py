from services.chat.core import KeywordChatCore
from services.profile import refresh_candidate_profile
from services.tools import jobpilot
from tests.evals.p5_5_helpers import build_p5_5_workspace


def test_p5_5_free_chat_does_not_write_candidate_profile_artifact(tmp_path):
    scenario = build_p5_5_workspace(tmp_path)
    workspace_id = scenario["workspace_id"]
    refresh_candidate_profile(workspace_id, scenario["job"]["job_id"], "Junior Frontend Developer")
    before = [item["artifact_type"] for item in jobpilot.list_artifacts(workspace_id)]

    session = jobpilot.create_chat_session(workspace_id, "P5.5 chat boundary")
    result = KeywordChatCore().handle_message(workspace_id, session["session_id"], "我适合这个岗位吗？还缺什么证据？")
    after = [item["artifact_type"] for item in jobpilot.list_artifacts(workspace_id)]

    assert result["artifacts"] == []
    assert after.count("candidate_profile") == before.count("candidate_profile")
