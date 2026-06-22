from datetime import UTC, datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAWIO = ROOT / "docs/active/jobpilot-stage-gap-and-acceptance.drawio"
MIRROR = ROOT / "docs/active/jobpilot-stage-gap-and-acceptance.md"


COLORS = {
    "done": ("#d5e8d4", "#82b366"),
    "p4": ("#fff2cc", "#d6b656"),
    "future": ("#f5f5f5", "#666666"),
    "risk": ("#f8cecc", "#b85450"),
    "info": ("#dae8fc", "#6c8ebf"),
    "white": ("#ffffff", "#bac8d3"),
}


def val(text: str) -> str:
    return escape(text).replace("\n", "&lt;br&gt;")


def cell(cid: str, text: str, x: int, y: int, w: int, h: int, color: str = "white", bold: bool = False) -> str:
    fill, stroke = COLORS[color]
    style = (
        "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;"
        f"fillColor={fill};strokeColor={stroke};fontSize=12;spacing=8;"
    )
    if bold:
        style += "fontStyle=1;"
    return (
        f'<mxCell id="{cid}" value="{val(text)}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
    )


def title(cid: str, text: str) -> str:
    return (
        f'<mxCell id="{cid}" value="{val(text)}" '
        'style="text;html=1;strokeColor=none;fillColor=none;fontSize=22;fontStyle=1;'
        'align=left;verticalAlign=middle;" vertex="1" parent="1">'
        '<mxGeometry x="40" y="24" width="1120" height="42" as="geometry"/></mxCell>'
    )


def arrow(cid: str, source: str, target: str, label: str = "", color: str = "#6c8ebf") -> str:
    return (
        f'<mxCell id="{cid}" value="{val(label)}" style="endArrow=block;html=1;rounded=0;'
        f'strokeColor={color};strokeWidth=2;" edge="1" parent="1" source="{source}" target="{target}">'
        '<mxGeometry relative="1" as="geometry"/></mxCell>'
    )


def page(name: str, cells: list[str]) -> str:
    root = '<mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells)
    return (
        f'<diagram name="{escape(name)}" id="{escape(name).replace(" ", "_")}">'
        '<mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" '
        f'pageHeight="827" math="0" shadow="0"><root>{root}</root></mxGraphModel></diagram>'
    )


