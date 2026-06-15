from services.llm.contracts import JobParseOutput
from services.llm.provider import FixtureProvider
from services.storage.db import loads
from services.storage.workspace import init_workspace, workspace_conn


SAMPLE_JOB_OUTPUT = {
    "job_id": "job_redaction",
    "title": "Junior Frontend Developer",
    "company": "Example Co",
    "requirements": {"must_have": ["React"], "nice_to_have": ["TypeScript"]},
    "responsibilities": ["Build accessible UI"],
    "tech_stack": ["React", "TypeScript"],
    "seniority_guess": "junior",
    "source_refs": [{"source_type": "document", "source_id": "jd_redaction"}],
    "questions_to_confirm": [],
}


def test_provider_invocation_logs_only_redacted_summary(tmp_path):
    workspace = init_workspace("p1-provider-redaction", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    secret = "sk-test_SECRET_SHOULD_NOT_APPEAR_123456789"
    long_resume = "candidate@example.com " + ("React frontend migration project. " * 80)

    provider = FixtureProvider()
    provider.generate_structured(
        "job_parse_jd",
        {
            "api_key": secret,
            "resume_text": long_resume,
            "jd_text": "Junior React role " * 80,
            "fixture_output": SAMPLE_JOB_OUTPUT,
        },
        JobParseOutput,
        request_options={"workspace_id": workspace_id},
    )

    conn, _ = workspace_conn(workspace_id)
    row = conn.execute(
        "SELECT * FROM provider_invocation WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1",
        (workspace_id,),
    ).fetchone()
    assert row is not None
    assert row["provider_name"] == "fixture"
    assert row["status"] == "success"
    assert row["redaction_applied"] == 1

    summary_text = row["input_summary"]
    summary = loads(summary_text, {})
    assert summary["api_key"] == "[REDACTED]"
    assert secret not in summary_text
    assert "candidate@example.com" not in summary_text
    assert "React frontend migration project. " * 20 not in summary_text


def test_provider_invocation_summary_is_bounded_for_nested_payloads(tmp_path):
    workspace = init_workspace("p1-provider-summary-bound", str(tmp_path / "workspace"))
    workspace_id = workspace["workspace_id"]
    nested_items = [
        {
            "title": f"fact-{idx}",
            "content": "React frontend migration project with detailed implementation notes. " * 20,
            "source_refs": [{"quote": "candidate@example.com " + ("private detail " * 40)}],
        }
        for idx in range(20)
    ]

    provider = FixtureProvider()
    provider.generate_structured(
        "job_parse_jd",
        {
            "facts": nested_items,
            "projects": nested_items,
            "fixture_output": SAMPLE_JOB_OUTPUT,
        },
        JobParseOutput,
        request_options={"workspace_id": workspace_id},
    )

    conn, _ = workspace_conn(workspace_id)
    row = conn.execute(
        "SELECT input_summary FROM provider_invocation WHERE workspace_id=? ORDER BY created_at DESC LIMIT 1",
        (workspace_id,),
    ).fetchone()
    assert row is not None
    summary_text = row["input_summary"]
    assert len(summary_text) < 5000
    assert "candidate@example.com" not in summary_text
    assert "React frontend migration project with detailed implementation notes. " * 5 not in summary_text
