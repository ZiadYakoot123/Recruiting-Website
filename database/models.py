from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


class Role(str, Enum):
    employee = "employee"
    employer = "employer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    employee_profile: Mapped["EmployeeProfile"] = relationship(back_populates="user", uselist=False)
    employer_profile: Mapped["EmployerProfile"] = relationship(back_populates="user", uselist=False)


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    skills: Mapped[str] = mapped_column(Text, default="")
    experience: Mapped[str] = mapped_column(Text, default="")
    education: Mapped[str] = mapped_column(Text, default="")
    portfolio_links: Mapped[str] = mapped_column(Text, default="")
    cv_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cv_parsed: Mapped[str] = mapped_column(Text, default="")

    user: Mapped["User"] = relationship(back_populates="employee_profile")
    applications: Mapped[list["Application"]] = relationship(back_populates="employee")


class EmployerProfile(Base):
    __tablename__ = "employer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_description: Mapped[str] = mapped_column(Text, default="")

    user: Mapped["User"] = relationship(back_populates="employer_profile")
    jobs: Mapped[list["Job"]] = relationship(back_populates="employer")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_profile_id: Mapped[int] = mapped_column(ForeignKey("employer_profiles.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[str] = mapped_column(Text, default="")
    experience_level: Mapped[str] = mapped_column(String(100), default="mid")
    difficulty_level: Mapped[str] = mapped_column(String(50), default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    employer: Mapped["EmployerProfile"] = relationship(back_populates="jobs")
    applications: Mapped[list["Application"]] = relationship(back_populates="job")
    test: Mapped["Test"] = relationship(back_populates="job", uselist=False)


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("employee_profile_id", "job_id", name="uq_employee_job"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_profile_id: Mapped[int] = mapped_column(ForeignKey("employee_profiles.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    test_submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    employee: Mapped["EmployeeProfile"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")
    answers: Mapped[list["Answer"]] = relationship(back_populates="application")
    score: Mapped["Score"] = relationship(back_populates="application", uselist=False)


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, default=1800)

    job: Mapped["Job"] = relationship(back_populates="test")
    questions: Mapped[list["Question"]] = relationship(back_populates="test")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), default="mcq")
    options_json: Mapped[str] = mapped_column(Text, default="[]")
    correct_answer: Mapped[str] = mapped_column(Text, default="")

    test: Mapped["Test"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    selected_answer: Mapped[str] = mapped_column(Text, default="")
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    application: Mapped["Application"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="answers")


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), unique=True, index=True)
    cv_relevance: Mapped[float] = mapped_column(Float, default=0.0)
    test_score: Mapped[float] = mapped_column(Float, default=0.0)
    final_score: Mapped[float] = mapped_column(Float, default=0.0)

    application: Mapped["Application"] = relationship(back_populates="score")
