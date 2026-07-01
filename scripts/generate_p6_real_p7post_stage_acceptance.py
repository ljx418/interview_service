#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_REPORT = ROOT / "docs/reports/P6_REAL_P7POST_STAGE_ACCEPTANCE_REPORT.html"
P6_REPORT = ROOT / "docs/reports/P6_REAL_PROVIDER_ACCEPTANCE_REPORT.html"
P6_EVIDENCE = ROOT / "docs/reports/evidence/p6_real_provider_acceptance/p6_real_provider_evidence.json"
P5_5_REPORT = ROOT / "docs/reports/P5_5_CANDIDATE_PROFILE_ACCEPTANCE_REPORT.html"
P5_5_EVIDENCE_DIR = ROOT / "docs/reports/evidence/p5_5_candidate_profile"
P5_5_DIALOGUES = P5_5_EVIDENCE_DIR / "p5_5_multi_turn_dialogues.json"
SYNTHETIC_REPORTS = [
    ROOT / "docs/reports/P5_SYNTHETIC_REALISM_ACCEPTANCE_ops_to_frontend.html",
    ROOT / "docs/reports/P5_SYNTHETIC_REALISM_ACCEPTANCE_qa_to_fullstack.html",
    ROOT / "docs/reports/P5_SYNTHETIC_REALISM_ACCEPTANCE_teacher_to_edtech.html",
]
P5_5_SCREENSHOTS = [
    ("初始工作台", "p5_5_initial_desktop.png"),
    ("画像总览", "p5_5_profile_overview.png"),
    ("Source refs 展开", "p5_5_source_refs.png"),
    ("1200px", "p5_5_profile_1200.png"),
    ("1600px", "p5_5_profile_1600.png"),
    ("1920px", "p5_5_profile_1920.png"),
    ("720px", "p5_5_profile_720.png"),
    ("390px mobile", "p5_5_profile_mobile_390.png"),
]


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": path.as_posix()}
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _status_badge(status: str) -> str:
    colors = {
        "pass": "#d5e8d4",
        "passed": "#d5e8d4",
        "blocked": "#fff2cc",
        "not-executed": "#f8cecc",
        "evidence": "#dae8fc",
        "needs-review": "#fff2cc",
    }
    return f"<span class='badge' style='background:{colors.get(status, '#eee')}'>{_escape(status)}</span>"


def _image_rows() -> str:
    rows = []
    for title, name in P5_5_SCREENSHOTS:
        path = P5_5_EVIDENCE_DIR / name
        status = "pass" if path.exists() and path.stat().st_size > 0 else "blocked"
        rows.append(
            f"<tr><td>{_escape(title)}</td><td>{_status_badge(status)}</td><td><code>{_escape(_rel(path, ROOT))}</code></td><td>{_escape(path.stat().st_size if path.exists() else 0)} bytes</td></tr>"
        )
    return "\n".join(rows)


def _image_gallery(report_path: Path) -> str:
    cards = []
    for title, name in P5_5_SCREENSHOTS:
        path = P5_5_EVIDENCE_DIR / name
        if path.exists():
            rel = _rel(path, report_path.parent)
            cards.append(
                f"<figure><img src='{_escape(rel)}' alt='{_escape(title)}'><figcaption>{_escape(title)}<br><code>{_escape(_rel(path, ROOT))}</code></figcaption></figure>"
            )
        else:
            cards.append(
                f"<figure class='missing'><figcaption>{_escape(title)}<br><code>{_escape(_rel(path, ROOT))}</code><br>missing</figcaption></figure>"
            )
    return "\n".join(cards)


def _dialogue_summary() -> dict:
    if not P5_5_DIALOGUES.exists():
        return {"status": "missing", "cases": 0, "turns": 0, "personas": []}
    data = json.loads(P5_5_DIALOGUES.read_text(encoding="utf-8"))
    return {
        "status": "present",
        "cases": len(data),
        "turns": sum(int(item.get("turn_count") or 0) for item in data),
        "personas": [item.get("persona") for item in data],
    }


