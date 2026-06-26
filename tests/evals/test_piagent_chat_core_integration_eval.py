from pathlib import Path
import subprocess
import sys
import types

import pytest

from services.chat.core import KeywordChatCore
from services.chat.piagent_adapter import PiAgentChatCore, PiAgentUnavailableError
from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _workspace_with_profile(tmp_path):
    workspace = init_workspace("piagent-chat-core", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume = jobpilot.save_document(workspace_id, str(ROOT / "examples/resumes/transition_frontend_resume.md"), "resume")
    readme = jobpilot.save_document(workspace_id, str(ROOT / "examples/projects/todoplus_README.md"), "project")
    jobpilot.extract_facts(workspace_id, [resume["document_id"], readme["document_id"]], ["Junior Frontend Developer"])
    return workspace_id


def test_keyword_chat_core_keeps_p0_jd_flow(tmp_path):
    workspace_id = _workspace_with_profile(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "keyword-core")
    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")

    result = KeywordChatCore().handle_message(workspace_id, session["session_id"], "JD\n" + jd_text)

    assert result["message"] == "我已解析岗位并生成适合度分析。"
    assert [artifact["type"] for artifact in result["artifacts"]] == ["job", "match_report"]
    assert result["artifacts"][1]["data"]["artifact_ref"]["artifact_type"] == "match_report"


def test_piagent_adapter_falls_back_when_source_is_not_migrated(tmp_path, monkeypatch):
    monkeypatch.setattr(PiAgentChatCore, "CANDIDATE_MODULES", ("missing_piagent_module",))
    workspace_id = _workspace_with_profile(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "piagent-fallback")

    core = PiAgentChatCore(fallback=KeywordChatCore(), strict=False, source_root=tmp_path / "missing_pi_source")
    result = core.handle_message(workspace_id, session["session_id"], "整理资料")

    assert result["chat_core"] == {"requested": "piagent", "active": "keyword", "reason": "piagent_unavailable"}
    assert result["artifacts"][0]["type"] == "career_facts"


def test_piagent_adapter_strict_mode_fails_when_source_is_not_migrated(tmp_path, monkeypatch):
    monkeypatch.setattr(PiAgentChatCore, "CANDIDATE_MODULES", ("missing_piagent_module",))

    with pytest.raises(PiAgentUnavailableError):
        PiAgentChatCore(fallback=KeywordChatCore(), strict=True, source_root=tmp_path / "missing_pi_source")


def test_piagent_adapter_reports_earendil_source_not_built(tmp_path, monkeypatch):
    monkeypatch.setattr(PiAgentChatCore, "CANDIDATE_MODULES", ("missing_piagent_module",))
    source_root = tmp_path / "earendil_pi_source"
    (source_root / "packages/agent/src").mkdir(parents=True)
    (source_root / "packages/ai/src").mkdir(parents=True)
    workspace_id = _workspace_with_profile(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "piagent-not-built")

    core = PiAgentChatCore(fallback=KeywordChatCore(), strict=False, source_root=source_root)
    result = core.handle_message(workspace_id, session["session_id"], "整理资料")

    assert result["chat_core"] == {"requested": "piagent", "active": "keyword", "reason": "pi_agent_not_built"}
    assert result["artifacts"][0]["type"] == "career_facts"


def test_piagent_adapter_falls_back_when_node_bridge_times_out(tmp_path, monkeypatch):
    monkeypatch.setattr(PiAgentChatCore, "CANDIDATE_MODULES", ("missing_piagent_module",))
    source_root = tmp_path / "earendil_pi_source"
    (source_root / "packages/agent/dist/index.js").parent.mkdir(parents=True)
    (source_root / "packages/ai/dist/index.js").parent.mkdir(parents=True)
    (source_root / "packages/agent/dist/index.js").write_text("export const Agent = null;", encoding="utf-8")
    (source_root / "packages/ai/dist/index.js").write_text("export const ai = null;", encoding="utf-8")
    workspace_id = _workspace_with_profile(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "piagent-timeout")

    def timeout_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs.get("timeout"))

    monkeypatch.setattr(subprocess, "run", timeout_run)
    core = PiAgentChatCore(fallback=KeywordChatCore(), strict=False, source_root=source_root)
    result = core.handle_message(workspace_id, session["session_id"], "整理资料")

    assert result["chat_core"] == {"requested": "piagent", "active": "keyword", "reason": "pi_agent_bridge_timeout"}
    assert result["artifacts"][0]["type"] == "career_facts"


