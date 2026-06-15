from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceRef(ContractModel):
    source_type: Literal[
        "career_fact",
        "skill_evidence",
        "tech_project",
        "document",
        "job",
        "story_card",
        "transcript",
        "artifact",
        "resume_version",
        "application_package",
        "interview",
        "realtime_session",
    ]
    source_id: str
    field: str | None = None
    quote: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"


class ConfirmationQuestion(ContractModel):
    question: str
    confirmation_level: Literal["blocking", "warning", "optional"] = "warning"
    reason: str | None = None
    source_refs: list[SourceRef] = Field(default_factory=list)


class ArtifactRecord(ContractModel):
    artifact_id: str
    artifact_type: str
    workspace_id: str
    status: Literal["draft", "needs_confirmation", "confirmed", "exported"]
    source_refs: list[SourceRef] = Field(default_factory=list)
    questions_to_confirm: list[ConfirmationQuestion] = Field(default_factory=list)


class GeneratedCareerFact(ContractModel):
    id: str
    type: str
    title: str
    content: str
    confidence: float
    needs_confirmation: bool = True
    source_refs: list[SourceRef] = Field(default_factory=list)


class ProfileExtractFactsOutput(ContractModel):
    facts: list[GeneratedCareerFact]
    missing_info: list[str] = Field(default_factory=list)
    questions_to_confirm: list[ConfirmationQuestion] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)


class JobParseOutput(ContractModel):
    job_id: str
    title: str
    company: str | None = None
    requirements: dict[str, list[str]]
    responsibilities: list[str]
    tech_stack: list[str]
    seniority_guess: Literal["junior", "entry", "mid", "senior", "unknown"]
    source_refs: list[SourceRef] = Field(default_factory=list)
    questions_to_confirm: list[ConfirmationQuestion] = Field(default_factory=list)


class MatchReportOutput(ContractModel):
    match_report_id: str
    fit_label: str
    fit_score_optional: float
    strengths: list[str]
    gaps: list[str]
    next_actions: list[str]
    apply_recommendation: str
    source_refs: list[SourceRef] = Field(default_factory=list)
    questions_to_confirm: list[ConfirmationQuestion] = Field(default_factory=list)


class ApplicationPackageOutput(ContractModel):
    package_id: str
    resume_version_id: str
    resume_markdown: str
    project_description: str
    recruiter_message: str
    questions_to_confirm: list[ConfirmationQuestion]
    source_refs: list[SourceRef]


class StoryCardOutput(ContractModel):
    id: str
    title: str
    applicable_questions: list[str]
    short_version: str
    medium_version: str
    long_version: str
    source_refs: list[SourceRef]


class RealtimeHintOutput(ContractModel):
    question_type: str
    hint_level: Literal["minimal", "outline"]
    recommended_project: str
    structure: list[str]
    reminder: str
    source_refs: list[SourceRef] = Field(default_factory=list)

    @field_validator("structure")
    @classmethod
    def no_full_answer(cls, value: list[str]) -> list[str]:
        joined = " ".join(value).lower()
        forbidden = ["full_answer", "逐字", "照着念", "完整答案"]
        if any(token in joined for token in forbidden):
            raise ValueError("formal_assist hint must not include a full answer")
        return value


class InterviewReviewOutput(ContractModel):
    review_id: str
    questions: list[str]
    strengths: list[str]
    improvements: list[str]
    training_tasks: list[str]
    thank_you_message: str
    source_refs: list[SourceRef] = Field(default_factory=list)

    @field_validator("training_tasks")
    @classmethod
    def at_least_three_tasks(cls, value: list[str]) -> list[str]:
        if len(value) < 3:
            raise ValueError("interview review must produce at least 3 training tasks")
        return value


class InterviewPrepOutput(ContractModel):
    prep_pack_id: str
    focus_areas: list[str]
    questions: list[str]
    reverse_questions: list[str]
    story_cards: list[dict[str, Any]] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    questions_to_confirm: list[ConfirmationQuestion] = Field(default_factory=list)


OUTPUT_CONTRACTS: dict[str, type[BaseModel]] = {
    "profile_extract_facts": ProfileExtractFactsOutput,
    "job_parse_jd": JobParseOutput,
    "job_match_profile": MatchReportOutput,
    "application_create_package": ApplicationPackageOutput,
    "interview_prepare": InterviewPrepOutput,
    "interview_create_story_card": StoryCardOutput,
    "realtime_generate_hint": RealtimeHintOutput,
    "interview_review": InterviewReviewOutput,
}


def validate_output(prompt_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    model = OUTPUT_CONTRACTS[prompt_name]
    try:
        return model.model_validate(payload).model_dump(mode="json")
    except ValidationError as exc:
        raise ValueError(f"VALIDATION_FAILED: {prompt_name} output failed schema validation") from exc
