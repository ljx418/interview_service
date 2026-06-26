#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.tools.core import extract_text_from_path


DEFAULT_SCENARIO = ROOT / ".tmp/p5-real-data-closure.scenario.json"
DEFAULT_MANIFEST = ROOT / ".tmp/p5-real-data-closure.manifest.json"
DEFAULT_REPORT = ROOT / "docs/reports/P5_REAL_DATA_CLOSURE_ACCEPTANCE_REPORT.html"
DEFAULT_OUTPUT_DIR = ROOT / "docs/reports/p5-real-data-closure-evidence"
DEFAULT_WORKSPACE_ROOT = ROOT / ".tmp/p5_real_workspace"


def fail(message: str) -> None:
    print(f"P5-REAL gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


def env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        fail(f"missing required environment variable {name}")
    return value


def resolve_input_path(raw: str) -> Path:
    if re.match(r"^[A-Za-z]:[\\/]", raw):
        converted = subprocess.run(["wslpath", "-a", raw], check=False, capture_output=True, text=True)
        if converted.returncode != 0:
            fail("Windows path could not be converted with wslpath")
        raw = converted.stdout.strip()
    path = Path(raw).expanduser().resolve()
    if not path.exists() or not path.is_file():
        fail("one configured data path does not point to a readable file")
    return path


def text_quality(path: Path, label: str, min_chars: int) -> dict:
    text = extract_text_from_path(path)
    compact = re.sub(r"\s+", "", text)
    if len(compact) < min_chars:
        fail(f"{label} text extraction is too short; provide UTF-8 text/Markdown or a parseable text PDF")
    readable = sum(1 for char in compact if char.isalnum() or "\u4e00" <= char <= "\u9fff")
    ratio = readable / max(len(compact), 1)
    if ratio < 0.35:
        fail(f"{label} text extraction looks unreadable; do not treat this file as accepted real data")
    return {
        "filename": path.name,
        "chars": len(text),
        "compact_chars": len(compact),
        "readable_ratio": round(ratio, 3),
    }


def scenario_for(resume: Path, project: Path, jd_text: str, workspace_root: Path, output_dir: Path, report: Path) -> dict:
    url = f"http://127.0.0.1:5173/?workspace_root={workspace_root.as_posix()}&acceptance_redaction=summary"
    api = "http://127.0.0.1:8000"
    root = workspace_root.as_posix()
    resume_path = resume.as_posix()
    project_path = project.as_posix()
    redaction_css = """
(() => {
  document.documentElement.dataset.p5RealRedaction = 'summary';
  const style = document.createElement('style');
  style.id = 'p5-real-redaction-style';
  style.textContent = `
    [data-p5-real-redaction="summary"] .message,
    [data-p5-real-redaction="summary"] .message-bubble,
    [data-p5-real-redaction="summary"] .artifact-card p,
    [data-p5-real-redaction="summary"] .artifact-card li,
    [data-p5-real-redaction="summary"] .artifact-card pre,
    [data-p5-real-redaction="summary"] .artifact-card code,
    [data-p5-real-redaction="summary"] textarea {
      color: transparent !important;
      text-shadow: 0 0 8px rgba(45, 55, 72, 0.55) !important;
    }
    [data-p5-real-redaction="summary"] button,
    [data-p5-real-redaction="summary"] .badge,
    [data-p5-real-redaction="summary"] .status-chip,
    [data-p5-real-redaction="summary"] .artifact-card h1,
    [data-p5-real-redaction="summary"] .artifact-card h2,
    [data-p5-real-redaction="summary"] .artifact-card h3 {
      color: inherit !important;
      text-shadow: none !important;
    }
  `;
  document.head.appendChild(style);
  return true;
})()
""".strip()
    provider_guard = f"""
(async () => {{
  const response = await fetch('{api}/api/provider/status');
  const payload = await response.json();
  const status = payload.data || payload;
  if (status.provider && status.provider !== 'mock') {{
    throw new Error('P5-REAL requires mock/local provider. Current provider: ' + status.provider);
  }}
  return status.provider || 'mock';
}})()
""".strip()
    ingest_expression = f"""
(async () => {{
  const root = {json.dumps(root, ensure_ascii=False)};
  const api = {json.dumps(api)};
  const status = await fetch(`${{api}}/api/workspace/status?root_path=${{encodeURIComponent(root)}}`).then((r) => r.json());
  const workspaceId = status.data.workspace_id || status.data.id;
  const qs = (obj) => new URLSearchParams(obj).toString();
  await fetch(`${{api}}/api/files/ingest-local?${{qs({{workspace_id: workspaceId, source_path: {json.dumps(resume_path, ensure_ascii=False)}, kind: 'resume'}})}}`, {{ method: 'POST' }});
  await fetch(`${{api}}/api/files/ingest-local?${{qs({{workspace_id: workspaceId, source_path: {json.dumps(project_path, ensure_ascii=False)}, kind: 'project'}})}}`, {{ method: 'POST' }});
  await fetch(`${{api}}/api/profile/extract-facts`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ workspace_id: workspaceId, target_roles: ['Junior Frontend Developer'] }}),
  }});
  return workspaceId;
}})()
""".strip()
    return {
        "name": "P5-REAL 真实授权资料本地闭环验收",
        "goal": "使用用户明确指定的简历、项目资料和目标 JD，在 mock/local 边界内完成真实资料本地闭环；报告只展示脱敏摘要，不证明真实外部 provider 或产品化发布通过。",
        "url": url,
        "targetArchitecture": [
            "Chatbox UI：展示本地资料入口、事实确认、申请包产物、导出和连续追问状态。",
            "FastAPI API：复用 workspace、ingest-local、profile、job、application、artifact 和 export 接口。",
            "JobPilot Domain Tools：从用户指定文件抽取事实、项目证据、岗位要求、匹配报告和申请包。",
            "Provider Policy Gate：P5-REAL 强制 mock/local；真实外部 provider 转入 P6 opt-in。",
            "Evidence Layer：Chrome/CDP 截图、脱敏 HTML 报告、PRD 规格检视和隐私审计。",
        ],
        "currentImplementation": [
            "真实资料路径只来自 JOBPILOT_REAL_RESUME_PATH、JOBPILOT_REAL_PROJECT_PATH、JOBPILOT_REAL_JD_PATH。",
            "脚本生成临时 .tmp scenario；真实原文和绝对路径不得进入仓库文档或最终报告正文。",
            "浏览器截图前注入 redacted summary 样式，隐藏消息正文、资料预览、source quote 和长文本。",
            "未确认 blocking questions_to_confirm 时导出必须失败；确认事实后允许 Markdown/DOCX 导出。",
        ],
        "acceptanceCriteria": [
            "只读取用户指定的三个文件，不递归扫描个人目录。",
            "文本抽取质量通过，不把空文本、乱码或二进制噪声写成解析成功。",
            "P5-REAL 使用 mock/local provider，不配置、不调用 MiniMax、DeepSeek 或 OpenAI-compatible。",
            "完成资料导入、JD 解析、匹配报告、申请包、导出拦截、事实确认、导出和连续追问。",
            "报告截图只展示脱敏摘要；不得出现联系方式、账号、API Key、私密链接或未授权长原文。",
            "报告明确 P5 尚未因本步骤自动冻结，P5-Freeze 仍需最终回归、人工体验记录和 final closure audit。",
        ],
        "prdReview": [
            {"requirement": "P5-REAL 使用真实授权资料完成本地闭环。", "evidence": "场景由三个用户指定文件路径生成，且不递归扫描目录。", "status": "PENDING UNTIL RUN"},
            {"requirement": "P5 默认不调用真实外部 provider。", "evidence": "Provider guard 在浏览器场景开始时检查 provider/status。", "status": "PENDING UNTIL RUN"},
            {"requirement": "报告必须脱敏。", "evidence": "截图前注入 redacted summary 样式，并在报告中列出隐私边界。", "status": "PENDING UNTIL RUN"},
            {"requirement": "blocking confirmation 未处理不得导出。", "evidence": "场景先触发未确认导出失败，再确认事实并导出。", "status": "PENDING UNTIL RUN"},
        ],
        "documentationAudit": [
            {"area": "P5/P6 边界", "finding": "P5-REAL 不启用真实 provider；provider-backed 能力仍属于 P6 opt-in。", "status": "pass"},
            {"area": "P5.5 职业画像", "finding": "职业画像与能力评估不插入 P5 冻结范围，作为 P5.5 候选阶段。", "status": "pass"},
        ],
        "unverifiedScope": [
            "未验证真实外部 provider、provider-backed 自由智能聊天、SaaS、ASR、会议平台、自动投递或 MCP/CLI。",
            "未证明最终产品化发布通过。",
            "未替代人工体验审查；P5-Freeze 仍需 final closure audit。",
        ],
        "auditOpinion": "该报告若执行通过，只能支持 P5-REAL 真实授权资料本地闭环通过；P5 冻结仍需 P5-Freeze 复验。",
        "commandResults": [
            {"command": "scripts/generate_p5_real_data_acceptance.py", "status": "planned", "evidence": "生成临时场景前完成路径、provider 和文本抽取质量检查。"},
            {"command": "node scripts/browser_tools/browser-acceptance.mjs --scenario .tmp/p5-real-data-closure.scenario.json", "status": "pending", "evidence": "执行真实界面截图并生成 HTML 报告。"},
        ],
        "viewports": [
            {"name": "desktop", "width": 1440, "height": 980},
            {"name": "desktop1200", "width": 1200, "height": 900},
            {"name": "desktop1600", "width": 1600, "height": 1000},
            {"name": "desktop1920", "width": 1920, "height": 1080},
            {"name": "narrow720", "width": 720, "height": 900},
            {"name": "mobile", "width": 390, "height": 844, "mobile": True},
        ],
        "steps": [
            {"name": "Open Chatbox", "action": "goto", "url": url, "viewport": "desktop"},
            {"name": "Wait for local workspace", "action": "waitText", "text": "本地就绪", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "Provider guard", "action": "evaluate", "expression": provider_guard, "viewport": "desktop"},
            {"name": "Enable redacted screenshot mode", "action": "evaluate", "expression": redaction_css, "viewport": "desktop"},
            {"name": "Initial redacted P5-REAL state", "action": "screenshot", "file": "p5_real_initial_redacted.png", "viewport": "desktop"},
            {"name": "Ingest authorized local materials", "action": "evaluate", "expression": ingest_expression, "viewport": "desktop"},
            {"name": "Fill authorized JD", "action": "fill", "selector": "textarea[aria-label='对话输入框']", "value": jd_text, "viewport": "desktop"},
            {"name": "Send JD", "action": "clickText", "text": "发送任务", "viewport": "desktop"},
            {"name": "Wait JD parsed", "action": "waitText", "text": "我已解析岗位并生成适合度分析", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "JD and match redacted evidence", "action": "screenshot", "file": "p5_real_jd_match_redacted.png", "viewport": "desktop"},
            {"name": "Fill package request", "action": "fill", "selector": "textarea[aria-label='对话输入框']", "value": "请基于当前资料和目标 JD，生成申请包草稿。", "viewport": "desktop"},
            {"name": "Send package request", "action": "clickText", "text": "发送任务", "viewport": "desktop"},
            {"name": "Wait package generated", "action": "waitText", "text": "申请包已生成，请先确认事实再导出", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "Package needs confirmation redacted evidence", "action": "screenshot", "file": "p5_real_package_needs_confirmation_redacted.png", "viewport": "desktop"},
            {
                "name": "Try export before confirmation",
                "action": "evaluate",
                "viewport": "desktop",
                "expression": "(() => { const cards=Array.from(document.querySelectorAll('.artifact-card')); const card=cards.find((node)=>node.innerText.includes('申请包草稿') || node.innerText.includes('申请包')); if (!card) throw new Error('Application package artifact card not found'); card.scrollIntoView({block:'center'}); const button=Array.from(card.querySelectorAll('button')).find((node)=>node.innerText.trim()==='导出'); if (!button) throw new Error('Export button not found in package card'); button.click(); return true; })()",
            },
            {"name": "Wait export blocked", "action": "waitText", "text": "EXPORT_PRECHECK_FAILED", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "Blocked export redacted evidence", "action": "screenshot", "file": "p5_real_export_blocked_redacted.png", "viewport": "desktop"},
            {
                "name": "Confirm package facts",
                "action": "evaluate",
                "viewport": "desktop",
                "expression": "(() => { const cards=Array.from(document.querySelectorAll('.artifact-card')); const card=cards.find((node)=>node.innerText.includes('申请包草稿') || node.innerText.includes('申请包')); if (!card) throw new Error('Application package artifact card not found'); card.scrollIntoView({block:'center'}); const button=Array.from(card.querySelectorAll('button')).find((node)=>node.innerText.trim()==='确认事实'); if (!button) throw new Error('Confirm button not found in package card'); button.click(); return true; })()",
            },
            {"name": "Wait package confirmed", "action": "waitText", "text": "产物已确认", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "Confirmed package redacted evidence", "action": "screenshot", "file": "p5_real_package_confirmed_redacted.png", "viewport": "desktop"},
            {
                "name": "Export after confirmation",
                "action": "evaluate",
                "viewport": "desktop",
                "expression": "(() => { const cards=Array.from(document.querySelectorAll('.artifact-card')); const card=cards.find((node)=>node.innerText.includes('申请包草稿') || node.innerText.includes('申请包')); if (!card) throw new Error('Application package artifact card not found'); card.scrollIntoView({block:'center'}); const button=Array.from(card.querySelectorAll('button')).find((node)=>node.innerText.trim()==='导出'); if (!button) throw new Error('Export button not found in package card after confirmation'); button.click(); return true; })()",
            },
            {"name": "Wait export completed", "action": "waitText", "text": "申请包已导出到本地", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "Export completed redacted evidence", "action": "screenshot", "file": "p5_real_export_completed_redacted.png", "viewport": "desktop"},
            {"name": "Export completed 1200 redacted evidence", "action": "screenshot", "file": "p5_real_export_completed_1200_redacted.png", "viewport": "desktop1200"},
            {"name": "Export completed 1600 redacted evidence", "action": "screenshot", "file": "p5_real_export_completed_1600_redacted.png", "viewport": "desktop1600"},
            {"name": "Export completed 1920 redacted evidence", "action": "screenshot", "file": "p5_real_export_completed_1920_redacted.png", "viewport": "desktop1920"},
            {"name": "Narrow exported layout redacted evidence", "action": "screenshot", "file": "p5_real_export_completed_720_redacted.png", "viewport": "narrow720"},
            {"name": "Mobile exported layout redacted evidence", "action": "screenshot", "file": "p5_real_export_completed_mobile_redacted.png", "viewport": "mobile"},
        ],
    }


def main() -> int:
    provider = os.environ.get("JOBPILOT_LLM_PROVIDER", "mock").strip().lower() or "mock"
    if provider not in {"mock", "fixture"}:
        fail("JOBPILOT_LLM_PROVIDER must be mock or fixture for P5-REAL")

    resume = resolve_input_path(env("JOBPILOT_REAL_RESUME_PATH"))
    project = resolve_input_path(env("JOBPILOT_REAL_PROJECT_PATH"))
    jd = resolve_input_path(env("JOBPILOT_REAL_JD_PATH"))
    workspace_root = Path(os.environ.get("JOBPILOT_REAL_WORKSPACE_ROOT", str(DEFAULT_WORKSPACE_ROOT))).expanduser().resolve()
    scenario_path = Path(os.environ.get("JOBPILOT_REAL_SCENARIO_PATH", str(DEFAULT_SCENARIO))).expanduser().resolve()
    manifest_path = Path(os.environ.get("JOBPILOT_REAL_MANIFEST_PATH", str(DEFAULT_MANIFEST))).expanduser().resolve()
    report = Path(os.environ.get("JOBPILOT_REAL_REPORT_PATH", str(DEFAULT_REPORT))).expanduser().resolve()
    output_dir = Path(os.environ.get("JOBPILOT_REAL_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))).expanduser().resolve()

    metrics = {
        "resume": text_quality(resume, "resume", 120),
        "project": text_quality(project, "project", 80),
        "jd": text_quality(jd, "target JD", 40),
    }
    jd_text = extract_text_from_path(jd)
    scenario = scenario_for(resume, project, jd_text, workspace_root, output_dir, report)

    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_path.write_text(
        json.dumps(
            {
                "stage": "P5-REAL",
                "visibility": "redacted_summary",
                "provider": provider,
                "workspace_root": workspace_root.as_posix(),
                "report": report.as_posix(),
                "output_dir": output_dir.as_posix(),
                "file_metrics": metrics,
                "warning": "This manifest intentionally omits source absolute paths and raw document text.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"scenario={scenario_path}")
    print(f"manifest={manifest_path}")
    print(f"report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