def test_piagent_adapter_uses_real_pi_core_for_basic_chat(tmp_path, monkeypatch):
    monkeypatch.setattr(PiAgentChatCore, "CANDIDATE_MODULES", ("missing_piagent_module",))
    source_root = ROOT / "vendor/earendil_pi_source"
    if not (source_root / "packages/agent/dist/index.js").exists():
        pytest.skip("earendil-works/pi dist is not built in this checkout")
    workspace_id = _workspace_with_profile(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "piagent-basic-chat")

    core = PiAgentChatCore(fallback=KeywordChatCore(), strict=False, source_root=source_root)
    result = core.handle_message(workspace_id, session["session_id"], "你好")

    assert result["chat_core"] == {
        "requested": "piagent",
        "active": "piagent_core_basic",
        "source_root": str(source_root),
        "workspace_id": workspace_id,
        "session_id": session["session_id"],
        "tool_bridge": "not_enabled",
    }
    assert result["artifacts"] == []
    assert "Pi Agent Core" in result["message"]
    recovered = jobpilot.get_chat_session(workspace_id, session["session_id"])
    assert [message["role"] for message in recovered["messages"]] == ["user", "assistant"]
    assert recovered["messages"][1]["content"] == result["message"]


def test_piagent_adapter_uses_real_pi_core_for_business_orchestration(tmp_path, monkeypatch):
    monkeypatch.setattr(PiAgentChatCore, "CANDIDATE_MODULES", ("missing_piagent_module",))
    source_root = ROOT / "vendor/earendil_pi_source"
    if not (source_root / "packages/agent/dist/index.js").exists():
        pytest.skip("earendil-works/pi dist is not built in this checkout")
    workspace_id = _workspace_with_profile(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "piagent-business-orchestration")
    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")

    core = PiAgentChatCore(fallback=KeywordChatCore(), strict=False, source_root=source_root)
    jd_result = core.handle_message(workspace_id, session["session_id"], "JD\n" + jd_text)
    package_result = core.handle_message(workspace_id, session["session_id"], "生成申请包")
    interview_result = core.handle_message(workspace_id, session["session_id"], "生成面试准备")

    assert jd_result["chat_core"]["active"] == "piagent_business_orchestrator"
    assert jd_result["chat_core"]["tool_bridge"] == "python_jobpilot_domain_tools"
    assert jd_result["orchestration"]["source"] == "pi_agent_tool_call"
    assert jd_result["orchestration"]["intent"] == "analyze_job"
    assert [artifact["type"] for artifact in jd_result["artifacts"]] == ["job", "match_report"]
    assert [step["tool"] for step in jd_result["orchestration"]["tool_plan"]] == ["job.parse_jd", "job.match_profile"]

    assert package_result["orchestration"]["intent"] == "create_application_package"
    assert [artifact["type"] for artifact in package_result["artifacts"]] == ["application_package"]
    assert package_result["artifacts"][0]["data"]["artifact_ref"]["artifact_type"] == "application_package"

    assert interview_result["orchestration"]["intent"] == "prepare_interview"
    assert [artifact["type"] for artifact in interview_result["artifacts"]] == ["interview_prep"]
    assert interview_result["artifacts"][0]["data"]["artifact_ref"]["artifact_type"] == "interview_prep"

    recovered = jobpilot.get_chat_session(workspace_id, session["session_id"])
    assert [message["role"] for message in recovered["messages"]] == ["user", "assistant", "user", "assistant", "user", "assistant"]
    assert recovered["messages"][1]["artifact_refs"]
    assert recovered["messages"][3]["artifact_refs"]
    assert recovered["messages"][5]["artifact_refs"]


def test_piagent_adapter_can_call_migrated_source_module(monkeypatch):
    module = types.ModuleType("services.piagent")

    def handle_message(workspace_id: str, session_id: str | None, message: str):
        return {"message": f"piagent:{message}", "artifacts": [], "workspace_id": workspace_id, "session_id": session_id}

    module.handle_message = handle_message
    monkeypatch.setitem(sys.modules, "services.piagent", module)
    monkeypatch.setattr(PiAgentChatCore, "CANDIDATE_MODULES", ("services.piagent",))

    core = PiAgentChatCore(fallback=KeywordChatCore(), strict=True)
    result = core.handle_message("ws_test", "chat_test", "hello")

    assert result == {"message": "piagent:hello", "artifacts": [], "workspace_id": "ws_test", "session_id": "chat_test"}
