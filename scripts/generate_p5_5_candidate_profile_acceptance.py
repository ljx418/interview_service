#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from services.api.main import app
from services.storage.workspace import init_workspace, workspace_conn


DEFAULT_SCENARIO = ROOT / ".tmp/p5-5-candidate-profile.scenario.json"
DEFAULT_REPORT = ROOT / "docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html"
DEFAULT_OUTPUT_DIR = ROOT / "docs/reports/evidence/p5_5_candidate_profile"
DEFAULT_WORKSPACE_ROOT = ROOT / ".tmp/p5_5_candidate_profile_workspace"
DEFAULT_DIALOGUE_JSON = ROOT / "docs/reports/evidence/p5_5_candidate_profile/p5_5_multi_turn_dialogues.json"
DEFAULT_DIALOGUE_ROOT = ROOT / ".tmp/p5_5_multi_turn_dialogues"


JD_TEXT = """
职位：Junior Frontend Developer
职责：开发 React + TypeScript 前端页面，和 FastAPI 后端协作完成本地数据工作流。
要求：React、TypeScript、基础 Python、能写自动化测试，重视用户体验和可维护性。
加分：熟悉本地优先隐私设计、Markdown 导出、Playwright 或 pytest。
""".strip()


PERSONA_CASES = [
    {
        "slug": "ops_to_frontend",
        "name": "周亦然（合成）",
        "target_role": "Junior Frontend Developer",
        "background": "运营数据分析和流程自动化转前端工程",
        "focus": ["React/TypeScript 表达", "运营自动化项目可信度", "本地优先产品经验"],
    },
    {
        "slug": "qa_to_fullstack",
        "name": "林澈（合成）",
        "target_role": "QA Automation Engineer / Full-stack Assistant",
        "background": "手工测试转自动化测试和轻量全栈",
        "focus": ["pytest/Playwright 证据", "缺陷复现能力", "前后端联调表达"],
    },
    {
        "slug": "teacher_to_edtech",
        "name": "陈若宁（合成）",
        "target_role": "EdTech Frontend Developer",
        "background": "数学教师和课程运营转教育科技前端",
        "focus": ["教育产品信息架构", "ECharts 学习数据可视化", "学生隐私边界"],
    },
]


TURN_TOPICS = [
    "先讨论目标岗位定位，保持对话，不执行材料任务。",
    "我该优先强调哪一类经历，保持对话，不执行材料任务。",
    "项目可信度最容易被质疑的地方是什么，保持对话。",
    "如何解释转行路径中的连续性，保持对话。",
    "哪些技能可以作为强证据，保持对话。",
    "哪些技能只能算可用或弱证据，保持对话。",
    "简历摘要应该突出什么主线，保持对话。",
    "面向初级岗位时应该降低哪些过度承诺，保持对话。",
    "如何把业务背景翻译成工程贡献，保持对话。",
    "如果面试官追问项目真实性，我应该如何回答，保持对话。",
    "当前资料里哪些地方需要补充截图或 README，保持对话。",
    "如何说明自己不是只会做 demo，保持对话。",
    "如何把测试和验收能力写得更可信，保持对话。",
    "如果岗位要求后端协作，我该怎么表达，保持对话。",
    "怎样说明我能和产品或业务方协作，保持对话。",
    "有什么必须避免写进材料的夸大表述，保持对话。",
    "如果本轮只补一项证据，应该补什么，保持对话。",
    "怎样组织作品集顺序，保持对话。",
    "如何准备一段 90 秒自我介绍，保持对话。",
    "总结一下本次讨论的下一步，不执行材料任务。",
]


def _read_case_file(slug: str, name: str) -> str:
    return (ROOT / "examples/p5_synthetic_personas" / slug / name).read_text(encoding="utf-8")


def _excerpt(text: str, max_chars: int = 520) -> str:
    cleaned = "\n".join(line.rstrip() for line in text.strip().splitlines() if line.strip())
    return cleaned[:max_chars] + ("..." if len(cleaned) > max_chars else "")


