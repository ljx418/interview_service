from datetime import UTC, datetime
from html import escape
from pathlib import Path


def value(text: str) -> str:
    return escape(text).replace("\n", "&lt;br&gt;")


COLORS = {
    "green": ("#d5e8d4", "#82b366"),
    "yellow": ("#fff2cc", "#d6b656"),
    "gray": ("#f5f5f5", "#666666"),
    "red": ("#f8cecc", "#b85450"),
    "blue": ("#dae8fc", "#6c8ebf"),
    "white": ("#ffffff", "#bac8d3"),
    "purple": ("#e1d5e7", "#9673a6"),
}


def cell(cid, text, x, y, w, h, color="white", font=12, bold=False):
    fill, stroke = COLORS[color]
    style = (
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};"
        f"strokeColor={stroke};fontSize={font};spacing=8;"
        "align=left;verticalAlign=top;"
    )
    if bold:
        style += "fontStyle=1;"
    return (
        f'<mxCell id="{cid}" value="{value(text)}" style="{style}" '
        f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
        f'width="{w}" height="{h}" as="geometry"/></mxCell>'
    )


def title(cid, text):
    return (
        f'<mxCell id="{cid}" value="{value(text)}" '
        'style="text;html=1;strokeColor=none;fillColor=none;'
        'fontSize=22;fontStyle=1;align=left;verticalAlign=middle;" '
        'vertex="1" parent="1"><mxGeometry x="40" y="24" '
        'width="1120" height="42" as="geometry"/></mxCell>'
    )


def arrow(cid, source, target, color="#6c8ebf", dashed=False, label=""):
    dash = "dashed=1;" if dashed else ""
    edge_label = f'value="{value(label)}" ' if label else 'value="" '
    return (
        f'<mxCell id="{cid}" {edge_label}style="endArrow=block;html=1;'
        f'rounded=0;{dash}strokeColor={color};strokeWidth=2;" edge="1" '
        f'parent="1" source="{source}" target="{target}">'
        '<mxGeometry relative="1" as="geometry"/></mxCell>'
    )


def page(name, cells):
    body = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>'] + cells
    page_id = escape(name).replace(" ", "_")
    return (
        f'<diagram name="{escape(name)}" id="{page_id}"><mxGraphModel '
        'dx="1422" dy="794" grid="1" gridSize="10" guides="1" '
        'tooltips="1" connect="1" arrows="1" fold="1" page="1" '
        'pageScale="1" pageWidth="1169" pageHeight="827" math="0" '
        f'shadow="0"><root>{"".join(body)}</root></mxGraphModel></diagram>'
    )


pages = []

# Page 1: System context and module map.
p1 = [title("p1_title", "1. 系统上下文与目标模块图")]
modules = [
    ("p1_user", "User\n转行程序员 / 体验审查者", 40, 120, 130, 80, "blue"),
    ("p1_chatbox", "Chatbox Client\n输入、展示、确认、编辑、导出触发\n禁止：生成求职内容 / 直接写库", 210, 90, 180, 140, "yellow"),
    ("p1_api", "FastAPI Agent Service\nHTTP 边界、请求校验、错误码、workspace 边界", 430, 90, 180, 140, "green"),
    ("p1_core", "ChatCore Facade\n隔离 KeywordChatCore / PiAgentChatCore\n输出 intent / tool plan", 650, 90, 180, 140, "green"),
    ("p1_flow", "Flow Orchestration\nIntent Router / Real User Flow Controller / P2 Workflow", 870, 90, 220, 140, "yellow"),
    ("p1_tools", "Domain Tool Layer\nprofile / project / job / application / interview / realtime / review", 210, 300, 260, 150, "green"),
    ("p1_provider", "Provider and Contract Layer\nPolicy Gate / Mock / External / Prompt Contract / Schema Validation", 520, 300, 270, 150, "green"),
    ("p1_artifact", "Artifact and Storage Layer\nArtifactVersion / Confirmation / Export / SQLite / local files", 840, 300, 250, 150, "green"),
    ("p1_evidence", "Evidence Layer\npytest eval / Chrome screenshots / HTML reports / PRD review", 430, 540, 390, 110, "yellow"),
    ("p1_future", "P4+ 后续\nMCP / CLI / ASR / 会议平台 / 自动海投 / SaaS", 850, 540, 240, 110, "gray"),
]
for item in modules:
    p1.append(cell(*item, bold=True))
for idx, (src, tgt) in enumerate(
    [
        ("p1_user", "p1_chatbox"),
        ("p1_chatbox", "p1_api"),
        ("p1_api", "p1_core"),
        ("p1_core", "p1_flow"),
        ("p1_flow", "p1_tools"),
        ("p1_tools", "p1_provider"),
        ("p1_provider", "p1_artifact"),
        ("p1_artifact", "p1_evidence"),
    ]
):
    p1.append(arrow(f"p1_a{idx}", src, tgt))
