from pathlib import Path

import pytest

from services.chat.core import KeywordChatCore
from services.storage.db import loads
from services.storage.workspace import init_workspace, workspace_conn
from services.tools import jobpilot


def _write_local_fixture(tmp_path: Path) -> tuple[Path, Path, str]:
    resume = tmp_path / "local_resume.md"
    resume.write_text(
        """
# 本地候选人资料

- 目标岗位：初级前端开发
- 技能：React、TypeScript、Python、FastAPI
- 项目：JobPilot Local Review，把聊天式求职材料工作台接入本地 workspace。
- 贡献：负责前端状态机、申请包确认门槛和自动化验收脚本。
""".strip(),
        encoding="utf-8",
    )
    project = tmp_path / "local_project.md"
    project.write_text(
        """
# Local Review 项目

使用 React 和 FastAPI 搭建本地求职材料闭环，支持上传资料、解析 JD、生成匹配报告、生成申请包和导出 Markdown。
本人负责界面状态管理、artifact 版本记录、导出前确认门槛和端到端测试。
""".strip(),
        encoding="utf-8",
    )
    jd_text = """
职位：Junior Frontend Developer
职责：开发 React + TypeScript 前端页面，和 FastAPI 后端协作完成本地数据工作流。
要求：React、TypeScript、基础 Python、能写自动化测试，重视用户体验和可维护性。
加分：熟悉本地优先隐私设计、Markdown 导出、Playwright 或 pytest。
""".strip()
    return resume, project, jd_text


def _build_p5_workspace(tmp_path: Path):
    workspace = init_workspace("p5-local-data", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume_path, project_path, jd_text = _write_local_fixture(tmp_path)
    resume = jobpilot.save_document(workspace_id, str(resume_path), "resume")
    project = jobpilot.save_document(workspace_id, str(project_path), "project")
    facts = jobpilot.extract_facts(workspace_id, [resume["document_id"], project["document_id"]], ["Junior Frontend Developer"])
    job = jobpilot.parse_jd(workspace_id, jd_text)
    match = jobpilot.match_profile(workspace_id, job["job_id"])
    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    return workspace_id, facts, job, match, package


def test_p5_local_data_flow_blocks_export_until_application_package_is_confirmed(tmp_path):
    workspace_id, facts, job, match, package = _build_p5_workspace(tmp_path)

    assert facts["facts"]
    assert job["tech_stack"]
    assert match["source_refs"]
    assert any(item["confirmation_level"] == "blocking" for item in package["questions_to_confirm"])

    with pytest.raises(ValueError, match="EXPORT_PRECHECK_FAILED"):
        jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])

    confirmed = jobpilot.confirm_artifact(workspace_id, package["artifact_ref"]["artifact_id"])
    assert confirmed["status"] == "confirmed"
    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown", "docx"])

    export_paths = [Path(item["path"]) for item in exported["exports"]]
    assert {path.suffix for path in export_paths} == {".md", ".docx"}
    assert all(path.exists() for path in export_paths)
    assert "导出前仍需注意" in export_paths[0].read_text(encoding="utf-8")


def test_p5_user_edit_reopens_confirmation_gate_before_export(tmp_path):
    workspace_id, _, _, _, package = _build_p5_workspace(tmp_path)
    artifact_id = package["artifact_ref"]["artifact_id"]

    jobpilot.confirm_artifact(workspace_id, artifact_id)
    first_export = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    assert Path(first_export["exports"][0]["path"]).exists()

    edited = dict(package)
    edited["resume_markdown"] = edited["resume_markdown"] + "\n\n## 用户补充\n这是一版用户编辑后的申请包。"
    edited.pop("artifact_ref", None)
    edited.pop("source_fact_refs", None)
    updated = jobpilot.update_artifact(workspace_id, artifact_id, edited)
    assert updated["status"] == "needs_confirmation"

    with pytest.raises(ValueError, match="EXPORT_PRECHECK_FAILED"):
        jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])

    jobpilot.confirm_artifact(workspace_id, artifact_id)
    second_export = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
    assert "用户编辑后的申请包" in Path(second_export["exports"][0]["path"]).read_text(encoding="utf-8")


def test_p5_confirm_artifact_marks_current_version_confirmed(tmp_path):
    workspace_id, _, _, _, package = _build_p5_workspace(tmp_path)
    artifact_id = package["artifact_ref"]["artifact_id"]
    confirmed = jobpilot.confirm_artifact(workspace_id, artifact_id)

    conn, _ = workspace_conn(workspace_id)
    version = conn.execute(
        "SELECT status, questions_to_confirm FROM artifact_version WHERE workspace_id=? AND artifact_id=? AND id=?",
        (workspace_id, artifact_id, confirmed["current_version_id"]),
    ).fetchone()

    assert version["status"] == "confirmed"
    assert any(item["confirmation_level"] == "blocking" for item in loads(version["questions_to_confirm"], []))


def test_p5_free_chat_followup_keeps_context_without_creating_artifacts(tmp_path):
    workspace_id, _, _, _, _ = _build_p5_workspace(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "P5 free local chat")
    core = KeywordChatCore()
    before = len(jobpilot.list_artifacts(workspace_id))

    result = core.handle_message(workspace_id, session["session_id"], "这个经历能用于这个 JD 吗？")
    after = len(jobpilot.list_artifacts(workspace_id))

    assert result["artifacts"] == []
    assert after == before
    assert "下一步" in result["message"] or "当前岗位" in result["message"] or "生成申请包" in result["message"]
    assert result["chat_mode"] == "free_local"


def test_p5_package_request_with_current_jd_context_does_not_reparse_jd(tmp_path):
    workspace_id, _, _, _, _ = _build_p5_workspace(tmp_path)
    session = jobpilot.create_chat_session(workspace_id, "P5 package routing")
    core = KeywordChatCore()
    before = [item["artifact_type"] for item in jobpilot.list_artifacts(workspace_id)]

    result = core.handle_message(workspace_id, session["session_id"], "请基于当前资料和目标 JD，生成申请包草稿。")
    after = [item["artifact_type"] for item in jobpilot.list_artifacts(workspace_id)]

    assert result["artifacts"][0]["type"] == "application_package"
    assert "申请包已生成" in result["message"]
    assert after.count("application_package") == before.count("application_package") + 1
    assert after.count("job_parse") == before.count("job_parse")


def test_p5_export_preflight_requires_source_refs(tmp_path):
    workspace_id, _, _, _, package = _build_p5_workspace(tmp_path)
    artifact_id = package["artifact_ref"]["artifact_id"]
    jobpilot.confirm_artifact(workspace_id, artifact_id)
    conn, _ = workspace_conn(workspace_id)
    artifact = conn.execute("SELECT current_version_id FROM artifact WHERE id=?", (artifact_id,)).fetchone()
    conn.execute("UPDATE artifact_version SET source_refs=? WHERE id=?", ("[]", artifact["current_version_id"]))
    conn.commit()

    with pytest.raises(ValueError, match="EXPORT_PRECHECK_FAILED"):
        jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown"])
