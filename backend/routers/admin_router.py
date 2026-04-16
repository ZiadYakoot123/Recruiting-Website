from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from auth.deps import require_role
from database.db import get_db
from database.models import Application, Job, Role, User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), user: User = Depends(require_role(Role.admin.value))):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]


@router.get("/jobs")
def list_jobs_admin(db: Session = Depends(get_db), user: User = Depends(require_role(Role.admin.value))):
    jobs = db.query(Job).all()
    return [{"id": j.id, "title": j.title, "employer_profile_id": j.employer_profile_id} for j in jobs]


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), user: User = Depends(require_role(Role.admin.value))):
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_jobs": db.query(func.count(Job.id)).scalar(),
        "total_applications": db.query(func.count(Application.id)).scalar(),
    }