def build_pages() -> list[str]:
    pages: list[str] = []

    p1 = [title("p1_t", "1. P4 目标 UX 架构与当前差距")]
    for item in [
        ("p1_user", "User\n转行程序员 / 人工体验审查者", 40, 120, 150, 90, "info"),
        ("p1_shell", "Experience Shell\nworkspace / mode / provider\n全尺寸桌面状态\n目标：状态清楚但不压过对话", 230, 90, 210, 135, "p4"),
        ("p1_launcher", "Empty State Suggested Prompts\n导入资料 / 粘贴 JD / 生成申请包 / 准备面试\n点击后进入 composer/对话", 480, 90, 230, 135, "p4"),
        ("p1_conv", "Conversation Plane\n消息 / suggested prompts / loading / 错误恢复 / 下一步\n目标：反馈更自然", 750, 90, 230, 150, "p4"),
        ("p1_workbench", "Workbench Plane / Desktop + Mobile\n当前任务 / 产物 / 确认项 / 导出\n1200/1440/1600/1920 桌面协同\n390px 下折叠，不压缩 Chatbox", 230, 300, 245, 150, "p4"),
        ("p1_artifact", "Artifact Review Cards\n岗位解析 / 匹配报告 / 申请包草稿\nprimary/secondary action 清楚", 520, 300, 240, 140, "p4"),
        ("p1_backend", "P0-P3 后端基线\nFastAPI / ChatCore / PiAgent / Domain Tools / Artifact / Export\n保持不退化", 780, 300, 290, 130, "done"),
        ("p1_evidence", "Evidence Plane\n1200/1440/1600/1920/720/390 screenshots\nHTML report / Gemini review package / PRD review\nemulation cleanup", 230, 520, 330, 120, "p4"),
        ("p1_future", "P5+ 非本阶段\nMCP / CLI / ASR / 会议平台 / 自动海投 / SaaS", 620, 520, 300, 110, "future"),
        ("p1_risk", "禁止路径\n前端生成求职内容；默认外呼；隐藏待确认项；任务入口与对话割裂；大屏布局空白；截图脚本污染 viewport；用静态原型冒充已实现", 40, 680, 1030, 70, "risk"),
    ]:
        p1.append(cell(*item, bold=True))
    for i, (src, tgt, label) in enumerate([
        ("p1_user", "p1_shell", ""),
        ("p1_shell", "p1_launcher", "从任务开始"),
        ("p1_launcher", "p1_conv", "触发对话/流程"),
        ("p1_conv", "p1_workbench", "返回状态"),
        ("p1_workbench", "p1_artifact", "管理产物"),
        ("p1_artifact", "p1_backend", "调用后端"),
        ("p1_workbench", "p1_evidence", "截图/报告"),
    ]):
        p1.append(arrow(f"p1_a{i}", src, tgt, label))
    pages.append(page("1 目标架构与差距", p1))

    p2 = [title("p2_t", "2. P4 前端页面功能角色与关联关系")]
    for item in [
        ("p2_strip", "Mode / Provider Strip\n示例模式 / 我的资料\nmock 默认 / external 需确认", 60, 100, 230, 110, "p4"),
        ("p2_launcher", "Empty State Suggested Prompts\n3-4 个主任务建议\n点击填入 composer 或触发对话", 330, 100, 230, 130, "p4"),
        ("p2_chat", "Chat Timeline\n用户消息\n系统计划\nthinking/loading\n错误恢复\n完成摘要", 600, 100, 210, 145, "p4"),
        ("p2_comp", "Composer Dock\n文本 / 上传 / 快捷任务\nEnter/Shift+Enter", 830, 100, 210, 130, "p4"),
        ("p2_current", "Current Task Panel\n当前阶段\n下一步\n缺口提示", 60, 330, 230, 120, "p4"),
        ("p2_artifacts", "Artifact List\n岗位解析\n匹配报告\n申请包\n面试准备", 330, 330, 210, 120, "p4"),
        ("p2_card", "Artifact Card\n摘要优先\n确认项可见\nprimary action 突出\nsource refs/版本可展开", 580, 330, 240, 140, "p4"),
        ("p2_export", "Confirm / Export Bar\nblocking 阻止导出\nwarning 写入导出文件", 860, 330, 210, 120, "done"),
        ("p2_mobile", "Responsive / Full-size Controller\n1200/1440/1600/1920 桌面工作台\n720 窄屏\n390 Chatbox 优先，Workbench 抽屉/折叠\n结束清理 emulation", 330, 570, 420, 125, "p4"),
        ("p2_rule", "页面规则：不要嵌套卡片；不要让工程字段成为主内容；任务入口必须在对话闭环内；移动端不能用可运行替代好用。", 60, 710, 980, 60, "risk"),
    ]:
        p2.append(cell(*item, bold=True))
    for i, (src, tgt, label) in enumerate([
        ("p2_strip", "p2_launcher", ""),
        ("p2_launcher", "p2_chat", "启动任务"),
        ("p2_chat", "p2_comp", "继续追问"),
        ("p2_chat", "p2_current", "更新状态"),
        ("p2_current", "p2_artifacts", "产物"),
        ("p2_artifacts", "p2_card", "查看"),
        ("p2_card", "p2_export", "导出"),
        ("p2_mobile", "p2_strip", "约束布局"),
    ]):
        p2.append(arrow(f"p2_a{i}", src, tgt, label))
    pages.append(page("2 前端职责", p2))

    p3 = [title("p3_t", "3. P4 开发及验收计划")]
    for item in [
        ("p3_m0", "P4-M0\n文档 / drawio / Gemini 包锁定\n状态：本轮交付", 50, 100, 170, 105, "done"),
        ("p3_m1", "P4-M1\nChatbox 空状态 suggested prompts\n证据：点击后 composer/对话", 250, 100, 190, 105, "p4"),
        ("p3_m2", "P4-M2\n对话反馈、loading 与错误恢复\n证据：有效/缺资料/错误态", 470, 100, 190, 105, "p4"),
        ("p3_m3", "P4-M3\n推进台与产物卡可读性\n证据：primary action 截图", 690, 100, 190, 105, "p4"),
        ("p3_m4", "P4-M4\n状态、错误恢复、provider 语义\n证据：外呼边界截图", 910, 100, 190, 105, "p4"),
        ("p3_m5", "P4-M5/M5A\n响应式、全尺寸桌面与可访问性冒烟\n证据：1200/1440/1600/1920/720/390 + emulation cleanup", 250, 310, 210, 135, "p4"),
        ("p3_m6", "P4-M6\nbefore/after 报告与冻结\n证据：HTML 报告 + 全尺寸截图 + PRD review", 500, 310, 220, 115, "p4"),
        ("p3_accept", "每阶段必须\n测试/截图/PRD 规格检视\n大屏空白或截图污染 viewport 直接打回计划", 760, 310, 260, 115, "risk"),
        ("p3_data", "验收数据\n默认 examples 真实感数据\n真实个人资料和真实外部调用需人工确认", 250, 520, 330, 110, "info"),
        ("p3_docs", "文档数控制\nactive docs 作为执行依据\nGemini 包文件数 < 20", 630, 520, 310, 110, "p4"),
    ]:
        p3.append(cell(*item, bold=True))
    for i, (src, tgt) in enumerate([
        ("p3_m0", "p3_m1"),
        ("p3_m1", "p3_m2"),
        ("p3_m2", "p3_m3"),
        ("p3_m3", "p3_m4"),
        ("p3_m4", "p3_m5"),
        ("p3_m5", "p3_m6"),
    ]):
        p3.append(arrow(f"p3_a{i}", src, tgt))
    pages.append(page("3 开发及验收计划", p3))

    p4 = [title("p4_t", "4. P4 项目里程碑、验收门槛与出门条件")]
    for item in [
        ("p4_g0", "门槛 0\nP0-P3 回归不退化\npytest + frontend build", 60, 100, 220, 95, "done"),
        ("p4_g1", "门槛 1\nChatbox 空状态任务入口清楚\nprompt 进入 composer/对话", 330, 100, 220, 95, "p4"),
        ("p4_g2", "门槛 2\n对话反馈可理解\n有效/缺资料/loading/错误恢复", 600, 100, 220, 95, "p4"),
        ("p4_g3", "门槛 3\n推进台和产物卡可读\n不依赖 JSON，按钮主次清楚", 870, 100, 220, 95, "p4"),
        ("p4_g4", "门槛 4\nprovider/隐私/外呼语义\n外部模型未调用/需确认", 60, 300, 220, 95, "p4"),
        ("p4_g5", "门槛 5\n全尺寸响应式与可访问性\n1200/1440/1600/1920 不留大面积空白\n390px Workbench 不压缩 Chatbox\n截图脚本清理 emulation", 330, 300, 240, 135, "p4"),
        ("p4_g6", "门槛 6\nGemini 包 + HTML 报告 + PRD 检视", 600, 300, 220, 95, "p4"),
        ("p4_exit", "最终出门条件\n不读文档也能完成导入资料 → 分析岗位 → 生成申请包 → 确认/编辑 → 导出；截图、测试、报告和人工体验记录齐全。", 870, 280, 220, 150, "risk"),
        ("p4_fail", "不通过即打回\n无响应；职责混乱；JSON 为主；外呼误导；全尺寸桌面大面积空白；截图脚本污染 viewport；移动端不可达；静态原型冒充实现。", 60, 540, 1030, 95, "risk"),
    ]:
        p4.append(cell(*item, bold=True))
    pages.append(page("4 门槛与出门条件", p4))

    p5 = [title("p5_t", "5. 安全边界、状态标记与审查证据")]
    for item in [
        ("p5_done", "绿色：已完成基线\nP0/P1/P2/P3 后端能力、workflow、artifact version、export、Chatbox 自动化验收", 60, 100, 300, 130, "done"),
        ("p5_p4", "黄色：P4 本阶段目标\nsuggested prompts、loading/error recovery、产物卡主次操作、provider 语义、全尺寸桌面、移动端 Workbench、Gemini 包", 420, 100, 340, 130, "p4"),
        ("p5_future", "灰色：P5+ 后续\nMCP / CLI / ASR / 会议平台 / 自动海投 / SaaS / Offer 分析", 820, 100, 260, 130, "future"),
        ("p5_risk", "红色：人工确认或禁止路径\n真实个人资料；真实外部调用；API Key；不可逆迁移；逐字代答；默认外呼", 60, 320, 430, 130, "risk"),
        ("p5_evidence", "P4 证据包\n1200/1440/1600/1920/720/390 Chrome screenshots\nP4 HTML report\nGemini review package\nPRD review\nemulation cleanup\nXML parse\nREADME/TODO sync", 550, 320, 280, 170, "info"),
        ("p5_review", "审计原则\n文档通过不等于实现通过\nGemini 建议不等于人工体验通过\n截图必须来自真实 Chrome", 870, 320, 210, 150, "risk"),
        ("p5_cmd", "最低命令\npython3 -m pytest\nnpm --prefix apps/chatbox run build\npython3 XML parse drawio", 60, 560, 1020, 110, "p4"),
    ]:
        p5.append(cell(*item, bold=True))
    pages.append(page("5 安全与证据", p5))

    return pages


