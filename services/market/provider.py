from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from services.storage.db import dumps, loads, row_to_dict
from services.storage.workspace import workspace_conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


PROVIDER_REGISTRY: list[dict[str, Any]] = [
    {
        "provider_id": "fixture_local",
        "provider_name": "Local fixture market sample",
        "provider_type": "fixture",
        "requires_key": False,
        "rate_limit": "local only",
        "license_note": "仓库内匿名样本和验收 fixture；不能声明真实市场。",
        "env_keys": [],
    },
    {
        "provider_id": "manual_paste",
        "provider_name": "Manual pasted JD",
        "provider_type": "manual_paste",
        "requires_key": False,
        "rate_limit": "user supplied",
        "license_note": "用户手动粘贴或导入的 JD；不读取网页。",
        "env_keys": [],
    },
    {
        "provider_id": "public_sample",
        "provider_name": "Public sample source",
        "provider_type": "public_source",
        "requires_key": False,
        "rate_limit": "recorded sample",
        "license_note": "公开来源的记录样本；不进行实时联网抓取。",
        "env_keys": [],
    },
    {
        "provider_id": "adzuna_opt_in",
        "provider_name": "Adzuna opt-in API",
        "provider_type": "opt_in_api",
        "requires_key": True,
        "rate_limit": "provider account limit",
        "license_note": "仅在用户提供合法凭据并确认后允许一次性检查；P11 默认不外呼。",
        "env_keys": ["JOBPILOT_ADZUNA_APP_ID", "JOBPILOT_ADZUNA_APP_KEY"],
    },
    {
        "provider_id": "theirstack_opt_in",
        "provider_name": "TheirStack opt-in API",
        "provider_type": "opt_in_api",
        "requires_key": True,
        "rate_limit": "provider account limit",
        "license_note": "仅在用户提供合法凭据并确认后允许一次性检查；P11 默认不外呼。",
        "env_keys": ["JOBPILOT_THEIRSTACK_API_KEY"],
    },
    {
        "provider_id": "jsearch_opt_in",
        "provider_name": "JSearch opt-in API",
        "provider_type": "opt_in_api",
        "requires_key": True,
        "rate_limit": "provider account limit",
        "license_note": "仅在用户提供合法凭据并确认后允许一次性检查；P11 默认不外呼。",
        "env_keys": ["JOBPILOT_RAPIDAPI_KEY"],
    },
]


FIXTURE_POSTS: list[dict[str, Any]] = [
    {
        "title": "LLM 应用前端工程师",
        "company": "北辰智能",
        "city": "北京",
        "salary_range": "25-40k",
        "seniority": "3-5年",
        "tech_stack": ["React", "TypeScript", "LLM", "ECharts"],
        "source_url": "examples/jds/llm_frontend_beijing.md",
        "source_type": "fixture",
        "confidence": 0.72,
    },
    {
        "title": "AI Copilot 前端工程师",
        "company": "海纳云",
        "city": "上海",
        "salary_range": "23-38k",
        "seniority": "3-5年",
        "tech_stack": ["React", "TypeScript", "Node.js", "Agent"],
        "source_url": "examples/jds/ai_copilot_shanghai.md",
        "source_type": "fixture",
        "confidence": 0.7,
    },
    {
        "title": "智能体平台前端开发",
        "company": "南山数科",
        "city": "深圳",
        "salary_range": "22-36k",
        "seniority": "2-4年",
        "tech_stack": ["Vue", "TypeScript", "Workflow", "RAG"],
        "source_url": "examples/jds/agent_platform_shenzhen.md",
        "source_type": "fixture",
        "confidence": 0.68,
    },
    {
        "title": "AI 产品前端工程师",
        "company": "西湖智造",
        "city": "杭州",
        "salary_range": "20-34k",
        "seniority": "2-4年",
        "tech_stack": ["React", "Canvas", "Map", "LLM"],
        "source_url": "examples/jds/ai_product_hangzhou.md",
        "source_type": "fixture",
        "confidence": 0.66,
    },
    {
        "title": "数据可视化前端工程师",
        "company": "天府数智",
        "city": "成都",
        "salary_range": "18-30k",
        "seniority": "2-4年",
        "tech_stack": ["ECharts", "TypeScript", "GeoJSON", "React"],
        "source_url": "examples/jds/dataviz_chengdu.md",
        "source_type": "fixture",
        "confidence": 0.64,
    },
]