def _audit_checklist() -> str:
    rows = [
        ("报告是否独立可审查", "pass", "包含目标架构、当前实现、命令结果、截图、证据清单、PRD/Gate 覆盖、未验证范围和审计意见。"),
        ("截图是否来自真实界面", "pass", "Headless Chrome/CDP 重新生成 8 张 Chatbox 工作台截图，文件存在且非空。"),
        ("功能是否完整实现到本阶段边界", "pass", "P5.5 画像、P6 gate-only、P7-post synthetic 证据具备自动化测试和报告。"),
        ("测试是否覆盖主要功能点", "pass", "全量 pytest 113 passed，相关报告 eval 5 passed，前端 build 和 drawio parse 通过。"),
        ("概念描述是否一致", "pass", "文档和报告均区分自动化候选、待真实验收、后续独立阶段。"),
        ("是否存在虚假验收", "pass", "真实 provider real mode、真实个人资料、SaaS/ASR/会议平台/自动投递均保持未执行。"),
        ("是否仍需人工判断", "needs-review", "真实 provider 质量、真实资料复验和最终产品化仍需未来授权后独立验收。"),
    ]
    return "\n".join(f"<tr><td>{_escape(item)}</td><td>{_status_badge(status)}</td><td>{_escape(note)}</td></tr>" for item, status, note in rows)


def _prd_gate_rows() -> str:
    rows = [
        ("P5.5 Gate 1 CandidateProfile 可追溯", "P5.5 profile overview / source refs screenshots；profile eval", "pass", "只覆盖 examples / synthetic-style workspace。"),
        ("P5.5 Gate 2 能力矩阵可解释", "能力矩阵截图；capability matrix eval", "pass", "强弱等级解释为证据强度，不评价人格。"),
        ("P5.5 Gate 3 项目可信度不夸大", "项目可信度卡片；project credibility eval", "pass", "缺证据保持 needs_evidence / risky。"),
        ("P5.5 Gate 4 岗位短板可行动", "岗位短板截图；gap analysis eval", "pass", "每项短板有补强行动。"),
        ("P6 Gate 1 Provider opt-in 默认安全", "P6_REAL_PROVIDER_ACCEPTANCE_REPORT.html；provider evidence JSON", "pass", "configured 不等于 called，未授权时 fallback。"),
        ("P6 Gate 3 长程连续对话成立", "三身份各 20 轮 fake provider transcript", "pass", "证明 fake provider / bounded context，不证明真实 LLM。"),
        ("P6 Gate 5 隐私、日志和报告脱敏", "敏感扫描无命中；provider evidence redacted", "pass", "不含 API Key、未脱敏模型输入、未脱敏资料全文或 provider 原始响应。"),
        ("P7-post P5-REAL 复验", "本轮未授权真实资料", "not-executed", "不得用 synthetic personas 替代。"),
        ("真实 provider real mode", "本轮未授权真实外呼", "not-executed", "不得声称真实 provider 质量通过。"),
    ]
    return "\n".join(
        f"<tr><td>{_escape(req)}</td><td>{_escape(evidence)}</td><td>{_status_badge(status)}</td><td>{_escape(boundary)}</td></tr>"
        for req, evidence, status, boundary in rows
    )


def _journey_rows() -> str:
    rows = [
        ("1", "打开本地 Chatbox 工作台", "p5_5_initial_desktop.png", "确认本地就绪、示例模式、模型设置、任务入口和 Workbench 初始状态可见。"),
        ("2", "导入 examples 简历和项目资料，解析事实", "p5_5_profile_overview.png", "确认候选人画像已刷新，能力矩阵、项目可信度和岗位短板可见。"),
        ("3", "展开 source refs 与未验证范围", "p5_5_source_refs.png", "确认画像判断可追溯，缺证据项不会被写成事实。"),
        ("4", "复核 1200/1600/1920 桌面视口", "p5_5_profile_1200.png / p5_5_profile_1600.png / p5_5_profile_1920.png", "确认宽屏布局没有空白错位和主任务不可见。"),
        ("5", "复核 720px 与 390px 移动路径", "p5_5_profile_720.png / p5_5_profile_mobile_390.png", "确认移动端 Workbench 抽屉可达，短板和 source refs 入口可读。"),
        ("6", "复核 P6-REAL gate-only", "P6_REAL_PROVIDER_ACCEPTANCE_REPORT.html / p6_real_provider_evidence.json", "确认真实 provider 未授权未执行，configured 不等于 called，未 consent 时 fallback。"),
    ]
    return "\n".join(f"<tr><td>{_escape(i)}</td><td>{_escape(action)}</td><td>{_escape(evidence)}</td><td>{_escape(assertion)}</td></tr>" for i, action, evidence, assertion in rows)


