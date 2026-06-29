from __future__ import annotations

from pathlib import Path

from services.storage.workspace import init_workspace
from services.tools import jobpilot


def build_p5_5_workspace(tmp_path: Path) -> dict:
    workspace = init_workspace("p5-5-candidate-profile", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    resume = tmp_path / "resume.md"
    resume.write_text(
        """
# 合成候选人资料

本资料为 JobPilot P5.5 自动化验收合成资料，不属于真实个人资料。

- 目标岗位：Junior Frontend Developer
- 技能：React、TypeScript、Python、FastAPI
- 经历：从运营自动化转向前端开发，长期负责跨团队需求整理和内部工具落地。
- 项目：JobPilot Local Review，围绕本地 workspace 完成资料导入、JD 解析、申请包确认和导出。
""".strip(),
        encoding="utf-8",
    )
    project = tmp_path / "project.md"
    project.write_text(
        """
# 合成项目：JobPilot Local Review

本资料为 JobPilot P5.5 自动化验收合成项目，不属于真实个人资料。

使用 React、TypeScript、Python 和 FastAPI 搭建本地求职材料工作台。
本人负责前端状态机、source refs 展示、artifact version、导出前确认门槛和端到端验收。
项目缺少公开部署链接和量化性能指标。
""".strip(),
        encoding="utf-8",
    )
    jd = """
职位：Junior Frontend Developer
职责：开发 React + TypeScript 前端页面，和 FastAPI 后端协作完成本地数据工作流。
要求：React、TypeScript、基础 Python、能写自动化测试，重视用户体验和可维护性。
加分：熟悉本地优先隐私设计、Markdown 导出、Playwright 或 pytest。
""".strip()
    resume_doc = jobpilot.save_document(workspace_id, str(resume), "resume")
    project_doc = jobpilot.save_document(workspace_id, str(project), "project")
    facts = jobpilot.extract_facts(workspace_id, [resume_doc["document_id"], project_doc["document_id"]], ["Junior Frontend Developer"])
    project_card = jobpilot.create_project_card(workspace_id, "JobPilot Local Review", [project_doc["document_id"]], "Junior Frontend Developer")
    job = jobpilot.parse_jd(workspace_id, jd)
    match = jobpilot.match_profile(workspace_id, job["job_id"])
    return {
        "workspace_id": workspace_id,
        "resume_doc": resume_doc,
        "project_doc": project_doc,
        "facts": facts,
        "project_card": project_card,
        "job": job,
        "match": match,
    }