CITY_REGION = {
    "北京": "110000",
    "上海": "310000",
    "深圳": "440300",
    "杭州": "330100",
    "成都": "510100",
}


def provider_status(workspace_id: str | None = None) -> dict[str, Any]:
    providers = []
    for provider in PROVIDER_REGISTRY:
        configured = _provider_configured(provider)
        provider_record = {
            "provider_id": provider["provider_id"],
            "provider_name": provider["provider_name"],
            "provider_type": provider["provider_type"],
            "configured_state": "configured" if configured else ("connected" if provider["provider_type"] in {"fixture", "manual_paste", "public_source"} else "not_configured"),
            "requires_key": provider["requires_key"],
            "rate_limit": provider["rate_limit"],
            "license_note": provider["license_note"],
            "last_checked_at": None,
            "api_key_redacted": True,
            "configured_is_called": False,
            "called": False,
        }
        providers.append(provider_record)
    recent_invocations: list[dict[str, Any]] = []
    if workspace_id:
        conn, _ = workspace_conn(workspace_id)
        _sync_provider_registry(conn, providers)
        rows = conn.execute(
            """
            SELECT invocation_id, provider_id, run_id, status, error_code, redacted, created_at
            FROM market_provider_invocation_logs
            WHERE workspace_id=? OR workspace_id IS NULL
            ORDER BY created_at DESC LIMIT 8
            """,
            (workspace_id,),
        ).fetchall()
        recent_invocations = [dict(row) for row in rows]
        checked = {row["provider_id"]: row["created_at"] for row in rows}
        for provider in providers:
            if provider["provider_id"] in checked:
                provider["last_checked_at"] = checked[provider["provider_id"]]
                provider["called"] = provider["provider_type"] == "opt_in_api" and any(
                    row["provider_id"] == provider["provider_id"] and row["status"] == "called" for row in rows
                )
    level = "Level 1"
    return {
        "level": level,
        "level_label": "Level 1 本地/记录数据路径",
        "providers": providers,
        "recent_invocations": recent_invocations,
        "default_policy": "fixture/manual/public/recorded only",
        "external_call_enabled": _truthy(os.environ.get("JOBPILOT_ALLOW_MARKET_PROVIDER_CALL")),
        "can_claim_real_market": False,
        "warnings": [
            "当前默认不外呼真实市场 provider。",
            "fixture/manual/public sample 不能声明全网搜索或真实市场验收通过。",
        ],
    }


def check_provider(workspace_id: str | None, provider_id: str, consent_preview_id: str | None, confirm: bool) -> dict[str, Any]:
    provider = _provider_by_id(provider_id)
    start = time.perf_counter()
    status = "checked"
    error_code = None
    message = "本地 provider 可用；未发生真实外呼。"
    checked = False
    configured_state = "connected"
    if provider["provider_type"] == "opt_in_api":
        configured = _provider_configured(provider)
        configured_state = "configured" if configured else "not_configured"
        if not configured:
            status = "failed"
            error_code = "PROVIDER_NOT_CONFIGURED"
            message = "provider 未配置，不能外呼。"
        elif not confirm:
            status = "rejected"
            error_code = "CONSENT_REQUIRED"
            message = "provider 已配置但未确认，不能外呼。"
        elif not _truthy(os.environ.get("JOBPILOT_ALLOW_MARKET_PROVIDER_CALL")):
            status = "rejected"
            error_code = "POLICY_REJECTED"
            message = "真实 provider 调用仍被 P11 安全策略关闭；需要用户明确打开 JOBPILOT_ALLOW_MARKET_PROVIDER_CALL。"
        else:
            status = "rejected"
            error_code = "POLICY_REJECTED"
            message = "P11 当前实现只完成 opt-in 边界，未执行真实 provider 网络调用。"
    else:
        checked = True
    duration_ms = int((time.perf_counter() - start) * 1000)
    invocation_id = _log_invocation(
        workspace_id=workspace_id,
        provider_id=provider_id,
        run_id=None,
        query_summary={"operation": "provider_check", "consent_preview_id": consent_preview_id or "", "confirm": bool(confirm)},
        status=status,
        duration_ms=duration_ms,
        error_code=error_code,
    )
    return {
        "provider_id": provider_id,
        "provider_name": provider["provider_name"],
        "configured_state": configured_state,
        "checked": checked,
        "called": False,
        "status": status,
        "error_code": error_code,
        "message": message,
        "invocation_id": invocation_id,
        "api_key_redacted": True,
        "raw_provider_response_included": False,
    }


