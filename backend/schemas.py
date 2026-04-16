from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmployeeProfileIn(BaseModel):
    skills: list[str] = []
    experience: str = ""
    education: str = ""
    portfolio_links: list[str] = []


class EmployerProfileIn(BaseModel):
    company_name: str
    company_description: str = ""


class JobIn(BaseModel):
    title: str
    description: str
    required_skills: list[str]
    experience_level: str = "mid"
    difficulty_level: str = "medium"
    test_time_limit_seconds: int = Field(default=1800, ge=300, le=7200)


class AnswerIn(BaseModel):
    question_id: int
    selected_answer: str


class SubmitTestIn(BaseModel):
    answers: list[AnswerIn]


class BasicMessage(BaseModel):
    message: str


class RankingOut(BaseModel):
    application_id: int
    employee_name: str
    cv_relevance: float
    test_score: float
    final_score: float
    applied_at: datetime
