import os

from services.config import load_dotenv


def test_dotenv_loads_local_jobpilot_keys(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        """
        # Local provider configuration
        JOBPILOT_LLM_PROVIDER=openai_compatible
        JOBPILOT_OPENAI_BASE_URL="https://api.example.test/v1"
        JOBPILOT_OPENAI_API_KEY='sk-test-secret'
        export JOBPILOT_OPENAI_MODEL=gpt-test
        """,
        encoding="utf-8",
    )
    for key in [
        "JOBPILOT_LLM_PROVIDER",
        "JOBPILOT_OPENAI_BASE_URL",
        "JOBPILOT_OPENAI_API_KEY",
        "JOBPILOT_OPENAI_MODEL",
    ]:
        monkeypatch.delenv(key, raising=False)

    loaded = load_dotenv(env_file)

    assert set(loaded) == {
        "JOBPILOT_LLM_PROVIDER",
        "JOBPILOT_OPENAI_BASE_URL",
        "JOBPILOT_OPENAI_API_KEY",
        "JOBPILOT_OPENAI_MODEL",
    }
    assert os.environ["JOBPILOT_LLM_PROVIDER"] == "openai_compatible"
    assert os.environ["JOBPILOT_OPENAI_BASE_URL"] == "https://api.example.test/v1"
    assert os.environ["JOBPILOT_OPENAI_API_KEY"] == "sk-test-secret"
    assert os.environ["JOBPILOT_OPENAI_MODEL"] == "gpt-test"


def test_dotenv_does_not_override_existing_environment_by_default(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("JOBPILOT_OPENAI_API_KEY=sk-from-file\n", encoding="utf-8")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "sk-from-shell")

    load_dotenv(env_file)

    assert os.environ["JOBPILOT_OPENAI_API_KEY"] == "sk-from-shell"


def test_dotenv_can_override_when_explicitly_requested(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("JOBPILOT_OPENAI_API_KEY=sk-from-file\n", encoding="utf-8")
    monkeypatch.setenv("JOBPILOT_OPENAI_API_KEY", "sk-from-shell")

    load_dotenv(env_file, override=True)

    assert os.environ["JOBPILOT_OPENAI_API_KEY"] == "sk-from-file"