def create_search_run(
    *,
    workspace_id: str,
    query: str,
    city_filters: list[str] | None = None,
    salary_range: str | None = None,
    tech_stack: list[str] | None = None,
    provider_ids: list[str] | None = None,
    consent_id: str | None = None,
    source_policy: str = "fixture",
) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("query is required")
    provider_ids = provider_ids or ["fixture_local"]
    providers = [_provider_by_id(provider_id) for provider_id in provider_ids]
    if source_policy == "opt_in_api" or any(provider["provider_type"] == "opt_in_api" for provider in providers):
        if not consent_id:
            raise ValueError("CONSENT_REQUIRED: opt-in market provider search requires explicit consent_id")
        raise ValueError("POLICY_REJECTED: real market provider calls are disabled in P11 Level 1 implementation")

    conn, _ = workspace_conn(workspace_id)
    _sync_provider_registry(conn, provider_status(workspace_id=None)["providers"])
    run_id = f"market_run_{uuid4().hex}"
    started_at = _now()
    cities = _normalize_city_filters(query, city_filters or [])
    posts = [_post for _post in FIXTURE_POSTS if not cities or _post["city"] in cities]
    if not posts:
        posts = FIXTURE_POSTS[:3]
    if tech_stack:
        wanted = {item.lower() for item in tech_stack}
        filtered = [post for post in posts if wanted.intersection({item.lower() for item in post["tech_stack"]})]
        posts = filtered or posts
    source_refs = []
    normalized_posts = []
    for post in posts:
        source_ref_id = f"src_{uuid4().hex}"
        job_id = f"market_job_{uuid4().hex}"
        source_refs.append(source_ref_id)
        normalized_posts.append({**post, "job_id": job_id, "source_ref_id": source_ref_id})
    snapshot = _build_snapshot(workspace_id, run_id, query, normalized_posts, source_refs, source_policy)
    completed_at = _now()
    status = "fallback" if source_policy in {"fixture", "recorded"} else "succeeded"
    boundary_note = (
        "Level 1 fallback only: 本次 search run 使用本地/记录数据，不代表真实市场 provider 或全网搜索通过。"
        if status == "fallback"
        else "Level 1 local/manual/public source: 未调用真实市场 provider。"
    )
    conn.execute(
        """
        INSERT INTO job_search_runs (
          run_id, workspace_id, query, city_filters, salary_range, tech_stack, source_policy,
          provider_ids, consent_id, started_at, completed_at, status, result_count,
          source_refs, boundary_note, error_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            workspace_id,
            query.strip(),
            dumps(cities),
            salary_range or "",
            dumps(tech_stack or []),
            source_policy,
            dumps(provider_ids),
            consent_id,
            started_at,
            completed_at,
            status,
            len(normalized_posts),
            dumps(source_refs),
            boundary_note,
            "FALLBACK_ONLY" if status == "fallback" else None,
        ),
    )
    for post in normalized_posts:
        conn.execute(
            """
            INSERT INTO normalized_job_posts (
              job_id, workspace_id, run_id, title, company, city, salary_range, seniority,
              tech_stack, source_url, source_type, fetched_at, confidence, source_ref_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post["job_id"],
                workspace_id,
                run_id,
                post["title"],
                post["company"],
                post["city"],
                post["salary_range"],
                post["seniority"],
                dumps(post["tech_stack"]),
                post["source_url"],
                post["source_type"],
                completed_at,
                post["confidence"],
                post["source_ref_id"],
            ),
        )
        conn.execute(
            """
            INSERT INTO region_source_refs (
              source_ref_id, workspace_id, run_id, region_code, region_name, metric_name,
              source_type, source_ref_ids, source_summary, source_url, confidence, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post["source_ref_id"],
                workspace_id,
                run_id,
                CITY_REGION.get(post["city"], "000000"),
                post["city"],
                "job_post",
                post["source_type"],
                dumps([post["source_ref_id"]]),
                f"{post['city']} · {post['title']} · {post['salary_range']} · {post['company']}",
                post["source_url"],
                post["confidence"],
                completed_at,
            ),
        )
    conn.execute(
        """
        INSERT INTO job_market_snapshots (
          snapshot_id, workspace_id, run_id, city_stats, salary_histogram, tech_heatmap,
          source_breakdown, remote_ratio, competition_level, trend_summary,
          low_confidence_notes, source_refs, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            snapshot["snapshot_id"],
            workspace_id,
            run_id,
            dumps(snapshot["city_stats"]),
            dumps(snapshot["salary_histogram"]),
            dumps(snapshot["tech_heatmap"]),
            dumps(snapshot["source_breakdown"]),
            snapshot["remote_ratio"],
            snapshot["competition_level"],
            snapshot["trend_summary"],
            dumps(snapshot["low_confidence_notes"]),
            dumps(source_refs),
            completed_at,
        ),
    )
    _log_invocation(
        workspace_id=workspace_id,
        provider_id=provider_ids[0],
        run_id=run_id,
        query_summary={"query": query.strip(), "cities": cities, "source_policy": source_policy, "result_count": len(normalized_posts)},
        status=status,
        duration_ms=0,
        error_code="FALLBACK_ONLY" if status == "fallback" else None,
    )
    return {
        "run_id": run_id,
        "status": status,
        "result_count": len(normalized_posts),
        "source_refs": source_refs,
        "boundary_note": boundary_note,
        "snapshot": snapshot,
        "raw_provider_response_included": False,
    }


