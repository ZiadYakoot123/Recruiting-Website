import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ai_services.service import generate_quiz
from auth.deps import get_current_user, require_role
from backend.schemas import JobIn
from database.db import get_db
from database.models import Application, EmployerProfile, Job, Question, Role, Test, User

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _get_employer_profile(db: Session, user_id: int) -> EmployerProfile:
    profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Employer profile not found")
    return profile


@router.post("")
def create_job(payload: JobIn, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employer.value))):
    employer = _get_employer_profile(db, user.id)
    job = Job(
        employer_profile_id=employer.id,
        title=payload.title,
        description=payload.description,
        required_skills=",".join(dict.fromkeys(payload.required_skills)),
        experience_level=payload.experience_level,
        difficulty_level=payload.difficulty_level,
    )
    db.add(job)
    db.flush()

    test = Test(job_id=job.id, time_limit_seconds=payload.test_time_limit_seconds)
    db.add(test)
    db.flush()

    for q in generate_quiz(job.title, payload.required_skills, payload.difficulty_level, count=6):
        db.add(
            Question(
                test_id=test.id,
                text=q["text"],
                question_type=q["question_type"],
                options_json=json.dumps(q["options"]),
                correct_answer=q["correct_answer"],
            )
        )

    db.commit()
    return {"message": "Job and AI-generated test created", "job_id": job.id, "test_id": test.id}


@router.get("")
def list_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    jobs = db.query(Job).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "description": j.description,
            "required_skills": j.required_skills.split(",") if j.required_skills else [],
            "experience_level": j.experience_level,
            "difficulty_level": j.difficulty_level,
        }
        for j in jobs
    ]


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    j = db.get(Job, job_id)
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": j.id,
        "title": j.title,
        "description": j.description,
        "required_skills": j.required_skills.split(",") if j.required_skills else [],
        "experience_level": j.experience_level,
        "difficulty_level": j.difficulty_level,
        "test_id": j.test.id if j.test else None,
    }


@router.put("/{job_id}")
def update_job(job_id: int, payload: JobIn, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employer.value))):
    employer = _get_employer_profile(db, user.id)
    j = db.get(Job, job_id)
    if not j or j.employer_profile_id != employer.id:
        raise HTTPException(status_code=404, detail="Job not found")
    j.title = payload.title
    j.description = payload.description
    j.required_skills = ",".join(dict.fromkeys(payload.required_skills))
    j.experience_level = payload.experience_level
    j.difficulty_level = payload.difficulty_level
    if j.test:
        j.test.time_limit_seconds = payload.test_time_limit_seconds
    db.commit()
    return {"message": "Job updated"}


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employer.value))):
    employer = _get_employer_profile(db, user.id)
    j = db.get(Job, job_id)
    if not j or j.employer_profile_id != employer.id:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(j)
    db.commit()
    return {"message": "Job deleted"}


@router.post("/{job_id}/apply")
def apply(job_id: int, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employee.value))):
    from database.models import EmployeeProfile

    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Employee profile missing")
    exists = db.query(Application).filter(Application.job_id == job_id, Application.employee_profile_id == profile.id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Already applied")
    app = Application(job_id=job_id, employee_profile_id=profile.id)
    db.add(app)
    db.commit()
    return {"message": "Application submitted", "application_id": app.id}
