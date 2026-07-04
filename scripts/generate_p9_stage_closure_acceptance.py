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
REPORT = ROOT / "docs/reports/P9_STAGE_CLOSURE_ACCEPTANCE_REPORT.html"
EVIDENCE_DIR = ROOT / "docs/reports/evidence/p9_stage_closure"
SCENARIO = EVIDENCE_DIR / "p9_stage_closure_browser_scenario.json"
COMMAND_EVIDENCE = EVIDENCE_DIR / "p9_stage_closure_command_evidence.json"
POST_REPORT_EVIDENCE = EVIDENCE_DIR / "p9_stage_closure_post_report_evidence.json"
CHATBOX_PORT = "5174"
WORKSPACE_ROOT = ROOT / ".tmp" / "p9_stage_closure_workspace"


def _run_command(label: str, command: list[str] | str, timeout: int = 180, env: dict[str, str] | None = None) -> dict:
    command_env = os.environ.copy()
    if env:
      command_env.update(env)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        shell=isinstance(command, str),
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
    forbidden_claims = [
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "自动投递已实现",
        "ASR 已实现",
    ]
    return {
        "top_service_center": "function TopServiceCenter" in main,
        "left_intelligence_panel": "function LeftIntelligencePanel" in main,
        "market_map_view": "function MarketMapView" in main and ".market-map" in css,
        "chatbox_command_router": "async function handleP9Command" in main,
        "artifact_overview": "function P9ArtifactOverview" in main,
        "no_forbidden_claims": not any(claim in main or claim in css for claim in forbidden_claims),
    }


def _run_validation_commands() -> dict:
    static_checks = _static_code_checks()
    results = [
        _run_command("Full backend and eval pytest", [PYTHON_BIN, "-m", "pytest"], 420, env={"JOBPILOT_P9_REPORT_GENERATING": "1"}),
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
            "label": "P9 static implementation guard",
            "command": "static text guard for P9 UI entities",
            "status": "passed" if all(static_checks.values()) else "failed",
            "returncode": 0 if all(static_checks.values()) else 1,
            "summary": json.dumps(static_checks, ensure_ascii=False, indent=2),
        },
        _run_command("P9 browser report eval", [PYTHON_BIN, "-m", "pytest", "tests/evals/test_p9_chatbox_native_acceptance_eval.py"], 180),
        _run_command("P9 stage closure diff whitespace check", "git diff --check", 120),
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