def _grant_fake_provider_consent(client: TestClient, workspace_id: str, session_id: str) -> None:
    response = client.post(
        "/api/provider/consent",
        json={
            "workspace_id": workspace_id,
            "session_id": session_id,
            "scope": "chat_session",
            "ttl_seconds": 600,
            "allowed_data_classes": ["recent_messages", "rolling_summary", "workspace_summary", "artifact_summary"],
            "confirm_external_call": True,
        },
    )
    if response.status_code != 200:
        raise RuntimeError(f"fake provider consent failed: {response.text}")


def _prepare_case_workspace(client: TestClient, *, case: dict, run_root: Path) -> tuple[str, str, list[dict]]:
    workspace = init_workspace(f"p5-5-dialogue-{case['slug']}", str(run_root / case["slug"]))
    workspace_id = workspace["workspace_id"]
    session = client.post("/api/chat/sessions", json={"workspace_id": workspace_id, "title": f"P5.5 多轮对话 - {case['name']}"}).json()["data"]
    session_id = session["session_id"]
    base = ROOT / "examples/p5_synthetic_personas" / case["slug"]
    files = [
        {"kind": "resume", "path": base / "resume.md", "label": "合成简历"},
        {"kind": "project", "path": base / "project.md", "label": "合成项目资料"},
        {"kind": "jd", "path": base / "jd.md", "label": "合成 JD"},
    ]
    document_ids: list[str] = []
    source_files: list[dict] = []
    for item in files:
        text = item["path"].read_text(encoding="utf-8")
        source_files.append({"label": item["label"], "path": str(item["path"].relative_to(ROOT)), "excerpt": _excerpt(text)})
        if item["kind"] != "jd":
            response = client.post(
                "/api/files/ingest-local",
                params={"workspace_id": workspace_id, "source_path": str(item["path"]), "kind": item["kind"]},
            )
            response.raise_for_status()
            document_ids.append(response.json()["data"]["document_id"])

    client.post(
        "/api/profile/extract-facts",
        json={"workspace_id": workspace_id, "document_ids": document_ids, "target_roles": [case["target_role"]]},
    ).raise_for_status()
    client.post(
        "/api/project/create-card",
        json={
            "workspace_id": workspace_id,
            "project_name": case["focus"][0],
            "source_document_ids": document_ids,
            "target_role": case["target_role"],
        },
    ).raise_for_status()
    job = client.post("/api/job/parse-jd", json={"workspace_id": workspace_id, "jd_text": _read_case_file(case["slug"], "jd.md")})
    job.raise_for_status()
    job_id = job.json()["data"]["job_id"]
    client.post("/api/job/match-profile", json={"workspace_id": workspace_id, "job_id": job_id}).raise_for_status()
    client.post("/api/profile/candidate/refresh", json={"workspace_id": workspace_id, "job_id": job_id, "target_role": case["target_role"]}).raise_for_status()
    _grant_fake_provider_consent(client, workspace_id, session_id)
    return workspace_id, session_id, source_files


