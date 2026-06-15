from __future__ import annotations

from pathlib import Path
from typing import Callable

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from services.api.schemas import (
    ArtifactConfirmRequest,
    ArtifactRegenerateRequest,
    ArtifactUpdateRequest,
    ApplicationPackageRequest,
    ChatMessageRequest,
    ChatSessionCreateRequest,
    ExportPackageRequest,
    ExtractFactsRequest,
    InterviewPrepareRequest,
    InterviewReviewRequest,
    MatchProfileRequest,
    ParseJdRequest,
    ProjectCardRequest,
    ProviderCheckRequest,
    RealtimeDetectRequest,
    RealtimeHintRequest,
    RealtimeStartRequest,
    SimulateInterviewRequest,
    SkillEvidenceRequest,
    StoryCardsRequest,
    UpdateFactRequest,
    WorkspaceInitRequest,
    P2DemoWorkflowRequest,
)
from services.chat import get_chat_core
from services.llm.contracts import JobParseOutput
from services.llm.provider import ProviderError, get_provider, normalize_provider_name, provider_status
from services.storage.db import rows_to_dicts
from services.storage.workspace import safe_child
from services.storage.workspace import get_workspace, init_workspace, workspace_conn
from services.tools import jobpilot
from services.workflows.p2_demo import run_p2_demo_flow


app = FastAPI(title="JobPilot AI Agent Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_tool(fn: Callable, *args, **kwargs):
    try:
        return {"ok": True, "data": fn(*args, **kwargs)}
    except ProviderError as exc:
        status_code = 422 if exc.error_code == "VALIDATION_FAILED" else 400
        if exc.error_code in {"LLM_TIMEOUT", "LLM_FAILED", "PROVIDER_RATE_LIMITED"}:
            status_code = 503
        raise HTTPException(
            status_code=status_code,
            detail={
                "ok": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "recoverable": exc.recoverable,
                "suggested_action": "检查 provider 配置、重试，或切换到 mock provider。",
            },
        )
    except ValueError as exc:
        message = str(exc)
        if "VALIDATION_FAILED" in message:
            raise HTTPException(status_code=422, detail={"ok": False, "error_code": "VALIDATION_FAILED", "message": "工具输出未通过结构化校验。", "recoverable": True, "suggested_action": "请检查输入或切换 mock provider 后重试。"})
        if "EXPORT_PRECHECK_FAILED" in message:
            raise HTTPException(status_code=400, detail={"ok": False, "error_code": "EXPORT_PRECHECK_FAILED", "message": message.split(":", 1)[-1].strip(), "recoverable": True, "suggested_action": "确认阻塞项、切换当前版本或编辑申请包后再导出。"})
        if "outside the current workspace" in message:
            raise HTTPException(status_code=403, detail={"ok": False, "error_code": "PERMISSION_DENIED", "message": message, "recoverable": False})
        raise HTTPException(status_code=400, detail={"ok": False, "error_code": "INVALID_INPUT", "message": str(exc), "recoverable": True})
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"ok": False, "error_code": "TOOL_FAILED", "message": "工具执行失败，请查看服务日志。", "recoverable": True})


@app.get("/api/health")
def health():
    return {"ok": True, "service": "jobpilot-ai", "version": "0.1.0"}


@app.get("/api/provider/status")
def provider_status_api(provider: str | None = None):
    return run_tool(provider_status, provider)


@app.post("/api/provider/check")
def provider_check(req: ProviderCheckRequest):
    def _check():
        provider_name = normalize_provider_name(req.provider)
        if provider_name == "openai_compatible" and not req.confirm_external_call:
            status = provider_status(provider_name)
            if status["configured"]:
                return {
                    **status,
                    "checked": False,
                    "message": "OpenAI-compatible provider 已配置；真实外部调用需要显式确认。",
                }
        sample_output = {
            "job_id": "provider_check_job",
            "title": "Junior Frontend Developer",
            "company": "Example Company",
            "requirements": {"must_have": ["React"], "nice_to_have": ["TypeScript"]},
            "responsibilities": ["Build UI components"],
            "tech_stack": ["React", "TypeScript"],
            "seniority_guess": "junior",
            "source_refs": [{"source_type": "document", "source_id": "provider_check"}],
            "questions_to_confirm": [],
        }
        payload = {"mock_output": sample_output, "fixture_output": sample_output}
        provider_instance = get_provider(provider_name)
        result = provider_instance.generate_structured(
            "job_parse_jd",
            payload,
            JobParseOutput,
            request_options={"workspace_id": req.workspace_id},
        )
        return {**provider_status(provider_name), "checked": True, "sample": result}

    return run_tool(_check)


