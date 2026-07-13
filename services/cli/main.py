from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_WORKSPACE_DIR = ".jobpilot_workspace"
FORBIDDEN_TOKENS = {
    "real-provider",
    "real_provider",
    "platform-scrape",
    "platform_scrape",
    "source-url-fetch",
    "source_url_fetch",
    "asr",
    "mcp",
    "auto-apply",
    "auto_apply",
    "cleanup",
    "delete",
    "migration",
    "migrate",
    "generate-report",
    "report-generate",
}


EXIT_SUCCESS = 0
EXIT_INVALID_ARGUMENT = 1
EXIT_SERVICE_UNAVAILABLE = 2
EXIT_WORKSPACE_NOT_FOUND = 3
EXIT_SAFETY_BLOCKED = 4
EXIT_EMPTY_RESULT = 5
EXIT_INTERNAL_ERROR = 10


@dataclass
class CliError(Exception):
    code: str
    message: str
    exit_code: int
    hint: str = ""
    retryable: bool = False


@dataclass
class CliResult:
    command: str
    workspace_id: str | None = None
    data_source: list[str] = field(default_factory=list)
    provider_state: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


def json_default(value: Any) -> str:
    return str(value)


def success_envelope(result: CliResult) -> dict[str, Any]:
    return {
        "ok": True,
        "command": result.command,
        "workspace_id": result.workspace_id,
        "data_source": result.data_source,
        "provider_state": result.provider_state,
        "data": result.data,
        "warnings": result.warnings,
        "next_actions": result.next_actions,
        "meta": {**result.meta, "redacted": True},
    }


def failure_envelope(command: str, error: CliError, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "command": command,
        "error": {
            "code": error.code,
            "message": error.message,
            "hint": error.hint,
            "retryable": error.retryable,
        },
        "exit_code": error.exit_code,
        "meta": {**(meta or {}), "redacted": True},
    }


class ApiClient:
    def __init__(self, api_url: str, timeout: float = 10.0) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, query: dict[str, Any] | None = None, *, timeout: float | None = None) -> Any:
        url = self._url(path, query)
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        return self._request(req, timeout=timeout)

    def post(self, path: str, body: dict[str, Any], *, timeout: float | None = None) -> Any:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self._url(path),
            data=data,
            method="POST",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        return self._request(req, timeout=timeout)

    def _url(self, path: str, query: dict[str, Any] | None = None) -> str:
        url = f"{self.api_url}{path}"
        clean = {k: v for k, v in (query or {}).items() if v is not None}
        if clean:
            url = f"{url}?{urllib.parse.urlencode(clean)}"
        return url

    def _request(self, req: urllib.request.Request, *, timeout: float | None = None) -> Any:
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            if exc.code in {502, 503, 504}:
                raise CliError(
                    "SERVICE_UNAVAILABLE",
                    f"本地 FastAPI 服务不可用：HTTP {exc.code}",
                    EXIT_SERVICE_UNAVAILABLE,
                    "请确认服务已启动并监听正确端口，CLI 不会自动启动后台服务。",
                    retryable=True,
                ) from exc
            raise CliError("API_ERROR", f"本地 API 返回错误：HTTP {exc.code}", EXIT_INTERNAL_ERROR, message) from exc
        except urllib.error.URLError as exc:
            raise CliError(
                "SERVICE_UNAVAILABLE",
                "本地 FastAPI 服务不可用。",
                EXIT_SERVICE_UNAVAILABLE,
                "请先运行 uvicorn services.api.main:app --reload，CLI 不会自动启动后台服务。",
                retryable=True,
            ) from exc
        except TimeoutError as exc:
            raise CliError(
                "SERVICE_UNAVAILABLE",
                "本地 FastAPI 服务连接超时。",
                EXIT_SERVICE_UNAVAILABLE,
                "请确认服务已启动并监听正确端口。",
                retryable=True,
            ) from exc
        return json.loads(raw) if raw else {}


