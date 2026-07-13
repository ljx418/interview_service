from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class WorkspaceInitRequest(BaseModel):
    name: str = "my-job-search"
    root_path: str | None = None
    llm_provider: str = "mock"
    privacy_mode: str = "local_first"


class WorkspaceStatusRequest(BaseModel):
    workspace_id: str
    root_path: str | None = None


class ProviderCheckRequest(BaseModel):
    workspace_id: str | None = None
    provider: Literal["mock", "fixture", "openai_compatible", "openai"] = "mock"
    confirm_external_call: bool = False


class ProviderRuntimeConfigRequest(BaseModel):
    provider: Literal["mock", "openai_compatible", "openai"] = "mock"
    preset: Literal["", "minimax", "deepseek"] = ""
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    timeout_seconds: int = 30
    max_retries: int = 1


class MarketProviderCheckRequest(BaseModel):
    workspace_id: str | None = None
    provider_id: str = "fixture_local"
    consent_preview_id: str | None = None
    confirm: bool = False


class MarketSearchRunRequest(BaseModel):
    workspace_id: str
    query: str
    city_filters: list[str] = Field(default_factory=list)
    salary_range: str | None = None
    tech_stack: list[str] = Field(default_factory=list)
    provider_ids: list[str] = Field(default_factory=lambda: ["fixture_local"])
    consent_id: str | None = None
    source_policy: Literal["fixture", "recorded", "manual", "public", "opt_in_api"] = "fixture"


class ProviderPreferencesRequest(BaseModel):
    provider: Literal["mock", "openai_compatible", "openai"] = "mock"
    preset: Literal["", "minimax", "deepseek"] = ""
    base_url: str = ""
    model: str = ""
    mode: Literal["mock_default", "provider_opt_in"] = "mock_default"


class ProviderConsentRequest(BaseModel):
    workspace_id: str
    session_id: str
    scope: Literal["current_message", "chat_session"] = "current_message"
    ttl_seconds: int = 900
    allowed_data_classes: list[str] = Field(default_factory=lambda: ["recent_messages", "workspace_summary"])
    confirm_external_call: bool = False


class ExtractFactsRequest(BaseModel):
    workspace_id: str
    document_ids: list[str] | None = None
    target_roles: list[str] = Field(default_factory=list)


class UpdateFactRequest(BaseModel):
    workspace_id: str
    updates: dict[str, Any]


class SkillEvidenceRequest(BaseModel):
    workspace_id: str
    skill_names: list[str] | None = None


class CandidateProfileRefreshRequest(BaseModel):
    workspace_id: str
    job_id: str | None = None
    target_role: str | None = None


class ProjectCardRequest(BaseModel):
    workspace_id: str
    project_name: str | None = None
    source_document_ids: list[str] | None = None
    target_role: str | None = None


class ParseJdRequest(BaseModel):
    workspace_id: str
    jd_text: str
    source_url: str | None = None


class JobIntakeRequest(BaseModel):
    workspace_id: str
    jd_text: str
    source_url: str | None = None
    platform: str | None = None
    import_method: Literal["manual_paste", "file_import", "chat_paste"] = "manual_paste"
    user_notes: str | None = None


class JobSelectRequest(BaseModel):
    workspace_id: str


class ResumeGenerateRequest(BaseModel):
    workspace_id: str
    job_id: str | None = None
    mode: Literal["targeted", "general"] = "targeted"
    style: str = "junior_developer"
    language: str = "zh-CN"


class MatchProfileRequest(BaseModel):
    workspace_id: str
    job_id: str


class ApplicationPackageRequest(BaseModel):
    workspace_id: str
    job_id: str
    style: str = "junior_developer"
    language: str = "zh-CN"


class ExportPackageRequest(BaseModel):
    workspace_id: str
    package_id: str
    formats: list[Literal["markdown", "pdf", "docx"]] = Field(default_factory=lambda: ["markdown"])
    artifact_version_id: str | None = None


class InterviewPrepareRequest(BaseModel):
    workspace_id: str
    job_id: str
    package_id: str | None = None
    interview_type: str = "mixed"


class StoryCardsRequest(BaseModel):
    workspace_id: str
    source_project_ids: list[str] | None = None
    job_id: str | None = None


class SimulateInterviewRequest(BaseModel):
    workspace_id: str
    prep_pack_id: str | None = None
    mode: str = "project_deep_dive"
    user_answer: str | None = None


class RealtimeStartRequest(BaseModel):
    workspace_id: str
    job_id: str | None = None
    mode: Literal["practice", "formal_assist", "ai_allowed"] = "formal_assist"
    save_policy: Literal["no_audio", "transcript_only", "save_all"] = "transcript_only"


class RealtimeDetectRequest(BaseModel):
    session_id: str
    transcript_chunk: str


class RealtimeHintRequest(BaseModel):
    session_id: str
    question_text: str
    hint_level: Literal["minimal", "outline", "draft"] = "outline"


class InterviewReviewRequest(BaseModel):
    workspace_id: str
    session_id: str | None = None
    transcript: str | None = None


class ChatMessageRequest(BaseModel):
    workspace_id: str
    message: str
    session_id: str | None = None
    provider_mode: Literal["local_default", "provider_opt_in"] = "local_default"


class ArtifactUpdateRequest(BaseModel):
    workspace_id: str
    content_json: dict[str, Any]


class ArtifactConfirmRequest(BaseModel):
    workspace_id: str


class ArtifactRegenerateRequest(BaseModel):
    workspace_id: str
    fail_for_test: bool = False


class ChatSessionCreateRequest(BaseModel):
    workspace_id: str
    title: str = "JobPilot Chat"


class P2DemoWorkflowRequest(BaseModel):
    workspace_id: str | None = None
    reset_workspace: bool = False
    data_mode: Literal["example", "my_data"] = "example"


class WorkspaceBackupRequest(BaseModel):
    workspace_id: str
    target: str | None = None


class WorkspaceCleanupPlanRequest(BaseModel):
    workspace_id: str
    rules: dict[str, Any] = Field(default_factory=dict)


class WorkspaceMigrationPlanRequest(BaseModel):
    workspace_id: str
    target_version: str


class DiagnosticsReportRequest(BaseModel):
    workspace_id: str
    include_provider: bool = True