def get_search_run(workspace_id: str, run_id: str) -> dict[str, Any]:
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute("SELECT * FROM job_search_runs WHERE workspace_id=? AND run_id=?", (workspace_id, run_id)).fetchone()
    if not row:
        raise ValueError("NO_RESULTS: market search run not found")
    result = dict(row)
    for key in ("city_filters", "tech_stack", "provider_ids", "source_refs"):
        result[key] = loads(result.get(key), [])
    return result


def get_snapshot(workspace_id: str, run_id: str) -> dict[str, Any]:
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute(
        "SELECT * FROM job_market_snapshots WHERE workspace_id=? AND run_id=? ORDER BY created_at DESC LIMIT 1",
        (workspace_id, run_id),
    ).fetchone()
    if not row:
        raise ValueError("NO_RESULTS: market snapshot not found")
    result = dict(row)
    for key, default in {
        "city_stats": [],
        "salary_histogram": [],
        "tech_heatmap": [],
        "source_breakdown": {},
        "low_confidence_notes": [],
        "source_refs": [],
    }.items():
        result[key] = loads(result.get(key), default)
    result["raw_provider_response_included"] = False
    return result


def get_source_ref(workspace_id: str, source_ref_id: str) -> dict[str, Any]:
    conn, _ = workspace_conn(workspace_id)
    row = conn.execute(
        "SELECT * FROM region_source_refs WHERE workspace_id=? AND source_ref_id=?",
        (workspace_id, source_ref_id),
    ).fetchone()
    if not row:
        raise ValueError("NO_RESULTS: market source ref not found")
    result = row_to_dict(row) or {}
    result["source_ref_ids"] = loads(result.get("source_ref_ids"), [])
    result["raw_provider_response_included"] = False
    result["api_key_redacted"] = True
    return result


def _sync_provider_registry(conn, providers: list[dict[str, Any]]) -> None:
    now = _now()
    for provider in providers:
        conn.execute(
            """
            INSERT INTO job_market_providers (
              provider_id, provider_name, provider_type, configured_state, requires_key,
              rate_limit, license_note, last_checked_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider_id) DO UPDATE SET
              provider_name=excluded.provider_name,
              provider_type=excluded.provider_type,
              configured_state=excluded.configured_state,
              requires_key=excluded.requires_key,
              rate_limit=excluded.rate_limit,
              license_note=excluded.license_note,
              updated_at=excluded.updated_at
            """,
            (
                provider["provider_id"],
                provider["provider_name"],
                provider["provider_type"],
                provider["configured_state"],
                int(provider["requires_key"]),
                provider.get("rate_limit"),
                provider["license_note"],
                provider.get("last_checked_at"),
                now,
            ),
        )


