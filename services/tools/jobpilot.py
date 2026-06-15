from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape
import zipfile

from services.storage.db import dumps, loads, row_to_dict, rows_to_dicts
from services.storage.workspace import new_id, now_iso, safe_child, workspace_conn
from services.tools.core import classify_question, compact_lines, detect_skills, extract_text_from_path, infer_project_name
from services.llm.contracts import (
    ApplicationPackageOutput,
    InterviewPrepOutput,
    InterviewReviewOutput,
    JobParseOutput,
    MatchReportOutput,
    ProfileExtractFactsOutput,
    RealtimeHintOutput,
    StoryCardOutput,
    validate_output,
)
from services.llm.provider import get_provider, normalize_provider_name


def _source_ref(source_type: str, source_id: str, field: str | None = None, quote: str | None = None, confidence: str = "medium") -> dict:
    return {"source_type": source_type, "source_id": source_id, "field": field, "quote": quote, "confidence": confidence}


def _confirmation(question: str, level: str = "warning", reason: str | None = None, source_refs: list[dict] | None = None) -> dict:
    return {"question": question, "confirmation_level": level, "reason": reason, "source_refs": source_refs or []}


def _write_artifact(
    conn,
    workspace_id: str,
    artifact_type: str,
    source_table: str | None,
    source_id: str | None,
    content: dict[str, Any],
    source_refs: list[dict] | None = None,
    questions_to_confirm: list[dict] | None = None,
    status: str = "needs_confirmation",
    created_by_tool: str | None = None,
    content_path: str | None = None,
) -> dict:
    artifact_id = new_id("art")
    stamp = now_iso()
    conn.execute(
        """
        INSERT INTO artifact (
          id, workspace_id, artifact_type, source_table, source_id, status,
          current_version_id, content_json, content_path, source_refs, questions_to_confirm,
          created_by_tool, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            artifact_id,
            workspace_id,
            artifact_type,
            source_table,
            source_id,
            status,
            None,
            dumps(content),
            content_path,
            dumps(source_refs or []),
            dumps(questions_to_confirm or []),
            created_by_tool,
            stamp,
            stamp,
        ),
    )
    version_id = _create_artifact_version(
        conn,
        workspace_id,
        artifact_id,
        content,
        source_refs or [],
        questions_to_confirm or [],
        status,
        "initial",
        None,
        "tool",
        created_by_tool,
        content_path,
    )
    conn.execute("UPDATE artifact SET current_version_id=? WHERE id=?", (version_id, artifact_id))
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "status": status,
        "current_version_id": version_id,
        "source_refs": source_refs or [],
        "questions_to_confirm": questions_to_confirm or [],
    }


def _log_tool(conn, workspace_id: str, tool_name: str, input_summary: str, output_refs: list[dict] | None = None, error_code: str | None = None) -> None:
    conn.execute(
        "INSERT INTO tool_invocation VALUES (?, ?, ?, ?, ?, ?, ?)",
        (new_id("tool"), workspace_id, tool_name, input_summary[:800], dumps(output_refs or []), error_code, now_iso()),
    )


def _next_artifact_version_number(conn, artifact_id: str) -> int:
    row = conn.execute("SELECT MAX(version_number) AS max_version FROM artifact_version WHERE artifact_id=?", (artifact_id,)).fetchone()
    return int((row["max_version"] if row else 0) or 0) + 1


def _create_artifact_version(
    conn,
    workspace_id: str,
    artifact_id: str,
    content: dict[str, Any],
    source_refs: list[dict],
    questions_to_confirm: list[dict],
    status: str,
    change_reason: str,
    parent_version_id: str | None,
    created_by: str,
    created_by_tool: str | None,
    content_path: str | None = None,
) -> str:
    version_id = new_id("artver")
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
            artifact_id,
            workspace_id,
            _next_artifact_version_number(conn, artifact_id),
            status,
            dumps(content),
            content_path,
            dumps(source_refs),
            dumps(questions_to_confirm),
            change_reason,
            parent_version_id,
            created_by,
            created_by_tool,
            now_iso(),
        ),
    )
    return version_id


def _workspace_provider_name(workspace: dict[str, Any]) -> str:
    return normalize_provider_name(workspace.get("llm_provider") or None)


def _provider_generate_if_enabled(
    workspace_id: str,
    workspace: dict[str, Any],
    prompt_name: str,
    input_payload: dict[str, Any],
    output_schema,
    fixture_output: dict[str, Any],
) -> dict[str, Any]:
    provider_name = _workspace_provider_name(workspace)
    if provider_name == "mock":
        return output_schema.model_validate(fixture_output).model_dump(mode="json")
    payload = {**input_payload}
    if provider_name == "fixture":
        payload["fixture_output"] = fixture_output
    return get_provider(provider_name).generate_structured(
        prompt_name,
        payload,
        output_schema,
        request_options={"workspace_id": workspace_id},
    )


def _has_blocking_confirmations(questions: list[dict] | list[str]) -> bool:
    for item in questions:
        if isinstance(item, dict) and item.get("confirmation_level") == "blocking":
            return True
    return False


def list_artifacts(workspace_id: str) -> list[dict]:
    conn, _ = workspace_conn(workspace_id)
    return rows_to_dicts(conn.execute("SELECT * FROM artifact WHERE workspace_id=? ORDER BY created_at", (workspace_id,)).fetchall())


def list_artifact_versions(workspace_id: str, artifact_id: str) -> list[dict]:
    conn, _ = workspace_conn(workspace_id)
    artifact = row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND id=?", (workspace_id, artifact_id)).fetchone())
    if not artifact:
        raise ValueError("Artifact not found.")
    return rows_to_dicts(conn.execute("SELECT * FROM artifact_version WHERE workspace_id=? AND artifact_id=? ORDER BY version_number", (workspace_id, artifact_id)).fetchall())


def get_artifact_version(workspace_id: str, artifact_id: str, version_id: str) -> dict:
    conn, _ = workspace_conn(workspace_id)
    version = row_to_dict(
        conn.execute(
            "SELECT * FROM artifact_version WHERE workspace_id=? AND artifact_id=? AND id=?",
            (workspace_id, artifact_id, version_id),
        ).fetchone()
    )
    if not version:
        raise ValueError("Artifact version not found.")
    return version


def restore_artifact_version(workspace_id: str, artifact_id: str, version_id: str) -> dict:
    conn, _ = workspace_conn(workspace_id)
    artifact = row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND id=?", (workspace_id, artifact_id)).fetchone())
    version = get_artifact_version(workspace_id, artifact_id, version_id)
    if not artifact:
        raise ValueError("Artifact not found.")
    conn.execute(
        """
        UPDATE artifact
        SET current_version_id=?, status=?, content_json=?, content_path=?, source_refs=?,
            questions_to_confirm=?, updated_at=?
        WHERE workspace_id=? AND id=?
        """,
        (
            version_id,
            version["status"],
            version["content_json"],
            version["content_path"],
            version["source_refs"],
            version["questions_to_confirm"],
            now_iso(),
            workspace_id,
            artifact_id,
        ),
    )
    _write_back_artifact_business_record(conn, workspace_id, artifact, loads(version["content_json"], {}))
    conn.commit()
    return row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND id=?", (workspace_id, artifact_id)).fetchone()) or {}


def confirm_artifact(workspace_id: str, artifact_id: str) -> dict:
    conn, _ = workspace_conn(workspace_id)
    row = row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND id=?", (workspace_id, artifact_id)).fetchone())
    if not row:
        raise ValueError("Artifact not found.")
    conn.execute("UPDATE artifact SET status='confirmed', updated_at=? WHERE workspace_id=? AND id=?", (now_iso(), workspace_id, artifact_id))
    conn.commit()
    row["status"] = "confirmed"
    return row


def update_artifact(workspace_id: str, artifact_id: str, content_json: dict[str, Any]) -> dict:
    conn, _ = workspace_conn(workspace_id)
    row = row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND id=?", (workspace_id, artifact_id)).fetchone())
    if not row:
        raise ValueError("Artifact not found.")
    parent_version_id = row.get("current_version_id")
    source_refs = loads(row.get("source_refs"), [])
    questions_to_confirm = loads(row.get("questions_to_confirm"), [])
    version_id = _create_artifact_version(
        conn,
        workspace_id,
        artifact_id,
        content_json,
        source_refs,
        questions_to_confirm,
        "needs_confirmation",
        "user_edit",
        parent_version_id,
        "user",
        row.get("created_by_tool"),
        row.get("content_path"),
    )
    conn.execute(
        "UPDATE artifact SET content_json=?, current_version_id=?, status='needs_confirmation', updated_at=? WHERE workspace_id=? AND id=?",
        (dumps(content_json), version_id, now_iso(), workspace_id, artifact_id),
    )
    _write_back_artifact_business_record(conn, workspace_id, row, content_json)
    conn.commit()
    row["content_json"] = dumps(content_json)
    row["current_version_id"] = version_id
    row["status"] = "needs_confirmation"
    return row


def _write_back_artifact_business_record(conn, workspace_id: str, artifact: dict[str, Any], content_json: dict[str, Any]) -> None:
    if artifact.get("source_table") == "application_package" and artifact.get("source_id"):
        package_id = artifact["source_id"]
        resume_version_id = content_json.get("resume_version_id")
        if content_json.get("project_description") or content_json.get("recruiter_message") or content_json.get("questions_to_confirm") is not None:
            conn.execute(
                """
                UPDATE application_package
                SET project_description=COALESCE(?, project_description),
                    recruiter_message=COALESCE(?, recruiter_message),
                    questions_to_confirm=COALESCE(?, questions_to_confirm)
                WHERE workspace_id=? AND id=?
                """,
                (
                    content_json.get("project_description"),
                    content_json.get("recruiter_message"),
                    dumps(content_json.get("questions_to_confirm")) if content_json.get("questions_to_confirm") is not None else None,
                    workspace_id,
                    package_id,
                ),
            )
        if resume_version_id and content_json.get("resume_markdown"):
            conn.execute(
                "UPDATE resume_version SET content_markdown=? WHERE workspace_id=? AND id=?",
                (content_json["resume_markdown"], workspace_id, resume_version_id),
            )


def regenerate_artifact(workspace_id: str, artifact_id: str, fail_for_test: bool = False) -> dict:
    conn, _ = workspace_conn(workspace_id)
    artifact = row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND id=?", (workspace_id, artifact_id)).fetchone())
    if not artifact:
        raise ValueError("Artifact not found.")
    parent_version_id = artifact.get("current_version_id")
    if not parent_version_id:
        raise ValueError("Artifact has no current version.")
    current = get_artifact_version(workspace_id, artifact_id, parent_version_id)
    current_content = loads(current["content_json"], {})
    if fail_for_test:
        _log_tool(conn, workspace_id, "artifact.regenerate", f"artifact_id={artifact_id}", [], "LLM_FAILED")
        conn.commit()
        raise ValueError("LLM_FAILED: regenerate failed before creating a new version.")

    regenerated = dict(current_content)
    regenerated["regenerated"] = True
    regenerated["regenerated_from_version_id"] = parent_version_id
    regenerated["regenerated_at"] = now_iso()
    if artifact.get("artifact_type") == "application_package" and regenerated.get("resume_markdown"):
        regenerated["resume_markdown"] = regenerated["resume_markdown"] + "\n\n<!-- regenerated draft: please review before export -->\n"

    source_refs = loads(current["source_refs"], [])
    questions_to_confirm = loads(current["questions_to_confirm"], [])
    version_id = _create_artifact_version(
        conn,
        workspace_id,
        artifact_id,
        regenerated,
        source_refs,
        questions_to_confirm,
        "needs_confirmation",
        "regenerate",
        parent_version_id,
        "tool",
        "artifact.regenerate",
        current["content_path"],
    )
    conn.execute(
        """
        UPDATE artifact
        SET current_version_id=?, content_json=?, status='needs_confirmation',
            source_refs=?, questions_to_confirm=?, updated_at=?
        WHERE workspace_id=? AND id=?
        """,
        (version_id, dumps(regenerated), dumps(source_refs), dumps(questions_to_confirm), now_iso(), workspace_id, artifact_id),
    )
    _write_back_artifact_business_record(conn, workspace_id, artifact, regenerated)
    _log_tool(conn, workspace_id, "artifact.regenerate", f"artifact_id={artifact_id} parent={parent_version_id}", [{"artifact_id": artifact_id, "version_id": version_id}])
    conn.commit()
    return row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND id=?", (workspace_id, artifact_id)).fetchone()) or {}


def create_chat_session(workspace_id: str, title: str = "JobPilot Chat") -> dict:
    conn, _ = workspace_conn(workspace_id)
    session_id = new_id("chat")
    stamp = now_iso()
    conn.execute("INSERT INTO chat_session VALUES (?, ?, ?, ?, ?)", (session_id, workspace_id, title, stamp, stamp))
    conn.commit()
    return {"session_id": session_id, "title": title}


def list_chat_sessions(workspace_id: str) -> list[dict]:
    conn, _ = workspace_conn(workspace_id)
    return rows_to_dicts(conn.execute("SELECT * FROM chat_session WHERE workspace_id=? ORDER BY updated_at DESC", (workspace_id,)).fetchall())


def get_chat_session(workspace_id: str, session_id: str) -> dict:
    conn, _ = workspace_conn(workspace_id)
    session = row_to_dict(conn.execute("SELECT * FROM chat_session WHERE workspace_id=? AND id=?", (workspace_id, session_id)).fetchone())
    if not session:
        raise ValueError("Chat session not found.")
    messages = rows_to_dicts(conn.execute("SELECT * FROM chat_message WHERE session_id=? ORDER BY created_at", (session_id,)).fetchall())
    artifacts = list_artifacts(workspace_id)
    return {"session": session, "messages": messages, "artifacts": artifacts}


def append_chat_message(conn, session_id: str | None, role: str, content: str, artifact_refs: list[dict] | None = None) -> None:
    if not session_id:
        return
    conn.execute("INSERT INTO chat_message VALUES (?, ?, ?, ?, ?, ?)", (new_id("msg"), session_id, role, content, dumps(artifact_refs or []), now_iso()))
    conn.execute("UPDATE chat_session SET updated_at=? WHERE id=?", (now_iso(), session_id))


def save_document(workspace_id: str, source_path: str, kind: str = "upload") -> dict:
    conn, workspace = workspace_conn(workspace_id)
    root = Path(workspace["root_path"])
    src = Path(source_path).expanduser().resolve()
    if not src.exists():
        raise ValueError(f"File not found: {source_path}")
    dest = safe_child(root, f"files/{src.name}")
    dest.write_bytes(src.read_bytes())
    text = extract_text_from_path(dest)
    doc_id = new_id("doc")
    conn.execute(
        "INSERT INTO document (id, workspace_id, filename, path, kind, text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, workspace_id, src.name, str(dest), kind, text, now_iso()),
    )
    source_refs = [_source_ref("document", doc_id, "text", text[:160], "high")]
    artifact_ref = _write_artifact(
        conn,
        workspace_id,
        "document",
        "document",
        doc_id,
        {"document_id": doc_id, "filename": src.name, "kind": kind, "text_preview": text[:600]},
        source_refs,
        [],
        "confirmed",
        "files.save_document",
        str(dest),
    )
    _log_tool(conn, workspace_id, "files.save_document", f"{kind}:{src.name}", [artifact_ref])
    conn.commit()
    return {"document_id": doc_id, "filename": src.name, "path": str(dest), "text_preview": text[:600], "next_tool": "profile.extract_facts", "artifact_ref": artifact_ref, "source_refs": source_refs}


def save_uploaded_bytes(workspace_id: str, filename: str, data: bytes, kind: str = "upload") -> dict:
    conn, workspace = workspace_conn(workspace_id)
    root = Path(workspace["root_path"])
    safe_name = Path(filename).name
    dest = safe_child(root, f"files/{safe_name}")
    dest.write_bytes(data)
    text = extract_text_from_path(dest)
    doc_id = new_id("doc")
    conn.execute(
        "INSERT INTO document (id, workspace_id, filename, path, kind, text, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (doc_id, workspace_id, safe_name, str(dest), kind, text, now_iso()),
    )
    source_refs = [_source_ref("document", doc_id, "text", text[:160], "high")]
    artifact_ref = _write_artifact(
        conn,
        workspace_id,
        "document",
        "document",
        doc_id,
        {"document_id": doc_id, "filename": safe_name, "kind": kind, "text_preview": text[:600]},
        source_refs,
        [],
        "confirmed",
        "files.upload",
        str(dest),
    )
    _log_tool(conn, workspace_id, "files.upload", f"{kind}:{safe_name}", [artifact_ref])
    conn.commit()
    return {"document_id": doc_id, "filename": safe_name, "path": str(dest), "text_preview": text[:600], "next_tool": "profile.extract_facts", "artifact_ref": artifact_ref, "source_refs": source_refs}


def extract_facts(workspace_id: str, document_ids: list[str] | None = None, target_roles: list[str] | None = None) -> dict:
    conn, workspace = workspace_conn(workspace_id)
    if document_ids:
        placeholders = ",".join("?" for _ in document_ids)
        docs = rows_to_dicts(conn.execute(f"SELECT * FROM document WHERE workspace_id=? AND id IN ({placeholders})", [workspace_id, *document_ids]).fetchall())
    else:
        docs = rows_to_dicts(conn.execute("SELECT * FROM document WHERE workspace_id=?", (workspace_id,)).fetchall())
    text = "\n".join(doc["text"] for doc in docs)
    skills = detect_skills(text)
    lines = compact_lines(text)
    stamp = now_iso()
    source_refs_for_docs = [_source_ref("document", doc["id"], "text", doc["text"][:160], "medium") for doc in docs]
    if _workspace_provider_name(workspace) != "mock":
        candidate_facts = []
        for skill in skills:
            candidate_facts.append(
                {
                    "id": new_id("fact"),
                    "type": "skill",
                    "title": skill,
                    "content": f"用户资料中出现 {skill}，可作为目标岗位的技能线索。",
                    "confidence": 0.78,
                    "needs_confirmation": False,
                    "source_refs": [_source_ref("document", docs[0]["id"], "text", skill, "medium")] if docs else [],
                }
            )
        for idx, line in enumerate(lines[:4]):
            candidate_facts.append(
                {
                    "id": new_id("fact"),
                    "type": "experience",
                    "title": "项目或经历线索" if idx else "背景摘要",
                    "content": line,
                    "confidence": 0.65,
                    "needs_confirmation": True,
                    "source_refs": [_source_ref("document", docs[0]["id"], "text", line[:160], "medium")] if docs else [],
                }
            )
        candidate_questions = [
            _confirmation("请确认项目是否已部署上线。", "warning", "部署状态会影响申请材料表述。", source_refs_for_docs),
            _confirmation("请补充可量化结果，例如性能、用户数、测试覆盖或交付周期。", "optional", "缺少数据时不能编造指标。", source_refs_for_docs),
            _confirmation("请确认每项技能是否由你本人实现过。", "blocking", "对外材料不能夸大本人贡献。", source_refs_for_docs),
        ]
        candidate_payload = {
            "facts": candidate_facts,
            "missing_info": [item["question"] for item in candidate_questions],
            "questions_to_confirm": candidate_questions,
            "target_roles": target_roles or [],
            "source_refs": source_refs_for_docs,
        }
        payload = _provider_generate_if_enabled(
            workspace_id,
            workspace,
            "profile_extract_facts",
            {"documents": [{"id": doc["id"], "filename": doc["filename"], "text": doc["text"]} for doc in docs], "target_roles": target_roles or []},
            ProfileExtractFactsOutput,
            candidate_payload,
        )
        fact_rows = payload["facts"]
        for fact in fact_rows:
            conn.execute(
                "INSERT INTO career_fact VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    fact["id"],
                    workspace_id,
                    fact["type"],
                    fact["title"],
                    fact["content"],
                    docs[0]["filename"] if docs else None,
                    (fact.get("source_refs") or [{}])[0].get("quote") if fact.get("source_refs") else fact["content"][:160],
                    float(fact["confidence"]),
                    0,
                    "application_only",
                    stamp,
                    stamp,
                ),
            )
        build_skill_evidence(workspace_id, [fact["title"] for fact in fact_rows if fact["type"] == "skill"])
        questions_to_confirm = payload["questions_to_confirm"]
        artifact_ref = _write_artifact(
            conn,
            workspace_id,
            "career_facts",
            "career_fact",
            fact_rows[0]["id"] if fact_rows else None,
            {"facts": fact_rows, "target_roles": target_roles or []},
            payload.get("source_refs") or [ref for fact in fact_rows for ref in fact.get("source_refs", [])],
            questions_to_confirm,
            "needs_confirmation",
            "profile.extract_facts",
        )
        _log_tool(conn, workspace_id, "profile.extract_facts", f"documents={len(docs)} roles={target_roles or []}", [artifact_ref])
        conn.commit()
        return {"facts": fact_rows, "missing_info": payload["missing_info"], "questions_to_confirm": questions_to_confirm, "target_roles": target_roles or [], "artifact_ref": artifact_ref}
    fact_rows = []
    for skill in skills:
        fact_id = new_id("fact")
        content = f"用户资料中出现 {skill}，可作为目标岗位的技能线索。"
        conn.execute(
            "INSERT INTO career_fact VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (fact_id, workspace_id, "skill", skill, content, docs[0]["filename"] if docs else None, skill, 0.78, 0, "application_only", stamp, stamp),
        )
        source_refs = [_source_ref("document", docs[0]["id"], "text", skill, "medium")] if docs else []
        fact_rows.append({"id": fact_id, "type": "skill", "title": skill, "content": content, "confidence": 0.78, "needs_confirmation": False, "source_refs": source_refs})
    for idx, line in enumerate(lines[:4]):
        fact_id = new_id("fact")
        title = "项目或经历线索" if idx else "背景摘要"
        conn.execute(
            "INSERT INTO career_fact VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (fact_id, workspace_id, "experience", title, line, docs[0]["filename"] if docs else None, line[:160], 0.65, 0, "application_only", stamp, stamp),
        )
        source_refs = [_source_ref("document", docs[0]["id"], "text", line[:160], "medium")] if docs else []
        fact_rows.append({"id": fact_id, "type": "experience", "title": title, "content": line, "confidence": 0.65, "needs_confirmation": True, "source_refs": source_refs})
    missing_info = ["请确认项目是否已部署上线。", "请补充可量化结果，例如性能、用户数、测试覆盖或交付周期。", "请确认每项技能是否由你本人实现过。"]
    questions_to_confirm = [
        _confirmation("请确认项目是否已部署上线。", "warning", "部署状态会影响申请材料表述。"),
        _confirmation("请补充可量化结果，例如性能、用户数、测试覆盖或交付周期。", "optional", "缺少数据时不能编造指标。"),
        _confirmation("请确认每项技能是否由你本人实现过。", "blocking", "对外材料不能夸大本人贡献。"),
    ]
    build_skill_evidence(workspace_id, skills)
    artifact_ref = _write_artifact(
        conn,
        workspace_id,
        "career_facts",
        "career_fact",
        fact_rows[0]["id"] if fact_rows else None,
        {"facts": fact_rows, "target_roles": target_roles or []},
        [ref for fact in fact_rows for ref in fact.get("source_refs", [])],
        questions_to_confirm,
        "needs_confirmation",
        "profile.extract_facts",
    )
    _log_tool(conn, workspace_id, "profile.extract_facts", f"documents={len(docs)} roles={target_roles or []}", [artifact_ref])
    conn.commit()
    return {"facts": fact_rows, "missing_info": missing_info, "questions_to_confirm": questions_to_confirm, "target_roles": target_roles or [], "artifact_ref": artifact_ref}


def list_facts(workspace_id: str) -> list[dict]:
    conn, _ = workspace_conn(workspace_id)
    return rows_to_dicts(conn.execute("SELECT * FROM career_fact WHERE workspace_id=? ORDER BY created_at", (workspace_id,)).fetchall())


def update_fact(workspace_id: str, fact_id: str, updates: dict[str, Any]) -> dict:
    allowed = {"title", "content", "confidence", "user_verified", "visibility"}
    pairs = [(key, updates[key]) for key in updates if key in allowed]
    if not pairs:
        raise ValueError("No supported fact fields to update.")
    conn, _ = workspace_conn(workspace_id)
    assignments = ", ".join(f"{key}=?" for key, _ in pairs)
    conn.execute(f"UPDATE career_fact SET {assignments}, updated_at=? WHERE workspace_id=? AND id=?", [*[value for _, value in pairs], now_iso(), workspace_id, fact_id])
    conn.commit()
    row = conn.execute("SELECT * FROM career_fact WHERE workspace_id=? AND id=?", (workspace_id, fact_id)).fetchone()
    return row_to_dict(row) or {}


def build_skill_evidence(workspace_id: str, skill_names: list[str] | None = None) -> dict:
    conn, _ = workspace_conn(workspace_id)
    if not skill_names:
        facts = rows_to_dicts(conn.execute("SELECT title FROM career_fact WHERE workspace_id=? AND type='skill'", (workspace_id,)).fetchall())
        skill_names = [fact["title"] for fact in facts]
    created = []
    for skill in dict.fromkeys(skill_names):
        exists = conn.execute("SELECT id FROM skill_evidence WHERE workspace_id=? AND skill_name=?", (workspace_id, skill)).fetchone()
        if exists:
            continue
        item_id = new_id("skill")
        description = f"{skill} 在用户资料中出现，需要通过项目 README、代码链接或面试故事进一步确认。"
        conn.execute(
            "INSERT INTO skill_evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (item_id, workspace_id, skill, "frontend" if skill in {"React", "TypeScript", "JavaScript", "HTML/CSS"} else "general", "project", None, description, 0.7, "usable", 0, now_iso()),
        )
        created.append({"id": item_id, "skill": skill, "evidence": description, "strength": "usable", "suggested_improvement": "补充具体实现、截图、部署链接或测试说明。"})
    return {"skill_evidence": created}


def create_project_card(workspace_id: str, project_name: str | None = None, source_document_ids: list[str] | None = None, target_role: str | None = None) -> dict:
    conn, _ = workspace_conn(workspace_id)
    docs = []
    if source_document_ids:
        placeholders = ",".join("?" for _ in source_document_ids)
        docs = rows_to_dicts(conn.execute(f"SELECT * FROM document WHERE workspace_id=? AND id IN ({placeholders})", [workspace_id, *source_document_ids]).fetchall())
    if not docs:
        docs = rows_to_dicts(conn.execute("SELECT * FROM document WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchall())
    text = "\n".join(doc["text"] for doc in docs)
    skills = detect_skills(text)
    name = project_name or infer_project_name(text, "TodoPlus")
    project_id = new_id("proj")
    summary = f"{name} 是一个可用于展示 {', '.join(skills[:4]) or 'Web 开发'} 能力的技术项目。"
    bullets = [
        f"基于 {', '.join(skills[:3]) or 'Web 技术'} 实现核心功能，并整理为可复用项目经验。",
        "围绕组件拆分、数据流、接口调用和用户体验描述个人贡献。",
        "补充部署、测试或性能指标后，可进一步增强简历可信度。",
    ]
    questions = ["讲一下这个项目的整体架构。", "你在项目中解决过哪个技术难点？", "如果重做一次，你会做哪些取舍？"]
    conn.execute(
        "INSERT INTO tech_project VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (project_id, workspace_id, name, summary, dumps(skills), "转行求职项目需要证明可交付能力。", text[:1200], "需要用户补充最难的一处实现。", "需要用户确认关键技术取舍。", "需要用户确认本人负责范围。", None, None, docs[0]["path"] if docs else None, dumps(bullets), dumps(questions), 0, now_iso(), now_iso()),
    )
    source_refs = [_source_ref("document", doc["id"], "text", doc["text"][:160], "medium") for doc in docs]
    questions_to_confirm = [
        _confirmation("请确认本人负责范围。", "blocking", "项目卡会进入对外申请材料。", source_refs),
        _confirmation("请确认最难的一处实现和关键技术取舍。", "warning", "面试故事需要真实细节。", source_refs),
    ]
    payload = {"project_id": project_id, "summary": summary, "tech_stack": skills, "resume_bullets": bullets, "interview_questions": questions}
    artifact_ref = _write_artifact(conn, workspace_id, "tech_project", "tech_project", project_id, payload, source_refs, questions_to_confirm, "needs_confirmation", "project.create_card")
    _log_tool(conn, workspace_id, "project.create_card", f"name={name} target_role={target_role}", [artifact_ref])
    conn.commit()
    return {**payload, "improvements": ["补充部署链接", "补充测试说明", "补充本人负责部分和结果指标"], "source_refs": source_refs, "questions_to_confirm": questions_to_confirm, "artifact_ref": artifact_ref}


def parse_jd(workspace_id: str, jd_text: str, source_url: str | None = None) -> dict:
    conn, workspace = workspace_conn(workspace_id)
    skills = detect_skills(jd_text)
    lower = jd_text.lower()
    title = "Junior Frontend Developer" if "front" in lower or "react" in lower else "Junior Developer"
    company = "Unknown"
    for line in compact_lines(jd_text, 12):
        if line.lower().startswith("company:"):
            company = line.split(":", 1)[1].strip()
        if line.lower().startswith("title:"):
            title = line.split(":", 1)[1].strip()
    must_section = []
    nice_section = []
    current_section: str | None = None
    for line in jd_text.splitlines():
        normalized = line.strip().lower()
        if "must have" in normalized or "requirements" in normalized:
            current_section = "must"
            continue
        if "nice to have" in normalized or "preferred" in normalized:
            current_section = "nice"
            continue
        if normalized.startswith("##") and current_section:
            current_section = None
        if current_section == "must":
            must_section.append(line)
        if current_section == "nice":
            nice_section.append(line)
    section_must = detect_skills("\n".join(must_section))
    section_nice = detect_skills("\n".join(nice_section))
    must = section_must or skills[:4] or ["JavaScript", "API", "Git"]
    nice = section_nice or [skill for skill in ["TypeScript", "Testing", "SQL"] if skill not in must]
    responsibilities = compact_lines(jd_text, 5) or ["Build product features", "Collaborate with the team", "Work with APIs"]
    seniority = "junior" if any(word in lower for word in ["junior", "entry", "初级", "入门"]) else "unknown"
    job_id = new_id("job")
    summary = f"{title} 岗位重点关注 {', '.join(must)}。"
    requirements = {"must_have": must, "nice_to_have": nice, "responsibilities": responsibilities}
    source_refs = [_source_ref("job", job_id, "jd_raw", jd_text[:160], "high")]
    questions_to_confirm = [_confirmation("请确认公司、地点和岗位级别是否与原 JD 一致。", "warning", "JD 文本可能缺少结构化公司信息。", source_refs)]
    candidate_payload = {
        "job_id": job_id,
        "title": title,
        "company": company,
        "requirements": requirements,
        "responsibilities": responsibilities,
        "tech_stack": skills,
        "seniority_guess": seniority,
        "source_refs": source_refs,
        "questions_to_confirm": questions_to_confirm,
    }
    payload = _provider_generate_if_enabled(
        workspace_id,
        workspace,
        "job_parse_jd",
        {
            "job_id": job_id,
            "jd_text": jd_text,
            "source_url": source_url,
            "detected_skills": skills,
            "candidate_title": title,
        },
        JobParseOutput,
        candidate_payload,
    )
    job_id = payload["job_id"]
    title = payload["title"]
    company = payload.get("company") or company
    requirements = payload["requirements"]
    responsibilities = payload["responsibilities"]
    skills = payload["tech_stack"]
    seniority = payload["seniority_guess"]
    summary = f"{title} 岗位重点关注 {', '.join(requirements.get('must_have', skills[:4]) or skills[:4])}。"
    source_refs = payload.get("source_refs") or source_refs
    questions_to_confirm = payload.get("questions_to_confirm") or questions_to_confirm
    conn.execute(
        "INSERT INTO job VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (job_id, workspace_id, title, company, None, jd_text, summary, source_url, dumps(requirements), dumps(skills), seniority, now_iso()),
    )
    artifact_ref = _write_artifact(conn, workspace_id, "job_parse", "job", job_id, payload, source_refs, questions_to_confirm, "needs_confirmation", "job.parse_jd")
    _log_tool(conn, workspace_id, "job.parse_jd", f"title={title} chars={len(jd_text)}", [artifact_ref])
    conn.commit()
    return {**payload, "artifact_ref": artifact_ref}


def match_profile(workspace_id: str, job_id: str) -> dict:
    conn, workspace = workspace_conn(workspace_id)
    job = row_to_dict(conn.execute("SELECT * FROM job WHERE workspace_id=? AND id=?", (workspace_id, job_id)).fetchone())
    if not job:
        raise ValueError("Job not found.")
    req = loads(job["requirements_json"], {})
    must = req.get("must_have", [])
    evidence = rows_to_dicts(conn.execute("SELECT * FROM skill_evidence WHERE workspace_id=?", (workspace_id,)).fetchall())
    evidence_skills = {item["skill_name"] for item in evidence}
    matched = [skill for skill in must if skill in evidence_skills]
    gaps = [skill for skill in must if skill not in evidence_skills]
    ratio = len(matched) / max(len(must), 1)
    fit_label = "good" if ratio >= 0.6 else "maybe" if ratio >= 0.3 else "not_now"
    cn_label = {"good": "比较适合", "maybe": "可以尝试", "not_now": "先补强再投"}[fit_label]
    strengths = [f"已有 {skill} 相关证据" for skill in matched] or ["已有项目资料，可先整理成面试表达。"]
    gap_text = [f"{skill} 证据较弱，建议补充项目或 README 说明" for skill in gaps]
    actions = ["优化项目描述并突出与 JD 相关的技能", "准备一个 90 秒自我介绍", "准备一个项目深挖故事卡"]
    report_id = new_id("match")
    source_refs = [_source_ref("job", job_id, "requirements_json", None, "high")] + [
        _source_ref("skill_evidence", item["id"], "description", item["description"][:160], "medium") for item in evidence if item["skill_name"] in matched
    ]
    questions_to_confirm = [
        _confirmation("请确认匹配报告中的强项是否都有真实项目或经历支撑。", "warning", "缺少证据的强项不能进入申请材料。", source_refs)
    ]
    candidate_payload = {
        "match_report_id": report_id,
        "fit_label": cn_label,
        "fit_score_optional": ratio,
        "strengths": strengths,
        "gaps": gap_text,
        "next_actions": actions,
        "apply_recommendation": f"{cn_label}，投递前先优化项目描述和待确认事实。",
        "source_refs": source_refs,
        "questions_to_confirm": questions_to_confirm,
    }
    payload = _provider_generate_if_enabled(
        workspace_id,
        workspace,
        "job_match_profile",
        {"job": job, "requirements": req, "skill_evidence": evidence, "candidate_output": candidate_payload},
        MatchReportOutput,
        candidate_payload,
    )
    report_id = payload["match_report_id"]
    cn_label = payload["fit_label"]
    ratio = payload["fit_score_optional"]
    strengths = payload["strengths"]
    gap_text = payload["gaps"]
    actions = payload["next_actions"]
    source_refs = payload.get("source_refs") or source_refs
    questions_to_confirm = payload.get("questions_to_confirm") or questions_to_confirm
    conn.execute(
        "INSERT INTO match_report VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (report_id, workspace_id, job_id, fit_label, ratio, dumps(strengths), dumps(gap_text), dumps(actions), payload["apply_recommendation"], dumps([item["id"] for item in evidence if item["skill_name"] in matched]), now_iso()),
    )
    artifact_ref = _write_artifact(conn, workspace_id, "match_report", "match_report", report_id, payload, source_refs, questions_to_confirm, "needs_confirmation", "job.match_profile")
    _log_tool(conn, workspace_id, "job.match_profile", f"job_id={job_id}", [artifact_ref])
    conn.commit()
    return {**payload, "artifact_ref": artifact_ref}


def create_application_package(workspace_id: str, job_id: str, style: str = "junior_developer", language: str = "zh-CN") -> dict:
    conn, workspace = workspace_conn(workspace_id)
    job = row_to_dict(conn.execute("SELECT * FROM job WHERE workspace_id=? AND id=?", (workspace_id, job_id)).fetchone())
    if not job:
        raise ValueError("Job not found.")
    facts = rows_to_dicts(conn.execute("SELECT * FROM career_fact WHERE workspace_id=? ORDER BY created_at LIMIT 12", (workspace_id,)).fetchall())
    projects = rows_to_dicts(conn.execute("SELECT * FROM tech_project WHERE workspace_id=? ORDER BY created_at LIMIT 3", (workspace_id,)).fetchall())
    fact_lines = "\n".join(f"- {fact['title']}: {fact['content']}" for fact in facts[:8]) or "- 需要先导入简历和项目资料。"
    project_lines = "\n".join(f"- {proj['name']}: {proj['summary']}" for proj in projects) or "- 需要补充项目卡。"
    source_refs = [_source_ref("career_fact", fact["id"], "content", fact["content"][:160], "medium") for fact in facts] + [
        _source_ref("tech_project", proj["id"], "summary", proj["summary"][:160], "medium") for proj in projects
    ] + [_source_ref("job", job_id, "jd_summary", job["jd_summary"][:160], "high")]
    confirmations = [
        _confirmation("请确认所有项目均由你本人完成或明确说明协作部分。", "warning", "对外材料需要准确描述个人贡献。", source_refs),
        _confirmation("请补充可量化结果；没有数据时不要编造。", "optional", "指标缺失不会阻塞 Markdown 导出，但必须保留提醒。", source_refs),
    ]
    resume_md = f"""# 定制简历草稿 - {job['title']}

## 目标岗位
{job['title']} / {job.get('company') or 'Unknown'}

## 求职摘要
面向转行程序员的初级开发岗位，重点突出真实项目、可验证技能和持续学习能力。

## 技能与证据
{fact_lines}

## 项目经历
{project_lines}

## 待确认
{chr(10).join(f"- {item['question']}（{item['confirmation_level']}）" for item in confirmations)}
"""
    resume_id = new_id("resume")
    package_id = new_id("pkg")
    project_description = project_lines
    recruiter_message = f"你好，我正在申请 {job['title']}。我有与岗位相关的项目练习和持续学习经历，已整理好项目说明，期待有机会进一步沟通。"
    candidate_payload = {
        "package_id": package_id,
        "resume_version_id": resume_id,
        "resume_markdown": resume_md,
        "project_description": project_description,
        "recruiter_message": recruiter_message,
        "questions_to_confirm": confirmations,
        "source_refs": source_refs,
    }
    payload = _provider_generate_if_enabled(
        workspace_id,
        workspace,
        "application_create_package",
        {
            "package_id": package_id,
            "resume_version_id": resume_id,
            "job": job,
            "facts": facts,
            "projects": projects,
            "style": style,
            "language": language,
            "candidate_output": candidate_payload,
        },
        ApplicationPackageOutput,
        candidate_payload,
    )
    package_id = payload["package_id"]
    resume_id = payload["resume_version_id"]
    resume_md = payload["resume_markdown"]
    project_description = payload["project_description"]
    recruiter_message = payload["recruiter_message"]
    confirmations = payload["questions_to_confirm"]
    source_refs = payload["source_refs"]
    conn.execute(
        "INSERT INTO resume_version VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (resume_id, workspace_id, job_id, f"{job['title']} resume draft", resume_md, dumps([fact["id"] for fact in facts]), dumps(confirmations), None, None, now_iso()),
    )
    conn.execute(
        "INSERT INTO application_package VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (package_id, workspace_id, job_id, resume_id, project_description, recruiter_message, None, dumps(confirmations), dumps([]), now_iso()),
    )
    conn.execute(
        "INSERT INTO application_record VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (new_id("apprec"), workspace_id, job_id, "preparing", "确认申请包事实并导出 Markdown", None, package_id, None, now_iso(), now_iso()),
    )
    artifact_ref = _write_artifact(conn, workspace_id, "application_package", "application_package", package_id, payload, source_refs, confirmations, "needs_confirmation", "application.create_package")
    _log_tool(conn, workspace_id, "application.create_package", f"job_id={job_id} style={style} language={language}", [artifact_ref])
    conn.commit()
    return {**payload, "artifact_ref": artifact_ref, "source_fact_refs": [fact["id"] for fact in facts]}


def _confirmation_notes(questions: list[dict], level: str | None = None) -> list[str]:
    notes = []
    for item in questions:
        if not isinstance(item, dict):
            continue
        if level and item.get("confirmation_level") != level:
            continue
        notes.append(f"[{item.get('confirmation_level', 'warning')}] {item.get('question', '')}")
    return notes


def _render_export_markdown(content: dict[str, Any], questions: list[dict]) -> str:
    markdown = content.get("resume_markdown") or ""
    warnings = _confirmation_notes(questions, "warning")
    optionals = _confirmation_notes(questions, "optional")
    if warnings or optionals:
        markdown += "\n\n## 导出前仍需注意\n"
        for note in [*warnings, *optionals]:
            markdown += f"- {note}\n"
    return markdown


def _write_docx(path: Path, title: str, markdown: str) -> None:
    lines = [line.strip() for line in markdown.splitlines()]
    paragraphs = []
    for line in lines:
        if not line:
            paragraphs.append("<w:p/>")
            continue
        text = escape(line.lstrip("# ").strip())
        style = ""
        if line.startswith("#"):
            style = '<w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
        paragraphs.append(f"<w:p>{style}<w:r><w:t>{text}</w:t></w:r></w:p>")
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(paragraphs)}<w:sectPr/></w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml)


def export_application_package(workspace_id: str, package_id: str, formats: list[str] | None = None, artifact_version_id: str | None = None) -> dict:
    formats = formats or ["markdown"]
    conn, workspace = workspace_conn(workspace_id)
    root = Path(workspace["root_path"])
    package = row_to_dict(conn.execute("SELECT * FROM application_package WHERE workspace_id=? AND id=?", (workspace_id, package_id)).fetchone())
    if not package:
        raise ValueError("Application package not found.")
    artifact = row_to_dict(conn.execute("SELECT * FROM artifact WHERE workspace_id=? AND source_table='application_package' AND source_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id, package_id)).fetchone())
    if not artifact:
        raise ValueError("EXPORT_PRECHECK_FAILED: Application package artifact not found.")
    version_id = artifact_version_id or artifact["current_version_id"]
    if not version_id:
        raise ValueError("EXPORT_PRECHECK_FAILED: Application package has no current artifact version.")
    version = get_artifact_version(workspace_id, artifact["id"], version_id)
    content = loads(version["content_json"], {})
    questions_to_confirm = loads(version["questions_to_confirm"], [])
    source_refs = loads(version["source_refs"], [])
    if not source_refs:
        raise ValueError("EXPORT_PRECHECK_FAILED: Application package has no source refs.")
    if _has_blocking_confirmations(questions_to_confirm):
        raise ValueError("EXPORT_PRECHECK_FAILED: Application package has blocking confirmations. Confirm or edit it before export.")
    markdown = _render_export_markdown(content, questions_to_confirm)
    exports = []
    if "markdown" in formats:
        path = safe_child(root, f"exports/{package_id}_resume.md")
        path.write_text(markdown, encoding="utf-8")
        exports.append({"format": "markdown", "path": str(path)})
    if "pdf" in formats:
        path = safe_child(root, f"exports/{package_id}_resume.pdf")
        path.write_text("P1 lightweight PDF text fallback. DOCX is the formal P1 rich export.\n\n" + markdown, encoding="utf-8")
        exports.append({"format": "pdf", "path": str(path)})
    if "docx" in formats:
        path = safe_child(root, f"exports/{package_id}_resume.docx")
        _write_docx(path, f"{package_id} resume", markdown)
        exports.append({"format": "docx", "path": str(path)})
    conn.execute("UPDATE application_package SET export_paths=? WHERE id=?", (dumps(exports), package_id))
    if artifact:
        conn.execute("UPDATE artifact SET status='exported', content_path=?, updated_at=? WHERE id=?", (exports[0]["path"] if exports else None, now_iso(), artifact["id"]))
    _log_tool(conn, workspace_id, "application.export_package", f"package_id={package_id} formats={formats}", [{"artifact_id": artifact["id"], "artifact_type": "application_package"}] if artifact else [])
    conn.commit()
    return {"exports": exports, "questions_to_confirm": questions_to_confirm, "artifact_ref": {"artifact_id": artifact["id"], "status": "exported"} if artifact else None}


def prepare_interview(workspace_id: str, job_id: str, package_id: str | None = None, interview_type: str = "mixed") -> dict:
    conn, workspace = workspace_conn(workspace_id)
    job = row_to_dict(conn.execute("SELECT * FROM job WHERE workspace_id=? AND id=?", (workspace_id, job_id)).fetchone())
    projects = rows_to_dicts(conn.execute("SELECT * FROM tech_project WHERE workspace_id=? LIMIT 3", (workspace_id,)).fetchall())
    focus = ["90 秒自我介绍", "转行动机", "项目深挖", "技术基础", "反问问题"]
    questions = [
        "请用 90 秒介绍你自己和转行目标。",
        f"为什么你适合 {job['title'] if job else '这个岗位'}？",
        "讲一个你解决技术难题的经历。",
        "你如何验证项目功能是可靠的？",
        "你希望这个岗位前三个月达成什么目标？",
    ]
    if _workspace_provider_name(workspace) != "mock":
        interview_id = new_id("int")
        source_refs = [_source_ref("job", job_id, "jd_summary", job["jd_summary"][:160], "high")] if job else []
        source_refs.extend([_source_ref("tech_project", proj["id"], "summary", proj["summary"][:160], "medium") for proj in projects])
        candidate_story_cards = [
            {
                "id": new_id("story"),
                "title": f"{project['name']} 技术难题故事",
                "applicable_questions": ["讲一个你解决技术难题的经历"],
                "short_version": f"围绕 {project['name']} 讲问题、实现、取舍和结果。",
                "medium_version": f"{project['name']} 可以用来说明项目拆解、实现过程和待确认结果。",
                "long_version": f"项目背景：{project['summary']}\n行动：说明本人贡献。\n结果：补充真实指标。",
                "source_refs": [_source_ref("tech_project", project["id"], "summary", project["summary"][:160], "medium")],
            }
            for project in projects
        ]
        candidate_payload = {
            "prep_pack_id": interview_id,
            "focus_areas": focus,
            "questions": questions,
            "reverse_questions": ["团队如何评估初级工程师的成长？", "这个岗位前三个月最重要的交付是什么？"],
            "story_cards": candidate_story_cards,
            "source_refs": source_refs,
            "questions_to_confirm": [],
        }
        payload = _provider_generate_if_enabled(
            workspace_id,
            workspace,
            "interview_prepare",
            {"job": job, "projects": projects, "package_id": package_id, "interview_type": interview_type},
            InterviewPrepOutput,
            candidate_payload,
        )
        prep = {
            "focus_areas": payload["focus_areas"],
            "questions": payload["questions"],
            "reverse_questions": payload["reverse_questions"],
            "story_cards": payload["story_cards"],
        }
        interview_id = payload["prep_pack_id"]
        source_refs = payload.get("source_refs") or source_refs
        conn.execute(
            "INSERT INTO interview VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (interview_id, workspace_id, None, interview_type, None, dumps(prep), dumps(payload["questions"]), None, None, dumps([]), now_iso(), now_iso()),
        )
        artifact_ref = _write_artifact(conn, workspace_id, "interview_prep", "interview", interview_id, prep, source_refs, payload.get("questions_to_confirm", []), "needs_confirmation", "interview.prepare")
        _log_tool(conn, workspace_id, "interview.prepare", f"job_id={job_id} package_id={package_id} type={interview_type}", [artifact_ref])
        conn.commit()
        return {"prep_pack_id": interview_id, **prep, "source_refs": source_refs, "artifact_ref": artifact_ref}
    story_cards = create_story_cards(workspace_id, [proj["id"] for proj in projects], job_id)
    prep = {"focus_areas": focus, "questions": questions, "reverse_questions": ["团队如何评估初级工程师的成长？", "这个岗位前三个月最重要的交付是什么？"], "story_cards": story_cards["story_cards"]}
    interview_id = new_id("int")
    conn.execute(
        "INSERT INTO interview VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (interview_id, workspace_id, None, interview_type, None, dumps(prep), dumps(questions), None, None, dumps([]), now_iso(), now_iso()),
    )
    source_refs = [_source_ref("job", job_id, "jd_summary", job["jd_summary"][:160], "high")] if job else []
    source_refs.extend([ref for card in story_cards["story_cards"] for ref in card.get("source_refs", [])])
    artifact_ref = _write_artifact(conn, workspace_id, "interview_prep", "interview", interview_id, prep, source_refs, [], "needs_confirmation", "interview.prepare")
    _log_tool(conn, workspace_id, "interview.prepare", f"job_id={job_id} package_id={package_id} type={interview_type}", [artifact_ref])
    conn.commit()
    return {"prep_pack_id": interview_id, **prep, "source_refs": source_refs, "artifact_ref": artifact_ref}


def create_story_cards(workspace_id: str, source_project_ids: list[str] | None = None, job_id: str | None = None) -> dict:
    conn, _ = workspace_conn(workspace_id)
    projects = []
    if source_project_ids:
        placeholders = ",".join("?" for _ in source_project_ids)
        projects = rows_to_dicts(conn.execute(f"SELECT * FROM tech_project WHERE workspace_id=? AND id IN ({placeholders})", [workspace_id, *source_project_ids]).fetchall())
    if not projects:
        projects = rows_to_dicts(conn.execute("SELECT * FROM tech_project WHERE workspace_id=? LIMIT 3", (workspace_id,)).fetchall())
    cards = []
    for project in projects:
        card_id = new_id("story")
        title = f"{project['name']} 技术难题故事"
        short = f"我在 {project['name']} 中围绕核心功能实现和项目表达做了整理，重点可以讲问题、实现、取舍和结果。"
        medium = f"在 {project['name']} 项目中，我先明确目标，再实现关键功能，并复盘技术取舍。需要补充真实结果指标，避免夸大。"
        long = f"项目背景：{project['summary']}\n行动：围绕关键功能、接口调用、组件拆分或数据处理说明本人贡献。\n结果：需要用户确认部署、测试和可量化结果。"
        conn.execute(
            "INSERT INTO story_card VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (card_id, workspace_id, title, dumps(["讲一个你解决技术难题的经历", "讲讲你的项目"]), dumps([project["id"]]), "转行项目需要证明可交付能力", "实现并解释关键功能", "说明定位、实现和取舍", "待用户补充真实结果", short, medium, long, dumps(["project", "technical"]), now_iso()),
        )
        source_refs = [_source_ref("tech_project", project["id"], "summary", project["summary"][:160], "high")]
        payload = validate_output(
            "interview_create_story_card",
            {
                "id": card_id,
                "title": title,
                "applicable_questions": ["讲一个你解决技术难题的经历"],
                "short_version": short,
                "medium_version": medium,
                "long_version": long,
                "source_refs": source_refs,
            },
        )
        artifact_ref = _write_artifact(conn, workspace_id, "story_card", "story_card", card_id, payload, source_refs, [_confirmation("请补充真实结果指标；没有数据时保持待确认。", "warning", "故事卡结果不能编造。", source_refs)], "needs_confirmation", "interview.create_story_cards")
        cards.append({**payload, "artifact_ref": artifact_ref})
    _log_tool(conn, workspace_id, "interview.create_story_cards", f"projects={source_project_ids or 'latest'} job_id={job_id}", [card.get("artifact_ref", {}) for card in cards])
    conn.commit()
    return {"story_cards": cards}


def simulate_interview(workspace_id: str, prep_pack_id: str | None = None, mode: str = "project_deep_dive", user_answer: str | None = None) -> dict:
    feedback = "你的回答已经有项目背景；下一轮建议补充个人贡献、技术取舍和结果。"
    if user_answer and len(user_answer) > 500:
        feedback = "回答信息较多，建议压缩到 2 分钟内，并优先讲问题、行动、结果。"
    return {"interviewer_question": "讲一下你最能代表开发能力的项目。", "follow_up": "这个项目里最难的一处实现是什么？你为什么这样取舍？", "feedback": feedback, "next_practice": "用 2 分钟版本重新回答，并引用一个真实项目结果。"}


def start_realtime_session(workspace_id: str, job_id: str | None = None, mode: str = "formal_assist", save_policy: str = "transcript_only") -> dict:
    conn, _ = workspace_conn(workspace_id)
    session_id = new_id("rt")
    if mode == "formal_assist" and save_policy == "save_all":
        save_policy = "transcript_only"
    conn.execute("INSERT INTO realtime_session VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (session_id, workspace_id, None, mode, now_iso(), None, save_policy, None, None))
    _log_tool(conn, workspace_id, "realtime.start", f"mode={mode} save_policy={save_policy}", [])
    conn.commit()
    return {"session_id": session_id, "mode": mode, "allowed_hint_levels": ["minimal", "outline"] if mode == "formal_assist" else ["minimal", "outline", "draft"], "message": "我会识别问题、推荐真实项目并提示回答结构。正式面试模式默认不生成逐字答案。"}


def detect_question(session_id: str, transcript_chunk: str) -> dict:
    question = transcript_chunk.strip()
    detected = bool(question.endswith("?") or "？" in question or any(word in question for word in ["讲", "说", "tell", "describe", "why", "how"]))
    return {"question_detected": detected, "question_text": question, "question_type": classify_question(question), "confidence": 0.86 if detected else 0.45}


def generate_hint(session_id: str, question_text: str, hint_level: str = "outline") -> dict:
    from services.storage.workspace import WORKSPACE_INDEX, workspace_root
    from services.storage.db import connect

    conn = None
    session = None
    for root in list(WORKSPACE_INDEX.values()) + [workspace_root()]:
        candidate = connect(root / "jobpilot.db")
        found = row_to_dict(candidate.execute("SELECT * FROM realtime_session WHERE id=?", (session_id,)).fetchone())
        if found:
            conn = candidate
            session = found
            break
    if not session:
        raise ValueError("Realtime session not found.")
    workspace_id = session["workspace_id"]
    if session["mode"] == "formal_assist" and hint_level not in {"minimal", "outline"}:
        raise ValueError("formal_assist only allows minimal or outline hints.")
    project = row_to_dict(conn.execute("SELECT * FROM tech_project WHERE workspace_id=? ORDER BY created_at LIMIT 1", (workspace_id,)).fetchone())
    story = row_to_dict(conn.execute("SELECT * FROM story_card WHERE workspace_id=? ORDER BY created_at LIMIT 1", (workspace_id,)).fetchone())
    structure = ["先复述问题", "说明项目背景", "讲你的实现", "讲一个取舍", "用真实结果或待确认项收尾"]
    reminder = "不要说没有事实来源的技术、指标或证书。正式面试模式只使用提纲。"
    source_refs = [ref for ref in [_source_ref("tech_project", project["id"], "summary", project["summary"][:160], "high") if project else None, _source_ref("story_card", story["id"], "short_version", story["short_version"], "medium") if story else None] if ref]
    payload = validate_output(
        "realtime_generate_hint",
        {
            "question_type": classify_question(question_text),
            "hint_level": hint_level if hint_level in {"minimal", "outline"} else "outline",
            "recommended_project": project["name"] if project else "先创建项目卡",
            "structure": structure,
            "reminder": reminder,
            "source_refs": source_refs,
        },
    )
    hint = {"recommended_project": payload["recommended_project"], "structure": payload["structure"], "reminder": payload["reminder"], "source_refs": payload["source_refs"], "question_type": payload["question_type"], "hint_level": payload["hint_level"]}
    conn.execute(
        "INSERT INTO realtime_hint VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (new_id("hint"), session_id, question_text, payload["question_type"], project["id"] if project else None, story["id"] if story else None, payload["hint_level"], dumps(hint), now_iso()),
    )
    _log_tool(conn, workspace_id, "realtime.generate_hint", f"session_id={session_id} level={hint_level}", [])
    conn.commit()
    return {"hint": hint}


def end_realtime_session(session_id: str) -> dict:
    from services.storage.workspace import WORKSPACE_INDEX, workspace_root
    from services.storage.db import connect

    for root in list(WORKSPACE_INDEX.values()) + [workspace_root()]:
        candidate = connect(root / "jobpilot.db")
        session = row_to_dict(candidate.execute("SELECT * FROM realtime_session WHERE id=?", (session_id,)).fetchone())
        if session:
            ended_at = now_iso()
            candidate.execute("UPDATE realtime_session SET ended_at=? WHERE id=?", (ended_at, session_id))
            _log_tool(candidate, session["workspace_id"], "realtime.end", f"session_id={session_id}", [])
            candidate.commit()
            return {"session_id": session_id, "workspace_id": session["workspace_id"], "ended": True, "ended_at": ended_at}
    raise ValueError("Realtime session not found.")


def review_interview(workspace_id: str, session_id: str | None = None, transcript: str | None = None) -> dict:
    conn, _ = workspace_conn(workspace_id)
    questions = []
    if transcript:
        questions = [line.strip() for line in transcript.splitlines() if "?" in line or "？" in line][:5]
    if not questions:
        questions = ["讲一个你解决技术难题的经历"]
    tasks = ["练习项目深挖 2 分钟版本", "补充项目结果指标", "准备一个转行动机故事"]
    for task in tasks:
        conn.execute("INSERT INTO training_task VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (new_id("task"), workspace_id, "interview_review", task, f"围绕本次面试复盘完成：{task}", "high" if "项目" in task else "medium", None, "open", now_iso(), now_iso()))
    source_refs = [_source_ref("transcript", session_id or "inline_transcript", "text", (transcript or "")[:160], "medium")]
    review = validate_output(
        "interview_review",
        {
            "review_id": new_id("review"),
            "questions": questions,
            "strengths": ["能围绕项目经验展开"],
            "improvements": ["补充结果和技术取舍", "减少没有来源的表述"],
            "training_tasks": tasks,
            "thank_you_message": "感谢今天的面试交流。我会继续补强项目表达和岗位相关技能，期待后续反馈。",
            "source_refs": source_refs,
        },
    )
    artifact_ref = _write_artifact(conn, workspace_id, "interview_review", "interview", session_id, review, source_refs, [], "needs_confirmation", "interview.review")
    _log_tool(conn, workspace_id, "interview.review", f"session_id={session_id} transcript_chars={len(transcript or '')}", [artifact_ref])
    conn.commit()
    return {**review, "artifact_ref": artifact_ref}
