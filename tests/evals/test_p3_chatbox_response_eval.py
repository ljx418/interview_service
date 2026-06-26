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


def test_chatbox_free_chat_keeps_multi_turn_context_without_forcing_tools(tmp_path):
    workspace = init_workspace("p3-chatbox-free-chat", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    session = jobpilot.create_chat_session(workspace_id, "P3 free chat eval")
    core = KeywordChatCore()

    first = core.handle_message(workspace_id, session["session_id"], "我现在还没准备好 JD，想先聊聊转前端岗位的方向。")
    assert "已收到你的补充" in first["message"]
    assert first["artifacts"] == []
    assert first["chat_mode"] == "free_local"
    assert jobpilot.list_artifacts(workspace_id) == []

    follow_up = core.handle_message(workspace_id, session["session_id"], "继续，我应该先补 React 还是项目经历？")
    assert "下一步" in follow_up["message"]
    assert follow_up["artifacts"] == []

    explicit_profile = core.handle_message(workspace_id, session["session_id"], "请整理资料，生成职业事实。")
    assert "职业事实" in explicit_profile["message"]
    assert explicit_profile["artifacts"][0]["type"] == "career_facts"

    recovered = jobpilot.get_chat_session(workspace_id, session["session_id"])
    contents = [row["content"] for row in recovered["messages"]]
    assert any("转前端岗位" in content for content in contents)
    assert any("职业事实" in content for content in contents)


def test_chatbox_does_not_generate_when_user_asks_to_explain_first(tmp_path):
    workspace = init_workspace("p4c-chatbox-explain-first", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    session = jobpilot.create_chat_session(workspace_id, "P4C explain first eval")
    session_id = session["session_id"]
    core = KeywordChatCore()

    result = core.handle_message(workspace_id, session_id, "申请包应该怎么写？先别生成，先解释一下结构。")

    assert result["chat_mode"] == "free_local"
    assert result["artifacts"] == []
    assert jobpilot.list_artifacts(workspace_id) == []


def test_chatbox_status_query_summarizes_current_workspace(tmp_path):
    workspace = init_workspace("p4c-chatbox-status-query", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    session = jobpilot.create_chat_session(workspace_id, "P4C status query eval")
    session_id = session["session_id"]
    core = KeywordChatCore()

    initial = core.handle_message(workspace_id, session_id, "当前进展如何？")
    assert "还没有生成求职产物" in initial["message"]

    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")
    core.handle_message(workspace_id, session_id, jd_text)
    status = core.handle_message(workspace_id, session_id, "现在有哪些产物？")

    assert "当前 workspace 里已有" in status["message"]
    assert "最近岗位" in status["message"]
    assert status["artifacts"] == []
