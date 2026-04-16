import json
import random
import re
from typing import Any
from backend.config import get_settings


def _normalize_skills(skills: list[str] | str) -> list[str]:
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    return [s.lower() for s in skills]


def parse_cv_bytes(file_bytes: bytes) -> dict[str, Any]:
    text = file_bytes.decode("utf-8", errors="ignore")
    words = re.findall(r"[A-Za-z+#.]{2,}", text)
    top_skills = sorted(set(w.lower() for w in words if len(w) < 20))[:20]
    return {"raw_text_excerpt": text[:1000], "skills": top_skills, "summary": "Auto-parsed CV summary"}


def match_jobs(employee_skills: list[str] | str, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = set(_normalize_skills(employee_skills))
    ranked = []
    for job in jobs:
        req = set(_normalize_skills(job.get("required_skills", [])))
        overlap = len(normalized & req)
        total = len(req) if req else 1
        score = round((overlap / total) * 100, 2)
        ranked.append({**job, "relevance": score})
    return sorted(ranked, key=lambda x: x["relevance"], reverse=True)


def generate_quiz(job_title: str, required_skills: list[str] | str, difficulty: str, count: int = 5) -> list[dict[str, Any]]:
    skills = _normalize_skills(required_skills) or [job_title.lower()]
    questions = []
    for i in range(count):
        skill = skills[i % len(skills)]
        options = [
            f"Best practice for {skill}",
            f"Irrelevant approach for {skill}",
            f"Deprecated handling of {skill}",
            f"Unsafe pattern in {skill}",
        ]
        questions.append(
            {
                "text": f"({difficulty}) Which option is most appropriate when working with {skill}?",
                "question_type": "mcq" if i < count - 1 else "coding",
                "options": options,
                "correct_answer": options[0],
            }
        )
    random.shuffle(questions)
    return questions


def maybe_use_openai(prompt: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return "OpenAI key not configured. Using built-in AI fallback."
    return "OpenAI integration point is configured; use your preferred client implementation."
