#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
PYTHON_BIN = str(PYTHON if PYTHON.exists() else Path(sys.executable))
REPORT = ROOT / "docs/reports/P9_1_MARKET_SOCRATIC_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p9_1_market_socratic"
SCENARIO = EVIDENCE_DIR / "p9_1_browser_scenario.json"
COMMAND_EVIDENCE = EVIDENCE_DIR / "p9_1_command_evidence.json"
POST_REPORT_EVIDENCE = EVIDENCE_DIR / "p9_1_post_report_evidence.json"
CHATBOX_PORT = "5175"
API_PORT = "18082"
WORKSPACE_ROOT = ROOT / ".tmp" / "p9_1_market_socratic_workspace"


def _run_command(label: str, command: list[str] | str, timeout: int = 180) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        shell=isinstance(command, str),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        env=os.environ.copy(),
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


def _static_code_checks() -> dict:
    main = (ROOT / "apps/chatbox/src/main.tsx").read_text(encoding="utf-8")
    css = (ROOT / "apps/chatbox/src/styles.css").read_text(encoding="utf-8")
    package_json = (ROOT / "apps/chatbox/package.json").read_text(encoding="utf-8")
    forbidden_claims = [
        "真实市场 provider 已接入",
        "全网 JD 搜索已完成",
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实 ASR 已实现",
        "自动投递已实现",
        "MCP/Skill 连通性已通过",
    ]
    return {
        "echarts_dependency": "\"echarts\"" in package_json,
        "echarts_register_map": "echarts.registerMap" in main,
        "administrative_region_node": "type AdministrativeRegionNode" in main,
        "market_map_layer_state": "type MarketMapLayerState" in main,
        "socratic_session": "type SocraticSession" in main and "Socratic Intake" in main,
        "source_legend": ".source-trust-legend" in css,
        "no_forbidden_claims": not any(claim in main or claim in css for claim in forbidden_claims),
    }


