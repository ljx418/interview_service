from __future__ import annotations

from hashlib import sha256
from typing import Any

from services.llm.provider import redact_text
from services.storage.db import loads, rows_to_dicts
from services.storage.workspace import workspace_conn
from services.tools import jobpilot


def _clip(value: str, max_chars: int = 220) -> str:
    redacted, _ = redact_text(value or "", max_chars=max_chars)
    return redacted


def _message_digest(messages: list[dict[str, Any]]) -> str:
    payload = "\n".join(f"{item.get('role')}:{item.get('content', '')}" for item in messages)
    return sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_chat_context(workspace_id: str, session_id: str, recent_limit: int = 12) -> dict[str, Any]:
    conn, _ = workspace_conn(workspace_id)
    session = conn.execute("SELECT * FROM chat_session WHERE workspace_id=? AND id=?", (workspace_id, session_id)).fetchone()
    if not session:
        raise ValueError("Chat session not found.")

    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_message WHERE session_id=? ORDER BY created_at ASC",
        (session_id,),
    ).fetchall()
    messages = rows_to_dicts(rows)
    recent_messages = messages[-recent_limit:]
    covered_messages = messages[:-recent_limit]
    summary_lines = []
    for item in covered_messages[-8:]:
        role = "用户" if item.get("role") == "user" else "助手"
        summary_lines.append(f"{role}: {_clip(item.get('content', ''), 96)}")
    rolling_summary = "；".join(summary_lines) if summary_lines else "尚未形成滚动摘要。"

    latest_job = conn.execute("SELECT id, title, company FROM job WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
    latest_package = conn.execute("SELECT id, job_id FROM application_package WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
    artifacts = jobpilot.list_artifacts(workspace_id)
    pending = [item for item in artifacts if item.get("status") == "needs_confirmation"]

    retrieved_blocks = []
    for artifact in artifacts[:6]:
        content = loads(artifact.get("content_json"), {})
        preview_source = content.get("project_description") or content.get("recruiter_message") or content.get("apply_recommendation") or content.get("resume_markdown") or ""
        retrieved_blocks.append(
            {
                "source_type": "artifact",
                "source_id": artifact.get("id"),
                "artifact_type": artifact.get("artifact_type"),
                "redacted_excerpt": _clip(str(preview_source), 180),
                "risk_label": "needs_confirmation" if artifact.get("status") == "needs_confirmation" else "normal",
            }
        )

    return {
        "session_id": session_id,
        "workspace_id": workspace_id,
        "recent_count": len(recent_messages),
        "total_message_count": len(messages),
        "recent_messages": [
            {
                "role": item.get("role"),
                "content": _clip(item.get("content", ""), 260),
                "created_at": item.get("created_at"),
            }
            for item in recent_messages
        ],
        "rolling_summary": {
            "summary_text": rolling_summary,
            "covered_message_count": len(covered_messages),
            "source_digest": _message_digest(covered_messages),
        },
        "workspace_snapshot": {
            "latest_job": dict(latest_job) if latest_job else None,
            "latest_package": dict(latest_package) if latest_package else None,
            "artifact_count": len(artifacts),
            "pending_confirmation_count": len(pending),
            "artifact_types": [item.get("artifact_type") for item in artifacts[:8]],
        },
        "retrieved_blocks": retrieved_blocks,
        "privacy_boundary": {
            "contains_api_key": False,
            "raw_provider_response_included": False,
            "full_history_included": False,
            "redacted": True,
        },
    }
