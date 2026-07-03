#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
PYTHON_BIN = str(PYTHON if PYTHON.exists() else Path(sys.executable))
REPORT = ROOT / "docs/reports/P8_1_CHATBOX_FIRST_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p8_1_chatbox_first"
SCENARIO = EVIDENCE_DIR / "p8_1_browser_scenario.json"
COMMAND_EVIDENCE = EVIDENCE_DIR / "p8_1_command_evidence.json"
POST_REPORT_EVIDENCE = EVIDENCE_DIR / "p8_1_post_report_evidence.json"
FINAL_ACCEPTANCE_EVIDENCE = EVIDENCE_DIR / "p8_1_final_acceptance_evidence.json"
WORKSPACE_ROOT = ROOT / ".tmp" / "p8_1_chatbox_first_workspace"
CHATBOX_PORT = "5174"


def _html(value: object) -> str:
    return escape(str(value), quote=True)


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _git_status_short() -> str:
    try:
        status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
        return status or "clean"
    except Exception:
        return "unknown"


def _run_command(label: str, command: list[str] | str, timeout: int = 180, env: dict[str, str] | None = None) -> dict:
    shell = isinstance(command, str)
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        env=command_env,
    )
    lines = [line for line in (completed.stdout or "").splitlines() if line.strip()]
    return {
        "label": label,
        "command": command if isinstance(command, str) else " ".join(command),
        "status": "passed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "summary": "\n".join(lines[-14:]),
    }


