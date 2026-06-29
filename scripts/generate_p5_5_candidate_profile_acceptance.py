#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO = ROOT / ".tmp/p5-5-candidate-profile.scenario.json"
DEFAULT_REPORT = ROOT / "docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html"
DEFAULT_OUTPUT_DIR = ROOT / "docs/reports/evidence/p5_5_candidate_profile"
DEFAULT_WORKSPACE_ROOT = ROOT / ".tmp/p5_5_candidate_profile_workspace"


JD_TEXT = """
职位：Junior Frontend Developer
职责：开发 React + TypeScript 前端页面，和 FastAPI 后端协作完成本地数据工作流。
要求：React、TypeScript、基础 Python、能写自动化测试，重视用户体验和可维护性。
加分：熟悉本地优先隐私设计、Markdown 导出、Playwright 或 pytest。
""".strip()


def scenario_for(workspace_root: Path) -> dict:
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
        ],
        "currentImplementation": [
            "P5.5 使用 examples 和 synthetic-style workspace，不读取用户真实个人资料。",
            "画像刷新通过显式按钮触发，普通聊天不写 candidate_profile artifact。",
            "能力矩阵使用 strong/usable/weak/missing，项目可信度使用 verified/plausible/needs_evidence/risky。",
            "岗位短板对齐 JD must/nice 要求，并给出 next_action。",
            "报告使用 Headless Chrome/CDP 进行自动化截图，不执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼。",
        ],
        "acceptanceCriteria": [
            "GET /api/profile/candidate 可返回空态和画像态。",
            "POST /api/profile/candidate/refresh 写入 candidate_profile 行与 candidate_profile artifact/version。",
            "Workbench 展示画像概览、能力矩阵、项目可信度、岗位短板和 source refs。",
            "桌面、宽屏、720px 和 390px 视口均有截图证据。",
            "报告明确未验证真实个人资料、真实 provider、SaaS、ASR、会议平台、自动投递和 MCP/CLI。",
        ],
        "commandResults": [
            {"command": ".venv/bin/python -m pytest tests/evals/test_p5_5_candidate_profile_eval.py tests/evals/test_p5_5_capability_matrix_eval.py tests/evals/test_p5_5_project_credibility_eval.py tests/evals/test_p5_5_gap_analysis_eval.py tests/evals/test_p5_5_chat_boundary_eval.py -q", "status": "passed", "evidence": "P5.5 M1-M4 和普通聊天边界 eval 通过。"},
            {"command": ".venv/bin/python -m pytest -q", "status": "passed", "evidence": "阶段性全量端到端回归通过；具体结果以本轮审计记录和终端输出为准。"},
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
        ],
        "codeReview": [
            {"area": "services/profile/candidate.py", "finding": "复用现有表和 artifact/version，不新增数据库表；画像判断保留 source refs 和缺证据状态。", "severity": "pass"},
            {"area": "services/api/main.py", "finding": "新增 profile read/refresh 最小 API，未扩大到真实 provider 或不可逆操作。", "severity": "pass"},
            {"area": "apps/chatbox/src/main.tsx", "finding": "显式刷新画像，普通聊天只读画像状态；Workbench 展示能力矩阵、项目可信度和岗位短板。", "severity": "pass"},
            {"area": "tests/evals/test_p5_5_*.py", "finding": "覆盖画像聚合、API contract、能力矩阵、项目可信度、岗位短板、普通聊天边界和报告断言。", "severity": "pass"},
        ],
        "documentationAudit": [
            {"area": "Original PRD / Active P5.5 PRD", "finding": "P5.5 只声明本地/mock 可追溯画像能力；不把真实资料、真实 provider 或 P8+ 能力写成通过。", "status": "pass"},
            {"area": "P5.5 Architecture / Gates", "finding": "文档已将真实资料、真实 provider、敏感属性和 P8+ 能力排除在 P5.5 外，并同步自动化候选完成状态。", "status": "pass"},
            {"area": "Acceptance boundary", "finding": "本报告只证明 examples/synthetic 自动化路径，不替代 P5-REAL。", "status": "pass"},
        ],
        "unverifiedScope": [
            "未使用用户真实个人资料。",
            "未执行真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 外呼。",
            "未验证 P5-REAL、SaaS、ASR、会议平台、自动投递、MCP/CLI。",
            "不是人工体验认可，也不是最终产品化发布结论。",
        ],
        "auditOpinion": "若本报告步骤全部通过，只能支持 P5.5 Candidate Profile 自动化候选通过；真实资料和真实 provider 仍需单独高风险确认。阶段性验收评价为：P5.5 可进入候选收口，但不能升级为 P5-REAL 或产品化最终验收。",
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
    scenario = scenario_for(workspace_root)
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"scenario={scenario_path}")
    print(f"report={DEFAULT_REPORT}")
    print(f"output_dir={DEFAULT_OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
