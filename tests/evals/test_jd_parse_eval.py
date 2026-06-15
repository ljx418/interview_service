from pathlib import Path

from services.storage.workspace import init_workspace
from services.tools import jobpilot


ROOT = Path(__file__).resolve().parents[2]


def test_jd_parse_distinguishes_must_and_nice_to_have(tmp_path):
    workspace = init_workspace("jd-eval", str(tmp_path / "workspace"))
    jd_text = (ROOT / "examples/jds/junior_frontend_jd.md").read_text(encoding="utf-8")

    parsed = jobpilot.parse_jd(workspace["workspace_id"], jd_text)

    assert "React" in parsed["requirements"]["must_have"]
    assert "TypeScript" in parsed["requirements"]["nice_to_have"]
    assert parsed["seniority_guess"] in {"junior", "entry"}
    assert parsed["source_refs"]