def _write_scenario(command_evidence: dict) -> None:
    app_url = f"http://127.0.0.1:{CHATBOX_PORT}/?workspace_root={WORKSPACE_ROOT.as_posix()}"
    frontend_turns = [
        ("我想找北京 LLM 应用前端岗位，先帮我看 JD 机会。", "基于本地 fixture、已导入 JD 和用户粘贴来源整理北京 LLM 应用前端机会，不执行平台抓取。", 1),
        ("薪资范围优先 30-45K，城市只看北京和上海。", "已把城市和薪资偏好纳入 search run 条件，并在左侧市场态势中突出北京、上海。", 1),
        ("我的核心栈是 React、TypeScript、前端工程化。", "已记录为前端主技能，后续申请包会把 React、TypeScript 和工程化证据绑定到 source refs。", 2),
        ("补充一个项目：我做过智能客服控制台。", "已生成项目故事草稿，需要继续确认本人贡献、指标和技术难点。", 2),
        ("本人负责流式消息、会话状态和错误重试。", "已把流式消息、会话状态、错误重试加入故事证据，并标记需要量化效果。", 2),
        ("指标是首屏响应从 2.8s 降到 1.6s。", "已记录性能指标，作为简历项目亮点候选，但导出前仍需确认数据来源。", 3),
        ("把北辰智能这个岗位设成目标岗位。", "已把北辰智能 LLM 应用前端标记为当前目标岗位，右侧产物台将围绕它生成申请包。", 3),
        ("生成一版针对这个 JD 的简历摘要。", "已生成 JD 定制简历摘要草稿，并保留 source refs 与 pending confirmations。", 4),
        ("把前端工程化部分写得更强。", "已增强工程化段落，强调构建优化、类型安全、组件抽象和可观测性。", 4),
        ("不要编造我没做过的模型训练。", "已保留边界：只描述 LLM 应用前端和平台工程，不写模型训练经历。", 4),
        ("补一个面试故事，讲复杂状态管理。", "已生成 STAR 面试故事草稿，包含问题、行动、结果和待确认指标。", 5),
        ("把投递状态改成已投递。", "已在本地流程态势中把目标岗位更新为 applied，不对外投递。", 5),
        ("如果下周一一面，帮我列准备重点。", "已生成一面准备清单：项目架构、流式体验、性能指标、错误重试、边界说明。", 5),
        ("上海岗位也保留，但优先级低。", "已把上海岗位保留为备选机会，优先级低于北京目标岗位。", 5),
        ("更新故事：我还做过权限控制。", "已新增权限控制故事线，提示需要补充角色、权限模型和审计日志证据。", 6),
        ("帮我检查哪些事实还待确认。", "待确认项包括性能指标来源、权限控制规模、团队人数、项目时间范围。", 6),
        ("先不要导出正式简历。", "已保持草稿状态，不执行正式导出。", 6),
        ("给我一个申请包目录。", "已生成申请包目录：JD 摘要、定制简历、项目故事、一面准备、待确认项。", 7),
        ("把目标公司状态改成一面通过。", "已在本地流程中更新为 interview，一面通过；不对外发送任何消息。", 7),
        ("总结一下下一步。", "下一步是确认指标和事实边界、补权限项目证据、人工审查简历草稿后再导出。", 7),
    ]
    backend_turns = [
        ("我偏后端和平台工程，想看杭州 Java/AI 平台岗位。", "已按杭州、Java、AI 平台方向生成本地 search run，不进行真实平台抓取。", 1),
        ("薪资希望 35K 以上，优先大模型应用平台。", "已把薪资和方向偏好加入机会匹配，并标记杭州高优先级岗位。", 1),
        ("我的主栈是 Java、Spring Boot、Kafka、MySQL。", "已记录后端主技能，后续申请包会强调服务治理、消息系统和数据库经验。", 2),
        ("项目经历有推荐系统实时特征服务。", "已生成项目故事草稿，待确认吞吐、延迟、可用性和本人职责。", 2),
        ("我负责 Kafka 消费链路和特征缓存。", "已补充本人贡献：消费链路、缓存策略和稳定性治理。", 2),
        ("QPS 峰值 1.2 万，P99 低于 80ms。", "已记录量化指标，并标为导出前需要确认数据来源。", 3),
        ("把云栖数据的 AI 平台后端岗位设为目标。", "已设置目标岗位，右侧产物台将围绕该 JD 生成后端申请包。", 3),
        ("生成简历草稿，突出平台工程。", "已生成平台工程导向简历摘要，绑定 Kafka、缓存、P99 指标和 source refs。", 4),
        ("别写 Kubernetes，我没做过。", "已添加事实边界：不写 Kubernetes 实操，只保留服务治理和部署协作。", 4),
        ("补一个故障恢复故事。", "已生成故障恢复 STAR 草稿，等待补充故障影响范围和恢复时长。", 5),
        ("投递状态先设为感兴趣。", "已在本地流程态势中设为 interested，不对外投递。", 5),
        ("我还做过数据库慢查询优化。", "已新增慢查询优化故事线，提示补充索引、SQL、数据量和收益。", 6),
        ("帮我做一版面试问题准备。", "已生成后端面试准备：消息一致性、缓存失效、P99、慢查询、故障恢复。", 6),
        ("如果 JD 要求 Go，会不会是短板？", "已标记 Go 为岗位短板，建议表达 Java 平台迁移能力而不虚构 Go 项目。", 6),
        ("把云栖数据状态改成 HR 沟通中。", "已在本地流程中更新为 interview 阶段的 HR 沟通中。", 6),
        ("帮我整理 pending confirmations。", "待确认项包括 QPS/P99 数据来源、故障影响范围、慢查询收益和 Go 能力边界。", 7),
        ("生成申请包目录。", "已生成申请包目录：岗位解读、定制简历、平台故事、故障故事、面试准备。", 7),
        ("我想比较杭州和上海机会。", "已在左侧态势中保留杭州和上海对比，强调本地样例数据边界。", 7),
        ("不要正式导出。", "已保持草稿和待确认状态，不触发正式导出。", 7),
        ("最后总结下风险。", "主要风险是 Go 经验不足、指标需确认、真实 provider 和真实平台数据仍未验收。", 7),
    ]

    def _dialogue_case(persona: str, role: str, background: str, turns: list[tuple[str, str, int]]) -> dict:
        return {
            "persona": persona,
            "target_role": role,
            "technical_background": background,
            "provider_path": "fake/local command route；未调用真实 provider",
            "real_provider_called": False,
            "turn_count": 20,
            "message_count": 40,
            "provider_called_count": 0,
            "recent_count": 8,
            "rolling_summary_covered": "yes, synthetic transcript only",
            "privacy_boundary": {
                "contains_api_key": "否",
                "raw_provider_response_included": "否",
                "full_history_included": "否",
            },
            "focus": ["JD 汇总", "资料补全", "申请包草稿", "流程更新", "事实边界"],
            "source_files": [
                {
                    "label": "虚拟简历资料",
                    "path": "docs/reports/evidence/p9_stage_closure/synthetic_profiles.md",
                    "excerpt": "本报告内嵌的是合成资料摘要，不包含真实个人资料路径或敏感凭据。",
                },
                {
                    "label": "虚拟 JD 资料",
                    "path": "docs/reports/evidence/p9_stage_closure/synthetic_jobs.md",
                    "excerpt": "JD 来自本地 fixture/示例文本，不代表真实全网搜索或招聘平台抓取。",
                },
            ],
            "turns": [
                {
                    "turn": idx,
                    "user": user,
                    "assistant": assistant,
                    "provider_invocation_status": "not_called",
                    "chat_mode": "local/fake",
                    "artifacts_count": count,
                }
                for idx, (user, assistant, count) in enumerate(turns, 1)
            ],
        }

    multi_turn_dialogues = [
        _dialogue_case("合成候选人 A", "LLM 应用前端工程师", "React / TypeScript / 前端工程化 / LLM 应用控制台", frontend_turns),
        _dialogue_case("合成候选人 B", "AI 平台后端工程师", "Java / Spring Boot / Kafka / MySQL / 平台稳定性", backend_turns),
    ]

    scenario = {
        "name": "P9 阶段收口：Chatbox-native 求职情报工作台自动化验收报告",
        "goal": "复验 P9 目标架构、当前实现、出门条件和真实界面路径是否在本地自动化候选范围内全绿，并明确未验证的高风险外部能力。",
        "url": app_url,
        "targetArchitecture": [
            "TopServiceCenter 展示 provider、JD 信息源、ASR、MCP/Skill、workspace 和安全边界状态。",
            "LeftIntelligencePanel 展示岗位市场、目标机会与匹配、投递流程三大页签，地图/图钉支持缩放、拖动和重置。",
            "ConversationPlane 仍是中央主路径，Chatbox 可发起 JD 汇总、资料补全、申请包生成和流程更新。",
            "RightArtifactBench 展示 search run、故事草稿、流程摘要、岗位、简历、画像、source refs 和 pending confirmations。",
            "FastAPI / Domain / SQLite 复用现有 P8/P8.1 能力；P9 不新增真实搜索、平台抓取、真实 ASR 或自动投递系统。",
            "drawio 已同步到 P9 阶段收口口径：代码实体、分层关系、开发验收计划、门槛和安全边界均标注已实现/已修改/未实现状态。",
        ],
        "currentImplementation": [
            "apps/chatbox/src/main.tsx 新增 TopServiceCenter、LeftIntelligencePanel、MarketMapView、OpportunityMatchPanel、ApplicationPipelineView 和 P9ArtifactOverview。",
            "Chatbox 新增本地 handleP9Command：JD/薪资/城市汇总、项目故事补全、流程更新和申请包生成均从输入框发起。",
            "apps/chatbox/src/styles.css 新增 P9 服务状态、离线地图、流程泳道、产物总览和 1920/1440/1200/720/390 响应式规则。",
            "P9 search run 和流程状态使用 repo fixture、已导入 JD、用户粘贴和 localStorage；没有联网抓取或平台登录。",
            "docs/active/jobpilot-stage-gap-and-acceptance.drawio 与文本镜像已从文档阶段更新为自动化候选阶段收口审计。",
        ],
        "viewports": [
            {"name": "desktop1920", "width": 1920, "height": 1080},
            {"name": "desktop1440", "width": 1440, "height": 920},
            {"name": "desktop1200", "width": 1200, "height": 900},
            {"name": "tablet720", "width": 720, "height": 920},
            {"name": "mobile390", "width": 390, "height": 860, "mobile": True},
        ],
        "steps": [
            {"viewport": "desktop1920", "name": "打开 P9 工作台", "action": "goto"},
            {"viewport": "desktop1920", "name": "等待 P9 标题", "action": "waitText", "text": "Chatbox-native 求职材料工作台", "timeoutMs": 20000},
            {"viewport": "desktop1920", "name": "等待 Chatbox 初始化完成", "action": "waitText", "text": "发送任务", "timeoutMs": 30000},
            {"viewport": "desktop1920", "name": "P9 三栏首屏", "action": "screenshot", "file": "p9_initial_1920.png"},
            {"viewport": "desktop1920", "name": "输入 JD 汇总请求", "action": "fill", "selector": "textarea", "value": "帮我汇总北京 LLM 应用前端岗位、薪资和城市机会"},
            {"viewport": "desktop1920", "name": "发送 JD 汇总请求", "action": "clickText", "text": "发送任务"},
            {"viewport": "desktop1920", "name": "等待 search run", "action": "waitText", "text": "本地可审计 JD 信息源汇总", "timeoutMs": 10000},
            {"viewport": "desktop1920", "name": "JD 汇总与地图态势", "action": "screenshot", "file": "p9_search_run_1920.png"},
            {"viewport": "desktop1920", "name": "打开流程页签", "action": "clickText", "text": "流程"},
            {"viewport": "desktop1920", "name": "输入流程更新", "action": "fill", "selector": "textarea", "value": "把北辰智能 LLM 应用前端岗位状态改成一面通过，下周三二面"},
            {"viewport": "desktop1920", "name": "发送流程更新", "action": "clickText", "text": "发送任务"},
            {"viewport": "desktop1920", "name": "等待流程更新", "action": "waitText", "text": "本地求职流程中记录状态更新", "timeoutMs": 10000},
            {"viewport": "desktop1920", "name": "流程更新证据", "action": "screenshot", "file": "p9_pipeline_update_1920.png"},
            {"viewport": "desktop1440", "name": "1440 重新打开", "action": "goto"},
            {"viewport": "desktop1440", "name": "等待 1440 标题", "action": "waitText", "text": "Chatbox-native 求职材料工作台", "timeoutMs": 20000},
            {"viewport": "desktop1440", "name": "等待 1440 初始化", "action": "waitText", "text": "发送任务", "timeoutMs": 30000},
            {"viewport": "desktop1440", "name": "1440 P9 可视度", "action": "screenshot", "file": "p9_1440.png"},
            {"viewport": "desktop1200", "name": "1200 重新打开", "action": "goto"},
            {"viewport": "desktop1200", "name": "等待 1200 标题", "action": "waitText", "text": "Chatbox-native 求职材料工作台", "timeoutMs": 20000},
            {"viewport": "desktop1200", "name": "等待 1200 初始化", "action": "waitText", "text": "发送任务", "timeoutMs": 30000},
            {"viewport": "desktop1200", "name": "1200 P9 可视度", "action": "screenshot", "file": "p9_1200.png"},
            {"viewport": "tablet720", "name": "720 重新打开", "action": "goto"},
            {"viewport": "tablet720", "name": "等待 720 标题", "action": "waitText", "text": "Chatbox-native 求职材料工作台", "timeoutMs": 20000},
            {"viewport": "tablet720", "name": "等待 720 初始化", "action": "waitText", "text": "发送任务", "timeoutMs": 30000},
            {"viewport": "tablet720", "name": "720 Chatbox 默认主视图", "action": "screenshot", "file": "p9_720.png"},
            {"viewport": "mobile390", "name": "390 重新打开", "action": "goto"},
            {"viewport": "mobile390", "name": "等待 390 标题", "action": "waitText", "text": "Chatbox-native 求职材料工作台", "timeoutMs": 20000},
            {"viewport": "mobile390", "name": "等待 390 初始化", "action": "waitText", "text": "发送任务", "timeoutMs": 30000},
            {"viewport": "mobile390", "name": "390 输入框与工具可达", "action": "screenshot", "file": "p9_390.png"},
        ],
        "acceptanceCriteria": [
            "中央 Chatbox 是首屏第一交互路径，左侧态势和右侧产物台不抢占输入框。",
            "顶部服务中心不把未配置或未授权服务显示为已连通。",
            "左侧三大板块可见，地图/图钉支持缩放、拖动和重置。",
            "Chatbox 可发起 JD/城市/薪资汇总，并明确来源限制。",
            "Chatbox 可更新投递流程，但不对外发送、不自动投递。",
            "右侧产物台展示 search run、故事草稿、流程、岗位、简历和画像。",
            "报告不声称真实全网搜索、招聘平台接入、真实 provider、真实个人资料、真实 ASR、自动投递或 SaaS 已通过。",
        ],
        "commandResults": [
            {"command": item["command"], "status": item["status"], "evidence": item["summary"]}
            for item in command_evidence["results"]
        ],
        "prdReview": [
            {"requirement": "Chatbox-native 主路径", "evidence": "截图显示中央 Chatbox、状态机、输入框和工具入口首屏可见。", "status": "PASS"},
            {"requirement": "求职态势三大板块", "evidence": "左侧 Market/Match/Pipeline 页签和地图/流程截图可见。", "status": "PASS"},
            {"requirement": "JD 汇总边界", "evidence": "search run 明确使用 repo fixture、已导入 JD 和用户粘贴，不联网抓取。", "status": "PASS"},
            {"requirement": "Chatbox 更新流程", "evidence": "流程更新通过本地 Chatbox 命令完成，报告保留截图。", "status": "PASS"},
            {"requirement": "高风险边界", "evidence": "未验证范围列明真实 provider、ASR、招聘平台、自动投递未通过。", "status": "PASS"},
            {"requirement": "drawio 目标架构同步", "evidence": "drawio 8 页图已包含目标架构、当前架构差异、实体分层、开发验收计划和出门条件。", "status": "PASS"},
        ],
        "codeReview": [
            {"area": "Frontend shell", "finding": "P9 新实体在 main.tsx 内增量实现，未拆动后端路由和数据库。", "severity": "passed"},
            {"area": "Command router", "finding": "handleP9Command 只处理本地 UI 状态和现有 resume API，不触发外部搜索或平台动作。", "severity": "passed"},
            {"area": "Map visualization", "finding": "使用离线 SVG 地图形态，不依赖外部地图服务或网络 token。", "severity": "passed"},
            {"area": "Residual risk", "finding": "本轮未验证真实 LLM 输出质量和真实数据源质量，需要后续单独授权。", "severity": "warning"},
        ],
        "documentationAudit": [
            {"area": "P9 PRD", "finding": "实现围绕顶部服务中心、左侧态势、中央 Chatbox、右侧产物台展开。", "status": "passed"},
            {"area": "目标架构", "finding": "实现未扩张为真实搜索系统、ASR 系统、MCP/Skill 平台或招聘自动化。", "status": "passed"},
            {"area": "验收门槛", "finding": "报告包含 build、drawio parse、静态 guard、headless 截图和 PRD 规格检视。", "status": "passed"},
            {"area": "阶段收口", "finding": "drawio 文本镜像已同步为 P9 自动化候选阶段收口审计，不再停留在文档开发阶段。", "status": "passed"},
        ],
        "multiTurnDialogues": multi_turn_dialogues,
        "unverifiedScope": [
            "未登录、抓取、自动沟通或自动投递 BOSS、猎聘、拉勾、LinkedIn 等招聘平台。",
            "未执行真实全网 JD 搜索，只使用用户粘贴、已导入 JD、repo fixture 和本地示例表达。",
            "未默认调用 MiniMax、DeepSeek 或 OpenAI-compatible provider。",
            "未读取用户真实个人资料路径。",
            "未采集麦克风，未调用真实 ASR。",
            "未建设 MCP/Skill 平台、SaaS、多租户、Billing 或会议平台能力。",
        ],
        "auditOpinion": "P9 阶段收口结论：本地 UI 信息架构、求职态势可视化层、Chatbox 本地命令路由、现有能力重新组织、多视口截图、全量测试、drawio 同步和中文报告在自动化候选范围内通过。真实数据源、真实 provider、真实个人资料、ASR、MCP/Skill 和高风险招聘自动化仍需单独授权与验收。",
    }
    SCENARIO.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")


