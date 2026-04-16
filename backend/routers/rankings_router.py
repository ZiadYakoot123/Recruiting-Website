from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.deps import require_role
from database.db import get_db
from database.models import Application, EmployerProfile, Job, Role, Score, User

router = APIRouter(prefix="/api/rankings", tags=["rankings"])


@router.get("/job/{job_id}")
def get_rankings(job_id: int, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employer.value, Role.admin.value))):
    if user.role == Role.employer.value:
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user.id).first()
        job = db.get(Job, job_id)
        if not profile or not job or job.employer_profile_id != profile.id:
            raise HTTPException(status_code=404, detail="Job not found")

    items = (
        db.query(Application, Score)
        .join(Score, Score.application_id == Application.id)
        .filter(Application.job_id == job_id)
        .order_by(Score.final_score.desc())
        .all()
    )
    return [
        {
            "application_id": app.id,
            "employee_name": app.employee.user.name,
            "cv_relevance": score.cv_relevance,
            "test_score": score.test_score,
            "final_score": score.final_score,
            "applied_at": app.applied_at,
        }
        for app, score in items
    ]
