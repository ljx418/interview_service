from __future__ import annotations

import re
from pathlib import Path


TECH_KEYWORDS = {
    "React": ["react", "jsx", "hooks"],
    "TypeScript": ["typescript", "ts"],
    "JavaScript": ["javascript", "js", "es6"],
    "HTML/CSS": ["html", "css", "tailwind", "responsive"],
    "Node.js": ["node", "express", "nestjs"],
    "Python": ["python", "fastapi", "django", "flask"],
    "SQL": ["sql", "postgres", "mysql", "sqlite"],
    "Testing": ["test", "jest", "pytest", "playwright", "unit"],
    "Git": ["git", "github"],
    "API": ["api", "rest", "http"],
}


def extract_text_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".json", ".csv", ".log"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        # P0 keeps parser dependency-light. Text PDFs often reveal enough bytes for a preview;
        # scanned PDFs should be routed to the LLM/parser adapter later.
        return path.read_bytes().decode("utf-8", errors="ignore")
    return path.read_bytes().decode("utf-8", errors="ignore")


def detect_skills(text: str) -> list[str]:
    lower = text.lower()
    found = []
    for skill, aliases in TECH_KEYWORDS.items():
        if any(alias in lower for alias in aliases):
            found.append(skill)
    return found


def compact_lines(text: str, limit: int = 8) -> list[str]:
    lines = [re.sub(r"\s+", " ", line.strip("- *\t ")) for line in text.splitlines()]
    return [line for line in lines if len(line) > 8][:limit]


def infer_project_name(text: str, fallback: str = "User Project") -> str:
    for line in text.splitlines()[:10]:
        cleaned = line.strip("# \t")
        if cleaned and len(cleaned) <= 60 and any(token in cleaned.lower() for token in ["todo", "project", "app", "系统", "项目"]):
            return cleaned
    return fallback


def classify_question(question: str) -> str:
    lower = question.lower()
    if any(word in lower for word in ["technical problem", "难题", "challenge", "解决", "debug"]):
        return "project_deep_dive"
    if any(word in lower for word in ["why", "转行", "motivation", "为什么"]):
        return "transition_motivation"
    if any(word in lower for word in ["react", "javascript", "api", "database", "算法", "技术"]):
        return "technical"
    if any(word in lower for word in ["conflict", "failure", "team", "失败", "冲突"]):
        return "behavioral"
    return "general"

