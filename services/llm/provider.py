from __future__ import annotations

import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Protocol

from pydantic import BaseModel, ValidationError

from services.config import load_project_dotenv


load_project_dotenv()


class ProviderError(ValueError):
    def __init__(self, error_code: str, message: str, recoverable: bool = True) -> None:
        super().__init__(f"{error_code}: {message}")
        self.error_code = error_code
        self.message = message
        self.recoverable = recoverable


class LLMProvider(Protocol):
    def generate_structured(
        self,
        prompt_name: str,
        input_payload: dict[str, Any],
        output_schema: type[BaseModel],
        safety_mode: str = "normal",
        request_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...


SENSITIVE_KEYS = {"api_key", "authorization", "token", "secret", "password"}
TOKEN_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{12,}|Bearer\s+[A-Za-z0-9._\-]{12,})")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_text(value: str, max_chars: int = 220) -> tuple[str, bool]:
    redaction_applied = False
    redacted = TOKEN_RE.sub("[REDACTED_TOKEN]", value)
    if redacted != value:
        redaction_applied = True
    value = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    if value != redacted:
        redaction_applied = True
    if len(value) > max_chars:
        value = f"{value[:max_chars]}... [TRUNCATED {len(value) - max_chars} chars]"
        redaction_applied = True
    return value, redaction_applied


def summarize_payload(payload: Any, max_chars: int = 160) -> tuple[Any, bool]:
    if isinstance(payload, dict):
        summary: dict[str, Any] = {}
        redacted = False
        max_items = 12
        items = list(payload.items())
        for key, value in items[:max_items]:
            key_lower = key.lower()
            if key_lower == "candidate_output" and isinstance(value, dict):
                summary[key] = {
                    "keys": sorted(value.keys()),
                    "package_id": value.get("package_id"),
                    "resume_version_id": value.get("resume_version_id"),
                    "resume_markdown_chars": len(value.get("resume_markdown", "")) if isinstance(value.get("resume_markdown"), str) else None,
                    "source_refs_count": len(value.get("source_refs", [])) if isinstance(value.get("source_refs"), list) else None,
                    "questions_to_confirm_count": len(value.get("questions_to_confirm", [])) if isinstance(value.get("questions_to_confirm"), list) else None,
                }
                redacted = True
                continue
            if key_lower in {"facts", "projects", "skill_evidence", "documents"} and isinstance(value, list):
                preview = []
                for item in value[:3]:
                    if isinstance(item, dict):
                        preview.append(
                            {
                                "id": item.get("id"),
                                "title": item.get("title") or item.get("name") or item.get("skill_name") or item.get("filename"),
                                "keys": sorted(item.keys())[:8],
                            }
                        )
                    else:
                        summarized, _ = summarize_payload(item, max_chars=80)
                        preview.append(summarized)
                summary[key] = {"count": len(value), "preview": preview}
                redacted = True
                continue
            if key_lower == "job" and isinstance(value, dict):
                summary[key] = {
                    "id": value.get("id"),
                    "title": value.get("title"),
                    "company": value.get("company"),
                    "keys": sorted(value.keys())[:12],
                }
                redacted = True
                continue
            if key.lower() in SENSITIVE_KEYS:
                summary[key] = "[REDACTED]"
                redacted = True
                continue
            summarized, did_redact = summarize_payload(value, max_chars=max_chars)
            summary[key] = summarized
            redacted = redacted or did_redact
        if len(items) > max_items:
            summary["_truncated_keys"] = len(items) - max_items
            redacted = True
        return summary, redacted
    if isinstance(payload, list):
        values = payload[:5]
        summary_list = []
        redacted = len(payload) > len(values)
        for value in values:
            summarized, did_redact = summarize_payload(value, max_chars=max_chars)
            summary_list.append(summarized)
            redacted = redacted or did_redact
        if len(payload) > len(values):
            summary_list.append(f"[TRUNCATED {len(payload) - len(values)} items]")
        return summary_list, redacted
    if isinstance(payload, str):
        return redact_text(payload, max_chars=max_chars)
    return payload, False


def _schema_name(output_schema: type[BaseModel]) -> str:
    return getattr(output_schema, "__name__", "BaseModel")


