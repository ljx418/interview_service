from __future__ import annotations

from typing import Any

from services.storage.db import dumps, loads, row_to_dict, rows_to_dicts
from services.storage.workspace import new_id, now_iso, workspace_conn
from services.tools.jobpilot import _write_artifact


def _source_ref(source_type: str, source_id: str, field: str | None = None, quote: str | None = None, confidence: str = "medium") -> dict[str, Any]:
    return {"source_type": source_type, "source_id": source_id, "field": field, "quote": quote, "confidence": confidence}


def _confirmation(question: str, level: str, reason: str, source_refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {"question": question, "confirmation_level": level, "reason": reason, "source_refs": source_refs}


def _json_list(value: Any) -> list[Any]:
    parsed = loads(value, [])
    return parsed if isinstance(parsed, list) else []


def _json_dict(value: Any) -> dict[str, Any]:
    parsed = loads(value, {})
    return parsed if isinstance(parsed, dict) else {}


def _latest_job(conn, workspace_id: str, job_id: str | None) -> dict[str, Any] | None:
    if job_id:
        return row_to_dict(conn.execute("SELECT * FROM job WHERE workspace_id=? AND id=?", (workspace_id, job_id)).fetchone())
    return row_to_dict(conn.execute("SELECT * FROM job WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1", (workspace_id,)).fetchone())


def _latest_profile_artifact(conn, workspace_id: str) -> dict[str, Any] | None:
    return row_to_dict(
        conn.execute(
            """
            SELECT * FROM artifact
            WHERE workspace_id=? AND artifact_type='candidate_profile'
            ORDER BY updated_at DESC LIMIT 1
            """,
            (workspace_id,),
        ).fetchone()
    )


def _existing_profile_row(conn, workspace_id: str) -> dict[str, Any] | None:
    return row_to_dict(conn.execute("SELECT * FROM candidate_profile WHERE workspace_id=? ORDER BY updated_at DESC LIMIT 1", (workspace_id,)).fetchone())


def _empty_profile(workspace_id: str, job_id: str | None = None) -> dict[str, Any]:
    return {
        "workspace_id": workspace_id,
        "job_id": job_id,
        "empty": True,
        "profile_summary": {
            "target_roles": [],
            "background_summary": "尚未形成候选人画像。",
            "transition_goal": "",
            "current_level": "unknown",
            "source_refs": [],
        },
        "capability_matrix": [],
        "project_credibility": [],
        "job_gaps": [],
        "source_refs": [],
        "questions_to_confirm": [
            _confirmation("请先导入简历、项目说明或目标 JD。", "warning", "P5.5 画像必须基于可追溯资料生成。", []),
        ],
        "artifact_ref": None,
        "next_actions": ["上传或导入资料", "解析目标 JD", "刷新候选人画像"],
    }


def _profile_source_refs(facts: list[dict[str, Any]], skills: list[dict[str, Any]], projects: list[dict[str, Any]], job: dict[str, Any] | None) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for fact in facts[:12]:
        refs.append(_source_ref("career_fact", fact["id"], "content", fact.get("source_quote") or fact.get("content", "")[:160], "medium"))
    for skill in skills[:12]:
        refs.append(_source_ref("skill_evidence", skill["id"], "description", skill.get("description", "")[:160], "medium"))
    for project in projects[:6]:
        refs.append(_source_ref("tech_project", project["id"], "summary", project.get("summary", "")[:160], "medium"))
    if job:
        refs.append(_source_ref("job", job["id"], "requirements_json", job.get("jd_summary", "")[:160], "high"))
    return refs


def _capability_matrix(skills: list[dict[str, Any]], facts: list[dict[str, Any]], job: dict[str, Any] | None) -> list[dict[str, Any]]:
    fact_by_title = {fact["title"]: fact for fact in facts if fact.get("type") == "skill"}
    req = _json_dict(job.get("requirements_json")) if job else {}
    must = set(req.get("must_have") or [])
    nice = set(req.get("nice_to_have") or [])
    matrix: list[dict[str, Any]] = []
    seen: set[str] = set()

    for skill in skills:
        name = skill["skill_name"]
        seen.add(name)
        fact = fact_by_title.get(name)
        confidence = float(skill.get("confidence") or fact.get("confidence") if fact else skill.get("confidence") or 0)
        verified = bool(skill.get("user_verified") or (fact and fact.get("user_verified")))
        source_refs = [_source_ref("skill_evidence", skill["id"], "description", skill.get("description", "")[:160], "medium")]
        if fact:
            source_refs.append(_source_ref("career_fact", fact["id"], "content", fact.get("content", "")[:160], "medium"))
        if verified and confidence >= 0.75:
            level = "strong"
        elif confidence >= 0.68:
            level = "usable"
        else:
            level = "weak"
        relevance = "high" if name in must else "medium" if name in nice or skill.get("target_role_relevance") == "usable" else "low"
        matrix.append(
            {
                "skill": name,
                "category": skill.get("category") or "general",
                "evidence_type": skill.get("evidence_type") or "profile",
                "evidence_level": level,
                "target_role_relevance": relevance,
                "source_refs": source_refs,
                "questions_to_confirm": []
                if level == "strong"
                else [_confirmation(f"请补充 {name} 的项目证据或本人贡献说明。", "warning", "弱证据技能不能直接写成强能力。", source_refs)],
            }
        )

    for requirement in [item for item in [*must, *nice] if item not in seen]:
        refs = [_source_ref("job", job["id"], "requirements_json", requirement, "high")] if job else []
        matrix.append(
            {
                "skill": requirement,
                "category": "job_requirement",
                "evidence_type": "missing",
                "evidence_level": "missing",
                "target_role_relevance": "high" if requirement in must else "medium",
                "source_refs": refs,
                "questions_to_confirm": [_confirmation(f"当前资料缺少 {requirement} 的可追溯证据。", "warning", "缺证据项必须标记为 missing。", refs)],
            }
        )
    return matrix


def _project_credibility(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for project in projects:
        refs = [_source_ref("tech_project", project["id"], "summary", project.get("summary", "")[:160], "medium")]
        contribution = (project.get("user_contribution") or "").strip()
        has_detail = bool((project.get("implementation") or "").strip() and (project.get("technical_challenges") or "").strip())
        verified = bool(project.get("verified"))
        if verified and contribution and has_detail:
            label = "verified"
        elif contribution and has_detail:
            label = "plausible"
        elif contribution:
            label = "needs_evidence"
        else:
            label = "risky"
        gaps = []
        if not contribution or "确认" in contribution:
            gaps.append("本人贡献需要用户确认")
        if not project.get("demo_url") and not project.get("repo_url"):
            gaps.append("缺少可验证链接或材料")
        if not project.get("technical_challenges") or "补充" in str(project.get("technical_challenges")) or "需要" in str(project.get("technical_challenges")):
            gaps.append("技术难点需要补充细节")
        items.append(
            {
                "project_id": project["id"],
                "project_name": project["name"],
                "credibility_label": label,
                "contribution": contribution or "待确认",
                "technical_challenges": project.get("technical_challenges") or "待补充",
                "strengths": [project.get("summary", "已有项目线索")],
                "evidence_gaps": gaps,
                "source_refs": refs,
                "questions_to_confirm": []
                if label == "verified"
                else [_confirmation("请确认本人负责范围、技术难点和可验证材料。", "blocking" if label == "risky" else "warning", "项目可信度不能把待确认贡献写成事实。", refs)],
            }
        )
    return items


def _job_gaps(matrix: list[dict[str, Any]], job: dict[str, Any] | None, match_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not job:
        return []
    req = _json_dict(job.get("requirements_json"))
    by_skill = {item["skill"]: item for item in matrix}
    gaps: list[dict[str, Any]] = []
    for req_type, requirements in [("must", req.get("must_have") or []), ("nice", req.get("nice_to_have") or [])]:
        for requirement in requirements:
            capability = by_skill.get(requirement)
            level = capability.get("evidence_level") if capability else "missing"
            gap_level = "covered" if level == "strong" else "partial" if level in {"usable", "weak"} else "missing"
            refs = capability.get("source_refs") if capability else [_source_ref("job", job["id"], "requirements_json", requirement, "high")]
            action = (
                f"保留 {requirement} 的强证据，用于申请材料。"
                if gap_level == "covered"
                else f"补充 {requirement} 的本人贡献、项目片段或 README 证据。"
            )
            gaps.append(
                {
                    "requirement": requirement,
                    "requirement_type": req_type,
                    "gap_level": gap_level,
                    "impact": "must-have 缺口会影响投递可信度。" if req_type == "must" and gap_level != "covered" else "作为表达加分项处理。",
                    "next_action": action,
                    "source_refs": refs,
                    "match_report_refs": [report["id"] for report in match_reports[:2]],
                }
            )
    return gaps


def _summary(facts: list[dict[str, Any]], job: dict[str, Any] | None, target_role: str | None, refs: list[dict[str, Any]]) -> dict[str, Any]:
    background = next((fact["content"] for fact in facts if fact.get("type") == "experience"), "")
    skill_names = [fact["title"] for fact in facts if fact.get("type") == "skill"]
    role = target_role or (job.get("title") if job else None) or "Junior Developer"
    return {
        "target_roles": [role],
        "background_summary": background or ("已有 " + "、".join(skill_names[:5]) + " 等技能线索。") if skill_names else "已有资料不足，需先补充简历或项目说明。",
        "transition_goal": f"围绕 {role} 整理可追溯项目、技能证据和岗位短板。",
        "current_level": "junior_candidate" if skill_names else "unknown",
        "source_refs": refs[:8],
    }


def get_candidate_profile(workspace_id: str, job_id: str | None = None) -> dict[str, Any]:
    conn, _ = workspace_conn(workspace_id)
    artifact = _latest_profile_artifact(conn, workspace_id)
    if not artifact:
        row = _existing_profile_row(conn, workspace_id)
        if not row:
            return _empty_profile(workspace_id, job_id)
        return {
            **_empty_profile(workspace_id, job_id),
            "empty": False,
            "profile_summary": {
                "target_roles": _json_list(row.get("target_roles")),
                "background_summary": row.get("background_summary") or "",
                "transition_goal": row.get("transition_goal") or "",
                "current_level": row.get("current_level") or "unknown",
                "source_refs": [],
            },
        }
    content = _json_dict(artifact.get("content_json"))
    return {
        "workspace_id": workspace_id,
        "job_id": job_id,
        "empty": False,
        **content,
        "artifact_ref": {
            "artifact_id": artifact["id"],
            "artifact_type": artifact["artifact_type"],
            "status": artifact["status"],
            "current_version_id": artifact["current_version_id"],
        },
    }


def refresh_candidate_profile(workspace_id: str, job_id: str | None = None, target_role: str | None = None) -> dict[str, Any]:
    conn, _ = workspace_conn(workspace_id)
    facts = rows_to_dicts(conn.execute("SELECT * FROM career_fact WHERE workspace_id=? ORDER BY created_at", (workspace_id,)).fetchall())
    skills = rows_to_dicts(conn.execute("SELECT * FROM skill_evidence WHERE workspace_id=? ORDER BY created_at", (workspace_id,)).fetchall())
    projects = rows_to_dicts(conn.execute("SELECT * FROM tech_project WHERE workspace_id=? ORDER BY created_at", (workspace_id,)).fetchall())
    job = _latest_job(conn, workspace_id, job_id)
    reports = rows_to_dicts(
        conn.execute(
            "SELECT * FROM match_report WHERE workspace_id=? AND (? IS NULL OR job_id=?) ORDER BY created_at DESC",
            (workspace_id, job["id"] if job else None, job["id"] if job else None),
        ).fetchall()
    )
    if not facts and not skills and not projects and not job:
        return _empty_profile(workspace_id, job_id)

    refs = _profile_source_refs(facts, skills, projects, job)
    matrix = _capability_matrix(skills, facts, job)
    credibility = _project_credibility(projects)
    gaps = _job_gaps(matrix, job, reports)
    summary = _summary(facts, job, target_role, refs)
    questions = [
        item
        for collection in [matrix, credibility]
        for entry in collection
        for item in entry.get("questions_to_confirm", [])
    ]
    if not refs:
        questions.append(_confirmation("请补充可追溯资料来源。", "warning", "P5.5 画像不能没有 source refs。", []))

    existing = _existing_profile_row(conn, workspace_id)
    stamp = now_iso()
    if existing:
        profile_id = existing["id"]
        conn.execute(
            """
            UPDATE candidate_profile
            SET target_roles=?, background_summary=?, transition_goal=?, current_level=?, updated_at=?
            WHERE workspace_id=? AND id=?
            """,
            (dumps(summary["target_roles"]), summary["background_summary"], summary["transition_goal"], summary["current_level"], stamp, workspace_id, profile_id),
        )
    else:
        profile_id = new_id("cand")
        conn.execute(
            """
            INSERT INTO candidate_profile (
              id, workspace_id, target_roles, target_locations, target_language,
              background_summary, transition_goal, current_level, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (profile_id, workspace_id, dumps(summary["target_roles"]), "[]", "zh-CN", summary["background_summary"], summary["transition_goal"], summary["current_level"], stamp, stamp),
        )

    content = {
        "profile_id": profile_id,
        "profile_summary": summary,
        "capability_matrix": matrix,
        "project_credibility": credibility,
        "job_gaps": gaps,
        "source_refs": refs,
        "questions_to_confirm": questions,
        "next_actions": [
            "确认本人项目贡献",
            "补充缺证据技能的项目说明",
            "根据 JD 短板补强申请材料",
        ],
        "unverified_scope": [
            "未使用用户真实个人资料",
            "未调用真实外部 provider",
            "不分析敏感属性或人格",
        ],
    }
    artifact_ref = _write_artifact(
        conn,
        workspace_id,
        "candidate_profile",
        "candidate_profile",
        profile_id,
        content,
        refs,
        questions,
        "needs_confirmation" if questions else "confirmed",
        "profile.candidate.refresh",
    )
    conn.commit()
    return {"workspace_id": workspace_id, "job_id": job["id"] if job else job_id, "empty": False, **content, "artifact_ref": artifact_ref}