@app.post("/api/workspace/init")
def workspace_init(req: WorkspaceInitRequest):
    return run_tool(init_workspace, req.name, req.root_path, req.llm_provider, req.privacy_mode)


@app.get("/api/workspace/status")
def workspace_status(workspace_id: str | None = None, root_path: str | None = None):
    return run_tool(get_workspace, root_path, workspace_id)


@app.post("/api/files/upload")
async def upload_file(workspace_id: str, file: UploadFile = File(...)):
    data = await file.read()
    return run_tool(jobpilot.save_uploaded_bytes, workspace_id, file.filename or "upload.txt", data, "upload")


@app.post("/api/files/ingest-local")
def ingest_local_file(workspace_id: str, source_path: str, kind: str = "upload"):
    return run_tool(jobpilot.save_document, workspace_id, source_path, kind)


@app.post("/api/profile/extract-facts")
def profile_extract(req: ExtractFactsRequest):
    return run_tool(jobpilot.extract_facts, req.workspace_id, req.document_ids, req.target_roles)


@app.get("/api/profile/facts")
def profile_facts(workspace_id: str):
    return run_tool(jobpilot.list_facts, workspace_id)


@app.patch("/api/profile/facts/{fact_id}")
def profile_update_fact(fact_id: str, req: UpdateFactRequest):
    return run_tool(jobpilot.update_fact, req.workspace_id, fact_id, req.updates)


@app.post("/api/profile/build-skill-evidence")
def profile_skill_evidence(req: SkillEvidenceRequest):
    return run_tool(jobpilot.build_skill_evidence, req.workspace_id, req.skill_names)


@app.post("/api/project/create-card")
def project_create_card(req: ProjectCardRequest):
    return run_tool(jobpilot.create_project_card, req.workspace_id, req.project_name, req.source_document_ids, req.target_role)


@app.get("/api/project/{project_id}")
def project_get(project_id: str, workspace_id: str):
    def _get():
        conn, _ = workspace_conn(workspace_id)
        row = conn.execute("SELECT * FROM tech_project WHERE workspace_id=? AND id=?", (workspace_id, project_id)).fetchone()
        if not row:
            raise ValueError("Project not found.")
        return dict(row)

    return run_tool(_get)


@app.post("/api/job/parse-jd")
def job_parse(req: ParseJdRequest):
    return run_tool(jobpilot.parse_jd, req.workspace_id, req.jd_text, req.source_url)


@app.post("/api/job/match-profile")
def job_match(req: MatchProfileRequest):
    return run_tool(jobpilot.match_profile, req.workspace_id, req.job_id)


@app.get("/api/job/{job_id}/match-report")
def job_match_report(job_id: str, workspace_id: str):
    def _get():
        conn, _ = workspace_conn(workspace_id)
        rows = conn.execute("SELECT * FROM match_report WHERE workspace_id=? AND job_id=? ORDER BY created_at DESC", (workspace_id, job_id)).fetchall()
        return rows_to_dicts(rows)

    return run_tool(_get)


@app.post("/api/application/create-package")
def application_create(req: ApplicationPackageRequest):
    return run_tool(jobpilot.create_application_package, req.workspace_id, req.job_id, req.style, req.language)


@app.post("/api/application/export-package")
def application_export(req: ExportPackageRequest):
    return run_tool(jobpilot.export_application_package, req.workspace_id, req.package_id, req.formats, req.artifact_version_id)


@app.get("/api/application/download")
def application_download(workspace_id: str, path: str):
    def _download():
        _, workspace = workspace_conn(workspace_id)
        root = Path(workspace["root_path"])
        export_path = safe_child(root, path)
        exports_root = safe_child(root, "exports")
        if not export_path.exists() or exports_root not in [export_path, *export_path.parents]:
            raise ValueError("Export file not found.")
        return export_path

    try:
        export_path = _download()
        return FileResponse(export_path, filename=export_path.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"ok": False, "error_code": "EXPORT_FAILED", "message": str(exc), "recoverable": True})