def _schema_contract_text(output_schema: type[BaseModel]) -> str:
    try:
        return json.dumps(output_schema.model_json_schema(), ensure_ascii=False)
    except Exception:
        return _schema_name(output_schema)


def _log_provider_invocation(
    *,
    workspace_id: str | None,
    provider_name: str,
    prompt_name: str,
    schema_name: str,
    input_summary: Any,
    redaction_applied: bool,
    status: str,
    error_code: str | None,
    latency_ms: int,
) -> None:
    if not workspace_id:
        return
    try:
        from services.storage.db import dumps
        from services.storage.workspace import workspace_conn

        conn, _ = workspace_conn(workspace_id)
        conn.execute(
            """
            INSERT INTO provider_invocation (
              id, workspace_id, provider_name, prompt_name, schema_name,
              input_summary, redaction_applied, status, error_code,
              latency_ms, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"provider_inv_{uuid4().hex}",
                workspace_id,
                provider_name,
                prompt_name,
                schema_name,
                dumps(input_summary),
                1 if redaction_applied else 0,
                status,
                error_code,
                latency_ms,
                _now(),
            ),
        )
    except Exception:
        return


def _validate_output(prompt_name: str, output_schema: type[BaseModel], payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProviderError("PROVIDER_BAD_RESPONSE", f"{prompt_name} provider output is not a JSON object.")
    try:
        return output_schema.model_validate(payload).model_dump(mode="json")
    except ValidationError as exc:
        errors = exc.errors(include_input=False)
        preview = json.dumps(errors[:6], ensure_ascii=False)
        raise ProviderError("VALIDATION_FAILED", f"{prompt_name} output failed schema validation: {preview}") from exc
    except Exception as exc:
        raise ProviderError("VALIDATION_FAILED", f"{prompt_name} output failed schema validation.") from exc


def _options(request_options: dict[str, Any] | None) -> dict[str, Any]:
    return request_options or {}


class MockProvider:
    """Deterministic provider used by P0 tests and local-first demos."""

    name = "mock"

    def generate_structured(
        self,
        prompt_name: str,
        input_payload: dict[str, Any],
        output_schema: type[BaseModel],
        safety_mode: str = "normal",
        request_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = time.monotonic()
        opts = _options(request_options)
        input_summary, redaction_applied = summarize_payload(input_payload)
        payload = input_payload.get("mock_output")
        if payload is None:
            error = ProviderError("PROVIDER_BAD_RESPONSE", f"No mock_output supplied for {prompt_name}.")
            _log_provider_invocation(
                workspace_id=opts.get("workspace_id"),
                provider_name=self.name,
                prompt_name=prompt_name,
                schema_name=_schema_name(output_schema),
                input_summary=input_summary,
                redaction_applied=redaction_applied,
                status="failed",
                error_code=error.error_code,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            raise error
        try:
            output = _validate_output(prompt_name, output_schema, payload)
        except ProviderError as error:
            _log_provider_invocation(
                workspace_id=opts.get("workspace_id"),
                provider_name=self.name,
                prompt_name=prompt_name,
                schema_name=_schema_name(output_schema),
                input_summary=input_summary,
                redaction_applied=redaction_applied,
                status="failed",
                error_code=error.error_code,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            raise
        _log_provider_invocation(
            workspace_id=opts.get("workspace_id"),
            provider_name=self.name,
            prompt_name=prompt_name,
            schema_name=_schema_name(output_schema),
            input_summary=input_summary,
            redaction_applied=redaction_applied,
            status="success",
            error_code=None,
            latency_ms=int((time.monotonic() - started) * 1000),
        )
        return output


class FixtureProvider:
    """Test-only provider that returns payloads from input or fixture files."""

    name = "fixture"

    def generate_structured(
        self,
        prompt_name: str,
        input_payload: dict[str, Any],
        output_schema: type[BaseModel],
        safety_mode: str = "normal",
        request_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = time.monotonic()
        opts = _options(request_options)
        input_summary, redaction_applied = summarize_payload(input_payload)
        error_name = input_payload.get("fixture_error")
        if error_name == "timeout":
            error = ProviderError("LLM_TIMEOUT", "Fixture provider simulated timeout.")
            _log_provider_invocation(
                workspace_id=opts.get("workspace_id"),
                provider_name=self.name,
                prompt_name=prompt_name,
                schema_name=_schema_name(output_schema),
                input_summary=input_summary,
                redaction_applied=redaction_applied,
                status="failed",
                error_code=error.error_code,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            raise error

        payload = input_payload.get("fixture_output")
        fixture_path = input_payload.get("fixture_path")
        if fixture_path:
            with open(fixture_path, encoding="utf-8") as handle:
                payload = json.load(handle)
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as exc:
                error = ProviderError("PROVIDER_BAD_RESPONSE", "Fixture provider returned invalid JSON.")
                _log_provider_invocation(
                    workspace_id=opts.get("workspace_id"),
                    provider_name=self.name,
                    prompt_name=prompt_name,
                    schema_name=_schema_name(output_schema),
                    input_summary=input_summary,
                    redaction_applied=redaction_applied,
                    status="failed",
                    error_code=error.error_code,
                    latency_ms=int((time.monotonic() - started) * 1000),
                )
                raise error from exc
        try:
            output = _validate_output(prompt_name, output_schema, payload)
        except ProviderError as error:
            _log_provider_invocation(
                workspace_id=opts.get("workspace_id"),
                provider_name=self.name,
                prompt_name=prompt_name,
                schema_name=_schema_name(output_schema),
                input_summary=input_summary,
                redaction_applied=redaction_applied,
                status="failed",
                error_code=error.error_code,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            raise
        _log_provider_invocation(
            workspace_id=opts.get("workspace_id"),
            provider_name=self.name,
            prompt_name=prompt_name,
            schema_name=_schema_name(output_schema),
            input_summary=input_summary,
            redaction_applied=redaction_applied,
            status="success",
            error_code=None,
            latency_ms=int((time.monotonic() - started) * 1000),
        )
        return output


class OpenAICompatibleProvider:
    name = "openai_compatible"

    def __init__(self, *, base_url: str | None = None, api_key: str | None = None, model: str | None = None) -> None:
        self.base_url = (base_url or os.environ.get("JOBPILOT_OPENAI_BASE_URL") or "").rstrip("/")
        self.api_key = api_key or os.environ.get("JOBPILOT_OPENAI_API_KEY")
        self.model = model or os.environ.get("JOBPILOT_OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_seconds = float(os.environ.get("JOBPILOT_LLM_TIMEOUT_SECONDS", "30"))
        self.max_retries = int(os.environ.get("JOBPILOT_LLM_MAX_RETRIES", "1"))
        self.provider_preset = os.environ.get("JOBPILOT_OPENAI_PROVIDER_PRESET", "").strip().lower()

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    def generate_structured(
        self,
        prompt_name: str,
        input_payload: dict[str, Any],
        output_schema: type[BaseModel],
        safety_mode: str = "normal",
        request_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = time.monotonic()
        opts = _options(request_options)
        input_summary, redaction_applied = summarize_payload(input_payload)
        if not self.configured:
            error = ProviderError("PROVIDER_NOT_CONFIGURED", "OpenAI-compatible provider is missing base URL, model, or API key.")
            _log_provider_invocation(
                workspace_id=opts.get("workspace_id"),
                provider_name=self.name,
                prompt_name=prompt_name,
                schema_name=_schema_name(output_schema),
                input_summary=input_summary,
                redaction_applied=True,
                status="failed",
                error_code=error.error_code,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            raise error

        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only one valid JSON object that exactly matches the requested output schema. "
                        "Do not include markdown fences, analysis, comments, or <think> tags. "
                        "Do not include fields that are not present in the schema. "
                        "If the input contains candidate_output, use it as a schema-valid draft: preserve IDs, source_refs, "
                        "questions_to_confirm, and required field shapes unless a change is necessary. "
                        "Use source_refs from the input when possible; if no source exists, create a low-confidence source_ref. "
                        f"Output schema JSON: {_schema_contract_text(output_schema)}. "
                        "Do not include markdown fences, analysis, or <think> tags. "
                        f"Prompt name: {prompt_name}. Safety mode: {safety_mode}."
                    ),
                },
                {"role": "user", "content": json.dumps(input_payload, ensure_ascii=False)},
            ],
            "temperature": 0,
        }
        if self.provider_preset == "minimax":
            body["thinking"] = {"type": "disabled"}
        else:
            body["response_format"] = {"type": "json_object"}
        url = self.base_url
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"

        last_error: ProviderError | None = None
        for attempt in range(self.max_retries + 1):
            try:
                request = urllib.request.Request(
                    url,
                    data=json.dumps(body).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    response_text = response.read().decode("utf-8")
                try:
                    response_payload = json.loads(response_text)
                except json.JSONDecodeError as exc:
                    raise ProviderError("PROVIDER_BAD_RESPONSE", "Provider response was not valid JSON.") from exc
                output_payload = _extract_openai_json(response_payload)
                output = _validate_output(prompt_name, output_schema, output_payload)
                _log_provider_invocation(
                    workspace_id=opts.get("workspace_id"),
                    provider_name=self.name,
                    prompt_name=prompt_name,
                    schema_name=_schema_name(output_schema),
                    input_summary=input_summary,
                    redaction_applied=redaction_applied,
                    status="success",
                    error_code=None,
                    latency_ms=int((time.monotonic() - started) * 1000),
                )
                return output
            except ProviderError as exc:
                last_error = exc
                if exc.error_code in {"PROVIDER_BAD_RESPONSE", "VALIDATION_FAILED"}:
                    break
            except urllib.error.HTTPError as exc:
                code = "PROVIDER_RATE_LIMITED" if exc.code == 429 else "LLM_FAILED"
                last_error = ProviderError(code, "Provider HTTP request failed.")
            except TimeoutError:
                last_error = ProviderError("LLM_TIMEOUT", "Provider request timed out.")
            except socket.timeout:
                last_error = ProviderError("LLM_TIMEOUT", "Provider request timed out.")
            except urllib.error.URLError as exc:
                reason = getattr(exc, "reason", None)
                if isinstance(reason, TimeoutError):
                    last_error = ProviderError("LLM_TIMEOUT", "Provider request timed out.")
                elif isinstance(reason, socket.timeout):
                    last_error = ProviderError("LLM_TIMEOUT", "Provider request timed out.")
                else:
                    last_error = ProviderError("LLM_FAILED", "Provider request failed.")
            if attempt < self.max_retries:
                time.sleep(min(0.2 * (attempt + 1), 1.0))

        error = last_error or ProviderError("LLM_FAILED", "Provider request failed.")
        _log_provider_invocation(
            workspace_id=opts.get("workspace_id"),
            provider_name=self.name,
            prompt_name=prompt_name,
            schema_name=_schema_name(output_schema),
            input_summary=input_summary,
            redaction_applied=redaction_applied,
            status="failed",
            error_code=error.error_code,
            latency_ms=int((time.monotonic() - started) * 1000),
        )
        raise error


def _extract_openai_json(response_payload: dict[str, Any]) -> dict[str, Any]:
    if "choices" not in response_payload:
        return response_payload
    try:
        content = response_payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("PROVIDER_BAD_RESPONSE", "Provider response did not include message content.") from exc
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        raise ProviderError("PROVIDER_BAD_RESPONSE", "Provider message content was not a JSON string.")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ProviderError("PROVIDER_BAD_RESPONSE", "Provider message content was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ProviderError("PROVIDER_BAD_RESPONSE", "Provider message content was not a JSON object.")
    return parsed


def provider_status(provider_name: str | None = None) -> dict[str, Any]:
    name = normalize_provider_name(provider_name)
    configured = True
    model = None
    external_calls_enabled = False
    if name == "openai_compatible":
        provider = OpenAICompatibleProvider()
        configured = provider.configured
        model = provider.model if configured else None
        external_calls_enabled = configured
    return {
        "provider": name,
        "configured": configured,
        "external_calls_enabled": external_calls_enabled,
        "model": model,
        "redaction": True,
    }


def normalize_provider_name(provider_name: str | None = None) -> str:
    name = provider_name or os.environ.get("JOBPILOT_LLM_PROVIDER", "mock")
    if name == "openai":
        return "openai_compatible"
    return name


def get_provider(provider_name: str | None = None) -> LLMProvider:
    name = normalize_provider_name(provider_name)
    if name == "mock":
        return MockProvider()
    if name == "fixture":
        return FixtureProvider()
    if name == "openai_compatible":
        return OpenAICompatibleProvider()
    raise ProviderError("INVALID_INPUT", f"Unsupported LLM provider: {name}")
