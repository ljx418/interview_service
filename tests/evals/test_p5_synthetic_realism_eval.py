import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "examples/p5_synthetic_personas"
SCRIPT = ROOT / "scripts/generate_p5_synthetic_realism_acceptance.py"
AUDIT = ROOT / "docs/active/stage-reviews/P5_SYNTHETIC_REALISM_ACCEPTANCE_AUDIT.md"
TODO = ROOT / "TODO.md"


def test_p5_synthetic_persona_fixtures_are_complete_and_marked_synthetic():
    for slug in ["ops_to_frontend", "qa_to_fullstack", "teacher_to_edtech"]:
        folder = FIXTURE_ROOT / slug
        for filename in ["resume.md", "project.md", "jd.md", "interview_brief.md"]:
            path = folder / filename
            assert path.exists(), f"missing {path}"
            text = path.read_text(encoding="utf-8")
            assert "合成" in text
            assert "不属于真实" in text or "仅用于 JobPilot" in text


def test_p5_synthetic_realism_generator_creates_all_scenarios(tmp_path):
    env = os.environ.copy()
    env["JOBPILOT_LLM_PROVIDER"] = "mock"
    env["JOBPILOT_SYNTHETIC_SCENARIO_DIR"] = str(tmp_path)
    env["JOBPILOT_SYNTHETIC_MANIFEST_PATH"] = str(tmp_path / "manifest.json")
    env["JOBPILOT_SYNTHETIC_WORKSPACE_ROOT"] = str(tmp_path / "workspaces")

    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["stage"] == "P5-SYNTHETIC-REALISM"
    assert len(manifest["personas"]) == 3
    assert "Do not claim P5-REAL" in manifest["warning"]

    for persona in manifest["personas"]:
        scenario_path = Path(persona["scenario"])
        assert scenario_path.exists()
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
        serialized = json.dumps(scenario, ensure_ascii=False)
        assert "P5-SYNTHETIC" in scenario["name"]
        assert "不代表 P5-REAL" in scenario["goal"]
        assert "acceptance_redaction=summary" in scenario["url"]
        assert "真实个人资料路径已通过" not in serialized


def test_p5_synthetic_realism_docs_do_not_replace_p5_real():
    audit = AUDIT.read_text(encoding="utf-8")
    todo = TODO.read_text(encoding="utf-8")

    assert "P5-SYNTHETIC-REALISM" in audit
    assert "不能替代 P5-REAL" in audit
    assert "不得声明真实个人资料路径已通过" in audit
    assert "P5-SYNTHETIC-REALISM" in todo
    assert "不能替代 P5-REAL" in todo