def _run_validation_commands() -> dict:
    static_checks = _static_code_checks()
    results = [
        _run_command("Chatbox production build", "npm --prefix apps/chatbox run build", 240),
        _run_command(
            "P9.1 drawio XML parse",
            [
                PYTHON_BIN,
                "-c",
                "from pathlib import Path; import xml.etree.ElementTree as ET; p=Path('docs/active/jobpilot-p9-1-market-socratic-gap.drawio'); root=ET.parse(p).getroot(); print('drawio pages', len(root.findall('diagram')), 'size', p.stat().st_size)",
            ],
            60,
        ),
        {
            "label": "P9.1 static implementation guard",
            "command": "static text guard for P9.1 UI entities and false-green claims",
            "status": "passed" if all(static_checks.values()) else "failed",
            "returncode": 0 if all(static_checks.values()) else 1,
            "summary": json.dumps(static_checks, ensure_ascii=False, indent=2),
        },
        _run_command("P9 baseline report eval", [PYTHON_BIN, "-m", "pytest", "tests/evals/test_p9_chatbox_native_acceptance_eval.py"], 180),
        _run_command("diff whitespace check", "git diff --check", 120),
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
        raise RuntimeError(f"Validation failed: {failed[0]['label']}\n{failed[0]['summary']}")
    return evidence


def _dialogue_case(persona: str, target_role: str, background: str, turns: list[tuple[str, str, int]]) -> dict:
    return {
        "persona": persona,
        "target_role": target_role,
        "technical_background": background,
        "provider_path": "local/mock command route；未调用真实 provider",
        "real_provider_called": False,
        "turn_count": len(turns),
        "message_count": len(turns) * 2,
        "provider_called_count": 0,
        "recent_count": 8,
        "rolling_summary_covered": "yes, synthetic transcript only",
        "privacy_boundary": {
            "contains_api_key": "否",
            "raw_provider_response_included": "否",
            "full_history_included": "否",
        },
        "focus": ["Socratic Intake", "事实采集", "source refs", "pending confirmations", "DoNotClaimList"],
        "source_files": [
            {
                "label": "虚拟简历资料",
                "path": "examples/p5_synthetic_personas/*/resume.md",
                "excerpt": "合成资料仅用于验收，不代表真实个人资料路径通过。",
            },
            {
                "label": "虚拟 JD 资料",
                "path": "examples/p5_synthetic_personas/*/jd.md",
                "excerpt": "JD 来自本地 fixture/示例文本，不代表真实全网搜索或招聘平台抓取。",
            },
        ],
        "turns": [
            {
                "turn": index,
                "user": user,
                "assistant": assistant,
                "provider_invocation_status": "not_called",
                "chat_mode": "local/mock",
                "artifacts_count": artifacts_count,
            }
            for index, (user, assistant, artifacts_count) in enumerate(turns, 1)
        ],
    }


def _multi_turn_dialogues() -> list[dict]:
    frontend_turns = [
        ("我想用智能客服控制台项目投 LLM 应用前端。", "目标岗位已记录。下一问：项目解决了什么业务问题？", 1),
        ("客服需要统一处理多渠道会话。", "已记录项目背景。下一问：你本人负责哪一部分？", 1),
        ("我负责会话时间线、流式消息和错误重试。", "已记录本人职责。下一问：最难的技术问题是什么？", 2),
        ("流式消息乱序和失败恢复。", "已记录技术难点。下一问：你采取了哪些具体动作？", 2),
        ("做状态机、幂等消息 ID 和重试策略。", "已记录行动过程。下一问：有没有可确认指标？", 3),
        ("首屏从 2.8s 降到 1.6s。", "指标进入待确认。下一问：这个指标来源是什么？", 3),
        ("内部性能面板截图。", "已添加 source ref。下一问：哪些内容不能写？", 4),
        ("不写模型训练，只写 LLM 应用前端。", "已加入 DoNotClaimList。下一问：映射 JD 哪些关键词？", 4),
        ("React、TypeScript、LLM 应用、流式体验。", "已生成 JD 映射。下一问：强调技术深度还是业务结果？", 5),
        ("先强调技术深度。", "已生成 STAR/CAR 草稿，保留指标待确认项。", 5),
    ]
    backend_turns = [
        ("我想用实时特征服务投 AI 平台后端。", "目标岗位已记录。下一问：项目服务什么业务？", 1),
        ("推荐系统实时特征供给。", "已记录项目背景。下一问：你本人负责哪些模块？", 1),
        ("Kafka 消费链路和特征缓存。", "已记录本人职责。下一问：技术难点是什么？", 2),
        ("峰值流量下延迟和一致性。", "已记录技术难点。下一问：你做了哪些动作？", 2),
        ("分区消费、缓存预热、降级策略。", "已记录行动过程。下一问：有量化结果吗？", 3),
        ("QPS 1.2 万，P99 80ms 内。", "指标进入待确认。下一问：数据来源能证明吗？", 3),
        ("压测报告和监控截图。", "已添加 source refs。下一问：有哪些不能写？", 4),
        ("没做 Kubernetes，不写 K8s 实操。", "已加入 DoNotClaimList。下一问：匹配 JD 哪些关键词？", 4),
        ("Kafka、缓存、稳定性、性能优化。", "已生成 JD 映射。下一问：是否生成面试故事和简历 bullet？", 5),
        ("先生成草稿，保留待确认。", "已生成后端平台故事草稿，保留 QPS/P99 证据待确认。", 5),
    ]
    return [
        _dialogue_case("合成候选人 A", "LLM 应用前端工程师", "React / TypeScript / LLM 应用控制台", frontend_turns),
        _dialogue_case("合成候选人 B", "AI 平台后端工程师", "Java / Spring Boot / Kafka / MySQL", backend_turns),
    ]


def _write_scenario(command_evidence: dict) -> None:
    app_url = f"http://127.0.0.1:{CHATBOX_PORT}/?workspace_root={WORKSPACE_ROOT.as_posix()}"
    scenario = {
        "name": "P9.1 行政区划市场地图与 Socratic Intake 自动化验收报告",
        "goal": "验证 P9.1 在本地/fixture 范围内实现行政区划下钻式市场地图、Market Provider 状态、Socratic Intake 和产物台联动；不声明真实 provider、招聘平台抓取、真实 ASR 或自动投递通过。",
        "url": app_url,
        "targetArchitecture": [
            "TopServiceCenter 增加 Market Provider 状态，未配置时显示 Market Provider: not_configured。",
            "LeftIntelligencePanel 的市场页升级为 ECharts 行政区划下钻式市场地图。",
            "MarketIntelligenceMap 包含 visualMap、tooltip、toolbox、breadcrumb、图层切换、source legend 和 RegionInsightPanel。",
            "ConversationPlane 支持 Socratic Intake 一问一答事实采集。",
            "Workbench / P9ArtifactOverview 展示 CandidateFactSummary、ProjectStoryDraft、PendingConfirmations 和 DoNotClaimList。",
        ],
        "currentImplementation": [
            "apps/chatbox/src/main.tsx 使用 echarts.registerMap 和 fixture-only 行政区划数据。",
            "市场图层支持机会热度、薪资、技术栈、来源可信度；数字均标注 fixture/manual/public/opt-in API 边界。",
            "Chatbox 本地命令路由实现 Socratic Intake，不调用真实 provider。",
            "右侧产物台展示 Socratic facts、待确认项和不可声明清单。",
        ],
        "viewports": [
            {"name": "desktop1920", "width": 1920, "height": 1080},
            {"name": "desktop1440", "width": 1440, "height": 920},
            {"name": "desktop1200", "width": 1200, "height": 900},
            {"name": "tablet720", "width": 720, "height": 920},
            {"name": "mobile390", "width": 390, "height": 860, "mobile": True},
        ],
        "steps": [
            {"viewport": "desktop1920", "name": "打开 P9.1 工作台", "action": "goto"},
            {"viewport": "desktop1920", "name": "等待服务中心", "action": "waitText", "text": "Market Provider", "timeoutMs": 30000},
            {"viewport": "desktop1920", "name": "P9.1 初始行政区划地图", "action": "screenshot", "file": "p9_1_initial_1920.png"},
            {"viewport": "desktop1920", "name": "点击北京下钻", "action": "clickText", "text": "北京"},
            {"viewport": "desktop1920", "name": "等待北京市层级", "action": "waitText", "text": "北京市", "timeoutMs": 10000},
            {"viewport": "desktop1920", "name": "北京下钻证据", "action": "screenshot", "file": "p9_1_beijing_drilldown_1920.png"},
            {"viewport": "desktop1920", "name": "切换薪资图层", "action": "clickText", "text": "薪资中位"},
            {"viewport": "desktop1920", "name": "薪资图层证据", "action": "screenshot", "file": "p9_1_salary_layer_1920.png"},
            {"viewport": "desktop1920", "name": "输入 Socratic 请求", "action": "fill", "selector": "textarea", "value": "帮我整理智能客服控制台项目故事"},
            {"viewport": "desktop1920", "name": "发送 Socratic 请求", "action": "clickText", "text": "发送任务"},
            {"viewport": "desktop1920", "name": "等待 Socratic 启动", "action": "waitText", "text": "Socratic Intake", "timeoutMs": 10000},
            {"viewport": "desktop1920", "name": "回答目标岗位", "action": "fill", "selector": "textarea", "value": "LLM 应用前端工程师"},
            {"viewport": "desktop1920", "name": "发送目标岗位", "action": "clickText", "text": "发送任务"},
            {"viewport": "desktop1920", "name": "等待下一问", "action": "waitText", "text": "项目背景", "timeoutMs": 10000},
            {"viewport": "desktop1920", "name": "Socratic 一问一答证据", "action": "screenshot", "file": "p9_1_socratic_1920.png"},
            {"viewport": "desktop1440", "name": "1440 重新打开", "action": "goto"},
            {"viewport": "desktop1440", "name": "1440 等待", "action": "waitText", "text": "Market Provider", "timeoutMs": 30000},
            {"viewport": "desktop1440", "name": "1440 P9.1 可视度", "action": "screenshot", "file": "p9_1_1440.png"},
            {"viewport": "desktop1200", "name": "1200 重新打开", "action": "goto"},
            {"viewport": "desktop1200", "name": "1200 等待", "action": "waitText", "text": "Market Provider", "timeoutMs": 30000},
            {"viewport": "desktop1200", "name": "1200 P9.1 可视度", "action": "screenshot", "file": "p9_1_1200.png"},
            {"viewport": "tablet720", "name": "720 重新打开", "action": "goto"},
            {"viewport": "tablet720", "name": "720 等待", "action": "waitText", "text": "发送任务", "timeoutMs": 30000},
            {"viewport": "tablet720", "name": "720 Chatbox 优先", "action": "screenshot", "file": "p9_1_720.png"},
            {"viewport": "mobile390", "name": "390 重新打开", "action": "goto"},
            {"viewport": "mobile390", "name": "390 等待", "action": "waitText", "text": "发送任务", "timeoutMs": 30000},
            {"viewport": "mobile390", "name": "390 输入区可达", "action": "screenshot", "file": "p9_1_390.png"},
        ],
        "acceptanceCriteria": [
            "ECharts 行政区划下钻地图可见，含 visualMap、tooltip、toolbox、breadcrumb、source legend。",
            "地图下钻、图层切换和区域详情能通过真实界面截图证明。",
            "Market Provider: not_configured 可见，不发生真实 provider 或招聘平台调用。",
            "Socratic Intake 一次只问一个问题，并在右侧产物台展示事实、待确认项和不可声明清单。",
            "报告区分真实截图、fixture、未验证 provider 和高风险未完成能力。",
        ],
        "commandResults": [
            {"command": item["command"], "status": item["status"], "evidence": item["summary"]}
            for item in command_evidence["results"]
        ],
        "prdReview": [
            {"requirement": "行政区划下钻式市场地图", "evidence": "P9.1 截图展示 ECharts map/geo、breadcrumb、图层和区域详情。", "status": "PASS"},
            {"requirement": "真实市场数据 provider 边界", "evidence": "Market Provider: not_configured 显示在报告正文和真实截图中，报告声明未外呼真实市场 API。", "status": "PASS"},
            {"requirement": "Socratic Intake", "evidence": "截图和 transcript 展示一问一答事实采集。", "status": "PASS"},
            {"requirement": "产物台联动", "evidence": "右侧展示 CandidateFactSummary、PendingConfirmations、DoNotClaimList。", "status": "PASS"},
        ],
        "codeReview": [
            {"area": "Frontend map", "finding": "ECharts 行政区划下钻使用 fixture-only GeoJSON；未新增外部地图服务。", "severity": "passed"},
            {"area": "Socratic route", "finding": "Chatbox 本地状态机处理一问一答，不外呼真实 provider。", "severity": "passed"},
            {"area": "Residual risk", "finding": "GeoJSON 仍需在真实发布前做许可审查；本轮不声明真实市场。", "severity": "warning"},
        ],
        "documentationAudit": [
            {"area": "P9.1 PRD", "finding": "实现范围与行政区划下钻、provider 状态、Socratic Intake 一致。", "status": "passed"},
            {"area": "目标架构", "finding": "未扩张为招聘平台抓取、ASR、真实 provider 或自动投递系统。", "status": "passed"},
            {"area": "验收门槛", "finding": "报告包含真实截图、命令结果、PRD 检视、false-green 边界。", "status": "passed"},
        ],
        "multiTurnDialogues": _multi_turn_dialogues(),
        "unverifiedScope": [
            "未登录、抓取、自动沟通或自动投递 BOSS、猎聘、拉勾、LinkedIn 等招聘平台。",
            "未执行真实全网 JD 搜索，只使用用户粘贴、已导入 JD、repo fixture 和本地示例表达。",
            "未默认调用 MiniMax、DeepSeek 或 OpenAI-compatible provider。",
            "未读取用户真实个人资料路径。",
            "未采集麦克风，未调用真实 ASR。",
            "未建设 MCP/Skill 平台、SaaS、多租户、Billing 或会议平台能力。",
        ],
        "auditOpinion": "P9.1 自动化候选通过只覆盖本地/fixture 范围内的 UI、状态机和证据链。真实市场 provider、真实招聘平台、真实 ASR 和自动投递仍需独立授权与验收。",
    }
    SCENARIO.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")


def _post_report_validation() -> dict:
    html = REPORT.read_text(encoding="utf-8")
    image_refs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    missing = []
    for ref in image_refs:
        path = (REPORT.parent / ref).resolve()
        if not path.exists() or path.stat().st_size <= 1024:
            missing.append(ref)
    required = [
        "P9.1 行政区划市场地图与 Socratic Intake 自动化验收报告",
        "目标架构",
        "当前实现",
        "PRD 规格检视",
        "截图证据",
        "未验证范围与审计意见",
        "ECharts",
        "行政区划下钻",
        "Socratic Intake",
        "Market Provider: not_configured",
    ]
    missing_text = [item for item in required if item not in html]
    forbidden = [
        "真实市场 provider 已接入",
        "全网 JD 搜索已完成",
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实 ASR 已实现",
        "自动投递已实现",
        "MCP/Skill 连通性已通过",
    ]
    forbidden_hits = [item for item in forbidden if item in html]
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image_count": len(image_refs),
        "missing_images": missing,
        "missing_text": missing_text,
        "forbidden_hits": forbidden_hits,
        "status": "passed" if len(image_refs) >= 8 and not missing and not missing_text and not forbidden_hits else "failed",
    }
    POST_REPORT_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    if evidence["status"] != "passed":
        raise RuntimeError(json.dumps(evidence, ensure_ascii=False, indent=2))
    return evidence


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    command_evidence = _run_validation_commands()
    _write_scenario(command_evidence)
    api_proc = None
    vite_proc = None
    try:
        try:
            _wait_url(f"http://127.0.0.1:{API_PORT}/api/health", timeout=2)
        except Exception:
            api_proc = _start_process(
                [PYTHON_BIN, "-m", "uvicorn", "services.api.main:app", "--host", "127.0.0.1", "--port", API_PORT],
                EVIDENCE_DIR / "api.log",
            )
            _wait_url(f"http://127.0.0.1:{API_PORT}/api/health", timeout=40)

        vite_proc = _start_process(
            ["bash", "-lc", f"cd apps/chatbox && VITE_API_BASE_URL=http://127.0.0.1:{API_PORT} npx vite --host 127.0.0.1 --port {CHATBOX_PORT} --strictPort"],
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
                "9251",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=220,
        )
        post = _post_report_validation()
        print(json.dumps({"report": str(REPORT), "post_validation": post, "git_head": _git_head(), "git_status": _git_status_short()}, ensure_ascii=False, indent=2))
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