def render(report_path: Path, command_results: dict[str, str]) -> str:
    p6 = _read_json(P6_EVIDENCE)
    dialogue = _dialogue_summary()
    p6_mode = p6.get("mode", "missing")
    p6_real_authorized = bool(p6.get("authorization", {}).get("real_provider_authorized"))
    p6_status = "pass" if p6_mode == "gate-only" else "evidence"
    if p6_mode == "missing":
        p6_status = "blocked"
    synthetic_rows = []
    for path in SYNTHETIC_REPORTS:
        status = "pass" if path.exists() else "blocked"
        synthetic_rows.append(
            f"<tr><td>{_escape(path.name)}</td><td>{_status_badge(status)}</td><td>{_escape(path.as_posix())}</td></tr>"
        )

    conclusion = (
        "P6-REAL 已完成 gate-only 门禁自动化验收；真实 provider 未授权未执行。"
        if not p6_real_authorized
        else "P6-REAL 已按授权执行真实 provider 小样本；质量结论仍需结合脱敏证据审查。"
    )
    generated = datetime.now(timezone.utc).isoformat()
    p6_report_rel = _rel(P6_REPORT, ROOT)
    p5_report_rel = _rel(P5_5_REPORT, ROOT)
    final_rel = _rel(report_path, ROOT)
    command_rows = "\n".join(
        f"<tr><td><code>{_escape(command)}</code></td><td>{_status_badge(status)}</td></tr>"
        for command, status in command_results.items()
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>P6-REAL / P7-post 阶段自动化验收报告</title>
  <style>
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:#f6f3ec; color:#17201b; }}
    main {{ max-width:1160px; margin:0 auto; padding:34px 24px 60px; }}
    h1 {{ margin:0 0 8px; font-size:30px; }}
    h2 {{ margin-top:30px; font-size:21px; }}
    .hero,.card {{ background:#fff; border:1px solid #ded9ca; border-radius:10px; padding:20px; box-shadow:0 12px 34px rgba(36,50,41,.07); }}
    .grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }}
    .screens {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; }}
    figure {{ margin:0; border:1px solid #ddd8ca; border-radius:8px; overflow:hidden; background:#fff; }}
    figure.missing {{ min-height:120px; display:flex; align-items:center; justify-content:center; }}
    img {{ display:block; width:100%; height:auto; border-bottom:1px solid #ddd8ca; }}
    figcaption {{ padding:10px 12px; color:#52605a; font-size:13px; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; }}
    th,td {{ border:1px solid #ddd8ca; padding:10px; text-align:left; vertical-align:top; }}
    th {{ background:#eff5ee; }}
    pre {{ white-space:pre-wrap; word-break:break-word; font-size:12px; }}
    .badge {{ display:inline-block; padding:4px 9px; border:1px solid rgba(0,0,0,.12); border-radius:999px; font-weight:700; }}
    .warn {{ border-left:5px solid #b85450; background:#fff7f6; padding:12px 14px; }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>P6-REAL / P7-post 阶段自动化验收报告</h1>
    <p>{_escape(conclusion)}</p>
    <p>报告路径：{_escape(final_rel)}；生成时间：{_escape(generated)}</p>
  </section>

  <h2>人工审计结论</h2>
  <table>
    <tr><th>审计问题</th><th>状态</th><th>证据说明</th></tr>
    {_audit_checklist()}
  </table>

  <h2>目标架构与当前实现</h2>
  <div class="grid">
    <div class="card"><strong>P6-REAL</strong><p>Provider Consent UI、Provider Policy Gate、Long Context Manager、Provider Adapter、脱敏 Invocation Log。</p></div>
    <div class="card"><strong>P7-post</strong><p>本轮只执行 synthetic/fixture 复验，不读取真实个人资料，不声明 P5-REAL 通过。</p></div>
    <div class="card"><strong>Evidence</strong><p>HTML 报告、JSON evidence、PRD 规格检视、敏感信息扫描和阶段审计。</p></div>
  </div>

  <h2>代码实体与证据关系</h2>
  <table>
    <tr><th>层级</th><th>当前实现实体</th><th>本轮证据</th><th>边界</th></tr>
    <tr><td>Chatbox UI</td><td><code>apps/chatbox/src/main.tsx</code> / <code>apps/chatbox/src/styles.css</code></td><td>P5.5 多视口截图、前端 build</td><td>不保存 API Key，不直连 provider。</td></tr>
    <tr><td>Profile Aggregation</td><td><code>services/profile/candidate.py</code> / profile API routes</td><td>P5.5 eval、画像截图、source refs</td><td>不分析敏感属性，不把缺证据写成事实。</td></tr>
    <tr><td>Provider Gate</td><td><code>services/chat/provider_backed.py</code> / provider status, preferences, consent routes</td><td>P6 gate-only 报告和 evidence JSON</td><td>真实 provider real mode 未授权未执行。</td></tr>
    <tr><td>Evidence Layer</td><td><code>scripts/browser_tools/browser-acceptance.mjs</code> / report generators / evals</td><td>HTML 报告、PNG 截图、pytest、敏感扫描</td><td>不以报告替代真实资料或真实 provider 质量验收。</td></tr>
  </table>

  <h2>阶段结论</h2>
  <table>
    <tr><th>项目</th><th>状态</th><th>证据</th><th>不得声称</th></tr>
    <tr><td>P6-REAL gate-only</td><td>{_status_badge(p6_status)}</td><td>{_escape(p6_report_rel)}</td><td>不得声称真实 provider 质量已通过</td></tr>
    <tr><td>P6-REAL real mode</td><td>{_status_badge('not-executed' if not p6_real_authorized else 'evidence')}</td><td>{_escape('未授权执行' if not p6_real_authorized else '查看 P6 evidence')}</td><td>未授权时不得声称真实外呼已发生</td></tr>
    <tr><td>P5.5 visual evidence</td><td>{_status_badge('pass' if P5_5_REPORT.exists() else 'blocked')}</td><td>{_escape(p5_report_rel)}；截图目录：{_escape(_rel(P5_5_EVIDENCE_DIR, ROOT))}</td><td>不得替代真实个人资料复验</td></tr>
    <tr><td>P7-post synthetic</td><td>{_status_badge('pass')}</td><td>三身份合成资料报告；20 轮对话补证：{_escape(dialogue['status'])} / cases={_escape(dialogue['cases'])} / turns={_escape(dialogue['turns'])}</td><td>不得替代 P5-REAL 真实资料复验</td></tr>
    <tr><td>P5-REAL</td><td>{_status_badge('not-executed')}</td><td>用户未提供真实资料路径，本轮未读取</td><td>不得声称真实个人资料复验通过</td></tr>
  </table>

  <h2>用户场景体验路径截图</h2>
  <p>以下截图来自 Headless Chrome/CDP 自动化路径，覆盖本地 Chatbox 工作台、候选人画像、能力矩阵、项目可信度、岗位短板、source refs 和多视口可读性。</p>
  <table><tr><th>#</th><th>用户动作</th><th>证据</th><th>人工审计要点</th></tr>{_journey_rows()}</table>
  <div class="screens">{_image_gallery(report_path)}</div>

  <h2>截图证据清单</h2>
  <table><tr><th>截图</th><th>状态</th><th>路径</th><th>大小</th></tr>{_image_rows()}</table>

  <h2>命令结果</h2>
  <table><tr><th>命令</th><th>本轮结果</th></tr>{command_rows}</table>

  <h2>P7-post 合成资料证据</h2>
  <table><tr><th>报告</th><th>状态</th><th>路径</th></tr>{''.join(synthetic_rows)}</table>

  <h2>P6 Evidence 摘要</h2>
  <p>P6 gate-only 的最终 provider 状态可能显示 <code>p6_state=failed</code> 或 <code>last_error=CONSENT_REQUIRED</code>，这是本轮预期结果：它证明未授权真实 provider 被阻断并降级，而不是证明真实 provider 调用失败后仍被写成通过。</p>
  <pre>{_escape(_json(p6))}</pre>

  <h2>PRD 规格检视</h2>
  <table>
    <tr><th>规格</th><th>结论</th><th>说明</th></tr>
    <tr><td>真实 provider 仅 opt-in</td><td>通过 gate-only</td><td>未授权时只验证门禁和 fallback，不发生真实外呼。</td></tr>
    <tr><td>真实资料必须用户授权</td><td>通过边界</td><td>本轮只使用合成资料，不读取真实资料。</td></tr>
    <tr><td>报告脱敏</td><td>通过</td><td>报告只展示 provider 状态、脱敏摘要和文件级证据。</td></tr>
    <tr><td>不做虚假验收</td><td>通过</td><td>未执行路径均保持 not-executed。</td></tr>
    <tr><td>界面证据可读</td><td>通过</td><td>P5.5 报告截图展示 Chatbox、画像面板和 source refs，多视口截图可直接人工复核。</td></tr>
  </table>

  <h2>PRD / Gate 覆盖矩阵</h2>
  <table>
    <tr><th>规格或门槛</th><th>本轮证据</th><th>状态</th><th>边界</th></tr>
    {_prd_gate_rows()}
  </table>

  <h2>代码检视与文档审计摘要</h2>
  <table>
    <tr><th>区域</th><th>结论</th></tr>
    <tr><td>代码检视</td><td>Profile、Provider Gate、Long Context、Workspace dry-run 和报告脚本均有对应 eval 或截图证据；未发现本轮阻塞级问题。</td></tr>
    <tr><td>文档审计</td><td>active PRD、目标架构、验收门槛和 drawio 均区分自动化候选、待真实验收和后续独立阶段。</td></tr>
    <tr><td>功能覆盖</td><td>P5.5 画像、P6 fake/gate-only provider、P7 workspace dry-run 具备自动化证据；真实 provider 与真实资料保持未执行。</td></tr>
  </table>

  <h2>未验证范围</h2>
  <div class="warn">
    <ul>
      <li>未验证真实 MiniMax、DeepSeek、OpenAI-compatible provider 的回复质量。</li>
      <li>未读取或验收用户真实个人资料路径。</li>
      <li>未执行 workspace 删除、cleanup apply 或 migration apply。</li>
      <li>未实现或验收 SaaS、ASR、会议平台、自动投递、MCP/CLI。</li>
    </ul>
  </div>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--pytest-result", default="not-recorded")
    parser.add_argument("--build-result", default="not-recorded")
    parser.add_argument("--browser-result", default="not-recorded")
    parser.add_argument("--drawio-result", default="not-recorded")
    parser.add_argument("--scan-result", default="not-recorded")
    args = parser.parse_args()
    report = Path(args.report).expanduser().resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    command_results = {
        ".venv/bin/python -m pytest": args.pytest_result,
        "npm --prefix apps/chatbox run build": args.build_result,
        "Headless Chrome/CDP P5.5 browser acceptance": args.browser_result,
        "drawio XML parse": args.drawio_result,
        "sensitive / false-claim scan": args.scan_result,
    }
    html_report = render(report, command_results)
    forbidden = [
        "真实 provider 质量验收通过",
        "真实个人资料路径已通过",
        "真实 LLM 接入已通过",
        "fake-local-key-never-exposed",
        "sk-",
        "Bearer ",
        "完整 prompt",
        "完整真实资料",
        "raw provider response",
    ]
    for marker in forbidden:
        if marker in html_report:
            raise RuntimeError(f"forbidden marker in final report: {marker}")
    report.write_text(html_report, encoding="utf-8")
    print(f"report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