def write_drawio() -> None:
    now = datetime.now(UTC).isoformat()
    xml = (
        f'<mxfile host="app.diagrams.net" modified="{now}" agent="codex" version="24.7.17" type="device">'
        + "".join(build_pages())
        + "</mxfile>\n"
    )
    DRAWIO.write_text(xml, encoding="utf-8")


def write_mirror() -> None:
    MIRROR.write_text(
        """# JobPilot AI P4 UX 架构、差距与验收图说明

本文档是 `jobpilot-stage-gap-and-acceptance.drawio` 的文本镜像，便于代码审查和 diff。

本轮图示主线是 P4 UX 体验强化：目标 UX 架构、当前架构差距、开发及验收计划、项目里程碑、验收门槛、出门条件和审查证据。它不把 MCP、CLI、ASR、会议平台、自动海投或 SaaS 放入 P4 出门条件。

## 图示页结构

P4 drawio 保持 5 页：

1. P4 目标 UX 架构与当前差距；
2. P4 前端页面功能角色与关联关系；
3. P4 开发及验收计划；
4. P4 项目里程碑、验收门槛与出门条件；
5. 安全边界、状态标记与审查证据。

颜色含义：

- 绿色：已完成 / P0+P1+P2+P3 基线；
- 黄色：P4 本阶段目标；
- 灰色：P5+ 后续能力；
- 红色：高风险人工确认或禁止路径；
- 蓝色：用户、证据或说明性节点。

## 第 1 页 - P4 目标 UX 架构与当前差距

目标架构主链路：

```text
User
→ Experience Shell
→ Conversation Plane
  → Empty State Suggested Prompts
  → Loading / Error Recovery
→ Full-size Desktop Workbench / Workbench Plane
→ Artifact Review Cards
→ P0-P3 后端基线
→ Evidence Plane
```

当前差距：

- 首屏仍偏工程状态，P4 目标是 Chatbox 空状态 suggested prompts 优先；
- Chatbox 可响应，但 P4 目标是反馈更自然，并包含 loading / error recovery；
- 推进台已分离，但 P4 目标是只管理结果、确认项、版本和导出，并在 1200px、1440px、1600px、1920px 形成完整桌面工作台；
- 产物卡仍有工程术语，P4 目标是求职语义优先，并区分 primary / secondary action；
- P4 不改变 FastAPI、ChatCore、PiAgent、Domain Tools、Artifact 和 Export 的后端主链路。
- 截图脚本必须隔离或清理 viewport emulation，避免污染人工审查浏览器。

禁止路径：

- 前端生成求职内容；
- 默认触发外部 provider；
- 隐藏待确认项；
- suggested prompts 与 composer 割裂；
- 1200px 以上桌面宽度出现布局错误造成的大面积空白；
- 截图脚本污染人工审查者浏览器 viewport；
- 用静态原型冒充已实现。

## 第 2 页 - P4 前端页面功能角色与关联关系

前端角色：

- Mode / Provider Strip：展示示例模式、我的资料模式、mock 默认和 external 需确认；
- Empty State Suggested Prompts：提供导入资料、粘贴 JD、生成申请包、准备面试等建议任务，点击后填入 composer 或触发对话；
- Chat Timeline：展示用户消息、系统计划、loading / thinking、错误恢复和完成摘要；
- Composer Dock：处理文本、上传和快捷任务；
- Current Task Panel：展示当前阶段、下一步和缺口提示；
- Artifact List / Artifact Card：展示岗位解析、匹配报告、申请包、面试准备，并突出 primary action；
- Confirm / Export Bar：执行导出前确认和导出触发；
- Responsive / Full-size Controller：约束 1200/1440/1600/1920/720/390 多档布局，390px 下 Workbench 不压缩 Chatbox，截图结束后清理 emulation。

页面规则：

- 不嵌套卡片；
- 不让工程字段成为主内容；
- 移动端不能用“可运行”替代“好用”；
- 全尺寸桌面不能用“左侧窄栏 + 右侧空白”冒充工作台。

## 第 3 页 - P4 开发及验收计划

执行顺序：

```text
P4-M0 文档 / drawio / Gemini 包锁定
→ P4-M1 Chatbox 空状态 suggested prompts
→ P4-M2 对话反馈、loading 与错误恢复
→ P4-M3 推进台与产物卡可读性、primary action
→ P4-M4 状态、错误恢复、provider 语义
→ P4-M5 响应式与可访问性冒烟
→ P4-M5A 全尺寸桌面工作台与截图脚本隔离
→ P4-M6 before/after 报告与冻结
```

每阶段都必须产生测试、截图或 PRD 规格检视证据；出现重大偏差必须打回计划。

## 第 4 页 - P4 项目里程碑、验收门槛与出门条件

P4 门槛：

1. P0-P3 回归不退化；
2. Chatbox 空状态任务入口清楚，suggested prompts 能进入 composer 或对话；
3. 对话反馈可理解，包含 loading 和错误恢复 action；
4. 推进台和产物卡可读，按钮主次清楚；
5. provider、隐私和外呼语义不误导；
6. 全尺寸响应式与基础可访问性，1200/1440/1600/1920 不留大面积空白，390px 下 Workbench 不压缩 Chatbox，截图脚本清理 emulation；
7. Gemini 审查包、HTML 报告和 PRD 规格检视。

最终出门条件：

一个转行程序员不读文档也能完成：

```text
导入资料 → 分析岗位 → 生成申请包 → 确认/编辑 → 导出
```

同时截图、测试、报告和人工体验记录齐全。

## 第 5 页 - 安全边界、状态标记与审查证据

P4 证据包：

- Chrome screenshots；
- 1200/1440/1600/1920/720/390 多档截图；
- P4 HTML report；
- Gemini review package；
- PRD review；
- drawio XML parse；
- README/TODO sync。

审计原则：

- 文档通过不等于实现通过；
- Gemini 建议不等于人工体验通过；
- 截图必须来自真实 Chrome；
- 截图脚本不能污染人工审查浏览器 viewport；
- 真实个人资料、真实外部调用、API Key、不可逆迁移和逐字代答必须人工确认。
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    write_drawio()
    write_mirror()