p1.append(
    cell(
        "p1_forbidden",
        "红线：Chatbox 不直连 Provider/SQLite；PiAgent 不直写 SQLite；Provider raw output 不直接导出；workflow 不伪造完成。",
        40,
        690,
        1050,
        70,
        "red",
        bold=True,
    )
)
pages.append(page("1 系统上下文", p1))

# Page 2: Frontend component responsibilities.
p2 = [title("p2_title", "2. Chatbox 前端组件职责")]
front = [
    ("p2_shell", "Experience Shell\nworkspace 状态\nprovider 状态\n示例/真实资料模式", 60, 100, 210, 120, "yellow"),
    ("p2_conv", "Conversation View\n消息流\n计划/执行结果\n错误和下一步", 320, 100, 210, 120, "yellow"),
    ("p2_comp", "Composer / Upload Entry\n文本输入\n文件上传\n快捷任务", 60, 280, 210, 120, "yellow"),
    ("p2_work", "Workbench Panel\n阶段\n下一步\n产物列表\n确认项", 320, 280, 210, 120, "yellow"),
    ("p2_card", "Artifact Cards\n摘要\nsource refs\nquestions_to_confirm\n版本操作", 580, 180, 230, 140, "green"),
    ("p2_export", "Export Actions\n只触发后端 preflight\n不直接生成文件", 860, 180, 210, 120, "green"),
    ("p2_api", "API Client\nchat / workflow / artifact / export / provider routes", 580, 420, 230, 120, "green"),
    ("p2_resp", "Responsive Layout Controller\n1280 / 720 / 390\n滚动和输入区约束", 860, 420, 210, 120, "yellow"),
]
for item in front:
    p2.append(cell(*item, bold=True))
for idx, (src, tgt) in enumerate(
    [
        ("p2_shell", "p2_conv"),
        ("p2_comp", "p2_conv"),
        ("p2_conv", "p2_api"),
        ("p2_api", "p2_work"),
        ("p2_work", "p2_card"),
        ("p2_card", "p2_export"),
        ("p2_resp", "p2_shell"),
        ("p2_resp", "p2_work"),
    ]
):
    p2.append(arrow(f"p2_a{idx}", src, tgt))
p2.append(
    cell(
        "p2_rule",
        "前端验收重点：有效输入必须有响应；错误必须可见；对话区负责输入和反馈，推进台负责状态和产物；窄屏不截断关键操作。",
        60,
        620,
        1010,
        90,
        "red",
        bold=True,
    )
)
pages.append(page("2 前端职责", p2))

# Page 3: Backend orchestration and domain tools.
p3 = [title("p3_title", "3. 后端编排与 Domain Tool 关系")]
backend = [
    ("p3_routes", "Routes\nChat / Workflow / Artifact / Export / Provider", 50, 110, 210, 120, "green"),
    ("p3_core", "ChatCore Facade\nKeyword fallback\nPiAgent adapter", 320, 110, 210, 120, "green"),
    ("p3_flow", "Real User Flow Controller\nintent → tool plan\n缺资料 → 下一步", 590, 110, 230, 120, "yellow"),
    ("p3_exec", "Domain Tool Executor\n统一调用\n错误码\ntool log 脱敏", 880, 110, 210, 120, "green"),
    ("p3_profile", "profile\nextract_facts\nskill evidence", 60, 330, 150, 95, "green"),
    ("p3_project", "project\ncreate_card", 230, 330, 150, 95, "green"),
    ("p3_job", "job\nparse_jd\nmatch_profile", 400, 330, 150, 95, "green"),
    ("p3_app", "application\ncreate_package", 570, 330, 150, 95, "green"),
    ("p3_interview", "interview\nprepare\nstory cards", 740, 330, 150, 95, "green"),
    ("p3_realtime", "realtime/review\nhint\nreview\ntraining", 910, 330, 150, 95, "green"),
    ("p3_policy", "Provider Policy Gate\nmock 默认\nexternal opt-in\nredaction", 230, 520, 230, 120, "red"),
    ("p3_schema", "Prompt Contract / Schema Validation\nmalformed output 不写库", 520, 520, 260, 120, "green"),
]
for item in backend:
    p3.append(cell(*item, bold=True))
for idx, (src, tgt) in enumerate(
    [
        ("p3_routes", "p3_core"),
        ("p3_core", "p3_flow"),
        ("p3_flow", "p3_exec"),
        ("p3_exec", "p3_profile"),
        ("p3_exec", "p3_project"),
        ("p3_exec", "p3_job"),
        ("p3_exec", "p3_app"),
        ("p3_exec", "p3_interview"),
        ("p3_exec", "p3_realtime"),
        ("p3_job", "p3_policy"),
        ("p3_app", "p3_policy"),
        ("p3_policy", "p3_schema"),
    ]
):
    p3.append(arrow(f"p3_a{idx}", src, tgt))
