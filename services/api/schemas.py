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


class ProjectCardRequest(BaseModel):
    workspace_id: str
    project_name: str | None = None
    source_document_ids: list[str] | None = None
    target_role: str | None = None


class ParseJdRequest(BaseModel):
    workspace_id: str
    jd_text: str
    source_url: str | None = None


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