def _provider_by_id(provider_id: str) -> dict[str, Any]:
    for provider in PROVIDER_REGISTRY:
        if provider["provider_id"] == provider_id:
            return provider
    raise ValueError(f"PROVIDER_NOT_CONFIGURED: unknown market provider {provider_id}")


def _provider_configured(provider: dict[str, Any]) -> bool:
    keys = provider.get("env_keys") or []
    return bool(keys) and all(os.environ.get(key, "").strip() for key in keys)


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_city_filters(query: str, city_filters: list[str]) -> list[str]:
    cities = [city for city in city_filters if city in CITY_REGION]
    for city in CITY_REGION:
        if city in query and city not in cities:
            cities.append(city)
    return cities


def _build_snapshot(
    workspace_id: str,
    run_id: str,
    query: str,
    posts: list[dict[str, Any]],
    source_refs: list[str],
    source_policy: str,
) -> dict[str, Any]:
    city_counts: dict[str, int] = {}
    salary_bins = {"15-25k": 0, "25-35k": 0, "35k+": 0}
    tech_counts: dict[str, int] = {}
    confidence_values: list[float] = []
    for post in posts:
        city_counts[post["city"]] = city_counts.get(post["city"], 0) + 1
        salary = post["salary_range"]
        if "40" in salary or "38" in salary or "36" in salary:
            salary_bins["35k+"] += 1
        elif "30" in salary or "34" in salary:
            salary_bins["25-35k"] += 1
        else:
            salary_bins["15-25k"] += 1
        for tech in post["tech_stack"]:
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        confidence_values.append(float(post["confidence"]))
    city_stats = [
        {
            "city": city,
            "region_code": CITY_REGION.get(city, "000000"),
            "job_count": count,
            "source_refs": [post["source_ref_id"] for post in posts if post["city"] == city],
            "confidence": round(sum(post["confidence"] for post in posts if post["city"] == city) / count, 2),
        }
        for city, count in sorted(city_counts.items(), key=lambda item: item[1], reverse=True)
    ]
    return {
        "snapshot_id": f"market_snapshot_{uuid4().hex}",
        "workspace_id": workspace_id,
        "run_id": run_id,
        "query": query.strip(),
        "city_stats": city_stats,
        "salary_histogram": [{"range": key, "count": value} for key, value in salary_bins.items()],
        "tech_heatmap": [{"tech": key, "count": value} for key, value in sorted(tech_counts.items(), key=lambda item: item[1], reverse=True)[:10]],
        "source_breakdown": {source_policy: len(posts)},
        "remote_ratio": 0.2,
        "competition_level": "中等",
        "trend_summary": "本地 Level 1 样本显示 LLM/Agent/可视化相关前端岗位集中在一线与新一线城市；该结论不能替代真实市场 provider。",
        "low_confidence_notes": [
            "当前 snapshot 来自 fixture/manual/public sample，不代表全网岗位量。",
            "缺少真实 provider invocation log，因此不能声明 Level 2 通过。",
        ],
        "source_refs": source_refs,
    }


def _log_invocation(
    *,
    workspace_id: str | None,
    provider_id: str,
    run_id: str | None,
    query_summary: dict[str, Any],
    status: str,
    duration_ms: int,
    error_code: str | None,
) -> str:
    invocation_id = f"market_inv_{uuid4().hex}"
    if workspace_id:
        conn, _ = workspace_conn(workspace_id)
        conn.execute(
            """
            INSERT INTO market_provider_invocation_logs (
              invocation_id, workspace_id, provider_id, run_id, query_summary,
              status, duration_ms, error_code, redacted, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                invocation_id,
                workspace_id,
                provider_id,
                run_id,
                dumps(query_summary),
                status,
                duration_ms,
                error_code,
                1,
                _now(),
            ),
        )
    return invocation_id