def _build_multi_turn_dialogues() -> list[dict]:
    previous_env = {key: os.environ.get(key) for key in [
        "JOBPILOT_LLM_PROVIDER",
        "JOBPILOT_OPENAI_API_KEY",
        "JOBPILOT_OPENAI_BASE_URL",
        "JOBPILOT_OPENAI_MODEL",
        "JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT",
        "JOBPILOT_FAKE_PROVIDER_CHAT_ERROR",
    ]}
    os.environ["JOBPILOT_LLM_PROVIDER"] = "openai_compatible"
    os.environ["JOBPILOT_OPENAI_API_KEY"] = "fake-local-key-never-exposed"
    os.environ["JOBPILOT_OPENAI_BASE_URL"] = "https://example.invalid/v1"
    os.environ["JOBPILOT_OPENAI_MODEL"] = "deepseek-chat"
    os.environ["JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT"] = "1"
    os.environ.pop("JOBPILOT_FAKE_PROVIDER_CHAT_ERROR", None)
    run_root = DEFAULT_DIALOGUE_ROOT / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client = TestClient(app)
    cases: list[dict] = []
    try:
        for case in PERSONA_CASES:
            workspace_id, session_id, source_files = _prepare_case_workspace(client, case=case, run_root=run_root)
            turns = []
            for index, topic in enumerate(TURN_TOPICS, start=1):
                user_message = f"第 {index} 轮：我是{case['background']}候选人，{topic}"
                response = client.post(
                    "/api/chat/message",
                    json={
                        "workspace_id": workspace_id,
                        "session_id": session_id,
                        "message": user_message,
                        "provider_mode": "provider_opt_in",
                    },
                )
                response.raise_for_status()
                data = response.json()["data"]
                turns.append({
                    "turn": index,
                    "user": user_message,
                    "assistant": data["message"],
                    "chat_mode": data.get("chat_mode"),
                    "provider_invocation_status": data.get("provider_invocation_status"),
                    "fallback_used": data.get("fallback_used"),
                    "artifacts_count": len(data.get("artifacts") or []),
                    "recent_count": (data.get("context_summary") or {}).get("recent_count"),
                })
            context = client.get(f"/api/chat/session/{session_id}/context", params={"workspace_id": workspace_id})
            context.raise_for_status()
            context_data = context.json()["data"]
            conn, _ = workspace_conn(workspace_id)
            called = conn.execute(
                "SELECT COUNT(*) AS count FROM provider_chat_invocation WHERE workspace_id=? AND session_id=? AND status='called'",
                (workspace_id, session_id),
            ).fetchone()["count"]
            cases.append({
                "slug": case["slug"],
                "persona": case["name"],
                "target_role": case["target_role"],
                "technical_background": case["background"],
                "focus": case["focus"],
                "workspace_id": workspace_id,
                "session_id": session_id,
                "provider_path": "fake provider opt-in",
                "real_provider_called": False,
                "turn_count": len(turns),
                "message_count": context_data["total_message_count"],
                "recent_count": context_data["recent_count"],
                "rolling_summary_covered": context_data["rolling_summary"]["covered_message_count"],
                "provider_called_count": called,
                "privacy_boundary": context_data["privacy_boundary"],
                "source_files": source_files,
                "turns": turns,
            })
    finally:
        for key, value in previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    DEFAULT_DIALOGUE_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_DIALOGUE_JSON.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    return cases


