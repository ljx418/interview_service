import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.llm.contracts import JobParseOutput
from services.llm.provider import FixtureProvider, ProviderError, get_provider, provider_status


SAMPLE_JOB_OUTPUT = {
    "job_id": "job_fixture",
    "title": "Junior Frontend Developer",
    "company": "Example Co",
    "requirements": {"must_have": ["React"], "nice_to_have": ["TypeScript"]},
    "responsibilities": ["Build accessible UI"],
    "tech_stack": ["React", "TypeScript"],
    "seniority_guess": "junior",
    "source_refs": [{"source_type": "document", "source_id": "jd_fixture"}],
    "questions_to_confirm": [],
}


def test_default_provider_is_mock(monkeypatch):
    monkeypatch.delenv("JOBPILOT_LLM_PROVIDER", raising=False)
    assert get_provider().__class__.__name__ == "MockProvider"
    status = provider_status()
    assert status["provider"] == "mock"
    assert status["configured"] is True
    assert status["external_calls_enabled"] is False


def test_fixture_provider_validates_structured_output():
    provider = FixtureProvider()
    output = provider.generate_structured(
        "job_parse_jd",
        {"fixture_output": SAMPLE_JOB_OUTPUT},
        JobParseOutput,
    )
    assert output["title"] == "Junior Frontend Developer"
    assert output["seniority_guess"] == "junior"


def test_fixture_provider_rejects_invalid_json_and_schema_mismatch():
    provider = FixtureProvider()
    with pytest.raises(ProviderError) as invalid_json:
        provider.generate_structured("job_parse_jd", {"fixture_output": "{bad json"}, JobParseOutput)
    assert invalid_json.value.error_code == "PROVIDER_BAD_RESPONSE"

    with pytest.raises(ProviderError) as schema_error:
        provider.generate_structured(
            "job_parse_jd",
            {"fixture_output": {**SAMPLE_JOB_OUTPUT, "seniority_guess": "lead"}},
            JobParseOutput,
        )
    assert schema_error.value.error_code == "VALIDATION_FAILED"


def test_openai_compatible_requires_explicit_configuration(monkeypatch):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "openai_compatible")
    monkeypatch.delenv("JOBPILOT_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("JOBPILOT_OPENAI_BASE_URL", raising=False)
    provider = get_provider()
    with pytest.raises(ProviderError) as missing_config:
        provider.generate_structured("job_parse_jd", {"jd_text": "React role"}, JobParseOutput)
    assert missing_config.value.error_code == "PROVIDER_NOT_CONFIGURED"


def test_fixture_provider_simulates_timeout():
    provider = FixtureProvider()
    with pytest.raises(ProviderError) as timeout:
        provider.generate_structured("job_parse_jd", {"fixture_error": "timeout"}, JobParseOutput)
    assert timeout.value.error_code == "LLM_TIMEOUT"


def test_provider_status_and_check_api(monkeypatch):
    monkeypatch.setenv("JOBPILOT_LLM_PROVIDER", "mock")
    monkeypatch.delenv("JOBPILOT_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("JOBPILOT_OPENAI_BASE_URL", raising=False)
    client = TestClient(app)

    status = client.get("/api/provider/status")
    assert status.status_code == 200
    assert status.json()["data"]["provider"] == "mock"
    assert status.json()["data"]["external_calls_enabled"] is False

    mock_check = client.post("/api/provider/check", json={"provider": "mock"})
    assert mock_check.status_code == 200
    assert mock_check.json()["data"]["checked"] is True

    openai_check = client.post("/api/provider/check", json={"provider": "openai_compatible", "confirm_external_call": True})
    assert openai_check.status_code == 400
    detail = openai_check.json()["detail"]
    assert detail["error_code"] == "PROVIDER_NOT_CONFIGURED"
    assert detail["recoverable"] is True
