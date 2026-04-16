from auth.security import get_password_hash
from database.db import SessionLocal
from database.models import EmployerProfile, EmployeeProfile, Job, User


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Seed skipped: data already exists")
            return

        employer = User(name="Acme HR", email="hr@acme.com", password=get_password_hash("Password123"), role="employer")
        employee = User(name="Jane Candidate", email="jane@example.com", password=get_password_hash("Password123"), role="employee")
        db.add_all([employer, employee])
        db.flush()

        emp_profile = EmployerProfile(user_id=employer.id, company_name="Acme Corp", company_description="Tech company")
        cand_profile = EmployeeProfile(user_id=employee.id, skills="python,fastapi,sql", experience="3 years", education="BS CS")
        db.add_all([emp_profile, cand_profile])
        db.flush()

        db.add(
            Job(
                employer_profile_id=emp_profile.id,
                title="Backend Engineer",
                description="Build scalable APIs",
                required_skills="python,fastapi,postgresql",
                experience_level="mid",
                difficulty_level="medium",
            )
        )
        db.commit()
        print("Sample data inserted")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
