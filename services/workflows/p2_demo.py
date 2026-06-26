from __future__ import annotations

from pathlib import Path
from typing import Any

from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def _artifact_ref(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if not item:
        return None
    ref = item.get("artifact_ref")
    return ref if isinstance(ref, dict) else None


def _step(key: str, title: str, status: str, summary: str, artifacts: list[dict[str, Any] | None] | None = None, metrics: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "key": key,
        "title": title,
        "status": status,
        "summary": summary,
        "artifact_refs": [ref for ref in (artifacts or []) if ref],
        "metrics": metrics or {},
    }


def run_p2_demo_flow(workspace_id: str | None = None, reset_workspace: bool = False, data_mode: str = "example") -> dict[str, Any]:
    """Run the P2 guided demo flow with repository examples.

    This is the automatic acceptance baseline for the user-facing end-to-end
    experience. It intentionally uses bundled anonymized, real-looking examples
    and the workspace's configured provider mode. The default workspace remains
    mock/local unless the caller explicitly initialized it otherwise.
    """

    if data_mode != "example":
        raise ValueError("EXAMPLE_WORKFLOW_MODE_REQUIRED: guided demo flow can only run with data_mode=example.")

    if reset_workspace or not workspace_id:
        workspace = init_workspace("p2-guided-demo")
        workspace_id = workspace["workspace_id"]

    resume_path = ROOT / "examples/resumes/transition_frontend_resume.md"
    project_path = ROOT / "examples/projects/todoplus_README.md"
    jd_path = ROOT / "examples/jds/junior_frontend_jd.md"
    transcript_path = ROOT / "examples/transcripts/project_deep_dive.txt"

    steps: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []

    resume = jobpilot.save_document(workspace_id, str(resume_path), "resume")
    project_doc = jobpilot.save_document(workspace_id, str(project_path), "project")
    artifacts.extend([_artifact_ref(resume), _artifact_ref(project_doc)])
    steps.append(
        _step(
            "import_materials",
            "导入资料",
            "completed",
            f"已导入示例简历 {resume['filename']} 和项目 README {project_doc['filename']}。",
            [_artifact_ref(resume), _artifact_ref(project_doc)],
            {"documents": 2},
        )
    )

    facts = jobpilot.extract_facts(workspace_id, [resume["document_id"], project_doc["document_id"]], ["Junior Frontend Developer"])
    artifacts.append(_artifact_ref(facts))
    steps.append(
        _step(
            "build_profile",
            "生成职业事实和技能证据",
            "completed",
            f"已生成 {len(facts.get('facts', []))} 条职业事实，并保留待确认问题。",
            [_artifact_ref(facts)],
            {"facts": len(facts.get("facts", [])), "confirmations": len(facts.get("questions_to_confirm", []))},
        )
    )

    project = jobpilot.create_project_card(workspace_id, "TodoPlus", [project_doc["document_id"]], "Junior Frontend Developer")
    artifacts.append(_artifact_ref(project))
    steps.append(
        _step(
            "create_project_card",
            "生成项目卡",
            "completed",
            f"已生成 TodoPlus 项目卡，技术栈：{', '.join(project.get('tech_stack', [])[:5])}。",
            [_artifact_ref(project)],
            {"tech_stack": project.get("tech_stack", [])},
        )
    )

    jd_text = jd_path.read_text(encoding="utf-8")
    job = jobpilot.parse_jd(workspace_id, jd_text)
    match = jobpilot.match_profile(workspace_id, job["job_id"])
    artifacts.extend([_artifact_ref(job), _artifact_ref(match)])
    steps.append(
        _step(
            "analyze_job",
            "分析岗位和匹配度",
            "completed",
            f"已解析 {job.get('title', '目标岗位')}，匹配结论：{match.get('fit_label')}。",
            [_artifact_ref(job), _artifact_ref(match)],
            {"job_id": job["job_id"], "fit_label": match.get("fit_label"), "next_actions": match.get("next_actions", [])},
        )
    )

    package = jobpilot.create_application_package(workspace_id, job["job_id"])
    artifacts.append(_artifact_ref(package))
    steps.append(
        _step(
            "create_application_package",
            "生成申请包",
            "completed",
            "已生成申请包，包含简历 Markdown、项目描述和 recruiter message。",
            [_artifact_ref(package)],
            {"package_id": package["package_id"], "confirmations": len(package.get("questions_to_confirm", []))},
        )
    )

    jobpilot.confirm_artifact(workspace_id, package["artifact_ref"]["artifact_id"])
    exported = jobpilot.export_application_package(workspace_id, package["package_id"], ["markdown", "docx"])
    steps.append(
        _step(
            "export_package",
            "导出申请包",
            "completed",
            "已完成申请包事实确认，并导出 Markdown 和 DOCX 到本地 workspace/exports。",
            [],
            {"exports": exported.get("exports", [])},
        )
    )

    prep = jobpilot.prepare_interview(workspace_id, job["job_id"], package["package_id"])
    artifacts.append(_artifact_ref(prep))
    steps.append(
        _step(
            "prepare_interview",
            "生成面试准备",
            "completed",
            f"已生成 {len(prep.get('questions', []))} 个面试问题和故事卡。",
            [_artifact_ref(prep)],
            {"questions": len(prep.get("questions", [])), "story_cards": len(prep.get("story_cards", []))},
        )
    )

    realtime = jobpilot.start_realtime_session(workspace_id, job["job_id"])
    detected = jobpilot.detect_question(realtime["session_id"], "讲一个你解决技术难题的经历。")
    hint = jobpilot.generate_hint(realtime["session_id"], detected["question_text"])
    steps.append(
        _step(
            "realtime_hint",
            "生成实时文本结构提示",
            "completed",
            "已基于示例面试问题生成 formal_assist 边界内的结构提示。",
            [],
            {"session_id": realtime["session_id"], "question_type": detected.get("question_type"), "hint_level": hint.get("hint", {}).get("hint_level")},
        )
    )

    transcript = transcript_path.read_text(encoding="utf-8")
    review = jobpilot.review_interview(workspace_id, realtime["session_id"], transcript)
    artifacts.append(_artifact_ref(review))
    steps.append(
        _step(
            "review_and_training",
            "生成复盘和训练任务",
            "completed",
            f"已生成复盘和 {len(review.get('training_tasks', []))} 个训练任务。",
            [_artifact_ref(review)],
            {"training_tasks": len(review.get("training_tasks", []))},
        )
    )

    export_paths = [item.get("path") for item in exported.get("exports", []) if item.get("path")]
    result = {
        "workspace_id": workspace_id,
        "data_mode": "example",
        "data_source": "repository_examples",
        "provider_mode": "workspace_default",
        "steps": steps,
        "artifacts": [ref for ref in artifacts if ref],
        "exports": exported.get("exports", []),
        "summary": {
            "headline": "P2 guided demo flow completed",
            "documents_imported": 2,
            "facts": len(facts.get("facts", [])),
            "fit_label": match.get("fit_label"),
            "package_id": package["package_id"],
            "job_id": job["job_id"],
            "exports": export_paths,
            "training_tasks": len(review.get("training_tasks", [])),
        },
        "key_outputs": {
            "facts": facts.get("facts", [])[:5],
            "project": {"project_id": project.get("project_id"), "name": project.get("name"), "tech_stack": project.get("tech_stack", [])},
            "job": {"job_id": job["job_id"], "title": job.get("title"), "company": job.get("company")},
            "match": {"fit_label": match.get("fit_label"), "strengths": match.get("strengths", []), "gaps": match.get("gaps", [])},
            "application_package": {
                "package_id": package["package_id"],
                "project_description": package.get("project_description"),
                "recruiter_message": package.get("recruiter_message"),
                "questions_to_confirm": package.get("questions_to_confirm", []),
                "artifact_ref": exported.get("artifact_ref") or package.get("artifact_ref"),
            },
            "interview": {"questions": prep.get("questions", []), "story_cards": prep.get("story_cards", [])},
            "realtime_hint": hint.get("hint", hint),
            "review": {"summary": review.get("summary"), "training_tasks": review.get("training_tasks", [])},
        },
    }
    return result