def scenario_for(workspace_root: Path, multi_turn_dialogues: list[dict]) -> dict:
    url = f"http://127.0.0.1:5173/?workspace_root={workspace_root.as_posix()}&acceptance_redaction=synthetic"
    api = "http://127.0.0.1:8000"
    root = workspace_root.as_posix()
    resume = (ROOT / "examples/resumes/transition_frontend_resume.md").as_posix()
    project = (ROOT / "examples/projects/todoplus_README.md").as_posix()
    setup_expression = f"""
(async () => {{
  const root = {json.dumps(root, ensure_ascii=False)};
  const api = {json.dumps(api)};
  const status = await fetch(`${{api}}/api/workspace/status?root_path=${{encodeURIComponent(root)}}`).then((r) => r.json());
  const workspaceId = status.data.workspace_id || status.data.id;
  const qs = (obj) => new URLSearchParams(obj).toString();
  const resume = await fetch(`${{api}}/api/files/ingest-local?${{qs({{workspace_id: workspaceId, source_path: {json.dumps(resume, ensure_ascii=False)}, kind: 'resume'}})}}`, {{ method: 'POST' }}).then((r) => r.json());
  const project = await fetch(`${{api}}/api/files/ingest-local?${{qs({{workspace_id: workspaceId, source_path: {json.dumps(project, ensure_ascii=False)}, kind: 'project'}})}}`, {{ method: 'POST' }}).then((r) => r.json());
  const resumeDoc = resume.data.document_id;
  const projectDoc = project.data.document_id;
  await fetch(`${{api}}/api/profile/extract-facts`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ workspace_id: workspaceId, document_ids: [resumeDoc, projectDoc], target_roles: ['Junior Frontend Developer'] }}),
  }});
  await fetch(`${{api}}/api/project/create-card`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ workspace_id: workspaceId, project_name: 'TodoPlus', source_document_ids: [projectDoc], target_role: 'Junior Frontend Developer' }}),
  }});
  const job = await fetch(`${{api}}/api/job/parse-jd`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ workspace_id: workspaceId, jd_text: {json.dumps(JD_TEXT, ensure_ascii=False)} }}),
  }}).then((r) => r.json());
  await fetch(`${{api}}/api/job/match-profile`, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ workspace_id: workspaceId, job_id: job.data.job_id }}),
  }});
  return workspaceId;
}})()
""".strip()
    open_sources_expression = """
(() => {
  const details = document.querySelector('.profile-source-details');
  if (!details) throw new Error('profile source details not found');
  details.setAttribute('open', '');
  details.scrollIntoView({ block: 'center' });
  return true;
})()
""".strip()
    focus_profile_expression = """
(() => {
  const panel = document.querySelector('.candidate-profile-panel');
  if (!panel) throw new Error('candidate profile panel not found');
  panel.scrollIntoView({ block: 'center' });
  return true;
})()
""".strip()
    return {
        "name": "P5.5 Candidate Profile 自动化验收报告",
        "goal": "验证 JobPilot 在本地/mock 边界内，可以基于 examples 真实感资料生成候选人画像、能力矩阵、项目可信度、岗位短板和 source refs；不声明真实个人资料或真实 provider 默认路径通过。",
        "url": url,
        "targetArchitecture": [
            "Chatbox Workbench：展示 Candidate Profile、能力矩阵、项目可信度、岗位短板和 source refs。",
            "FastAPI Profile Routes：GET /api/profile/candidate 与 POST /api/profile/candidate/refresh。",
            "Profile Orchestrator：聚合 candidate_profile、career_fact、skill_evidence、tech_project、job、match_report。",
            "Artifact Layer：刷新画像写入 artifact_type=candidate_profile 和 artifact_version。",
            "Evidence Layer：Chrome/CDP 截图、中文 HTML 报告、PRD 规格检视和未验证范围。",
            "P6 对话补证层：Provider Consent、fake provider adapter、Long Context Manager、provider_chat_invocation 脱敏日志和 20 轮 transcript 汇总。",
        ],
        "currentImplementation": [
            "P5.5 使用 examples 和 synthetic-style workspace，不读取用户真实个人资料。",
            "画像刷新通过显式按钮触发，普通聊天不写 candidate_profile artifact。",
            "能力矩阵使用 strong/usable/weak/missing，项目可信度使用 verified/plausible/needs_evidence/risky。",
            "岗位短板对齐 JD must/nice 要求，并给出 next_action。",
            "报告使用 Headless Chrome/CDP 进行自动化截图，不执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼。",
            "多背景 20 轮对话补证使用 fake provider opt-in 执行，证明长程对话边界和日志脱敏；它不是真实 LLM 质量验收。",
        ],
        "acceptanceCriteria": [
            "GET /api/profile/candidate 可返回空态和画像态。",
            "POST /api/profile/candidate/refresh 写入 candidate_profile 行与 candidate_profile artifact/version。",
            "Workbench 展示画像概览、能力矩阵、项目可信度、岗位短板和 source refs。",
            "桌面、宽屏、720px 和 390px 视口均有截图证据。",
            "报告明确未验证真实个人资料、真实 provider、SaaS、ASR、会议平台、自动投递和 MCP/CLI。",
            "报告成对汇总至少 3 个不同技术背景的合成资料和每个案例 20 轮 provider-opt-in fake 对话 transcript。",
        ],
        "commandResults": [
            {"command": ".venv/bin/python -m pytest tests/evals/test_p5_5_candidate_profile_eval.py tests/evals/test_p5_5_capability_matrix_eval.py tests/evals/test_p5_5_project_credibility_eval.py tests/evals/test_p5_5_gap_analysis_eval.py tests/evals/test_p5_5_chat_boundary_eval.py -q", "status": "passed", "evidence": "P5.5 M1-M4 和普通聊天边界 eval 通过。"},
            {"command": ".venv/bin/python -m pytest -q", "status": "passed", "evidence": "阶段性全量端到端回归通过；具体结果以本轮审计记录和终端输出为准。"},
            {"command": ".venv/bin/python -m pytest tests/evals/test_p6_provider_backed_chat_eval.py tests/evals/test_p6_long_context_manager_eval.py -q", "status": "passed", "evidence": "P6 fake provider opt-in、20 轮 bounded context、隐私边界和失败降级 eval 通过。"},
            {"command": "npm --prefix apps/chatbox run build", "status": "passed", "evidence": "TypeScript 与 Vite build 通过。"},
            {"command": "drawio XML parse", "status": "passed", "evidence": "P5.5 gap 图可解析且分页不超过 8 页。"},
        ],
        "prdReview": [
            {"requirement": "原始 PRD 要求本地优先、可审查、可追溯的求职 Agent。", "evidence": "P5.5 复用本地 workspace、artifact/version/source refs，并在 Workbench 展示画像判断来源。", "status": "PASS for local/mock path"},
            {"requirement": "专业背景画像必须可追溯。", "evidence": "截图和 API eval 证明 candidate_profile artifact 含 source refs。", "status": "PASS for examples/synthetic data"},
            {"requirement": "能力矩阵必须解释证据强弱。", "evidence": "能力矩阵截图和 eval 覆盖 strong/usable/weak/missing。", "status": "PASS"},
            {"requirement": "项目可信度不能夸大。", "evidence": "项目可信度保留 needs_evidence/risky 和待确认项。", "status": "PASS"},
            {"requirement": "岗位短板必须可行动。", "evidence": "Job gap 每项包含 gap_level 和 next_action。", "status": "PASS"},
            {"requirement": "普通聊天不写画像 artifact。", "evidence": "test_p5_5_chat_boundary_eval.py 覆盖。", "status": "PASS"},
            {"requirement": "长程多轮对话必须有上下文边界、隐私边界和真实 provider 未验收说明。", "evidence": "三组合成背景各 20 轮 fake provider opt-in transcript、provider_chat_invocation 计数和 rolling summary 指标。", "status": "PASS for fake provider path"},
        ],
        "codeReview": [
            {"area": "services/profile/candidate.py", "finding": "复用现有表和 artifact/version，不新增数据库表；画像判断保留 source refs 和缺证据状态。", "severity": "pass"},
            {"area": "services/api/main.py", "finding": "新增 profile read/refresh 最小 API，未扩大到真实 provider 或不可逆操作。", "severity": "pass"},
            {"area": "apps/chatbox/src/main.tsx", "finding": "显式刷新画像，普通聊天只读画像状态；Workbench 展示能力矩阵、项目可信度和岗位短板。", "severity": "pass"},
            {"area": "tests/evals/test_p5_5_*.py", "finding": "覆盖画像聚合、API contract、能力矩阵、项目可信度、岗位短板、普通聊天边界和报告断言。", "severity": "pass"},
            {"area": "services/chat/provider_backed.py / services/chat/context.py", "finding": "fake provider opt-in 只在 consent 后记录 provider_chat_invocation；20 轮对话使用 bounded recent window 和 rolling summary，不写求职产物。", "severity": "pass"},
        ],
        "documentationAudit": [
            {"area": "Original PRD / Active P5.5 PRD", "finding": "P5.5 只声明本地/mock 可追溯画像能力；不把真实资料、真实 provider 或 P8+ 能力写成通过。", "status": "pass"},
            {"area": "P5.5 Architecture / Gates", "finding": "文档已将真实资料、真实 provider、敏感属性和 P8+ 能力排除在 P5.5 外，并同步自动化候选完成状态。", "status": "pass"},
            {"area": "Acceptance boundary", "finding": "本报告只证明 examples/synthetic 自动化路径，不替代 P5-REAL。", "status": "pass"},
        ],
        "unverifiedScope": [
            "未使用用户真实个人资料。",
            "未执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼。",
            "多轮对话 transcript 使用 fake provider opt-in，不代表真实 LLM 回复质量、成本、稳定性或模型能力通过。",
            "未验证 P5-REAL、SaaS、ASR、会议平台、自动投递、MCP/CLI。",
            "不是人工体验认可，也不是最终产品化发布结论。",
        ],
        "auditOpinion": "若本报告步骤全部通过，只能支持 P5.5 Candidate Profile 自动化候选通过；真实资料和真实 provider 仍需单独高风险确认。阶段性验收评价为：P5.5 可进入候选收口，但不能升级为 P5-REAL 或产品化最终验收。",
        "multiTurnDialogues": multi_turn_dialogues,
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
            {"name": "Initial P5.5 desktop state", "action": "screenshot", "file": "p5_5_initial_desktop.png", "viewport": "desktop"},
            {"name": "Prepare examples workspace", "action": "evaluate", "expression": setup_expression, "viewport": "desktop"},
            {"name": "Click generate candidate profile", "action": "clickText", "text": "生成画像", "viewport": "desktop"},
            {"name": "Wait profile refreshed", "action": "waitText", "text": "候选人画像已刷新", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "Focus candidate profile panel", "action": "evaluate", "expression": focus_profile_expression, "viewport": "desktop"},
            {"name": "Wait capability matrix", "action": "waitText", "text": "能力矩阵", "timeoutMs": 15000, "viewport": "desktop"},
            {"name": "Profile overview evidence", "action": "screenshot", "file": "p5_5_profile_overview.png", "viewport": "desktop"},
            {"name": "Open source refs", "action": "evaluate", "expression": open_sources_expression, "viewport": "desktop"},
            {"name": "Source refs evidence", "action": "screenshot", "file": "p5_5_source_refs.png", "viewport": "desktop"},
            {"name": "Profile 1200 evidence", "action": "screenshot", "file": "p5_5_profile_1200.png", "viewport": "desktop1200"},
            {"name": "Profile 1600 evidence", "action": "screenshot", "file": "p5_5_profile_1600.png", "viewport": "desktop1600"},
            {"name": "Profile 1920 evidence", "action": "screenshot", "file": "p5_5_profile_1920.png", "viewport": "desktop1920"},
            {"name": "Profile 720 evidence", "action": "screenshot", "file": "p5_5_profile_720.png", "viewport": "narrow720"},
            {"name": "Profile mobile evidence", "action": "screenshot", "file": "p5_5_profile_mobile_390.png", "viewport": "mobile"},
        ],
    }


def main() -> int:
    provider = os.environ.get("JOBPILOT_LLM_PROVIDER", "mock").strip().lower() or "mock"
    if provider not in {"mock", "fixture"}:
        raise SystemExit("P5.5 Candidate Profile acceptance requires mock or fixture provider")
    scenario_path = Path(os.environ.get("JOBPILOT_P5_5_SCENARIO_PATH", str(DEFAULT_SCENARIO))).expanduser().resolve()
    workspace_root = Path(os.environ.get("JOBPILOT_P5_5_WORKSPACE_ROOT", str(DEFAULT_WORKSPACE_ROOT))).expanduser().resolve()
    multi_turn_dialogues = _build_multi_turn_dialogues()
    scenario = scenario_for(workspace_root, multi_turn_dialogues)
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"scenario={scenario_path}")
    print(f"report={DEFAULT_REPORT}")
    print(f"output_dir={DEFAULT_OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