def resolve_workspace(path_arg: str | None) -> tuple[Path, str]:
    raw = path_arg or os.environ.get("JOBPILOT_WORKSPACE") or DEFAULT_WORKSPACE_DIR
    root = Path(raw).expanduser().resolve()
    source = "--workspace" if path_arg else ("JOBPILOT_WORKSPACE" if os.environ.get("JOBPILOT_WORKSPACE") else "cwd_default")
    if not root.exists() or not (root / "jobpilot.db").exists():
        raise CliError(
            "WORKSPACE_NOT_FOUND",
            f"本地 workspace 不存在或未初始化：{root}",
            EXIT_WORKSPACE_NOT_FOUND,
            "请传入 --workspace，设置 JOBPILOT_WORKSPACE，或在当前目录初始化 .jobpilot_workspace。",
            retryable=True,
        )
    return root, source


def workspace_id_from_status(status: Any) -> str | None:
    if isinstance(status, dict):
        if isinstance(status.get("data"), dict):
            return status["data"].get("workspace_id") or status["data"].get("id")
        return status.get("workspace_id") or status.get("id")
    return None


def api_payload(response: Any) -> Any:
    if isinstance(response, dict) and response.get("ok") is True and "data" in response:
        return response["data"]
    return response


def check_safety(raw_args: list[str], command: str) -> None:
    joined = " ".join(raw_args).lower()
    for token in FORBIDDEN_TOKENS:
        if token in joined:
            raise CliError(
                "SAFETY_BLOCKED",
                f"命令被安全门拒绝：{token}",
                EXIT_SAFETY_BLOCKED,
                "P10-CLI 默认不执行真实外呼、平台抓取、ASR、MCP、报告生成或不可逆 workspace 操作。",
            )
    if command == "reports open" and ("generate" in joined or "生成" in joined):
        raise CliError("SAFETY_BLOCKED", "reports open 只定位/打开已有报告，不生成报告。", EXIT_SAFETY_BLOCKED)


