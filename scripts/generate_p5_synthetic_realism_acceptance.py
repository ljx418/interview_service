#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_p5_real_data_acceptance import DEFAULT_OUTPUT_DIR, DEFAULT_REPORT, scenario_for, text_quality
from services.tools.core import extract_text_from_path


PERSONAS = {
    "ops_to_frontend": {
        "label": "运营数据分析转前端",
        "dir": ROOT / "examples/p5_synthetic_personas/ops_to_frontend",
    },
    "qa_to_fullstack": {
        "label": "手工测试转自动化全栈",
        "dir": ROOT / "examples/p5_synthetic_personas/qa_to_fullstack",
    },
    "teacher_to_edtech": {
        "label": "数学教师转教育科技前端",
        "dir": ROOT / "examples/p5_synthetic_personas/teacher_to_edtech",
    },
}


def build_persona(slug: str, config: dict, base_workspace: Path, scenario_dir: Path) -> dict:
    source_dir = config["dir"]
    resume = source_dir / "resume.md"
    project = source_dir / "project.md"
    jd = source_dir / "jd.md"
    for path in [resume, project, jd, source_dir / "interview_brief.md"]:
        if not path.exists():
            raise SystemExit(f"missing synthetic fixture: {path}")

    metrics = {
        "resume": text_quality(resume, f"{slug} resume", 120),
        "project": text_quality(project, f"{slug} project", 80),
        "jd": text_quality(jd, f"{slug} JD", 40),
    }
    workspace_root = base_workspace / slug
    report = DEFAULT_REPORT.with_name(f"P5_SYNTHETIC_REALISM_ACCEPTANCE_{slug}.html")
    output_dir = DEFAULT_OUTPUT_DIR.with_name(f"p5-synthetic-realism-{slug}-evidence")
    scenario = scenario_for(resume, project, extract_text_from_path(jd), workspace_root, output_dir, report)
    scenario["name"] = f"P5-SYNTHETIC 真实感合成资料闭环验收 - {config['label']}"
    scenario["goal"] = (
        "使用多身份合成资料加强 P5 本地资料闭环验收真实性；"
        "本场景不使用真实个人资料，不代表 P5-REAL 真实个人资料路径通过。"
    )
    scenario["currentImplementation"].insert(0, "资料来源为 examples/p5_synthetic_personas 下的合成简历、合成项目资料和合成 JD。")
    scenario["acceptanceCriteria"].insert(0, "资料必须明确标注为合成，不得在报告中写成真实个人资料验收。")
    scenario["unverifiedScope"].insert(0, "未使用真实个人资料；本场景只能加强自动化真实性，不能替代 P5-REAL。")
    scenario["documentationAudit"].append(
        {
            "area": "合成资料边界",
            "finding": "该 persona 用于覆盖不同背景和目标岗位，不证明真实个人资料路径通过。",
            "status": "pass",
        }
    )
    scenario_path = scenario_dir / f"p5-synthetic-realism-{slug}.scenario.json"
    scenario_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_path.write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "slug": slug,
        "label": config["label"],
        "scenario": scenario_path.as_posix(),
        "report": report.as_posix(),
        "output_dir": output_dir.as_posix(),
        "file_metrics": metrics,
    }


def main() -> int:
    provider = os.environ.get("JOBPILOT_LLM_PROVIDER", "mock").strip().lower() or "mock"
    if provider not in {"mock", "fixture"}:
        raise SystemExit("P5 synthetic realism acceptance requires mock or fixture provider")

    selected = os.environ.get("JOBPILOT_SYNTHETIC_PERSONA", "all").strip()
    if selected == "all":
        slugs = list(PERSONAS)
    elif selected in PERSONAS:
        slugs = [selected]
    else:
        raise SystemExit(f"unknown synthetic persona: {selected}")

    scenario_dir = Path(os.environ.get("JOBPILOT_SYNTHETIC_SCENARIO_DIR", str(ROOT / ".tmp"))).expanduser().resolve()
    base_workspace = Path(os.environ.get("JOBPILOT_SYNTHETIC_WORKSPACE_ROOT", str(ROOT / ".tmp/p5_synthetic_workspaces"))).expanduser().resolve()
    manifest_path = Path(os.environ.get("JOBPILOT_SYNTHETIC_MANIFEST_PATH", str(ROOT / ".tmp/p5-synthetic-realism.manifest.json"))).expanduser().resolve()

    personas = [build_persona(slug, PERSONAS[slug], base_workspace, scenario_dir) for slug in slugs]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "stage": "P5-SYNTHETIC-REALISM",
                "provider": provider,
                "personas": personas,
                "warning": "Synthetic personas only. Do not claim P5-REAL real personal data validation.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"manifest={manifest_path}")
    for item in personas:
        print(f"{item['slug']}={item['scenario']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
