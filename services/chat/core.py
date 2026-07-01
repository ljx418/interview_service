from __future__ import annotations

import os
from typing import Protocol

from services.config import load_project_dotenv
from services.storage.db import rows_to_dicts
from services.storage.workspace import workspace_conn
from services.tools import jobpilot


load_project_dotenv()

class ChatCore(Protocol):
    def handle_message(self, workspace_id: str, session_id: str | None, message: str) -> dict:
        ...


class KeywordChatCore:
    """Deterministic local chat router used as the offline acceptance baseline.

    This core intentionally stays local/mock by default. It supports free-form,
    multi-turn guidance without pretending to be a provider-backed LLM: explicit
    JobPilot intents execute tools; general follow-ups use recent workspace state
    to explain next steps and keep the conversation continuous.
    """

    def _looks_like_job_description(self, text: str, lower: str) -> bool:
        markers = [
            "job description",
            "职责",
            "任职要求",
            "requirements",
            "responsibilities",
            "must have",
            "nice to have",
            "we are looking for",
            "frontend developer",
            "backend developer",
            "software engineer",
        ]
        explicit_jd_action = "jd" in lower and ("解析" in text or "粘贴" in text or "目标" in text or "\n" in text or len(text) > 160)
        explicit_job_action = "岗位" in text and ("解析" in text or "粘贴" in text or "目标" in text or "\n" in text or len(text) > 160)
        return explicit_jd_action or explicit_job_action or any(marker in lower or marker in text for marker in markers)

    def _looks_like_profile_request(self, lower: str) -> bool:
        markers = [
            "整理资料",
            "职业事实",
            "提取事实",
            "技能证据",
            "整理简历",
            "分析我的简历",
            "extract facts",
            "profile",
            "resume facts",
        ]
        return any(marker in lower for marker in markers)

    def _looks_like_next_step_request(self, lower: str) -> bool:
        markers = [
            "下一步",
            "然后呢",
            "继续",
            "怎么做",
            "怎么办",
            "还缺",
            "缺什么",
            "能用于",
            "能投吗",
            "适合这个 jd",
            "next",
            "continue",
            "what now",
        ]
        return any(marker in lower for marker in markers)

    def _looks_like_status_request(self, lower: str) -> bool:
        markers = ["现在进展", "当前进展", "状态", "有哪些产物", "完成了什么", "status", "progress"]
        return any(marker in lower for marker in markers)

    def _looks_like_package_request(self, text: str, lower: str) -> bool:
        return "申请包" in text or "package" in lower

    def _looks_like_resume_request(self, text: str, lower: str) -> bool:
        markers = ["生成简历", "定制简历", "简历草稿", "resume", "cv"]
        return any(marker in text or marker in lower for marker in markers)

    def _declines_execution(self, lower: str) -> bool:
        markers = [
            "先别生成",
            "不要生成",
            "不用生成",
            "别执行",
            "先解释",
            "只解释",
            "先聊",
            "don't generate",
            "do not generate",
            "no generation",
            "explain first",
        ]
        return any(marker in lower for marker in markers)

    def _recent_messages(self, workspace_id: str, session_id: str | None, limit: int = 8) -> list[dict]:
        if not session_id:
            return []
        conn, _ = workspace_conn(workspace_id)
        rows = conn.execute(
            "SELECT role, content, created_at FROM chat_message WHERE session_id=? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        return list(reversed(rows_to_dicts(rows)))

    def _workspace_snapshot(self, workspace_id: str) -> dict:
        conn, _ = workspace_conn(workspace_id)
        latest_job = conn.execute(
            """
            SELECT id, title, company FROM job
            WHERE workspace_id=?
            ORDER BY is_current_target DESC, created_at DESC
            LIMIT 1
            """,
            (workspace_id,),
        ).fetchone()
        latest_package = conn.execute("SELECT id FROM application_package WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
        artifacts = jobpilot.list_artifacts(workspace_id)
        pending = [artifact for artifact in artifacts if artifact.get("status") == "needs_confirmation"]
        return {
            "latest_job": dict(latest_job) if latest_job else None,
            "latest_package": dict(latest_package) if latest_package else None,
            "artifact_count": len(artifacts),
            "pending_count": len(pending),
            "artifact_types": [artifact.get("artifact_type") for artifact in artifacts[:6]],
        }

    def _assistant_reply(self, workspace_id: str, session_id: str | None, user_text: str, message: str) -> dict:
        conn, _ = workspace_conn(workspace_id)
        jobpilot.append_chat_message(conn, session_id, "assistant", message)
        conn.commit()
        return {"message": message, "artifacts": [], "chat_mode": "free_local"}

    def _status_reply(self, workspace_id: str, session_id: str | None) -> dict:
        snapshot = self._workspace_snapshot(workspace_id)
        job = snapshot["latest_job"]
        if not job and snapshot["artifact_count"] == 0:
            return self._assistant_reply(
                workspace_id,
                session_id,
                "",
                "当前还没有生成求职产物。你可以先上传简历/项目资料，或直接粘贴一个目标 JD；如果只是想讨论方向，也可以继续问我。",
            )
        parts = [f"当前 workspace 里已有 {snapshot['artifact_count']} 个产物"]
        if job:
            parts.append(f"最近岗位是 {job.get('title') or '目标岗位'}" + (f"（{job.get('company')}）" if job.get("company") else ""))
        if snapshot["pending_count"]:
            parts.append(f"还有 {snapshot['pending_count']} 个产物需要确认事实")
        if snapshot["latest_package"]:
            parts.append("已经生成过申请包，可以检查待确认项后导出")
        else:
            parts.append("还没有可导出的申请包")
        return self._assistant_reply(workspace_id, session_id, "", "；".join(parts) + "。")

    def _next_step_reply(self, workspace_id: str, session_id: str | None) -> dict:
        snapshot = self._workspace_snapshot(workspace_id)
        if snapshot["latest_package"]:
            message = "下一步建议先检查推进台里的待确认项；确认事实后再导出 Markdown/DOCX。如果你想继续对话，可以告诉我你想强化哪一段经历或哪类岗位。"
        elif snapshot["latest_job"]:
            message = "下一步可以生成申请包，或先追问匹配报告里的优势和缺口。你可以直接说“生成申请包”，也可以继续问“这个岗位我最需要补什么”。"
        elif snapshot["artifact_count"]:
            message = "下一步可以粘贴目标 JD，让我把已有资料和岗位要求做匹配；也可以继续补充你的求职偏好，比如城市、岗位方向或希望突出的项目。"
        else:
            message = "下一步可以上传简历/项目资料，或直接粘贴 JD。你也可以先自由描述目标，我会先帮你整理思路，不会默认调用外部模型。"
        return self._assistant_reply(workspace_id, session_id, "", message)

    def _free_chat_reply(self, workspace_id: str, session_id: str | None, text: str) -> dict:
        self._recent_messages(workspace_id, session_id)
        snapshot = self._workspace_snapshot(workspace_id)
        if snapshot["latest_job"]:
            job = snapshot["latest_job"]
            context = f"我会沿用当前岗位上下文：{job.get('title') or '目标岗位'}。"
        elif snapshot["artifact_count"]:
            context = "我会沿用当前 workspace 里已有的资料和产物。"
        else:
            context = "当前还没有明确岗位或资料上下文。"
        message = (
            f"{context}我已收到你的补充：“{text[:120]}”。"
            "你可以继续追问、补充偏好，或明确让我执行：整理资料、解析 JD、生成申请包、准备面试。"
            "默认仍使用本地 mock 路径，不会自动外呼真实 provider。"
        )
        return self._assistant_reply(workspace_id, session_id, text, message)

    def handle_message(self, workspace_id: str, session_id: str | None, message: str) -> dict:
        text = message.strip()
        lower = text.lower()
        conn, _ = workspace_conn(workspace_id)
        if not text:
            assistant = "请输入 JD、资料整理任务，或先上传简历 / 项目 README。"
            jobpilot.append_chat_message(conn, session_id, "assistant", assistant)
            return {"message": assistant, "artifacts": []}
        jobpilot.append_chat_message(conn, session_id, "user", text)
        if self._declines_execution(lower):
            return self._free_chat_reply(workspace_id, session_id, text)
        if self._looks_like_resume_request(text, lower):
            conn, _ = workspace_conn(workspace_id)
            job = conn.execute(
                """
                SELECT id FROM job
                WHERE workspace_id=?
                ORDER BY is_current_target DESC, created_at DESC
                LIMIT 1
                """,
                (workspace_id,),
            ).fetchone()
            if job:
                resume = jobpilot.generate_resume(workspace_id, job["id"])
                jobpilot.append_chat_message(conn, session_id, "assistant", "JD 定制简历草稿已生成，请先检查 source refs 和待确认项。", [resume.get("artifact_ref")])
                return {"message": "JD 定制简历草稿已生成，请先检查 source refs 和待确认项。", "artifacts": [{"type": "application_package", "data": resume}]}
            assistant = "请先手动导入或粘贴一个目标 JD，我才能生成 JD 定制简历。"
            jobpilot.append_chat_message(conn, session_id, "assistant", assistant)
            return {"message": assistant, "artifacts": []}
        if self._looks_like_package_request(text, lower):
            conn, _ = workspace_conn(workspace_id)
            job = conn.execute(
                """
                SELECT id FROM job
                WHERE workspace_id=?
                ORDER BY is_current_target DESC, created_at DESC
                LIMIT 1
                """,
                (workspace_id,),
            ).fetchone()
            if job:
                package = jobpilot.create_application_package(workspace_id, job["id"])
                jobpilot.append_chat_message(conn, session_id, "assistant", "申请包已生成，请先确认事实再导出。", [package.get("artifact_ref")])
                return {"message": "申请包已生成，请先确认事实再导出。", "artifacts": [{"type": "application_package", "data": package}]}
            if not self._looks_like_job_description(text, lower):
                assistant = "请先粘贴一个 JD，我才能生成申请包。"
                jobpilot.append_chat_message(conn, session_id, "assistant", assistant)
                return {"message": assistant, "artifacts": []}
        if self._looks_like_job_description(text, lower):
            parsed = jobpilot.parse_jd(workspace_id, text, import_method="chat_paste", set_current_target=True)
            matched = jobpilot.match_profile(workspace_id, parsed["job_id"])
            artifacts = [{"type": "job", "data": parsed}, {"type": "match_report", "data": matched}]
            jobpilot.append_chat_message(conn, session_id, "assistant", "我已解析岗位并生成适合度分析。", [parsed.get("artifact_ref"), matched.get("artifact_ref")])
            return {"message": "我已解析岗位并生成适合度分析。", "artifacts": artifacts}
        if "面试" in text or "interview" in lower:
            conn, _ = workspace_conn(workspace_id)
            job = conn.execute("SELECT id FROM job WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
            if not job:
                assistant = "请先分析目标岗位，再生成面试准备。"
                jobpilot.append_chat_message(conn, session_id, "assistant", assistant)
                return {"message": assistant, "artifacts": []}
            prep = jobpilot.prepare_interview(workspace_id, job["id"])
            jobpilot.append_chat_message(conn, session_id, "assistant", "面试准备包和故事卡已生成。", [prep.get("artifact_ref")])
            return {"message": "面试准备包和故事卡已生成。", "artifacts": [{"type": "interview_prep", "data": prep}]}
        if self._looks_like_profile_request(lower):
            facts = jobpilot.extract_facts(workspace_id)
            jobpilot.append_chat_message(conn, session_id, "assistant", "我先整理了你的职业事实、技能线索和待确认信息。", [facts.get("artifact_ref")])
            return {"message": "我先整理了你的职业事实、技能线索和待确认信息。", "artifacts": [{"type": "career_facts", "data": facts}]}
        if self._looks_like_status_request(lower):
            return self._status_reply(workspace_id, session_id)
        if self._looks_like_next_step_request(lower):
            return self._next_step_reply(workspace_id, session_id)
        return self._free_chat_reply(workspace_id, session_id, text)


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
