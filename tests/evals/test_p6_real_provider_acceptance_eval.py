import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/generate_p6_real_provider_acceptance.py"
DEFAULT_REPORT = ROOT / "docs/reports/P6_REAL_PROVIDER_ACCEPTANCE_REPORT.html"
DEFAULT_EVIDENCE = ROOT / "docs/reports/evidence/p6_real_provider_acceptance/p6_real_provider_evidence.json"
FINAL_REPORT = ROOT / "docs/reports/P6_REAL_P7POST_STAGE_ACCEPTANCE_REPORT.html"


def _clean_env() -> dict:
    env = os.environ.copy()
    for key in [
        "JOBPILOT_LLM_PROVIDER",
        "JOBPILOT_OPENAI_API_KEY",
        "JOBPILOT_OPENAI_BASE_URL",
        "JOBPILOT_OPENAI_MODEL",
        "JOBPILOT_OPENAI_PROVIDER_PRESET",
        "JOBPILOT_ENABLE_FAKE_PROVIDER_CHAT",
        "JOBPILOT_FAKE_PROVIDER_CHAT_ERROR",
        "JOBPILOT_ALLOW_REAL_PROVIDER_CHAT",
    ]:
        env.pop(key, None)
    return env


def test_p6_real_provider_gate_only_report_blocks_real_call_and_redacts(tmp_path):
    report = tmp_path / "p6-real.html"
    evidence_dir = tmp_path / "evidence"
    workspace_root = tmp_path / "workspace"
    env = _clean_env()

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--mode",
            "gate-only",
            "--report",
            str(report),
            "--evidence-dir",
            str(evidence_dir),
            "--workspace-root",
            str(workspace_root),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    html = report.read_text(encoding="utf-8")
    evidence = json.loads((evidence_dir / "p6_real_provider_evidence.json").read_text(encoding="utf-8"))

    assert "P6-REAL 真实 Provider 受控验收报告" in html
    assert "真实 provider 未执行" in html
    assert "configured_is_called" in html
    assert evidence["mode"] == "gate-only"
    assert evidence["authorization"]["real_provider_authorized"] is False
    assert evidence["steps"][1]["name"] == "configured_not_called"
    assert evidence["steps"][1]["evidence"]["configured_is_called"] is False
    assert evidence["steps"][2]["evidence"]["provider_invocation_status"] == "consent_required"
    assert evidence["steps"][2]["evidence"]["fallback_used"] is True
    assert evidence["latest_invocation"]["status"] == "policy_denied"
    assert evidence["latest_invocation"]["error_code"] == "CONSENT_REQUIRED"

    serialized = html + json.dumps(evidence, ensure_ascii=False)
    assert "fake-local-key-never-exposed" not in serialized
    assert "sk-" not in serialized
    assert "真实 provider 质量验收通过" not in serialized
    assert "真实个人资料路径已通过" not in serialized


def test_p6_real_provider_real_mode_requires_explicit_env_authorization(tmp_path):
    env = _clean_env()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--mode",
            "real",
            "--report",
            str(tmp_path / "real.html"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--workspace-root",
            str(tmp_path / "workspace"),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "JOBPILOT_ALLOW_REAL_PROVIDER_CHAT=1" in result.stderr
    assert not (tmp_path / "real.html").exists()


def test_p6_real_provider_default_report_exists_and_does_not_overclaim():
    assert DEFAULT_REPORT.exists()
    assert DEFAULT_EVIDENCE.exists()
    html = DEFAULT_REPORT.read_text(encoding="utf-8")
    evidence = json.loads(DEFAULT_EVIDENCE.read_text(encoding="utf-8"))

    assert "P6-REAL 真实 Provider 受控验收报告" in html
    assert evidence["mode"] in {"gate-only", "real"}
    assert "真实 provider 质量验收通过" not in html
    assert "真实个人资料路径已通过" not in html
    assert "fake-local-key-never-exposed" not in html


def test_p6_real_p7post_final_report_summarizes_gate_and_synthetic_boundaries():
    assert FINAL_REPORT.exists()
    html = FINAL_REPORT.read_text(encoding="utf-8")

    assert "P6-REAL / P7-post 阶段自动化验收报告" in html
    assert "P6-REAL 已完成 gate-only 门禁自动化验收" in html
    assert "真实 provider 未授权未执行" in html
    assert "用户场景体验路径截图" in html
    assert "命令结果" in html
    assert "代码检视与文档审计摘要" in html
    assert "P5.5 visual evidence" in html
    assert "p5_5_profile_overview.png" in html
    assert "p5_5_source_refs.png" in html
    assert "p5_5_profile_mobile_390.png" in html
    assert "P7-post synthetic" in html
    assert "P5-REAL" in html
    assert "用户未提供真实资料路径，本轮未读取" in html
    assert "P5_SYNTHETIC_REALISM_ACCEPTANCE_ops_to_frontend.html" in html
    assert "P5_SYNTHETIC_REALISM_ACCEPTANCE_qa_to_fullstack.html" in html
    assert "P5_SYNTHETIC_REALISM_ACCEPTANCE_teacher_to_edtech.html" in html
    assert "真实 provider 质量验收通过" not in html
    assert "真实个人资料路径已通过" not in html
    assert "真实 LLM 接入已通过" not in html
    assert "fake-local-key-never-exposed" not in html
    assert "Bearer " not in html
