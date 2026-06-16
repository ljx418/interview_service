from pathlib import Path

from services.chat.core import KeywordChatCore
from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def test_chatbox_response_loop_handles_missing_prerequisites_and_artifacts(tmp_path):
    workspace = init_workspace("p3-chatbox-response", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    session = jobpilot.create_chat_session(workspace_id, "P3 response eval")
    session_id = session["session_id"]
    core = KeywordChatCore()

    missing_package = core.handle_message(workspace_id, session_id, "生成申请包")
    assert "请先粘贴一个 JD" in missing_package["message"]
    assert missing_package["artifacts"] == []

    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")
    parsed = core.handle_message(workspace_id, session_id, jd_text)
    assert "解析岗位" in parsed["message"]
    assert [artifact["type"] for artifact in parsed["artifacts"]] == ["job", "match_report"]

    package = core.handle_message(workspace_id, session_id, "生成申请包")
    assert "申请包已生成" in package["message"]
    assert package["artifacts"][0]["type"] == "application_package"
    assert package["artifacts"][0]["data"]["questions_to_confirm"]

    prep = core.handle_message(workspace_id, session_id, "准备面试")
    assert "面试准备包" in prep["message"]
    assert prep["artifacts"][0]["type"] == "interview_prep"

    recovered = jobpilot.get_chat_session(workspace_id, session_id)
    assistant_messages = [row["content"] for row in recovered["messages"] if row["role"] == "assistant"]
    assert any("请先粘贴一个 JD" in message for message in assistant_messages)
    assert any("申请包已生成" in message for message in assistant_messages)


def test_chatbox_response_loop_empty_input_is_visible(tmp_path):
    workspace = init_workspace("p3-chatbox-empty-input", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    session = jobpilot.create_chat_session(workspace_id, "P3 empty input eval")
    core = KeywordChatCore()

    result = core.handle_message(workspace_id, session["session_id"], "   ")
    assert "请输入 JD" in result["message"]
    assert result["artifacts"] == []

    recovered = jobpilot.get_chat_session(workspace_id, session["session_id"])
    assert recovered["messages"][-1]["role"] == "assistant"
    assert "请输入 JD" in recovered["messages"][-1]["content"]
