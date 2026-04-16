import json
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.deps import get_current_user, require_role
from backend.schemas import SubmitTestIn
from database.db import get_db
from database.models import Answer, Application, EmployeeProfile, Job, Question, Role, Score, User

router = APIRouter(prefix="/api/tests", tags=["tests"])


@router.get("/job/{job_id}")
def get_test_for_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employee.value))):
    job = db.get(Job, job_id)
    if not job or not job.test:
        raise HTTPException(status_code=404, detail="Test not found")
    questions = job.test.questions[:]
    random.shuffle(questions)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")
    return {
        "test_id": job.test.id,
        "time_limit_seconds": job.test.time_limit_seconds,
        "questions": [
            {"id": q.id, "text": q.text, "question_type": q.question_type, "options": json.loads(q.options_json)} for q in questions
        ],
    }


@router.post("/job/{job_id}/submit")
def submit_test(job_id: int, payload: SubmitTestIn, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employee.value))):
    job = db.get(Job, job_id)
    if not job or not job.test:
        raise HTTPException(status_code=404, detail="Test not found")

    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    app = db.query(Application).filter(Application.job_id == job_id, Application.employee_profile_id == profile.id).first() if profile else None
    if not app:
        raise HTTPException(status_code=400, detail="Apply before submitting test")
    if app.test_submitted_at:
        raise HTTPException(status_code=400, detail="Multiple attempts are not allowed")
    if (datetime.utcnow() - app.applied_at).total_seconds() > job.test.time_limit_seconds:
        raise HTTPException(status_code=400, detail="Test time limit exceeded")

    question_map: dict[int, Question] = {q.id: q for q in job.test.questions}
    correct = 0
    for item in payload.answers:
        question = question_map.get(item.question_id)
        if not question:
            continue
        is_correct = item.selected_answer.strip() == question.correct_answer.strip()
        if is_correct:
            correct += 1
        db.add(Answer(application_id=app.id, question_id=question.id, selected_answer=item.selected_answer, is_correct=is_correct))

    total = max(len(question_map), 1)
    test_score = round((correct / total) * 100, 2)

    required = set((job.required_skills or "").split(","))
    current_skills = set((profile.skills or "").split(",")) if profile else set()
    cv_relevance = round((len(required & current_skills) / max(len(required), 1)) * 100, 2)
    final_score = round((cv_relevance * 0.4) + (test_score * 0.6), 2)

    score = db.query(Score).filter(Score.application_id == app.id).first()
    if not score:
        score = Score(application_id=app.id)
        db.add(score)

    score.cv_relevance = cv_relevance
    score.test_score = test_score
    score.final_score = final_score
    app.test_submitted_at = datetime.utcnow()
    db.commit()
    return {"message": "Test submitted", "cv_relevance": cv_relevance, "test_score": test_score, "final_score": final_score}