def audit_log(workspace_root: Path | None, command: str, exit_code: int, ok: bool) -> None:
    base = workspace_root if workspace_root else Path(".tmp")
    try:
        base.mkdir(parents=True, exist_ok=True)
        path = base / "jobpilot-cli-audit.jsonl"
        record = {
            "ts": int(time.time()),
            "command": command,
            "exit_code": exit_code,
            "ok": ok,
            "redacted": True,
            "api_key_recorded": False,
            "full_personal_data_recorded": False,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def find_latest_report() -> Path:
    reports = sorted(Path("docs/reports").glob("*.html"), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    if not reports:
        raise CliError("EMPTY_RESULT", "未找到本地 HTML 验收报告。", EXIT_EMPTY_RESULT, "请先运行对应阶段验收脚本。")
    return reports[0].resolve()


def to_windows_path(path: Path) -> str | None:
    try:
        result = subprocess.run(["wslpath", "-w", str(path)], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def command_workspace_status(args: argparse.Namespace) -> CliResult:
    workspace_root, source = resolve_workspace(args.workspace)
    client = ApiClient(args.api_url)
    health = client.get("/api/health", timeout=3)
    workspace = api_payload(client.get("/api/workspace/status", {"root_path": str(workspace_root)}, timeout=5))
    workspace_id = workspace_id_from_status(workspace)
    provider = api_payload(client.get("/api/provider/status", {"workspace_id": workspace_id}, timeout=5)) if workspace_id else {}
    runtime = api_payload(client.get("/api/provider/runtime-config", {"workspace_id": workspace_id}, timeout=5)) if workspace_id else {}
    market = api_payload(client.get("/api/market/providers/status", {"workspace_id": workspace_id}, timeout=5)) if workspace_id else {}
    reports = sorted(Path("docs/reports").glob("*.html"))
    provider_state = {
        "configured": bool(provider.get("configured") or runtime.get("api_key_configured")),
        "consented": bool(provider.get("consented", False)),
        "called": bool(provider.get("called", False)),
        "fallback": provider.get("provider") or "mock",
        "market_level": market.get("level"),
        "market_external_call_enabled": bool(market.get("external_call_enabled", False)),
        "market_can_claim_real_market": bool(market.get("can_claim_real_market", False)),
    }
    return CliResult(
        command="workspace status",
        workspace_id=workspace_id,
        data_source=["local_api", "workspace", "reports"],
        provider_state=provider_state,
        data={
            "health": health,
            "workspace": workspace,
            "workspace_root": str(workspace_root),
            "workspace_source": source,
            "reports_count": len(reports),
            "latest_report": str(reports[-1]) if reports else None,
            "market_provider_state": market,
        },
        next_actions=["运行 demo run --example 验证 examples 路径。"],
        meta={"api_url": args.api_url},
    )


def command_demo_run(args: argparse.Namespace) -> CliResult:
    workspace_root, _ = resolve_workspace(args.workspace)
    client = ApiClient(args.api_url)
    workspace = api_payload(client.get("/api/workspace/status", {"root_path": str(workspace_root)}, timeout=5))
    workspace_id = workspace_id_from_status(workspace)
    body = {"workspace_id": workspace_id, "reset_workspace": False, "data_mode": "example"}
    demo = api_payload(client.post("/api/workflows/p2-demo/run", body, timeout=60))
    return CliResult(
        command="demo run --example",
        workspace_id=demo.get("workspace_id") or workspace_id,
        data_source=["local_api", "examples", "fixture"],
        provider_state={"configured": False, "consented": False, "called": False, "fallback": "mock"},
        data={"summary": demo.get("summary"), "steps": demo.get("steps", []), "provider_mode": demo.get("provider_mode")},
        warnings=["本命令只运行 examples / fixture 路径，不代表真实个人资料或真实 provider 验收通过。"],
        meta={"api_url": args.api_url},
    )


def command_jobs_list(args: argparse.Namespace) -> CliResult:
    workspace_root, _ = resolve_workspace(args.workspace)
    client = ApiClient(args.api_url)
    workspace = api_payload(client.get("/api/workspace/status", {"root_path": str(workspace_root)}, timeout=5))
    workspace_id = workspace_id_from_status(workspace)
    jobs = api_payload(client.get("/api/jobs", {"workspace_id": workspace_id}, timeout=10))
    rows = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
    if not rows:
        raise CliError("EMPTY_RESULT", "当前 workspace 没有本地岗位。", EXIT_EMPTY_RESULT, "请先导入 JD 或运行 demo run --example。")
    summarized = [
        {
            "job_id": row.get("id") or row.get("job_id"),
            "title": row.get("title"),
            "city": row.get("location") or row.get("city"),
            "source_url_present": bool(row.get("source_url")),
            "is_current": bool(row.get("is_current") or row.get("current")),
        }
        for row in rows
    ]
    return CliResult("jobs list", workspace_id, ["local_api", "workspace"], data={"jobs": summarized}, meta={"api_url": args.api_url})


def command_artifacts_list(args: argparse.Namespace) -> CliResult:
    workspace_root, _ = resolve_workspace(args.workspace)
    client = ApiClient(args.api_url)
    workspace = api_payload(client.get("/api/workspace/status", {"root_path": str(workspace_root)}, timeout=5))
    workspace_id = workspace_id_from_status(workspace)
    artifacts = api_payload(client.get("/api/artifacts", {"workspace_id": workspace_id}, timeout=10))
    rows = artifacts if isinstance(artifacts, list) else artifacts.get("artifacts", [])
    if not rows:
        raise CliError("EMPTY_RESULT", "当前 workspace 没有本地产物。", EXIT_EMPTY_RESULT, "请先运行 demo run --example。")
    summarized = [
        {
            "artifact_id": row.get("id") or row.get("artifact_id"),
            "type": row.get("artifact_type") or row.get("type"),
            "status": row.get("status"),
            "current_version_id": row.get("current_version_id"),
            "updated_at": row.get("updated_at"),
        }
        for row in rows
    ]
    return CliResult("artifacts list", workspace_id, ["local_api", "workspace"], data={"artifacts": summarized}, meta={"api_url": args.api_url})


def command_artifacts_show(args: argparse.Namespace) -> CliResult:
    workspace_root, _ = resolve_workspace(args.workspace)
    client = ApiClient(args.api_url)
    workspace = api_payload(client.get("/api/workspace/status", {"root_path": str(workspace_root)}, timeout=5))
    workspace_id = workspace_id_from_status(workspace)
    versions = api_payload(client.get(f"/api/artifacts/{args.artifact_id}/versions", {"workspace_id": workspace_id}, timeout=10))
    rows = versions if isinstance(versions, list) else versions.get("versions", [])
    if not rows:
        raise CliError("EMPTY_RESULT", f"未找到 artifact 版本：{args.artifact_id}", EXIT_EMPTY_RESULT)
    version_id = args.version or rows[0].get("version_id") or rows[0].get("id")
    content = api_payload(client.get(f"/api/artifacts/{args.artifact_id}/versions/{version_id}", {"workspace_id": workspace_id}, timeout=10))
    payload = content.get("content_json") if isinstance(content, dict) else {}
    if not isinstance(payload, dict):
        payload = {"summary": str(payload)[:500]}
    summary = {
        "artifact_id": args.artifact_id,
        "version_id": version_id,
        "artifact_type": content.get("artifact_type") if isinstance(content, dict) else None,
        "status": content.get("status") if isinstance(content, dict) else None,
        "source_refs": payload.get("source_refs", [])[:8],
        "pending_confirmations": payload.get("pending_confirmations") or payload.get("questions_to_confirm") or [],
        "content_keys": sorted(payload.keys())[:20],
    }
    return CliResult("artifacts show", workspace_id, ["local_api", "workspace"], data={"artifact": summary}, meta={"api_url": args.api_url})


def command_reports_open(args: argparse.Namespace) -> CliResult:
    report = find_latest_report()
    windows_path = to_windows_path(report)
    opened = False
    warnings: list[str] = []
    if not args.no_browser:
        try:
            opened = webbrowser.open(report.as_uri())
        except Exception as exc:  # pragma: no cover - platform dependent
            warnings.append(f"浏览器打开失败：{exc}")
    return CliResult(
        "reports open",
        data_source=["local_report"],
        data={"report_path": str(report), "windows_path": windows_path, "opened": opened, "no_browser": bool(args.no_browser)},
        warnings=warnings,
        meta={"report_generated": False},
    )


def render_text(result: CliResult) -> str:
    env = success_envelope(result)
    lines = [f"JobPilot CLI - {result.command}", f"状态：成功", f"workspace_id：{result.workspace_id or '-'}"]
    if result.data_source:
        lines.append(f"数据来源：{', '.join(result.data_source)}")
    if result.provider_state:
        lines.append(f"Provider：{json.dumps(result.provider_state, ensure_ascii=False)}")
    for warning in result.warnings:
        lines.append(f"警告：{warning}")
    if result.next_actions:
        lines.append("下一步：" + "；".join(result.next_actions))
    lines.append("摘要：")
    lines.append(json.dumps(env["data"], ensure_ascii=False, indent=2, default=json_default)[:4000])
    return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jobpilot", description="JobPilot 本地 CLI：只包装本地 API、workspace、artifact 和报告能力。")
    p.add_argument("--api-url", default=os.environ.get("JOBPILOT_API_URL", DEFAULT_API_URL), help="本地 FastAPI 地址，默认 http://127.0.0.1:8000")
    p.add_argument("--json", action="store_true", help="输出机器可读 JSON envelope")
    sub = p.add_subparsers(dest="group")

    ws = sub.add_parser("workspace", help="workspace 状态命令")
    ws_sub = ws.add_subparsers(dest="action")
    ws_status = ws_sub.add_parser("status", help="查看本地服务、workspace、provider 和报告状态")
    ws_status.add_argument("--workspace", help="显式 workspace 路径")

    demo = sub.add_parser("demo", help="examples / fixture 演示命令")
    demo_sub = demo.add_subparsers(dest="action")
    demo_run = demo_sub.add_parser("run", help="运行本地演示路径")
    demo_run.add_argument("--example", action="store_true", help="只允许运行 examples / fixture 路径")
    demo_run.add_argument("--workspace", help="显式 workspace 路径")

    jobs = sub.add_parser("jobs", help="岗位命令")
    jobs_sub = jobs.add_subparsers(dest="action")
    jobs_list = jobs_sub.add_parser("list", help="列出本地岗位")
    jobs_list.add_argument("--workspace", help="显式 workspace 路径")

    artifacts = sub.add_parser("artifacts", help="产物命令")
    art_sub = artifacts.add_subparsers(dest="action")
    art_list = art_sub.add_parser("list", help="列出本地产物")
    art_list.add_argument("--workspace", help="显式 workspace 路径")
    art_show = art_sub.add_parser("show", help="展示产物摘要")
    art_show.add_argument("artifact_id")
    art_show.add_argument("--version")
    art_show.add_argument("--workspace", help="显式 workspace 路径")

    reports = sub.add_parser("reports", help="验收报告命令")
    rep_sub = reports.add_subparsers(dest="action")
    rep_open = rep_sub.add_parser("open", help="打开或列出最近中文 HTML 验收报告")
    rep_open.add_argument("--no-browser", action="store_true", help="只打印路径，不打开浏览器")
    return p


def dispatch(args: argparse.Namespace, raw_args: list[str]) -> CliResult:
    command = f"{args.group or ''} {getattr(args, 'action', '')}".strip()
    check_safety(raw_args, command)
    if args.group == "workspace" and args.action == "status":
        return command_workspace_status(args)
    if args.group == "demo" and args.action == "run":
        if not args.example:
            raise CliError("INVALID_ARGUMENT", "demo run 必须显式传入 --example。", EXIT_INVALID_ARGUMENT)
        return command_demo_run(args)
    if args.group == "jobs" and args.action == "list":
        return command_jobs_list(args)
    if args.group == "artifacts" and args.action == "list":
        return command_artifacts_list(args)
    if args.group == "artifacts" and args.action == "show":
        return command_artifacts_show(args)
    if args.group == "reports" and args.action == "open":
        return command_reports_open(args)
    raise CliError("INVALID_ARGUMENT", "未知或不完整命令。请运行 jobpilot --help。", EXIT_INVALID_ARGUMENT)


def main(argv: list[str] | None = None) -> int:
    raw_args = list(argv if argv is not None else sys.argv[1:])
    p = parser()
    try:
        args, unknown = p.parse_known_args(raw_args)
    except SystemExit as exc:
        return EXIT_SUCCESS if exc.code == 0 else int(exc.code or EXIT_INVALID_ARGUMENT)
    if unknown:
        command_for_unknown = " ".join(raw_args[:2]) if raw_args else ""
        try:
            check_safety(raw_args, command_for_unknown)
        except CliError as exc:
            if "--json" in raw_args:
                print(json.dumps(failure_envelope(command_for_unknown, exc), ensure_ascii=False, indent=2), file=sys.stderr)
            else:
                print(f"JobPilot CLI 错误：{exc.message}", file=sys.stderr)
                if exc.hint:
                    print(f"建议：{exc.hint}", file=sys.stderr)
                print(f"error_code={exc.code} exit_code={exc.exit_code}", file=sys.stderr)
            return exc.exit_code
        print(f"JobPilot CLI 错误：未知参数：{' '.join(unknown)}", file=sys.stderr)
        print(f"error_code=INVALID_ARGUMENT exit_code={EXIT_INVALID_ARGUMENT}", file=sys.stderr)
        return EXIT_INVALID_ARGUMENT
    if not args.group:
        p.print_help()
        return EXIT_SUCCESS
    command = f"{args.group or ''} {getattr(args, 'action', '')}".strip()
    workspace_root: Path | None = None
    try:
        workspace_arg = getattr(args, "workspace", None)
        if workspace_arg or os.environ.get("JOBPILOT_WORKSPACE") or Path(DEFAULT_WORKSPACE_DIR).exists():
            try:
                workspace_root, _ = resolve_workspace(workspace_arg)
            except CliError:
                workspace_root = None
        result = dispatch(args, raw_args)
        audit_log(workspace_root, result.command, EXIT_SUCCESS, True)
        if args.json:
            print(json.dumps(success_envelope(result), ensure_ascii=False, indent=2, default=json_default))
        else:
            print(render_text(result))
        return EXIT_SUCCESS
    except CliError as exc:
        audit_log(workspace_root, command, exc.exit_code, False)
        if getattr(args, "json", False):
            print(json.dumps(failure_envelope(command, exc, {"api_url": getattr(args, "api_url", DEFAULT_API_URL)}), ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            print(f"JobPilot CLI 错误：{exc.message}", file=sys.stderr)
            if exc.hint:
                print(f"建议：{exc.hint}", file=sys.stderr)
            print(f"error_code={exc.code} exit_code={exc.exit_code}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