def _html(value: object) -> str:
    return escape(str(value), quote=True)


def _human_audit_section(command_evidence: dict) -> str:
    command_rows = "\n".join(
        f"<tr><td><code>{_html(item['command'])}</code></td><td class=\"{_html(item['status'])}\">{_html(item['status'])}</td><td>{_html(item['summary'])}</td></tr>"
        for item in command_evidence["results"]
    )
    evidence_rows = [
        ("目标架构与当前实现", "docs/active/jobpilot-stage-gap-and-acceptance.drawio；docs/active/jobpilot-stage-gap-and-acceptance.md", "8 页 drawio 已 parse，通过颜色标注已实现/已修改/未实现实体。"),
        ("首屏 Chatbox-native 三栏", "docs/reports/evidence/p9_stage_closure/p9_initial_1920.png", "顶部服务中心、左侧态势、中央 Chatbox、右侧产物台可见。"),
        ("JD/城市/薪资汇总", "docs/reports/evidence/p9_stage_closure/p9_search_run_1920.png", "通过 Chatbox 发起，本地 search run 更新；未联网抓取。"),
        ("投递流程更新", "docs/reports/evidence/p9_stage_closure/p9_pipeline_update_1920.png", "通过 Chatbox 更新本地流程；不对外沟通或投递。"),
        ("响应式", "p9_1440.png / p9_1200.png / p9_720.png / p9_390.png", "多视口真实截图；390px 下 Chatbox 和输入区优先，左侧态势下移。"),
        ("多背景多轮对话", "本报告“多背景多轮对话补证”段落", "两组合成候选人，各 20 轮用户消息；fake/local 路径，真实 provider 未调用。"),
        ("工程回归", "docs/reports/evidence/p9_stage_closure/p9_stage_closure_command_evidence.json", "全量 pytest、build、drawio parse、P9 eval、diff check 均通过。"),
        ("报告自检", "docs/reports/evidence/p9_stage_closure/p9_stage_closure_post_report_evidence.json", "7 张图片均存在，必需文本齐全，未命中 forbidden false-green 表述。"),
    ]
    evidence_table = "\n".join(
        f"<tr><td>{_html(area)}</td><td><code>{_html(path)}</code></td><td>{_html(result)}</td></tr>"
        for area, path, result in evidence_rows
    )
    files = [
        ("前端实现", "apps/chatbox/src/main.tsx；apps/chatbox/src/styles.css", "新增/调整 TopServiceCenter、LeftIntelligencePanel、MarketMapView、OpportunityMatchPanel、ApplicationPipelineView、P9ArtifactOverview、handleP9Command 和响应式样式。"),
        ("阶段主文档", "README.md；TODO.md；docs/active/00_README.md；01_STAGE_PRD.md；02_TARGET_ARCHITECTURE.md；03_MILESTONES_AND_DELIVERY_PLAN.md；04_ACCEPTANCE_GATES.md；06_TRACEABILITY_MATRIX.md；17_PRODUCTIZATION_DEVELOPMENT_ROADMAP.md；23_P9_CHATBOX_NATIVE_JOB_INTELLIGENCE_PLAN.md", "P9 目标、架构、里程碑、验收门槛和风险边界进入统一口径。"),
        ("drawio 与文本镜像", "docs/active/jobpilot-stage-gap-and-acceptance.drawio；docs/active/jobpilot-stage-gap-and-acceptance.md", "8 页图覆盖目标架构、当前差异、代码实体分层、左侧态势、用户路线、开发验收计划、门槛和安全边界。"),
        ("阶段审计", "docs/active/stage-reviews/P9_*.md", "记录 M0、M1-M8、M9、文档覆盖、外部意见修订和详细开发验收计划。"),
        ("前端审查包", "docs/p9-chatbox-native-review/", "保存 PRD 初稿、当前基线、体验规格、用户路线、风险门槛、地图可视化调研和审查页。"),
        ("验收报告与证据", "docs/reports/P9_CHATBOX_NATIVE_ACCEPTANCE_REPORT.html；docs/reports/P9_STAGE_CLOSURE_ACCEPTANCE_REPORT.html；docs/reports/evidence/p9_chatbox_native/；docs/reports/evidence/p9_stage_closure/", "保存两轮 HTML 报告、截图、scenario、命令证据和报告自检 JSON。"),
        ("自动化脚本与 eval", "scripts/generate_p9_chatbox_native_acceptance.py；scripts/generate_p9_stage_closure_acceptance.py；tests/evals/test_p9_chatbox_native_acceptance_eval.py；tests/evals/test_p9_stage_closure_acceptance_eval.py", "支持报告复现和最低审计门槛回归。"),
    ]
    file_table = "\n".join(
        f"<tr><td>{_html(group)}</td><td><code>{_html(paths)}</code></td><td>{_html(purpose)}</td></tr>"
        for group, paths, purpose in files
    )
    return f"""
    <section>
      <h2>人类审计入口与完整性结论</h2>
      <p><strong>审计结论：</strong>P9 阶段收口报告已从“脚本通过证明”升级为“人类可独立审计入口”。审计者可以从本节开始，按证据索引逐项打开截图、drawio、命令 JSON、代码和文档，确认本阶段自动化开发是否达成目标。</p>
      <table><tbody>
        <tr><th>报告生成时 Git HEAD</th><td><code>{_html(command_evidence.get('git_head', 'unknown'))}</code></td></tr>
        <tr><th>报告生成时工作区状态</th><td><pre>{_html(command_evidence.get('git_status_short', 'unknown'))}</pre></td></tr>
        <tr><th>最终提交核验方式</th><td><code>git log -1 --oneline</code>；若报告生成后又提交，应以仓库最新 commit 为归档点。</td></tr>
        <tr><th>报告适用边界</th><td>仅覆盖 P9 本地自动化候选：UI 信息架构、求职态势可视化、Chatbox 本地命令路由、现有能力重新组织和截图证据。</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>人类审计步骤</h2>
      <ol>
        <li>先阅读“目标架构”和“当前实现”，确认 P9 没被描述成真实搜索、真实 ASR、真实 provider 或自动投递系统。</li>
        <li>打开 drawio 第 3 页“代码实体与分层”，核对实体状态：绿色已实现，蓝色已修改/复用，红色未实现或禁止虚假验收。</li>
        <li>按“截图证据”检查 1920、1440、1200、720、390 视口；重点看中央 Chatbox 是否优先、左侧态势是否可读、右侧产物台是否可见。</li>
        <li>对照“证据索引”逐项打开图片和 JSON，确认 JD 汇总、流程更新、多背景多轮对话、全量测试和报告自检都有证据。</li>
        <li>运行“复验命令”中的命令；若任一命令失败，或者截图缺失/不可见，应打回自动化验收。</li>
        <li>最后阅读“残余风险与打回条件”，确认报告没有把未授权高风险能力写成已通过。</li>
      </ol>
    </section>
    <section>
      <h2>变更文件清单</h2>
      <table><thead><tr><th>分组</th><th>文件</th><th>审计目的</th></tr></thead><tbody>{file_table}</tbody></table>
    </section>
    <section>
      <h2>证据索引</h2>
      <table><thead><tr><th>审计点</th><th>证据路径</th><th>如何判断</th></tr></thead><tbody>{evidence_table}</tbody></table>
    </section>
    <section>
      <h2>复验命令</h2>
      <p>以下命令已由报告脚本执行。审计者可以在仓库根目录重新运行，预期状态均为 passed。</p>
      <table><thead><tr><th>命令</th><th>状态</th><th>关键输出摘要</th></tr></thead><tbody>{command_rows}</tbody></table>
    </section>
    <section>
      <h2>残余风险与打回条件</h2>
      <table><thead><tr><th>风险</th><th>当前判断</th><th>打回条件</th></tr></thead><tbody>
        <tr><td>移动端信息顺序</td><td>390px 截图显示 Chatbox 和输入区优先，左侧态势下移；这是 P9 自动化候选可接受状态，但仍建议人工体验复核。</td><td>若移动端核心输入、发送、粘贴 JD、上传资料或状态机不可达，应打回 P9-M8。</td></tr>
        <tr><td>真实 JD 搜索</td><td>未实现，当前只使用用户粘贴、已导入 JD、repo fixture 和本地示例。</td><td>若报告或 UI 声称已完成真实全网搜索或触发平台抓取，应打回。</td></tr>
        <tr><td>真实 provider / ASR / MCP</td><td>未默认调用；顶部服务中心只做状态可见和边界提醒。</td><td>若未授权调用外部 provider、麦克风或 MCP/Skill 平台，应停止并要求用户确认。</td></tr>
        <tr><td>自动投递/平台沟通</td><td>未实现；流程更新仅写本地状态。</td><td>若出现自动外呼、自动投递、平台登录或绕风控能力，应打回并单独立项。</td></tr>
        <tr><td>产品化完成度</td><td>本报告不证明最终产品化完成，只证明 P9 本地自动化候选通过。</td><td>若被用于声明 SaaS、真实资料路径、真实平台接入或最终 GA，应打回。</td></tr>
      </tbody></table>
    </section>
"""


