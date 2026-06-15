from __future__ import annotations

import os
from typing import Protocol

from services.config import load_project_dotenv
from services.storage.workspace import workspace_conn
from services.tools import jobpilot


load_project_dotenv()

class ChatCore(Protocol):
    def handle_message(self, workspace_id: str, session_id: str | None, message: str) -> dict:
        ...


class KeywordChatCore:
    """P0 deterministic chat router used as the offline acceptance baseline."""

    def handle_message(self, workspace_id: str, session_id: str | None, message: str) -> dict:
        text = message.strip()
        lower = text.lower()
        conn, _ = workspace_conn(workspace_id)
        jobpilot.append_chat_message(conn, session_id, "user", text)
        if "job description" in lower or "jd" in lower or "岗位" in text:
            parsed = jobpilot.parse_jd(workspace_id, text)
            matched = jobpilot.match_profile(workspace_id, parsed["job_id"])
            artifacts = [{"type": "job", "data": parsed}, {"type": "match_report", "data": matched}]
            jobpilot.append_chat_message(conn, session_id, "assistant", "我已解析岗位并生成适合度分析。", [parsed.get("artifact_ref"), matched.get("artifact_ref")])
            return {"message": "我已解析岗位并生成适合度分析。", "artifacts": artifacts}
        if "申请包" in text or "package" in lower:
            conn, _ = workspace_conn(workspace_id)
            job = conn.execute("SELECT id FROM job WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
            if not job:
                return {"message": "请先粘贴一个 JD，我才能生成申请包。", "artifacts": []}
            package = jobpilot.create_application_package(workspace_id, job["id"])
            jobpilot.append_chat_message(conn, session_id, "assistant", "申请包已生成，请先确认事实再导出。", [package.get("artifact_ref")])
            return {"message": "申请包已生成，请先确认事实再导出。", "artifacts": [{"type": "application_package", "data": package}]}
        if "面试" in text or "interview" in lower:
            conn, _ = workspace_conn(workspace_id)
            job = conn.execute("SELECT id FROM job WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
            if not job:
                return {"message": "请先分析目标岗位，再生成面试准备。", "artifacts": []}
            prep = jobpilot.prepare_interview(workspace_id, job["id"])
            jobpilot.append_chat_message(conn, session_id, "assistant", "面试准备包和故事卡已生成。", [prep.get("artifact_ref")])
            return {"message": "面试准备包和故事卡已生成。", "artifacts": [{"type": "interview_prep", "data": prep}]}
        facts = jobpilot.extract_facts(workspace_id)
        jobpilot.append_chat_message(conn, session_id, "assistant", "我先整理了你的职业事实、技能线索和待确认信息。", [facts.get("artifact_ref")])
        return {"message": "我先整理了你的职业事实、技能线索和待确认信息。", "artifacts": [{"type": "career_facts", "data": facts}]}


def get_chat_core() -> ChatCore:
    mode = os.getenv("JOBPILOT_CHAT_CORE", "keyword").strip().lower()
    fallback = KeywordChatCore()
    if mode in {"keyword", "default", ""}:
        return fallback
    if mode == "piagent":
        from services.chat.piagent_adapter import PiAgentChatCore

        strict = os.getenv("JOBPILOT_CHAT_CORE_STRICT", "0").strip().lower() in {"1", "true", "yes"}
        return PiAgentChatCore(fallback=fallback, strict=strict)
    raise ValueError(f"Unsupported chat core: {mode}")
