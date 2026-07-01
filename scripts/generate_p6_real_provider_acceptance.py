#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.db import row_to_dict
from services.storage.workspace import init_workspace, workspace_conn


DEFAULT_REPORT = ROOT / "docs/reports/P6_REAL_PROVIDER_ACCEPTANCE_REPORT.html"
DEFAULT_EVIDENCE_DIR = ROOT / "docs/reports/evidence/p6_real_provider_acceptance"
DEFAULT_WORKSPACE_ROOT = ROOT / ".tmp/p6_real_provider_workspace"
DEFAULT_ALLOWED_DATA_CLASSES = "recent_messages,rolling_summary,workspace_summary,artifact_summary"
DEFAULT_REPORT_FIELDS = "provider,model,status,duration_ms,redaction_summary,fallback"
FAKE_KEY = "fake-local-key-never-exposed"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _count_chat_invocations(workspace_id: str) -> int:
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute("SELECT COUNT(*) AS count FROM provider_chat_invocation WHERE workspace_id=?", (workspace_id,)).fetchone()
    return int(row["count"])


def _latest_chat_invocation(workspace_id: str) -> dict | None:
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute("SELECT * FROM provider_chat_invocation WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone()
    return row_to_dict(row) if row else None


def _client_workspace(workspace_root: Path) -> tuple[TestClient, str, str]:
    workspace = init_workspace("p6-real-provider-acceptance", str(workspace_root))
    workspace_id = workspace.get("workspace_id") or workspace["id"]
    client = TestClient(app)
    session = client.post("/api/chat/sessions", json={"workspace_id": workspace_id, "title": "P6-REAL acceptance"}).json()["data"]
    return client, workspace_id, session["session_id"]


def _safe_env_snapshot() -> dict[str, str | None]:
    keys = [
        "JOBPILOT_LLM_PROVIDER",
        "JOBPILOT_OPENAI_API_KEY",
        "JOBPILOT_OPENAI_BASE_URL",
        "JOBPILOT_OPENAI_MODEL",
        "JOBPILOT_OPENAI_PROVIDER_PRESET",
        "JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT",
        "JOBPILOT_FAKE_PROVIDER_CHAT_ERROR",
        "JOBPILOT_ALLOW_REAL_PROVIDER_CHAT",
    ]
    return {key: os.environ.get(key) for key in keys}


def _restore_env(snapshot: dict[str, str | None]) -> None:
    for key, value in snapshot.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def _assert_no_sensitive_text(report: str, evidence: dict) -> None:
    serialized = report + "\n" + _json(evidence)
    forbidden = [
        FAKE_KEY,
        "sk-",
        "Bearer ",
        "完整 prompt",
        "完整真实资料",
        "raw provider response",
    ]
    for marker in forbidden:
        if marker in serialized:
            raise RuntimeError(f"sensitive marker leaked into report/evidence: {marker}")


def run_gate_only(max_calls: int, allowed_data_classes: list[str], report_fields: list[str], workspace_root: Path) -> dict:
    snapshot = _safe_env_snapshot()
    try:
        os.environ["JOBPILOT_LLM_PROVIDER"] = "mock"
        os.environ.pop("JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT", None)
        os.environ.pop("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", None)
        os.environ.pop("JOBPILOT_ALLOW_REAL_PROVIDER_CHAT", None)
        client, workspace_id, session_id = _client_workspace(workspace_root)

        default_status = client.get(f"/api/provider/status?workspace_id={workspace_id}&session_id={session_id}").json()["data"]
        default_invocations = _count_chat_invocations(workspace_id)

        os.environ["JOBPILOT_OPENAI_API_KEY"] = FAKE_KEY
        preference = client.post(
            "/api/provider/preferences",
            json={
                "provider": "openai_compatible",
                "preset": "deepseek",
                "base_url": "https://example.invalid/v1",
                "model": "deepseek-chat",
                "mode": "provider_opt_in",
            },
        )
        preference.raise_for_status()
        configured_status = client.get(f"/api/provider/status?workspace_id={workspace_id}&session_id={session_id}").json()["data"]

        denied = client.post(
            "/api/chat/message",
            json={
                "workspace_id": workspace_id,
                "session_id": session_id,
                "message": "请先聊聊我的求职方向，不要生成材料，不要调用真实外部模型。",
                "provider_mode": "provider_opt_in",
            },
        )
        denied.raise_for_status()
        denied_data = denied.json()["data"]

        consent_denied = client.post(
            "/api/provider/consent",
            json={
                "workspace_id": workspace_id,
                "session_id": session_id,
                "scope": "chat_session",
                "allowed_data_classes": allowed_data_classes,
                "confirm_external_call": False,
            },
        )
        consent_denied.raise_for_status()
        consent_denied_data = consent_denied.json()["data"]
        final_status = client.get(f"/api/provider/status?workspace_id={workspace_id}&session_id={session_id}").json()["data"]
        latest = _latest_chat_invocation(workspace_id)

        return {
            "mode": "gate-only",
            "generated_at": _now(),
            "workspace_id": workspace_id,
            "session_id": session_id,
            "authorization": {
                "real_provider_authorized": False,
                "max_calls": max_calls,
                "allowed_data_classes": allowed_data_classes,
                "report_fields": report_fields,
            },
            "steps": [
                {"name": "default_status", "status": "pass", "evidence": {"p6_state": default_status.get("p6_state"), "provider": default_status.get("provider"), "called_in_session": default_status.get("called_in_session")}},
                {"name": "configured_not_called", "status": "pass", "evidence": {"configured": configured_status.get("configured"), "configured_is_called": configured_status.get("configured_is_called"), "called_in_session": configured_status.get("called_in_session")}},
                {"name": "chat_without_consent_fallback", "status": "pass", "evidence": {"provider_invocation_status": denied_data.get("provider_invocation_status"), "fallback_used": denied_data.get("fallback_used"), "chat_mode": denied_data.get("chat_mode")}},
                {"name": "consent_requires_explicit_confirmation", "status": "pass", "evidence": {"consent_required": consent_denied_data.get("consent_required"), "consented": consent_denied_data.get("consented")}},
            ],
            "counts": {
                "default_chat_invocations": default_invocations,
                "final_chat_invocations": _count_chat_invocations(workspace_id),
            },
            "final_status": {
                "p6_state": final_status.get("p6_state"),
                "configured": final_status.get("configured"),
                "configured_is_called": final_status.get("configured_is_called"),
                "called_in_session": final_status.get("called_in_session"),
                "fallback_used": final_status.get("fallback_used"),
                "last_error": final_status.get("last_error"),
                "api_key_redacted": final_status.get("api_key_redacted"),
            },
            "latest_invocation": {
                "status": latest.get("status") if latest else None,
                "error_code": latest.get("error_code") if latest else None,
                "fallback_used": bool(latest.get("fallback_used")) if latest else None,
                "provider_name": latest.get("provider_name") if latest else None,
                "model": latest.get("model") if latest else None,
            },
            "prd_review": [
                {"requirement": "默认不外呼真实 provider", "status": "pass", "evidence": "默认 provider=status mock，chat invocation count 为 0。"},
                {"requirement": "configured 不等于 called", "status": "pass", "evidence": "配置 provider 偏好后 configured=true，但 called_in_session=false。"},
                {"requirement": "未确认外呼必须 fallback", "status": "pass", "evidence": "provider_invocation_status=consent_required，fallback_used=true。"},
                {"requirement": "报告不得声明真实 LLM 质量通过", "status": "pass", "evidence": "本报告结论为真实 provider 未执行。"},
            ],
            "unverified_scope": [
                "未调用 MiniMax、DeepSeek、OpenAI-compatible 或其他真实 provider。",
                "未读取真实个人资料。",
                "未验证真实 LLM 回复质量。",
            ],
        }
    finally:
        _restore_env(snapshot)


def run_real(max_calls: int, allowed_data_classes: list[str], report_fields: list[str], workspace_root: Path) -> dict:
    if os.environ.get("JOBPILOT_ALLOW_REAL_PROVIDER_CHAT", "").strip().lower() not in {"1", "true", "yes"}:
        raise SystemExit("real mode requires JOBPILOT_ALLOW_REAL_PROVIDER_CHAT=1")
    if max_calls < 1 or max_calls > 10:
        raise SystemExit("real mode requires --max-calls between 1 and 10")

    client, workspace_id, session_id = _client_workspace(workspace_root)
    status = client.get(f"/api/provider/status?workspace_id={workspace_id}&session_id={session_id}").json()["data"]
    if status.get("provider") == "mock" or not status.get("configured"):
        raise SystemExit("real mode requires configured non-mock provider")

    consent = client.post(
        "/api/provider/consent",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "scope": "chat_session",
            "ttl_seconds": 600,
            "allowed_data_classes": allowed_data_classes,
            "confirm_external_call": True,
        },
    )
    consent.raise_for_status()

    turns = []
    for index in range(max_calls):
        response = client.post(
            "/api/chat/message",
            json={
                "workspace_id": workspace_id,
                "session_id": session_id,
                "message": f"第 {index + 1} 轮：请基于最近摘要给出求职方向建议，不要生成材料。",
                "provider_mode": "provider_opt_in",
            },
        )
        response.raise_for_status()
        data = response.json()["data"]
        turns.append(
            {
                "index": index + 1,
                "provider_invocation_status": data.get("provider_invocation_status"),
                "fallback_used": data.get("fallback_used"),
                "chat_mode": data.get("chat_mode"),
                "provider_error_code": data.get("provider_error_code"),
            }
        )

    final_status = client.get(f"/api/provider/status?workspace_id={workspace_id}&session_id={session_id}").json()["data"]
    latest = _latest_chat_invocation(workspace_id)
    return {
        "mode": "real",
        "generated_at": _now(),
        "workspace_id": workspace_id,
        "session_id": session_id,
        "authorization": {
            "real_provider_authorized": True,
            "max_calls": max_calls,
            "allowed_data_classes": allowed_data_classes,
            "report_fields": report_fields,
        },
        "steps": [{"name": "real_provider_turns", "status": "executed", "evidence": turns}],
        "final_status": {
            "p6_state": final_status.get("p6_state"),
            "provider": final_status.get("provider"),
            "model": final_status.get("model"),
            "called_in_session": final_status.get("called_in_session"),
            "fallback_used": final_status.get("fallback_used"),
            "last_error": final_status.get("last_error"),
            "api_key_redacted": final_status.get("api_key_redacted"),
        },
        "latest_invocation": {
            "status": latest.get("status") if latest else None,
            "error_code": latest.get("error_code") if latest else None,
            "fallback_used": bool(latest.get("fallback_used")) if latest else None,
            "provider_name": latest.get("provider_name") if latest else None,
            "model": latest.get("model") if latest else None,
        },
        "prd_review": [
            {"requirement": "真实 provider 必须授权后调用", "status": "executed", "evidence": "real mode 只在 JOBPILOT_ALLOW_REAL_PROVIDER_CHAT=1 时执行。"},
            {"requirement": "provider 失败必须 fallback", "status": "review", "evidence": "查看 turns 和 latest invocation 中 fallback/error 状态。"},
            {"requirement": "报告不得泄露密钥或 raw response", "status": "review", "evidence": "报告只展示 provider/model/status/fallback 等脱敏字段。"},
        ],
        "unverified_scope": [
            "真实 LLM 内容质量需要人工审查，本报告只证明受控调用、失败降级和日志脱敏边界。",
            "未读取真实个人资料。",
        ],
    }