p3.append(
    cell(
        "p3_rule",
        "后端规则：ChatCore 只做计划；Python Domain Tools 才写业务数据；workflow 只编排工具；失败返回失败步骤和错误码，不继续标绿。",
        50,
        690,
        1040,
        70,
        "red",
        bold=True,
    )
)
pages.append(page("3 后端编排", p3))

# Page 4: Data, artifact, provider, export relationships.
p4 = [title("p4_title", "4. 数据、Artifact、Provider、Export 关系")]
data = [
    ("p4_ws", "Workspace\n本地根\n路径沙箱", 50, 110, 150, 100, "green"),
    ("p4_doc", "Document\n简历 / README / JD / transcript\nsource refs 根", 250, 110, 230, 100, "green"),
    ("p4_domain", "Domain Objects\nCareerFact / SkillEvidence / TechProject / Job / MatchReport / ApplicationPackage / InterviewPrep", 530, 90, 300, 140, "green"),
    ("p4_art", "Artifact Service\nmetadata\nstatus\ncurrent_version_id", 880, 110, 190, 100, "green"),
    ("p4_ver", "ArtifactVersion\ncontent_json/path\nsource_refs\nquestions_to_confirm\nparent_version_id", 250, 330, 260, 135, "green"),
    ("p4_export", "Export Service\npreflight\nMarkdown/DOCX\nworkspace/exports", 570, 330, 220, 120, "green"),
    ("p4_provider", "ProviderInvocation\ninput_summary\nschema_name\nstatus\nlatency\nerror_code", 840, 330, 230, 135, "green"),
    ("p4_forbid", "不得入库/日志\nAPI Key\n完整简历\n完整 JD\n完整 transcript\n完整 raw response", 50, 330, 150, 160, "red"),
]
for item in data:
    p4.append(cell(*item, bold=True))
for idx, (src, tgt) in enumerate(
    [
        ("p4_ws", "p4_doc"),
        ("p4_doc", "p4_domain"),
        ("p4_domain", "p4_art"),
        ("p4_art", "p4_ver"),
        ("p4_ver", "p4_export"),
        ("p4_domain", "p4_provider"),
    ]
):
    p4.append(arrow(f"p4_a{idx}", src, tgt))
p4.append(
    cell(
        "p4_inv",
        "数据不变量：source_refs 不丢；questions_to_confirm 不静默删除；edit/regenerate 生成新版本；blocking confirmation 未解决不得导出；export 不写 workspace 外。",
        50,
        590,
        1020,
        100,
        "yellow",
        bold=True,
    )
)
pages.append(page("4 数据与产物", p4))

# Page 5: Safety, evidence, status.
p5 = [title("p5_title", "5. 安全边界、验收证据和状态标记")]
safety = [
    ("p5_policy", "Provider Policy Gate\n外部调用唯一出口\nmock 默认\nexternal opt-in", 60, 100, 230, 130, "red"),
    ("p5_confirm", "人工确认点\n真实个人资料\nAPI Key\n真实外部调用\n不可逆迁移\n删除 workspace", 330, 100, 230, 160, "red"),
    ("p5_realtime", "Realtime 边界\ntext-in / hint-out\nformal_assist 不逐字代答\n不做 ASR/会议平台", 600, 100, 240, 150, "yellow"),
    ("p5_evidence", "验收证据\npytest\nfrontend build\nChrome 1280/720/390\nHTML report\nPRD review", 880, 100, 220, 170, "yellow"),
    ("p5_green", "绿色\nP0/P1/P2 已完成：工具链、Provider Runtime、Artifact Versioning、Export、Workflow、P2 报告", 60, 360, 310, 140, "green"),
    ("p5_yellow", "黄色\nP3 正在完善：Chatbox 响应、模式边界、推进台分离、响应式 UX、截图验收", 420, 360, 300, 140, "yellow"),
    ("p5_gray", "灰色\nP4+：MCP、CLI、ASR、会议平台、自动海投、SaaS、岗位数据源、Offer 分析", 770, 360, 300, 140, "gray"),
    ("p5_gate", "P3 出门条件\n模块边界清楚；用户输入有响应；产物可管理；三档宽度截图可用；报告不做虚假验收。", 60, 590, 1010, 100, "blue"),
]
for item in safety:
    p5.append(cell(*item, bold=True))
for idx, (src, tgt) in enumerate(
    [
        ("p5_policy", "p5_confirm"),
        ("p5_confirm", "p5_evidence"),
        ("p5_realtime", "p5_evidence"),
    ]
):
    p5.append(arrow(f"p5_a{idx}", src, tgt))
pages.append(page("5 安全与验收", p5))

xml = (
    f'<mxfile host="app.diagrams.net" modified="{datetime.now(UTC).isoformat()}" '
    f'agent="Codex" version="24.7.17">{"".join(pages)}</mxfile>'
)
Path("docs/active/jobpilot-stage-gap-and-acceptance.drawio").write_text(xml, encoding="utf-8")
