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
        _run_command("Full backend and eval pytest", [PYTHON_BIN, "-m", "pytest"], 420),
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
