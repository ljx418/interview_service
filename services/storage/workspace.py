from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from services.config import load_project_dotenv
from services.storage.db import connect, row_to_dict


load_project_dotenv()

DEFAULT_WORKSPACE = ".jobpilot_workspace"
WORKSPACE_INDEX: dict[str, Path] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def workspace_root(root_path: str | None = None) -> Path:
    raw = root_path or os.environ.get("JOBPILOT_DEFAULT_WORKSPACE") or DEFAULT_WORKSPACE
    return Path(raw).expanduser().resolve()


def db_path(root: Path) -> Path:
    return root / "jobpilot.db"


def ensure_workspace_dirs(root: Path) -> None:
    for name in ["files", "exports", "transcripts", "vector_index"]:
        (root / name).mkdir(parents=True, exist_ok=True)


def init_workspace(
    name: str,
    root_path: str | None = None,
    llm_provider: str = "mock",
    privacy_mode: str = "local_first",
) -> dict:
    root = workspace_root(root_path)
    ensure_workspace_dirs(root)
    conn = connect(db_path(root))
    existing = conn.execute("SELECT * FROM workspace LIMIT 1").fetchone()
    stamp = now_iso()
    if existing:
        workspace = row_to_dict(existing) or {}
        conn.execute(
            "UPDATE workspace SET name=?, root_path=?, llm_provider=?, privacy_mode=?, updated_at=? WHERE id=?",
            (name, str(root), llm_provider, privacy_mode, stamp, workspace["id"]),
        )
        conn.commit()
        workspace.update({"name": name, "root_path": str(root), "llm_provider": llm_provider, "privacy_mode": privacy_mode})
        WORKSPACE_INDEX[workspace["id"]] = root
        return {**workspace, "created": False, "next_actions": ["上传简历", "添加项目 README", "粘贴目标岗位 JD"]}

    workspace_id = new_id("ws")
    conn.execute(
        "INSERT INTO workspace (id, name, root_path, llm_provider, privacy_mode, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (workspace_id, name, str(root), llm_provider, privacy_mode, stamp, stamp),
    )
    conn.commit()
    WORKSPACE_INDEX[workspace_id] = root
    return {
        "id": workspace_id,
        "workspace_id": workspace_id,
        "name": name,
        "root_path": str(root),
        "llm_provider": llm_provider,
        "privacy_mode": privacy_mode,
        "created": True,
        "next_actions": ["上传简历", "添加项目 README", "粘贴目标岗位 JD"],
    }


def get_workspace(root_path: str | None = None, workspace_id: str | None = None) -> dict:
    root = WORKSPACE_INDEX.get(workspace_id or "") if root_path is None else None
    root = root or workspace_root(root_path)
    conn = connect(db_path(root))
    row = conn.execute("SELECT * FROM workspace WHERE (? IS NULL OR id = ?) LIMIT 1", (workspace_id, workspace_id)).fetchone()
    workspace = row_to_dict(row)
    if not workspace:
        raise ValueError("Workspace not initialized. Call /api/workspace/init first.")
    return workspace


def workspace_conn(workspace_id: str, root_path: str | None = None):
    workspace = get_workspace(root_path=root_path, workspace_id=workspace_id)
    return connect(db_path(Path(workspace["root_path"]))), workspace


def safe_child(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if root not in candidate.parents and candidate != root:
        raise ValueError("Path is outside the current workspace.")
    return candidate


def delete_workspace(root_path: str | None = None) -> None:
    root = workspace_root(root_path)
    if root.exists():
        shutil.rmtree(root)