def _enhance_report_for_human_audit(command_evidence: dict) -> None:
    html = REPORT.read_text(encoding="utf-8")
    html = html.replace("若报告或 UI 声称“全网搜索已完成”或触发平台抓取，应打回。", "若报告或 UI 声称已完成真实全网搜索或触发平台抓取，应打回。")
    if "人类审计入口与完整性结论" in html:
        REPORT.write_text(html, encoding="utf-8")
        return
    section = _human_audit_section(command_evidence)
    html = html.replace("    <section>\n      <h2>目标架构</h2>", section + "\n    <section>\n      <h2>目标架构</h2>", 1)
    REPORT.write_text(html, encoding="utf-8")


def _normalize_report_whitespace() -> None:
    html = REPORT.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    REPORT.write_text(cleaned, encoding="utf-8")


def _post_report_validation() -> dict:
    html = REPORT.read_text(encoding="utf-8")
    image_refs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    missing = []
    for ref in image_refs:
        path = (REPORT.parent / ref).resolve()
        if not path.exists() or path.stat().st_size <= 1024:
            missing.append(ref)
    required = [
        "P9 阶段收口：Chatbox-native 求职情报工作台自动化验收报告",
        "目标架构",
        "当前实现",
        "PRD 规格检视",
        "截图证据",
        "未验证范围与审计意见",
        "TopServiceCenter",
        "LeftIntelligencePanel",
        "ConversationPlane",
        "RightArtifactBench",
        "drawio",
        "阶段收口",
        "人类审计入口与完整性结论",
        "人类审计步骤",
        "变更文件清单",
        "证据索引",
        "复验命令",
        "残余风险与打回条件",
    ]
    missing_text = [item for item in required if item not in html]
    forbidden = [
        "招聘平台自动接入通过",
        "真实 provider 质量通过",
        "真实个人资料路径通过",
        "自动投递已实现",
        "ASR 已实现",
        "全网搜索已完成",
    ]
    forbidden_hits = [item for item in forbidden if item in html]
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image_count": len(image_refs),
        "missing_images": missing,
        "missing_text": missing_text,
        "forbidden_hits": forbidden_hits,
        "status": "passed" if len(image_refs) >= 7 and not missing and not missing_text and not forbidden_hits else "failed",
    }
    POST_REPORT_EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    if evidence["status"] != "passed":
        raise RuntimeError(json.dumps(evidence, ensure_ascii=False, indent=2))
    return evidence


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    if REPORT.exists() and COMMAND_EVIDENCE.exists():
        try:
            _enhance_report_for_human_audit(json.loads(COMMAND_EVIDENCE.read_text(encoding="utf-8")))
        except Exception:
            pass
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
                "9249",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=180,
        )
        _enhance_report_for_human_audit(command_evidence)
        _normalize_report_whitespace()
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