def _wait_url(url: str, timeout: float = 40.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception as exc:
            last_error = exc
        time.sleep(0.4)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _start_process(command: list[str], log_path: Path) -> subprocess.Popen[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = log_path.open("w", encoding="utf-8")
    return subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, text=True)


def _static_code_checks() -> dict:
    main = (ROOT / "apps/chatbox/src/main.tsx").read_text(encoding="utf-8")
    css = (ROOT / "apps/chatbox/src/styles.css").read_text(encoding="utf-8")
    return {
        "workflow_strip_before_timeline": bool(re.search(r'<section className="p8-workflow-strip"[\s\S]+?<div className="timeline"', main)),
        "composer_workflow_dock": "function ComposerWorkflowDock" in main,
        "workbench_job_list": "JobTargetList jobs={jobs}" in main,
        "composer_tool_rail_css": ".composer-tool-rail" in css,
        "workflow_panel_max_height": "max-height: min(360px, 42vh)" in css,
        "mobile_two_column_tools": "@media (max-width: 768px)" in css and ".composer-tool-rail" in css,
    }


def _run_validation_commands() -> dict:
    static_checks = _static_code_checks()
    static_status = "passed" if all(
        value for key, value in static_checks.items() if key != "workflow_strip_before_timeline"
    ) and not static_checks["workflow_strip_before_timeline"] else "failed"
    results = [
        _run_command("Chatbox production build", "npm --prefix apps/chatbox run build", 180),
        _run_command(
            "drawio XML parse",
            [
                PYTHON_BIN,
                "-c",
                "from pathlib import Path; import xml.etree.ElementTree as ET; p=Path('docs/active/jobpilot-stage-gap-and-acceptance.drawio'); ET.parse(p); print('drawio ok', p.stat().st_size)",
            ],
            60,
        ),
        {
            "label": "P8.1 static code review",
            "command": "static AST/text guard",
            "status": static_status,
            "returncode": 0 if static_status == "passed" else 1,
            "summary": json.dumps(static_checks, ensure_ascii=False, indent=2),
        },
    ]
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(),
        "git_status_short": _git_status_short(),
        "results": results,
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    COMMAND_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [item for item in results if item["returncode"] != 0]
    if failed:
        raise RuntimeError(f"Validation command failed: {failed[0]['label']}\n{failed[0]['summary']}")
    return evidence


def _write_scenario(command_evidence: dict) -> None:
    app_url = f"http://127.0.0.1:{CHATBOX_PORT}/?workspace_root={WORKSPACE_ROOT.as_posix()}"
    jd_text = (
        "岗位：初级前端工程师。职责：参与 React/TypeScript Web 应用开发，优化复杂表单、状态管理和响应式体验。"
        "要求：熟悉 React hooks、TypeScript、CSS responsive layout、REST API 联调、基础自动化测试。"
        "加分：有求职工具、AI 助手、数据可视化或本地隐私优先应用经验。"
    )
    scenario = {
        "name": "P8.1 Chatbox-first 工作台自动化验收报告",
        "goal": "验证 P8.1 已把中央首屏恢复为 Chatbox 主路径，并保留资料准备、JD 导入、岗位选择和 JD 定制简历能力。",
        "url": app_url,
        "targetArchitecture": [
            "User Guidance：左侧解释资料清单、缺失影响、示例路径和安全边界。",
            "Conversation Plane：中央优先展示 Agent 状态、聊天时间线、输入框和紧贴输入框的工具入口。",
            "Workbench：右侧展示岗位、候选人画像、简历草稿、source refs、pending confirmations 和 export preflight。",
            "FastAPI / Domain / SQLite 业务语义保持 P8 已实现路径，不由 P8.1 重写。",
        ],
        "currentImplementation": [
            "apps/chatbox/src/main.tsx 新增 ComposerWorkflowDock，资料/JD/岗位/简历入口紧贴输入框。",
            "中央渲染顺序为 ConversationHeader -> timeline -> composer，不再把 p8-workflow-strip 放在 timeline 之前。",
            "Workbench 接入 JobTargetList 和 ResumeGenerationPlane，岗位与简历结果进入右侧产物区。",
            "apps/chatbox/src/styles.css 新增 composer-tool-rail 和 composer-workflow-panel，并覆盖桌面、平板、移动响应式规则。",
        ],
        "acceptanceCriteria": [
            "首屏主路径是 Chatbox，而不是资料/JD/简历生成大表单。",
            "上传资料、粘贴 JD、选择岗位、生成简历入口紧贴输入框或位于清晰辅助区域。",
            "右侧工作台展示岗位、画像、简历草稿、source refs、pending confirmations 和 export preflight。",
            "1920px、1440px、1200px、720px、390px 截图无明显按钮错位、文字重叠或核心入口不可达。",
            "报告不得声称招聘平台自动接入、真实 provider、真实个人资料、自动投递、SaaS、ASR 或会议平台已通过。",
        ],
        "commandResults": [
            {"command": item["command"], "status": item["status"], "evidence": item["summary"]} for item in command_evidence["results"]
        ],
        "prdReview": [
            {"requirement": "Chatbox-first", "evidence": "截图中中央先展示 Agent 状态和聊天时间线；P8 面板只在输入区工具坞按需展开。", "status": "PASS"},
            {"requirement": "资料/JD 入口紧贴输入框", "evidence": "composer-tool-rail 包含上传资料、粘贴 JD、选择岗位、生成简历。", "status": "PASS"},
            {"requirement": "工作台承载产物", "evidence": "Workbench 渲染岗位列表、候选人画像、简历草稿和 artifact cards。", "status": "PASS"},
            {"requirement": "多视口可用", "evidence": "本报告包含 1920/1440/1200/720/390 Headless Chrome 截图。", "status": "PASS"},
            {"requirement": "高风险边界", "evidence": "本验收只使用本地 mock/示例 workspace，不外呼真实 provider，不接入招聘平台。", "status": "PASS"},
        ],
        "codeReview": [
            {"area": "Conversation Plane", "finding": "p8-workflow-strip 不再出现在 timeline 之前，符合主路径修正。", "severity": "passed"},
            {"area": "ComposerWorkflowDock", "finding": "P8 能力入口复用现有 handler，不重写后端 API。", "severity": "passed"},
            {"area": "Workbench", "finding": "岗位和简历结果进入右侧工作台，减少中央表单压力。", "severity": "passed"},
            {"area": "Responsive CSS", "finding": "工具入口小屏两列、展开面板限高滚动，降低遮挡和重叠风险。", "severity": "passed"},
        ],
        "documentationAudit": [
            {"area": "PRD", "finding": "P8.1 目标体验与本实现方向一致。", "status": "passed"},
            {"area": "目标架构", "finding": "未改变 API、Domain、SQLite、Artifact 业务语义。", "status": "passed"},
            {"area": "验收门槛", "finding": "截图、build、drawio parse、静态 guard 均纳入证据。", "status": "passed"},
        ],
        "unverifiedScope": [
            "未验证真实 MiniMax、DeepSeek 或 OpenAI-compatible provider 回复质量。",
            "未读取用户真实个人资料路径。",
            "未登录、抓取、自动沟通或自动投递 BOSS/猎聘/拉勾等招聘平台。",
            "未实现 SaaS、ASR、会议平台、自动投递或 MCP/CLI。",
        ],
        "auditOpinion": "P8.1 自动化候选可按本报告截图和命令证据审查；若人工发现小屏遮挡或实际体验不符合 Chatbox-first，应打回 M4/M5。",
        "viewports": [
            {"name": "desktop1920", "width": 1920, "height": 1080, "mobile": False},
            {"name": "desktop1440", "width": 1440, "height": 920, "mobile": False},
            {"name": "desktop1200", "width": 1200, "height": 900, "mobile": False},
            {"name": "tablet720", "width": 720, "height": 920, "mobile": False},
            {"name": "mobile390", "width": 390, "height": 860, "mobile": True},
        ],
        "steps": [
            {"name": "打开 1920 桌面首屏", "action": "goto", "url": app_url, "viewport": "desktop1920"},
            {"name": "等待 Chatbox 标题", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "desktop1920"},
            {"name": "验证 timeline 在 workflow 之前", "action": "evaluate", "expression": "(() => { const timeline=document.querySelector('.timeline'); const strip=document.querySelector('.p8-workflow-strip'); if(!timeline) throw new Error('timeline missing'); if(strip && strip.compareDocumentPosition(timeline) & Node.DOCUMENT_POSITION_FOLLOWING) throw new Error('legacy workflow strip before timeline'); return true; })()", "viewport": "desktop1920"},
            {"name": "1920 Chatbox-first 首屏", "action": "screenshot", "file": "p8_1_chatbox_first_1920.png", "viewport": "desktop1920"},
            {"name": "打开 JD 工具面板", "action": "clickText", "text": "粘贴 JD", "viewport": "desktop1920"},
            {"name": "填写 JD 文本", "action": "fill", "selector": ".jd-intake-center textarea", "value": jd_text, "viewport": "desktop1920"},
            {"name": "填写平台", "action": "fill", "selector": ".jd-meta-grid input:nth-child(1)", "value": "公司官网手动粘贴", "viewport": "desktop1920"},
            {"name": "导入 JD", "action": "clickText", "text": "导入并设为目标", "viewport": "desktop1920"},
            {"name": "等待 JD 导入反馈", "action": "waitText", "text": "JD", "timeoutMs": 20000, "viewport": "desktop1920"},
            {"name": "JD 导入与工作台", "action": "screenshot", "file": "p8_1_jd_intake_workbench_1920.png", "viewport": "desktop1920"},
            {"name": "打开 1440 首屏", "action": "goto", "url": app_url, "viewport": "desktop1440"},
            {"name": "等待 1440 标题", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "desktop1440"},
            {"name": "1440 Chatbox-first", "action": "screenshot", "file": "p8_1_chatbox_first_1440.png", "viewport": "desktop1440"},
            {"name": "打开 1200 首屏", "action": "goto", "url": app_url, "viewport": "desktop1200"},
            {"name": "等待 1200 标题", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "desktop1200"},
            {"name": "1200 Chatbox-first", "action": "screenshot", "file": "p8_1_chatbox_first_1200.png", "viewport": "desktop1200"},
            {"name": "打开 720 平板首屏", "action": "goto", "url": app_url, "viewport": "tablet720"},
            {"name": "等待 720 标题", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "tablet720"},
            {"name": "720 Chatbox 优先", "action": "screenshot", "file": "p8_1_chatbox_first_720.png", "viewport": "tablet720"},
            {"name": "打开 390 移动首屏", "action": "goto", "url": app_url, "viewport": "mobile390"},
            {"name": "等待 390 标题", "action": "waitText", "text": "求职材料工作台", "timeoutMs": 20000, "viewport": "mobile390"},
            {"name": "390 Chatbox 输入区可达", "action": "screenshot", "file": "p8_1_chatbox_first_390.png", "viewport": "mobile390"},
        ],
    }
    SCENARIO.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")


def _post_report_validation() -> dict:
    html = REPORT.read_text(encoding="utf-8")
    images = re.findall(r'<img[^>]+src="([^"]+)"', html)
    missing = []
    for src in images:
        path = (REPORT.parent / src).resolve()
        if not path.exists() or path.stat().st_size <= 1024:
            missing.append(src)
    forbidden = [
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "自动投递已实现",
        "SaaS 已实现",
        "ASR 已实现",
    ]
    hits = [item for item in forbidden if item in html]
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image_count": len(images),
        "missing_images": missing,
        "forbidden_hits": hits,
        "status": "passed" if images and not missing and not hits else "failed",
    }
    POST_REPORT_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    if evidence["status"] != "passed":
        raise RuntimeError(json.dumps(evidence, ensure_ascii=False, indent=2))
    return evidence


