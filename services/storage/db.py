from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workspace (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  root_path TEXT NOT NULL,
  llm_provider TEXT NOT NULL DEFAULT 'mock',
  privacy_mode TEXT NOT NULL DEFAULT 'local_first',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS document (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  path TEXT NOT NULL,
  kind TEXT NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidate_profile (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  target_roles TEXT NOT NULL DEFAULT '[]',
  target_locations TEXT NOT NULL DEFAULT '[]',
  target_language TEXT,
  background_summary TEXT,
  transition_goal TEXT,
  current_level TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS career_fact (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  source_file TEXT,
  source_quote TEXT,
  confidence REAL NOT NULL,
  user_verified INTEGER NOT NULL DEFAULT 0,
  visibility TEXT NOT NULL DEFAULT 'application_only',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_evidence (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  skill_name TEXT NOT NULL,
  category TEXT NOT NULL,
  evidence_type TEXT NOT NULL,
  evidence_ref TEXT,
  description TEXT NOT NULL,
  confidence REAL NOT NULL,
  target_role_relevance TEXT NOT NULL,
  user_verified INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tech_project (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  name TEXT NOT NULL,
  summary TEXT NOT NULL,
  tech_stack TEXT NOT NULL DEFAULT '[]',
  problem TEXT,
  implementation TEXT,
  technical_challenges TEXT,
  tradeoffs TEXT,
  user_contribution TEXT,
  demo_url TEXT,
  repo_url TEXT,
  readme_path TEXT,
  resume_bullets TEXT NOT NULL DEFAULT '[]',
  interview_questions TEXT NOT NULL DEFAULT '[]',
  verified INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  title TEXT NOT NULL,
  company TEXT,
  location TEXT,
  jd_raw TEXT NOT NULL,
  jd_summary TEXT NOT NULL,
  source_url TEXT,
  platform TEXT,
  import_method TEXT NOT NULL DEFAULT 'parse_jd',
  user_notes TEXT,
  parse_status TEXT NOT NULL DEFAULT 'parsed',
  is_current_target INTEGER NOT NULL DEFAULT 0,
  requirements_json TEXT NOT NULL,
  tech_stack TEXT NOT NULL DEFAULT '[]',
  seniority_guess TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS match_report (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  fit_label TEXT NOT NULL,
  fit_score_optional REAL,
  strengths TEXT NOT NULL DEFAULT '[]',
  gaps TEXT NOT NULL DEFAULT '[]',
  suggested_next_actions TEXT NOT NULL DEFAULT '[]',
  apply_recommendation TEXT NOT NULL,
  evidence_refs TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resume_version (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  job_id TEXT,
  title TEXT NOT NULL,
  content_markdown TEXT NOT NULL,
  source_fact_refs TEXT NOT NULL DEFAULT '[]',
  pending_confirmations TEXT NOT NULL DEFAULT '[]',
  export_pdf_path TEXT,
  export_docx_path TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS application_package (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  resume_version_id TEXT NOT NULL,
  project_description TEXT NOT NULL,
  recruiter_message TEXT NOT NULL,
  cover_letter TEXT,
  questions_to_confirm TEXT NOT NULL DEFAULT '[]',
  export_paths TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS application_record (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'preparing',
  next_action TEXT,
  next_action_due TEXT,
  application_package_id TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS story_card (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  title TEXT NOT NULL,
  applicable_questions TEXT NOT NULL DEFAULT '[]',
  source_fact_refs TEXT NOT NULL DEFAULT '[]',
  situation TEXT,
  task TEXT,
  action TEXT,
  result TEXT,
  short_version TEXT,
  medium_version TEXT,
  long_version TEXT,
  tags TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interview (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  application_record_id TEXT,
  type TEXT NOT NULL,
  scheduled_at TEXT,
  prep_pack TEXT NOT NULL DEFAULT '{}',
  questions TEXT NOT NULL DEFAULT '[]',
  notes TEXT,
  review TEXT,
  next_training_tasks TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS realtime_session (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  interview_id TEXT,
  mode TEXT NOT NULL,
  started_at TEXT NOT NULL,
  ended_at TEXT,
  save_policy TEXT NOT NULL,
  transcript_path TEXT,
  review_id TEXT
);

CREATE TABLE IF NOT EXISTS realtime_hint (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  question_text TEXT NOT NULL,
  question_type TEXT NOT NULL,
  recommended_project_id TEXT,
  recommended_story_id TEXT,
  hint_level TEXT NOT NULL,
  hint_content TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS training_task (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  priority TEXT NOT NULL DEFAULT 'medium',
  due_date TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_session (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_message (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  artifact_refs TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifact (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  source_table TEXT,
  source_id TEXT,
  status TEXT NOT NULL DEFAULT 'draft',
  current_version_id TEXT,
  content_json TEXT,
  content_path TEXT,
  source_refs TEXT NOT NULL DEFAULT '[]',
  questions_to_confirm TEXT NOT NULL DEFAULT '[]',
  created_by_tool TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tool_invocation (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  input_summary TEXT,
  output_refs TEXT NOT NULL DEFAULT '[]',
  error_code TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_invocation (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  provider_name TEXT NOT NULL,
  prompt_name TEXT NOT NULL,
  schema_name TEXT NOT NULL,
  input_summary TEXT NOT NULL DEFAULT '{}',
  redaction_applied INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL,
  error_code TEXT,
  latency_ms INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_chat_invocation (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  session_id TEXT,
  provider_name TEXT NOT NULL,
  model TEXT,
  consent_id TEXT,
  consent_scope TEXT,
  status TEXT NOT NULL,
  error_code TEXT,
  latency_ms INTEGER NOT NULL DEFAULT 0,
  token_estimate INTEGER NOT NULL DEFAULT 0,
  input_summary TEXT NOT NULL DEFAULT '{}',
  redaction_summary TEXT NOT NULL DEFAULT '{}',
  fallback_used INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifact_version (
  id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL,
  workspace_id TEXT NOT NULL,
  version_number INTEGER NOT NULL,
  status TEXT NOT NULL,
  content_json TEXT,
  content_path TEXT,
  source_refs TEXT NOT NULL DEFAULT '[]',
  questions_to_confirm TEXT NOT NULL DEFAULT '[]',
  change_reason TEXT NOT NULL,
  parent_version_id TEXT,
  created_by TEXT NOT NULL,
  created_by_tool TEXT,
  created_at TEXT NOT NULL
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.executescript(SCHEMA)
    migrate_p1_artifact_versions(conn)
    migrate_p6_provider_chat_invocations(conn)
    migrate_p8_job_intake(conn)
    migrate_p11_market_provider(conn)
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def migrate_p1_artifact_versions(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(artifact)").fetchall()}
    if "current_version_id" not in columns:
        conn.execute("ALTER TABLE artifact ADD COLUMN current_version_id TEXT")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS artifact_version (
          id TEXT PRIMARY KEY,
          artifact_id TEXT NOT NULL,
          workspace_id TEXT NOT NULL,
          version_number INTEGER NOT NULL,
          status TEXT NOT NULL,
          content_json TEXT,
          content_path TEXT,
          source_refs TEXT NOT NULL DEFAULT '[]',
          questions_to_confirm TEXT NOT NULL DEFAULT '[]',
          change_reason TEXT NOT NULL,
          parent_version_id TEXT,
          created_by TEXT NOT NULL,
          created_by_tool TEXT,
          created_at TEXT NOT NULL
        )
        """
    )
    artifacts = conn.execute("SELECT * FROM artifact WHERE current_version_id IS NULL").fetchall()
    for artifact in artifacts:
        existing = conn.execute(
            "SELECT * FROM artifact_version WHERE artifact_id=? ORDER BY version_number LIMIT 1",
            (artifact["id"],),
        ).fetchone()
        if existing:
            conn.execute("UPDATE artifact SET current_version_id=? WHERE id=?", (existing["id"], artifact["id"]))
            continue
        version_id = f"artver_{uuid4().hex}"
        conn.execute(
            """
            INSERT INTO artifact_version (
              id, artifact_id, workspace_id, version_number, status,
              content_json, content_path, source_refs, questions_to_confirm,
              change_reason, parent_version_id, created_by, created_by_tool, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                version_id,
                artifact["id"],
                artifact["workspace_id"],
                1,
                artifact["status"],
                artifact["content_json"],
                artifact["content_path"],
                artifact["source_refs"],
                artifact["questions_to_confirm"],
                "migration_v1",
                None,
                "migration",
                artifact["created_by_tool"],
                artifact["created_at"] or _now(),
            ),
        )
        conn.execute("UPDATE artifact SET current_version_id=? WHERE id=?", (version_id, artifact["id"]))


def migrate_p6_provider_chat_invocations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS provider_chat_invocation (
          id TEXT PRIMARY KEY,
          workspace_id TEXT NOT NULL,
          session_id TEXT,
          provider_name TEXT NOT NULL,
          model TEXT,
          consent_id TEXT,
          consent_scope TEXT,
          status TEXT NOT NULL,
          error_code TEXT,
          latency_ms INTEGER NOT NULL DEFAULT 0,
          token_estimate INTEGER NOT NULL DEFAULT 0,
          input_summary TEXT NOT NULL DEFAULT '{}',
          redaction_summary TEXT NOT NULL DEFAULT '{}',
          fallback_used INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        )
        """
    )


def migrate_p8_job_intake(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(job)").fetchall()}
    if "platform" not in columns:
        conn.execute("ALTER TABLE job ADD COLUMN platform TEXT")
    if "import_method" not in columns:
        conn.execute("ALTER TABLE job ADD COLUMN import_method TEXT NOT NULL DEFAULT 'parse_jd'")
    if "user_notes" not in columns:
        conn.execute("ALTER TABLE job ADD COLUMN user_notes TEXT")
    if "parse_status" not in columns:
        conn.execute("ALTER TABLE job ADD COLUMN parse_status TEXT NOT NULL DEFAULT 'parsed'")
    if "is_current_target" not in columns:
        conn.execute("ALTER TABLE job ADD COLUMN is_current_target INTEGER NOT NULL DEFAULT 0")


def migrate_p11_market_provider(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS job_market_providers (
          provider_id TEXT PRIMARY KEY,
          provider_name TEXT NOT NULL,
          provider_type TEXT NOT NULL,
          configured_state TEXT NOT NULL,
          requires_key INTEGER NOT NULL DEFAULT 0,
          rate_limit TEXT,
          license_note TEXT NOT NULL,
          last_checked_at TEXT,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS job_search_runs (
          run_id TEXT PRIMARY KEY,
          workspace_id TEXT NOT NULL,
          query TEXT NOT NULL,
          city_filters TEXT NOT NULL DEFAULT '[]',
          salary_range TEXT,
          tech_stack TEXT NOT NULL DEFAULT '[]',
          source_policy TEXT NOT NULL,
          provider_ids TEXT NOT NULL DEFAULT '[]',
          consent_id TEXT,
          started_at TEXT NOT NULL,
          completed_at TEXT,
          status TEXT NOT NULL,
          result_count INTEGER NOT NULL DEFAULT 0,
          source_refs TEXT NOT NULL DEFAULT '[]',
          boundary_note TEXT NOT NULL,
          error_code TEXT
        );

        CREATE TABLE IF NOT EXISTS normalized_job_posts (
          job_id TEXT PRIMARY KEY,
          workspace_id TEXT NOT NULL,
          run_id TEXT NOT NULL,
          title TEXT NOT NULL,
          company TEXT,
          city TEXT NOT NULL,
          salary_range TEXT,
          seniority TEXT,
          tech_stack TEXT NOT NULL DEFAULT '[]',
          source_url TEXT,
          source_type TEXT NOT NULL,
          fetched_at TEXT NOT NULL,
          confidence REAL NOT NULL,
          source_ref_id TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS job_market_snapshots (
          snapshot_id TEXT PRIMARY KEY,
          workspace_id TEXT NOT NULL,
          run_id TEXT NOT NULL,
          city_stats TEXT NOT NULL DEFAULT '[]',
          salary_histogram TEXT NOT NULL DEFAULT '[]',
          tech_heatmap TEXT NOT NULL DEFAULT '[]',
          source_breakdown TEXT NOT NULL DEFAULT '{}',
          remote_ratio REAL NOT NULL DEFAULT 0,
          competition_level TEXT NOT NULL,
          trend_summary TEXT NOT NULL,
          low_confidence_notes TEXT NOT NULL DEFAULT '[]',
          source_refs TEXT NOT NULL DEFAULT '[]',
          created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS region_source_refs (
          source_ref_id TEXT PRIMARY KEY,
          workspace_id TEXT NOT NULL,
          run_id TEXT NOT NULL,
          region_code TEXT NOT NULL,
          region_name TEXT NOT NULL,
          metric_name TEXT NOT NULL,
          source_type TEXT NOT NULL,
          source_ref_ids TEXT NOT NULL DEFAULT '[]',
          source_summary TEXT NOT NULL,
          source_url TEXT,
          confidence REAL NOT NULL,
          fetched_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS market_provider_invocation_logs (
          invocation_id TEXT PRIMARY KEY,
          workspace_id TEXT,
          provider_id TEXT NOT NULL,
          run_id TEXT,
          query_summary TEXT NOT NULL DEFAULT '{}',
          status TEXT NOT NULL,
          duration_ms INTEGER NOT NULL DEFAULT 0,
          error_code TEXT,
          redacted INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL
        );
        """
    )


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [row_to_dict(row) or {} for row in rows]


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)