@app.get("/api/application/packages/{package_id}")
def application_get(package_id: str, workspace_id: str):
    def _get():
        conn, _ = workspace_conn(workspace_id)
        row = conn.execute("SELECT * FROM application_package WHERE workspace_id=? AND id=?", (workspace_id, package_id)).fetchone()
        if not row:
            raise ValueError("Package not found.")
        return dict(row)

    return run_tool(_get)


@app.post("/api/interview/prepare")
def interview_prepare(req: InterviewPrepareRequest):
    return run_tool(jobpilot.prepare_interview, req.workspace_id, req.job_id, req.package_id, req.interview_type)


@app.post("/api/interview/create-story-cards")
def interview_story_cards(req: StoryCardsRequest):
    return run_tool(jobpilot.create_story_cards, req.workspace_id, req.source_project_ids, req.job_id)


@app.post("/api/interview/simulate")
def interview_simulate(req: SimulateInterviewRequest):
    return run_tool(jobpilot.simulate_interview, req.workspace_id, req.prep_pack_id, req.mode, req.user_answer)


@app.post("/api/interview/review")
def interview_review(req: InterviewReviewRequest):
    return run_tool(jobpilot.review_interview, req.workspace_id, req.session_id, req.transcript)


@app.post("/api/realtime/start")
def realtime_start(req: RealtimeStartRequest):
    return run_tool(jobpilot.start_realtime_session, req.workspace_id, req.job_id, req.mode, req.save_policy)


@app.post("/api/realtime/detect-question")
def realtime_detect(req: RealtimeDetectRequest):
    return run_tool(jobpilot.detect_question, req.session_id, req.transcript_chunk)


@app.post("/api/realtime/generate-hint")
def realtime_hint(req: RealtimeHintRequest):
    return run_tool(jobpilot.generate_hint, req.session_id, req.question_text, req.hint_level)


@app.get("/api/artifacts")
def artifacts_list(workspace_id: str):
    return run_tool(jobpilot.list_artifacts, workspace_id)


@app.post("/api/artifacts/{artifact_id}/confirm")
def artifacts_confirm(artifact_id: str, req: ArtifactConfirmRequest):
    return run_tool(jobpilot.confirm_artifact, req.workspace_id, artifact_id)


@app.patch("/api/artifacts/{artifact_id}")
def artifacts_update(artifact_id: str, req: ArtifactUpdateRequest):
    return run_tool(jobpilot.update_artifact, req.workspace_id, artifact_id, req.content_json)


@app.get("/api/artifacts/{artifact_id}/versions")
def artifacts_versions(artifact_id: str, workspace_id: str):
    return run_tool(jobpilot.list_artifact_versions, workspace_id, artifact_id)


@app.get("/api/artifacts/{artifact_id}/versions/{version_id}")
def artifacts_version_get(artifact_id: str, version_id: str, workspace_id: str):
    return run_tool(jobpilot.get_artifact_version, workspace_id, artifact_id, version_id)


@app.post("/api/artifacts/{artifact_id}/versions/{version_id}/restore")
def artifacts_version_restore(artifact_id: str, version_id: str, req: ArtifactConfirmRequest):
    return run_tool(jobpilot.restore_artifact_version, req.workspace_id, artifact_id, version_id)


@app.post("/api/artifacts/{artifact_id}/regenerate")
def artifacts_regenerate(artifact_id: str, req: ArtifactRegenerateRequest):
    return run_tool(jobpilot.regenerate_artifact, req.workspace_id, artifact_id, req.fail_for_test)


@app.post("/api/chat/sessions")
def chat_sessions_create(req: ChatSessionCreateRequest):
    return run_tool(jobpilot.create_chat_session, req.workspace_id, req.title)


@app.get("/api/chat/sessions")
def chat_sessions_list(workspace_id: str):
    return run_tool(jobpilot.list_chat_sessions, workspace_id)


@app.get("/api/chat/sessions/{session_id}")
def chat_sessions_get(session_id: str, workspace_id: str):
    return run_tool(jobpilot.get_chat_session, workspace_id, session_id)


@app.post("/api/realtime/end")
def realtime_end(session_id: str):
    return run_tool(jobpilot.end_realtime_session, session_id)


@app.post("/api/chat/message")
def chat_message(req: ChatMessageRequest):
    return run_tool(get_chat_core().handle_message, req.workspace_id, req.session_id, req.message)


@app.post("/api/workflows/p2-demo/run")
def p2_demo_run(req: P2DemoWorkflowRequest):
    return run_tool(run_p2_demo_flow, req.workspace_id, req.reset_workspace)