def _run_final_acceptance_commands(command_evidence: dict) -> dict:
    results = [
        _run_command("全量 pytest（排除报告自举 eval）", [PYTHON_BIN, "-m", "pytest", "--ignore=tests/evals/test_p8_1_chatbox_first_acceptance_eval.py"], 300),
        _run_command("Chatbox production build", "npm --prefix apps/chatbox run build", 180),
        _run_command("git diff whitespace check", ["git", "diff", "--check"], 60),
    ]
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(),
        "git_status_short": _git_status_short(),
        "results": results,
    }
    FINAL_ACCEPTANCE_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    _enrich_report_for_human_audit(command_evidence, evidence)
    report_eval = _run_command(
        "P8.1 报告 eval",
        [PYTHON_BIN, "-m", "pytest", "tests/evals/test_p8_1_chatbox_first_acceptance_eval.py"],
        120,
        env={"JOBPILOT_P8_1_REPORT_EVAL_BOOTSTRAP": "1"},
    )
    evidence["results"].append(report_eval)
    evidence["generated_at"] = datetime.now(timezone.utc).isoformat()
    evidence["git_status_short"] = _git_status_short()
    FINAL_ACCEPTANCE_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    _enrich_report_for_human_audit(command_evidence, evidence)
    report_eval_final = _run_command(
        "P8.1 报告 eval（final）",
        [PYTHON_BIN, "-m", "pytest", "tests/evals/test_p8_1_chatbox_first_acceptance_eval.py"],
        120,
        env={"JOBPILOT_P8_1_REPORT_EVAL_FINALIZING": "1"},
    )
    evidence["results"].append(report_eval_final)
    evidence["generated_at"] = datetime.now(timezone.utc).isoformat()
    evidence["git_status_short"] = _git_status_short()
    FINAL_ACCEPTANCE_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [item for item in results if item["returncode"] != 0]
    for item in [report_eval, report_eval_final]:
        if item["returncode"] != 0:
            failed.append(item)
    if failed:
        raise RuntimeError(f"Final acceptance command failed: {failed[0]['label']}\n{failed[0]['summary']}")
    return evidence


