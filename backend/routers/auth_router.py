from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.security import create_access_token, get_password_hash, verify_password
from backend.schemas import LoginIn, RegisterIn, TokenOut
from database.db import get_db
from database.models import EmployerProfile, EmployeeProfile, Role, User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    role = payload.role.lower().strip()
    if role not in {Role.employee.value, Role.employer.value}:
        raise HTTPException(status_code=400, detail="Role must be employee or employer")

    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(name=payload.name.strip(), email=payload.email.lower(), password=get_password_hash(payload.password), role=role)
    db.add(user)
    db.flush()

    if role == Role.employee.value:
        db.add(EmployeeProfile(user_id=user.id))
    elif role == Role.employer.value:
        db.add(EmployerProfile(user_id=user.id, company_name=f"{payload.name}'s Company"))

    db.commit()
    return TokenOut(access_token=create_access_token(str(user.id)))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(str(user.id)))