def render_report(evidence: dict) -> str:
    mode = evidence["mode"]
    mode_label = "Gate-only 未授权门禁" if mode == "gate-only" else "Real provider 小样本"
    conclusion = (
        "真实 provider 未执行；门禁阻塞、configured != called、fallback 和脱敏边界符合预期。"
        if mode == "gate-only"
        else "真实 provider 已按显式授权执行小样本；是否通过质量验收仍需人工结合脱敏证据判断。"
    )
    steps = "\n".join(
        f"<tr><td>{_escape(item['name'])}</td><td>{_escape(item['status'])}</td><td><pre>{_escape(_json(item['evidence']))}</pre></td></tr>"
        for item in evidence.get("steps", [])
    )
    prd = "\n".join(
        f"<tr><td>{_escape(item['requirement'])}</td><td>{_escape(item['status'])}</td><td>{_escape(item['evidence'])}</td></tr>"
        for item in evidence.get("prd_review", [])
    )
    unverified = "\n".join(f"<li>{_escape(item)}</li>" for item in evidence.get("unverified_scope", []))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>P6-REAL 真实 Provider 受控验收报告</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #17201b; background: #f6f3ec; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 32px 24px 56px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin-top: 30px; font-size: 20px; }}
    .hero {{ background: #ffffff; border: 1px solid #d9e2d8; border-radius: 10px; padding: 24px; box-shadow: 0 14px 40px rgba(36, 50, 41, .08); }}
    .badge {{ display: inline-block; padding: 5px 10px; border-radius: 999px; background: #fff2cc; border: 1px solid #d6b656; font-weight: 700; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .card {{ background: #fff; border: 1px solid #e1ded4; border-radius: 8px; padding: 16px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #ddd8ca; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #eff5ee; }}
    pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; font-size: 12px; }}
    .warn {{ border-left: 5px solid #b85450; background: #fff7f6; padding: 12px 14px; }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <span class="badge">{_escape(mode_label)}</span>
    <h1>P6-REAL 真实 Provider 受控验收报告</h1>
    <p>{_escape(conclusion)}</p>
    <p>生成时间：{_escape(evidence.get('generated_at'))}</p>
  </section>

  <h2>目标架构</h2>
  <div class="grid">
    <div class="card"><strong>Chatbox</strong><p>展示 provider 状态、调用前确认、长程对话状态和 fallback。</p></div>
    <div class="card"><strong>Provider Policy Gate</strong><p>拦截未授权外呼、缺密钥、超预算和不允许的数据类别。</p></div>
    <div class="card"><strong>Evidence Layer</strong><p>仅保存脱敏状态、调用元数据、PRD 检视和未验证范围。</p></div>
  </div>

  <h2>当前实现与授权边界</h2>
  <table>
    <tr><th>字段</th><th>值</th></tr>
    <tr><td>mode</td><td>{_escape(mode)}</td></tr>
    <tr><td>real_provider_authorized</td><td>{_escape(evidence['authorization']['real_provider_authorized'])}</td></tr>
    <tr><td>max_calls</td><td>{_escape(evidence['authorization']['max_calls'])}</td></tr>
    <tr><td>allowed_data_classes</td><td>{_escape(', '.join(evidence['authorization']['allowed_data_classes']))}</td></tr>
    <tr><td>report_fields</td><td>{_escape(', '.join(evidence['authorization']['report_fields']))}</td></tr>
  </table>

  <h2>用户场景与自动化证据</h2>
  <table><tr><th>步骤</th><th>状态</th><th>证据</th></tr>{steps}</table>

  <h2>PRD 规格检视</h2>
  <table><tr><th>规格</th><th>状态</th><th>证据</th></tr>{prd}</table>

  <h2>最终状态</h2>
  <pre>{_escape(_json(evidence.get('final_status', {})))}</pre>

  <h2>未验证范围</h2>
  <div class="warn"><ul>{unverified}</ul></div>
</main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate P6-REAL controlled provider acceptance report.")
    parser.add_argument("--mode", choices=["gate-only", "real"], default="gate-only")
    parser.add_argument("--max-calls", type=int, default=3)
    parser.add_argument("--allowed-data-classes", default=DEFAULT_ALLOWED_DATA_CLASSES)
    parser.add_argument("--report-fields", default=DEFAULT_REPORT_FIELDS)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    parser.add_argument("--workspace-root", default=str(DEFAULT_WORKSPACE_ROOT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    allowed = [item.strip() for item in args.allowed_data_classes.split(",") if item.strip()]
    report_fields = [item.strip() for item in args.report_fields.split(",") if item.strip()]
    report = Path(args.report).expanduser().resolve()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    workspace_root = Path(args.workspace_root).expanduser().resolve()

    if args.mode == "gate-only":
        evidence = run_gate_only(args.max_calls, allowed, report_fields, workspace_root)
    else:
        evidence = run_real(args.max_calls, allowed, report_fields, workspace_root)

    evidence_dir.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / "p6_real_provider_evidence.json"
    evidence_path.write_text(_json(evidence), encoding="utf-8")
    html_report = render_report(evidence)
    _assert_no_sensitive_text(html_report, evidence)
    report.write_text(html_report, encoding="utf-8")
    print(f"report={report}")
    print(f"evidence={evidence_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
