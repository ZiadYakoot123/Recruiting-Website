import json
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ai_services.service import match_jobs, parse_cv_bytes
from auth.deps import get_current_user, require_role
from backend.schemas import EmployeeProfileIn, EmployerProfileIn
from database.db import get_db
from database.models import EmployeeProfile, EmployerProfile, Job, Role, User

router = APIRouter(prefix="/api/profiles", tags=["profiles"])
UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _model_to_dict(model_obj):
    if not model_obj:
        return {}
    return {k: v for k, v in model_obj.__dict__.items() if not k.startswith("_")}


@router.get("/me")
def get_me_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == Role.employee.value:
        profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    elif user.role == Role.employer.value:
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user.id).first()
    else:
        return {"user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}
    return {"user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}, "profile": _model_to_dict(profile)}


@router.put("/employee")
def upsert_employee_profile(payload: EmployeeProfileIn, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employee.value))):
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    if not profile:
        profile = EmployeeProfile(user_id=user.id)
        db.add(profile)
    profile.skills = ",".join(dict.fromkeys(payload.skills))
    profile.experience = payload.experience
    profile.education = payload.education
    profile.portfolio_links = json.dumps(payload.portfolio_links)
    db.commit()
    return {"message": "Employee profile saved"}


@router.put("/employer")
def upsert_employer_profile(payload: EmployerProfileIn, db: Session = Depends(get_db), user: User = Depends(require_role(Role.employer.value))):
    profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == user.id).first()
    if not profile:
        profile = EmployerProfile(user_id=user.id, company_name=payload.company_name)
        db.add(profile)
    profile.company_name = payload.company_name
    profile.company_description = payload.company_description
    db.commit()
    return {"message": "Employer profile saved"}


@router.post("/employee/cv")
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(require_role(Role.employee.value))):
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    parsed = parse_cv_bytes(data)
    target = UPLOAD_DIR / f"{user.id}_{file.filename}"
    target.write_bytes(data)

    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    if not profile:
        profile = EmployeeProfile(user_id=user.id)
        db.add(profile)
    profile.cv_filename = str(target)
    profile.cv_parsed = json.dumps(parsed)
    existing_skills = set(s.strip() for s in profile.skills.split(",") if s.strip())
    for skill in parsed.get("skills", [])[:15]:
        existing_skills.add(skill)
    profile.skills = ",".join(sorted(existing_skills))
    db.commit()
    return {"message": "CV uploaded and parsed", "parsed": parsed}


@router.get("/employee/matches")
def get_matches(db: Session = Depends(get_db), user: User = Depends(require_role(Role.employee.value))):
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    jobs = db.query(Job).all()
    job_docs = [
        {"id": j.id, "title": j.title, "description": j.description, "required_skills": j.required_skills.split(",") if j.required_skills else []}
        for j in jobs
    ]
    return {"matches": match_jobs(profile.skills.split(",") if profile.skills else [], job_docs)[:10]}
