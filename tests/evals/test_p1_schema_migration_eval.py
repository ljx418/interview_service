import sqlite3

from services.storage.db import connect


def test_artifact_version_schema_exists_on_empty_workspace(tmp_path):
    conn = connect(tmp_path / "workspace" / "jobpilot.db")

    artifact_columns = {row["name"] for row in conn.execute("PRAGMA table_info(artifact)").fetchall()}
    tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

    assert "current_version_id" in artifact_columns
    assert "artifact_version" in tables


def test_old_artifact_migrates_to_v1_idempotently(tmp_path):
    db_path = tmp_path / "legacy" / "jobpilot.db"
    db_path.parent.mkdir(parents=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE artifact (
          id TEXT PRIMARY KEY,
          workspace_id TEXT NOT NULL,
          artifact_type TEXT NOT NULL,
          source_table TEXT,
          source_id TEXT,
          status TEXT NOT NULL DEFAULT 'draft',
          content_json TEXT,
          content_path TEXT,
          source_refs TEXT NOT NULL DEFAULT '[]',
          questions_to_confirm TEXT NOT NULL DEFAULT '[]',
          created_by_tool TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT INTO artifact VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("art_legacy", "ws_1", "application_package", "application_package", "pkg_1", "needs_confirmation", '{"hello":"world"}', None, "[]", "[]", "test", "2026-01-01", "2026-01-01"),
    )
    conn.commit()
    conn.close()

    migrated = connect(db_path)
    current = migrated.execute("SELECT current_version_id FROM artifact WHERE id='art_legacy'").fetchone()["current_version_id"]
    versions = migrated.execute("SELECT * FROM artifact_version WHERE artifact_id='art_legacy'").fetchall()
    assert current
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1

    migrated.close()
    migrated_again = connect(db_path)
    versions_again = migrated_again.execute("SELECT * FROM artifact_version WHERE artifact_id='art_legacy'").fetchall()
    assert len(versions_again) == 1
