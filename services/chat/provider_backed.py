from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel

from services.chat.context import build_chat_context
from services.llm.provider import ProviderError, get_provider, provider_status, redact_text, summarize_payload
from services.storage.db import dumps
from services.storage.workspace import workspace_conn
from services.tools import jobpilot


class FreeChatOutput(BaseModel):
    message: str
    source_notes: list[str] = []
    confidence: str = "bounded"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _estimate_tokens(value: Any) -> int:
    text = dumps(value) if not isinstance(value, str) else value
    return max(1, len(text) // 4)


def _log_chat_invocation(
    *,
    workspace_id: str,
    session_id: str | None,
    provider_name: str,
    model: str | None,
    consent: dict | None,
    status: str,
    error_code: str | None = None,
    latency_ms: int = 0,
    token_estimate: int = 0,
    input_summary: Any | None = None,
    redaction_summary: dict | None = None,
    fallback_used: bool = False,
) -> None:
    try:
        conn, _ = workspace_conn(workspace_id)
        conn.execute(
            """
            INSERT INTO provider_chat_invocation (
              id, workspace_id, session_id, provider_name, model,
              consent_id, consent_scope, status, error_code, latency_ms,
              token_estimate, input_summary, redaction_summary, fallback_used, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"provider_chat_inv_{uuid4().hex}",
                workspace_id,
                session_id,
                provider_name,
                model,
                consent.get("consent_id") if consent else None,
                consent.get("scope") if consent else None,
                status,
                error_code,
                latency_ms,
                token_estimate,
                dumps(input_summary or {}),
                dumps(redaction_summary or {"metadata_only": True}),
                1 if fallback_used else 0,
                _now(),
            ),
        )
    except Exception:
        return


def _is_explicit_tool_intent(message: str) -> bool:
    text = message.strip()
    lower = text.lower()
    tool_markers = [
        "解析 jd",
        "解析这个 jd",
        "粘贴 jd",
        "目标 jd",
        "生成申请包",
        "申请包",
        "整理资料",
        "提取事实",
        "分析我的简历",
        "准备面试",
        "面试准备",
        "导出",
        "重新生成",
        "parse jd",
        "job description",
        "application package",
        "export",
    ]
    if any(marker in lower for marker in tool_markers):
        return True
    return len(text) > 180 and ("职责" in text or "任职要求" in text or "requirements" in lower)


def _context_envelope(workspace_id: str, session_id: str, message: str, consent: dict) -> dict:
    context = build_chat_context(workspace_id, session_id)
    clipped_message, redacted = redact_text(message, max_chars=500)
    return {
        "consent_scope": consent.get("scope"),
        "allowed_data_classes": consent.get("allowed_data_classes", []),
        "user_message": clipped_message,
        "message_redacted": redacted,
        "recent_window": context["recent_messages"],
        "rolling_summary": context["rolling_summary"],
        "workspace_snapshot": context["workspace_snapshot"],
        "retrieved_blocks": context["retrieved_blocks"],
        "privacy_boundary": context["privacy_boundary"],
    }


def _fake_provider_reply(envelope: dict, provider: dict) -> str:
    snapshot = envelope.get("workspace_snapshot", {})
    job = snapshot.get("latest_job") or {}
    artifact_count = snapshot.get("artifact_count", 0)
    pending = snapshot.get("pending_confirmation_count", 0)
    context_hint = "当前还没有岗位上下文"
    if job:
        context_hint = f"当前岗位上下文是 {job.get('title') or '目标岗位'}"
    elif artifact_count:
        context_hint = f"当前 workspace 已有 {artifact_count} 个产物"
    pending_hint = f"，其中 {pending} 个需要确认" if pending else ""
    model = provider.get("model") or "fake-provider-model"
    return (
        f"（Fake provider · {model}）{context_hint}{pending_hint}。"
        "我会基于最近对话、滚动摘要和 workspace 摘要继续回答，不会把这次普通聊天写成产物。"
        "如果你要执行解析、生成或导出，请明确发出对应任务。"
    )


def handle_provider_backed_message(
    *,
    fallback_core: Any,
    workspace_id: str,
    session_id: str | None,
    message: str,
    consent: dict | None,
) -> dict:
    if not session_id:
        return fallback_core.handle_message(workspace_id, session_id, message)
    if _is_explicit_tool_intent(message):
        result = fallback_core.handle_message(workspace_id, session_id, message)
        result["provider_invocation_status"] = "skipped_tool_intent"
        result["fallback_used"] = False
        return result

    status = provider_status()
    provider_name = status.get("provider", "mock")
    if provider_name == "mock" or not status.get("configured"):
        _log_chat_invocation(
            workspace_id=workspace_id,
            session_id=session_id,
            provider_name=provider_name,
            model=status.get("model"),
            consent=consent,
            status="policy_denied",
            error_code="PROVIDER_NOT_CONFIGURED",
            fallback_used=True,
        )
        result = fallback_core.handle_message(workspace_id, session_id, message)
        result["provider_invocation_status"] = "policy_denied"
        result["fallback_used"] = True
        return result
    if not consent:
        _log_chat_invocation(
            workspace_id=workspace_id,
            session_id=session_id,
            provider_name=provider_name,
            model=status.get("model"),
            consent=None,
            status="policy_denied",
            error_code="CONSENT_REQUIRED",
            fallback_used=True,
        )
        result = fallback_core.handle_message(workspace_id, session_id, message)
        result["provider_invocation_status"] = "consent_required"
        result["fallback_used"] = True
        return result

    started = time.monotonic()
    envelope = _context_envelope(workspace_id, session_id, message, consent)
    summary, did_redact = summarize_payload(envelope, max_chars=180)
    redaction_summary = {
        "metadata_only": True,
        "redaction_applied": True if did_redact else envelope.get("message_redacted", False),
        "context_boundary": envelope["privacy_boundary"],
    }

    fake_enabled = os.getenv("JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT", "").strip().lower() in {"1", "true", "yes"}
    fake_error = os.getenv("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", "").strip().lower()
    real_enabled = os.getenv("JOBPILOT_ALLOW_REAL_PROVIDER_CHAT", "").strip().lower() in {"1", "true", "yes"}

    try:
        if fake_error:
            error_map = {
                "timeout": "LLM_TIMEOUT",
                "429": "PROVIDER_RATE_LIMITED",
                "schema": "VALIDATION_FAILED",
                "network": "LLM_FAILED",
            }
            raise ProviderError(error_map.get(fake_error, "LLM_FAILED"), f"Fake provider simulated {fake_error}.")
        if fake_enabled:
            assistant = _fake_provider_reply(envelope, status)
        elif real_enabled:
            provider = get_provider(provider_name)
            output = provider.generate_structured(
                "chat_free_dialogue",
                {"provider_context_envelope": envelope},
                FreeChatOutput,
                safety_mode="privacy_bounded_chat",
                request_options={"workspace_id": workspace_id},
            )
            assistant = output["message"]
        else:
            raise ProviderError("REAL_PROVIDER_CHAT_DISABLED", "Provider-backed chat is disabled unless fake or explicit real-provider mode is enabled.")

        conn, _ = workspace_conn(workspace_id)
        jobpilot.append_chat_message(conn, session_id, "user", message.strip())
        jobpilot.append_chat_message(conn, session_id, "assistant", assistant, [])
        _log_chat_invocation(
            workspace_id=workspace_id,
            session_id=session_id,
            provider_name=provider_name,
            model=status.get("model"),
            consent=consent,
            status="called",
            latency_ms=int((time.monotonic() - started) * 1000),
            token_estimate=_estimate_tokens(envelope),
            input_summary=summary,
            redaction_summary=redaction_summary,
            fallback_used=False,
        )
        return {
            "message": assistant,
            "artifacts": [],
            "chat_mode": "provider_fake" if fake_enabled else "provider_backed",
            "provider_invocation_status": "called",
            "fallback_used": False,
            "context_summary": {
                "recent_count": len(envelope["recent_window"]),
                "rolling_summary": envelope["rolling_summary"],
                "workspace_snapshot": envelope["workspace_snapshot"],
                "privacy_boundary": envelope["privacy_boundary"],
            },
        }
    except ProviderError as error:
        _log_chat_invocation(
            workspace_id=workspace_id,
            session_id=session_id,
            provider_name=provider_name,
            model=status.get("model"),
            consent=consent,
            status="failed",
            error_code=error.error_code,
            latency_ms=int((time.monotonic() - started) * 1000),
            token_estimate=_estimate_tokens(envelope),
            input_summary=summary,
            redaction_summary=redaction_summary,
            fallback_used=True,
        )
        result = fallback_core.handle_message(workspace_id, session_id, message)
        result["provider_invocation_status"] = "failed"
        result["provider_error_code"] = error.error_code
        result["fallback_used"] = True
        result["context_summary"] = {
            "recent_count": len(envelope["recent_window"]),
            "rolling_summary": envelope["rolling_summary"],
            "workspace_snapshot": envelope["workspace_snapshot"],
            "privacy_boundary": envelope["privacy_boundary"],
        }
        return result