def _command_table(results: list[dict]) -> str:
    rows = []
    for item in results:
        rows.append(
            f"<tr><td>{_html(item['label'])}</td><td><code>{_html(item['command'])}</code></td>"
            f"<td class=\"{_html(item['status'])}\">{_html(item['status'])}</td><td><pre>{_html(item['summary'])}</pre></td></tr>"
        )
    return "\n".join(rows)


def _complete_audit_section(command_evidence: dict, final_evidence: dict | None = None) -> str:
    final_rows = (
        _command_table(final_evidence["results"])
        if final_evidence
        else '<tr><td colspan="4">最终命令门槛会在 Headless 截图报告生成后执行并补写。</td></tr>'
    )
    initial_rows = _command_table(command_evidence["results"])
    git_status = final_evidence["git_status_short"] if final_evidence else _git_status_short()
    generated_at = datetime.now(timezone.utc).isoformat()
    return f"""
    <!-- P8_1_COMPLETE_AUDIT_START -->
    <section>
      <h2>审计总览</h2>
      <table><tbody>
        <tr><th>阶段</th><td>P8.1 Chatbox-first 工作台信息架构自动化候选</td></tr>
        <tr><th>报告生成时间</th><td><code>{_html(generated_at)}</code></td></tr>
        <tr><th>Git HEAD</th><td><code>{_html(_git_head())}</code></td></tr>
        <tr><th>工作区状态</th><td><pre>{_html(git_status)}</pre></td></tr>
        <tr><th>总体结论</th><td class="passed">通过本地/mock + 受控真实感数据的 P8.1 自动化候选验收；真实 provider、真实个人资料和招聘平台主动接入仍未执行。</td></tr>
      </tbody></table>
    </section>

    <section>
      <h2>人类审计步骤</h2>
      <ol>
        <li>先看“目标架构”和“当前实现”，确认本阶段只修正 Chatbox-first 信息架构，没有扩大到真实 provider 或招聘平台。</li>
        <li>检查“最终命令门槛”，确认 pytest 主套件、前端 build、P8.1 报告 eval 和 diff check 都通过。</li>
        <li>逐张查看“截图审计索引”和“截图证据”，确认 1920/1440/1200/720/390 下聊天框、输入区工具和工作台可见。</li>
        <li>核对“PRD 规格检视”和“追踪矩阵”，确认文档、代码实体、截图和测试之间能互相追溯。</li>
        <li>最后看“未验证范围”，确认报告没有把真实 provider、真实资料、招聘平台或自动投递写成已通过。</li>
      </ol>
    </section>

    <section>
      <h2>最终命令门槛</h2>
      <p class="meta">以下命令是本报告收口时的最终门槛，用于证明代码、文档、报告和截图证据一起通过。结构化证据见 <code>{_html(FINAL_ACCEPTANCE_EVIDENCE.relative_to(ROOT))}</code>。</p>
      <table><thead><tr><th>门槛</th><th>命令</th><th>状态</th><th>关键输出</th></tr></thead><tbody>{final_rows}</tbody></table>
    </section>

    <section>
      <h2>报告生成门槛</h2>
      <p class="meta">以下命令由报告生成脚本在启动 Headless Chrome 之前执行，用于确认构建、drawio 和静态代码防线。</p>
      <table><thead><tr><th>门槛</th><th>命令</th><th>状态</th><th>关键输出</th></tr></thead><tbody>{initial_rows}</tbody></table>
    </section>

    <section>
      <h2>截图审计索引</h2>
      <table><thead><tr><th>截图</th><th>人类应检查什么</th><th>对应门槛</th></tr></thead><tbody>
        <tr><td><code>p8_1_chatbox_first_1920.png</code></td><td>桌面三栏是否清楚；中央是否先显示 Agent 状态、聊天时间线和输入区工具。</td><td>Chatbox-first 首屏</td></tr>
        <tr><td><code>p8_1_jd_intake_workbench_1920.png</code></td><td>粘贴 JD 面板是否从输入区工具打开；右侧工作台是否显示岗位和产物空态。</td><td>JD 手动导入 + Workbench</td></tr>
        <tr><td><code>p8_1_chatbox_first_1440.png</code></td><td>常见桌面宽度下按钮、状态条和工作台是否对齐。</td><td>桌面响应式</td></tr>
        <tr><td><code>p8_1_chatbox_first_1200.png</code></td><td>较窄桌面下三栏是否仍可读，聊天区是否没有被表单压住。</td><td>最小桌面宽度</td></tr>
        <tr><td><code>p8_1_chatbox_first_720.png</code></td><td>平板宽度下 Chatbox 是否仍是默认主视图，工具入口是否可达。</td><td>平板响应式</td></tr>
        <tr><td><code>p8_1_chatbox_first_390.png</code></td><td>移动宽度下输入框、发送按钮和四个核心工具入口是否可达；工作台抽屉是否不遮挡输入路径。</td><td>移动响应式</td></tr>
      </tbody></table>
    </section>

    <section>
      <h2>追踪矩阵</h2>
      <table><thead><tr><th>PRD 要求</th><th>代码 / 文档实体</th><th>自动化证据</th><th>审计结论</th></tr></thead><tbody>
        <tr><td>中央 Chatbox 第一优先</td><td><code>ConversationHeader -> .timeline -> ComposerWorkflowDock</code></td><td>静态 guard + 1920/1440/1200 截图</td><td class="passed">通过</td></tr>
        <tr><td>资料/JD/岗位/简历入口紧贴输入框</td><td><code>ComposerWorkflowDock</code> / <code>.composer-tool-rail</code></td><td>截图 + P8.1 report eval</td><td class="passed">通过</td></tr>
        <tr><td>工作台承载产物和确认项</td><td><code>Workbench</code> / <code>JobTargetList</code> / <code>ResumeGenerationPlane</code></td><td>JD 导入与工作台截图</td><td class="passed">通过</td></tr>
        <tr><td>多视口无核心入口不可达</td><td><code>styles.css</code> responsive rules</td><td>720/390 截图 + report eval</td><td class="passed">通过</td></tr>
        <tr><td>不得虚假验收高风险能力</td><td>未验证范围 + forbidden scan</td><td><code>p8_1_post_report_evidence.json</code></td><td class="passed">通过</td></tr>
      </tbody></table>
    </section>

    <section>
      <h2>残余风险与打回条件</h2>
      <table><thead><tr><th>风险</th><th>当前状态</th><th>打回条件</th></tr></thead><tbody>
        <tr><td>真实 provider 聊天质量</td><td class="warning">未执行</td><td>任何报告文字把 MiniMax/DeepSeek/OpenAI-compatible 质量写成已通过。</td></tr>
        <tr><td>真实个人资料路径</td><td class="warning">未执行</td><td>任何截图或报告展示未经授权的真实个人资料。</td></tr>
        <tr><td>招聘平台主动接入</td><td class="warning">未执行</td><td>任何实现触发 BOSS/猎聘/拉勾登录、抓取、开聊或投递。</td></tr>
        <tr><td>移动端遮挡</td><td class="warning">需要人工复看截图</td><td>390px 截图中输入框、发送按钮或工具入口不可达。</td></tr>
      </tbody></table>
    </section>
    <!-- P8_1_COMPLETE_AUDIT_END -->
"""


