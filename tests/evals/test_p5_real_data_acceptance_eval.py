import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/generate_p5_real_data_acceptance.py"
PLAN = ROOT / "docs/active/stage-reviews/P5_REAL_DATA_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md"
CHECKLIST = ROOT / "docs/active/stage-reviews/P5_HUMAN_EXPERIENCE_REVIEW_CHECKLIST.md"
TODO = ROOT / "TODO.md"


def test_p5_real_data_generator_requires_explicit_paths(tmp_path):
    env = os.environ.copy()
    for key in ["JOBPILOT_REAL_RESUME_PATH", "JOBPILOT_REAL_PROJECT_PATH", "JOBPILOT_REAL_JD_PATH"]:
        env.pop(key, None)
    env["JOBPILOT_LLM_PROVIDER"] = "mock"
    env["JOBPILOT_REAL_SCENARIO_PATH"] = str(tmp_path / "scenario.json")

    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True)

    assert result.returncode != 0
    assert "JOBPILOT_REAL_RESUME_PATH" in result.stderr
    assert not (tmp_path / "scenario.json").exists()


def test_p5_real_data_generator_creates_redacted_mock_only_scenario(tmp_path):
    resume = tmp_path / "resume.md"
    resume.write_text(
        """
# 张三 简历

联系方式：138-0000-0000 / zhangsan@example.com
目标：初级前端开发。
技能：React、TypeScript、Python、FastAPI、pytest。
经历：负责本地求职材料工作台的前端状态机、导出确认门槛和自动化验收。
项目：JobPilot Real Review，支持资料导入、JD 解析、申请包生成和本地导出。
""".strip(),
        encoding="utf-8",
    )
    project = tmp_path / "project.md"
    project.write_text(
        """
# JobPilot Real Review 项目

使用 React、TypeScript、FastAPI、SQLite 和 pytest 搭建本地优先的求职材料闭环。
本人负责资料导入、artifact 版本、blocking confirmation、Markdown/DOCX 导出和多视口截图验收。
""".strip(),
        encoding="utf-8",
    )
    jd = tmp_path / "jd.md"
    jd.write_text(
        """
职位：Junior Frontend Developer
要求：React、TypeScript、Python、API、Testing。
职责：开发前端页面，和 FastAPI 后端协作，重视用户体验、可维护性和本地隐私。
""".strip(),
        encoding="utf-8",
    )
    scenario = tmp_path / "scenario.json"
    manifest = tmp_path / "manifest.json"
    env = os.environ.copy()
    env.update(
        {
            "JOBPILOT_LLM_PROVIDER": "mock",
            "JOBPILOT_REAL_RESUME_PATH": str(resume),
            "JOBPILOT_REAL_PROJECT_PATH": str(project),
            "JOBPILOT_REAL_JD_PATH": str(jd),
            "JOBPILOT_REAL_SCENARIO_PATH": str(scenario),
            "JOBPILOT_REAL_MANIFEST_PATH": str(manifest),
            "JOBPILOT_REAL_WORKSPACE_ROOT": str(tmp_path / "workspace"),
        }
    )

    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    data = json.loads(scenario.read_text(encoding="utf-8"))
    serialized = json.dumps(data, ensure_ascii=False)
    assert data["name"] == "P5-REAL 真实授权资料本地闭环验收"
    assert "acceptance_redaction=summary" in data["url"]
    assert "Enable redacted screenshot mode" in serialized
    assert "Provider guard" in serialized
    assert "P6 opt-in" in serialized
    assert "138-0000-0000" not in serialized
    assert "zhangsan@example.com" not in serialized

    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_data["visibility"] == "redacted_summary"
    assert manifest_data["provider"] == "mock"
    assert manifest_data["file_metrics"]["resume"]["filename"] == "resume.md"
    assert str(resume) not in json.dumps(manifest_data, ensure_ascii=False)


def test_p5_real_data_docs_lock_boundaries_and_p5_5_candidate():
    assert PLAN.exists()
    plan = PLAN.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    todo = TODO.read_text(encoding="utf-8")

    assert "P5-REAL-M0" in plan
    assert "仅脱敏摘要" in plan
    assert "职业画像与能力评估" in plan
    assert "P5.5" in plan
    assert "不得递归扫描" in plan
    assert "真实外部 provider" in plan
    assert "仅脱敏摘要" in checklist
    assert "P5.5-Candidate" in todo
    assert "真实个人资料路径已通过" not in plan
