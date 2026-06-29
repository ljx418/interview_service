from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from services.llm.provider import provider_status
from services.storage.workspace import safe_child, workspace_conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _workspace_root(workspace_id: str) -> Path:
    _, workspace = workspace_conn(workspace_id)
    return Path(workspace["root_path"])


def workspace_backup(workspace_id: str, target: str | None = None) -> dict:
    root = _workspace_root(workspace_id)
    backup_root = safe_child(root, target or "backups")
    backup_root.mkdir(parents=True, exist_ok=True)
    manifest_path = safe_child(backup_root, f"backup_manifest_{uuid4().hex}.json")
    files = [path for path in root.rglob("*") if path.is_file() and ".jobpilot" not in path.parts]
    manifest = {
        "workspace_id": workspace_id,
        "created_at": _now(),
        "backup_type": "manifest_only",
        "file_count": len(files),
        "redaction_status": "metadata_only",
        "contains_file_contents": False,
        "root": str(root),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**manifest, "manifest_path": str(manifest_path)}


def workspace_cleanup_plan(workspace_id: str, rules: dict | None = None) -> dict:
    root = _workspace_root(workspace_id)
    rules = rules or {}
    include_exports = bool(rules.get("include_exports", True))
    candidates = []
    if include_exports:
        exports = safe_child(root, "exports")
        if exports.exists():
            for path in exports.rglob("*"):
                if path.is_file():
                    candidates.append({"path": str(path), "risk": "user_output", "action": "would_keep_until_confirmed"})
    return {
        "workspace_id": workspace_id,
        "dry_run": True,
        "affected_count": len(candidates),
        "affected_files": candidates,
        "confirmation_required": True,
        "message": "这是清理 dry-run；没有删除任何文件。",
    }


def workspace_migration_plan(workspace_id: str, target_version: str) -> dict:
    root = _workspace_root(workspace_id)
    return {
        "workspace_id": workspace_id,
        "target_version": target_version,
        "dry_run": True,
        "steps": [
            {"name": "检查 workspace schema", "action": "inspect_only"},
            {"name": "生成回滚说明", "action": "document_only"},
            {"name": "等待用户确认 apply", "action": "blocked_until_confirmed"},
        ],
        "rollback_notes": "当前只生成迁移计划；未修改数据库或文件。",
        "workspace_root": str(root),
        "confirmation_required": True,
    }


def diagnostics_report(workspace_id: str, include_provider: bool = True) -> dict:
    conn, workspace = workspace_conn(workspace_id)
    artifact_count = conn.execute("SELECT COUNT(*) AS count FROM artifact WHERE workspace_id=?", (workspace_id,)).fetchone()["count"]
    session_count = conn.execute("SELECT COUNT(*) AS count FROM chat_session WHERE workspace_id=?", (workspace_id,)).fetchone()["count"]
    provider = provider_status() if include_provider else {"provider": "not_included"}
    return {
        "workspace_id": workspace_id,
        "generated_at": _now(),
        "redaction_status": "metadata_only",
        "contains_api_key": False,
        "contains_full_profile": False,
        "contains_provider_raw_response": False,
        "workspace": {
            "privacy_mode": workspace["privacy_mode"],
            "llm_provider": workspace["llm_provider"],
            "root_path": workspace["root_path"],
        },
        "counts": {
            "artifacts": artifact_count,
            "chat_sessions": session_count,
        },
        "provider": {
            "provider": provider.get("provider"),
            "configured": provider.get("configured"),
            "external_calls_enabled": provider.get("external_calls_enabled"),
            "model": provider.get("model"),
            "api_key_redacted": True,
        },
    }
