import json
import urllib.request

from services.llm.contracts import JobParseOutput
from services.llm.provider import OpenAICompatibleProvider


SAMPLE_JOB_OUTPUT = {
    "job_id": "job_minimax",
    "title": "Junior Frontend Developer",
    "company": "Example Co",
    "requirements": {"must_have": ["React"], "nice_to_have": ["TypeScript"]},
    "responsibilities": ["Build accessible UI"],
    "tech_stack": ["React", "TypeScript"],
    "seniority_guess": "junior",
    "source_refs": [{"source_type": "document", "source_id": "jd_minimax"}],
    "questions_to_confirm": [],
}


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(SAMPLE_JOB_OUTPUT),
                        }
                    }
                ]
            }
        ).encode("utf-8")


def test_minimax_preset_uses_official_openai_compatible_shape(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["authorization"] = request.headers.get("Authorization")
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("JOBPILOT_OPENAI_PROVIDER_PRESET", "minimax")
    monkeypatch.setenv("JOBPILOT_LLM_TIMEOUT_SECONDS", "7")
    monkeypatch.setenv("JOBPILOT_LLM_MAX_RETRIES", "0")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = OpenAICompatibleProvider(
        base_url="https://api.minimaxi.com/v1",
        api_key="sk-fake-minimax-key",
        model="MiniMax-M3",
    )
    output = provider.generate_structured("job_parse_jd", {"jd_text": "React role"}, JobParseOutput)

    assert output["title"] == "Junior Frontend Developer"
    assert captured["url"] == "https://api.minimaxi.com/v1/chat/completions"
    assert captured["body"]["model"] == "MiniMax-M3"
    assert captured["body"]["thinking"] == {"type": "disabled"}
    assert "response_format" not in captured["body"]
    system_prompt = captured["body"]["messages"][0]["content"]
    assert "Output schema JSON" in system_prompt
    assert "JobParseOutput" in system_prompt
    assert "Do not include markdown fences" in system_prompt
    assert "sk-fake-minimax-key" not in json.dumps(captured["body"])
    assert captured["authorization"] == "Bearer sk-fake-minimax-key"
    assert captured["timeout"] == 7
