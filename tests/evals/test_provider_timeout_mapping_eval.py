import socket
import urllib.request

import pytest

from services.llm.contracts import JobParseOutput
from services.llm.provider import OpenAICompatibleProvider, ProviderError


def test_openai_compatible_maps_socket_timeout_to_provider_error(monkeypatch):
    def fake_urlopen(request, timeout):
        raise socket.timeout("timed out")

    monkeypatch.setenv("JOBPILOT_OPENAI_PROVIDER_PRESET", "minimax")
    monkeypatch.setenv("JOBPILOT_LLM_MAX_RETRIES", "0")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = OpenAICompatibleProvider(
        base_url="https://api.minimaxi.com/v1",
        api_key="sk-fake-minimax-key",
        model="MiniMax-M3",
    )

    with pytest.raises(ProviderError) as exc:
        provider.generate_structured("job_parse_jd", {"jd_text": "React role"}, JobParseOutput)

    assert exc.value.error_code == "LLM_TIMEOUT"