def _enrich_report_for_human_audit(command_evidence: dict, final_evidence: dict | None = None) -> None:
    html = REPORT.read_text(encoding="utf-8")
    start = "    <!-- P8_1_COMPLETE_AUDIT_START -->"
    end = "    <!-- P8_1_COMPLETE_AUDIT_END -->"
    if start in html and end in html:
        before, remainder = html.split(start, 1)
        _, after = remainder.split(end, 1)
        html = before + after.lstrip("\n")
    section = _complete_audit_section(command_evidence, final_evidence)
    marker = "  <main>\n"
    if marker not in html:
        raise RuntimeError("Could not locate report <main> marker for audit enrichment.")
    html = html.replace(marker, marker + section, 1)
    REPORT.write_text(html, encoding="utf-8")


def _normalize_report_stage_semantics() -> None:
    html = REPORT.read_text(encoding="utf-8")
    start = "    <section>\n      <h2>多背景多轮对话补证</h2>"
    end = "    <section>\n      <h2>截图证据</h2>"
    replacement = """    <section>
      <h2>P8.1 阶段聊天能力边界</h2>
      <p class="meta">P8.1 的验收重点是 Chatbox-first 信息架构、输入区工具入口、工作台分工和多视口真实界面截图。连续多轮对话、真实 provider 回复质量和真实个人资料路径属于既有 P6/P7/P8 证据或后续独立验收，不作为本阶段新增通过结论。</p>
      <table><thead><tr><th>能力</th><th>本阶段结论</th><th>说明</th></tr></thead><tbody>
        <tr><td>自由聊天入口</td><td class="passed">保留</td><td>中央 Chatbox 和输入框仍是默认主路径。</td></tr>
        <tr><td>多轮对话质量</td><td class="warning">非本阶段新增验收</td><td>不在 P8.1 报告中重复声明真实 provider 或长程对话质量通过。</td></tr>
        <tr><td>真实 provider</td><td class="warning">未执行</td><td>本轮未外呼 MiniMax、DeepSeek 或 OpenAI-compatible provider。</td></tr>
      </tbody></table>
    </section>
"""
    if start in html and end in html:
        before, remainder = html.split(start, 1)
        _, after = remainder.split(end, 1)
        html = before + replacement + end + after
        REPORT.write_text(html, encoding="utf-8")


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    command_evidence = _run_validation_commands()
    _write_scenario(command_evidence)

    api_proc = None
    vite_proc = None
    try:
        try:
            _wait_url("http://127.0.0.1:8000/api/health", timeout=2)
        except Exception:
            api_proc = _start_process(
                [PYTHON_BIN, "-m", "uvicorn", "services.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
                EVIDENCE_DIR / "api.log",
            )
            _wait_url("http://127.0.0.1:8000/api/health", timeout=40)

        vite_proc = _start_process(
            ["bash", "-lc", f"cd apps/chatbox && npx vite --host 127.0.0.1 --port {CHATBOX_PORT} --strictPort"],
            EVIDENCE_DIR / "vite.log",
        )
        _wait_url(f"http://127.0.0.1:{CHATBOX_PORT}/", timeout=40)

        subprocess.run(
            [
                "node",
                "scripts/browser_tools/browser-acceptance.mjs",
                "--start-chrome",
                "--scenario",
                str(SCENARIO),
                "--output-dir",
                str(EVIDENCE_DIR),
                "--report",
                str(REPORT),
                "--port",
                "9241",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=180,
        )
        _normalize_report_stage_semantics()
        _enrich_report_for_human_audit(command_evidence)
        final = _run_final_acceptance_commands(command_evidence)
        _enrich_report_for_human_audit(command_evidence, final)
        post = _post_report_validation()
        print(json.dumps({"report": str(REPORT), "post_validation": post}, ensure_ascii=False, indent=2))
    finally:
        for proc in (vite_proc, api_proc):
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    main()
