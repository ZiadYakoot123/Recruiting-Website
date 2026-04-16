# AI Recruitment Platform

Production-ready recruitment web platform connecting employees and employers with AI-assisted CV parsing, job matching, and test generation.

## Project Structure

- `/frontend` – responsive HTML/CSS/JS pages
- `/backend` – FastAPI app and API routers
- `/database` – SQLAlchemy models and DB layer
- `/ai_services` – AI CV parsing, matching, quiz generation services
- `/auth` – JWT auth, password hashing, role guards

## Core Features

- JWT auth with roles: Employee / Employer / Admin
- Employee profile, portfolio, CV upload (PDF-only), AI CV parsing
- Employer company profile and job CRUD
- AI-generated tests per job (MCQ + coding prompt)
- Test engine with timer + single-attempt enforcement
- Scoring: CV relevance + test score => final ranking
- Employer ranking dashboard endpoint
- Admin endpoints for users/jobs/analytics
- Basic rate limiting middleware and input validation

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` from `.env.example` and configure values.
4. Run app:
   ```bash
   uvicorn backend.main:app --reload
   ```
5. Open frontend pages directly from `/frontend` (or serve them with any static web server).

## API Endpoints

- Auth: `POST /api/auth/register`, `POST /api/auth/login`
- Profiles: `GET /api/profiles/me`, `PUT /api/profiles/employee`, `PUT /api/profiles/employer`, `POST /api/profiles/employee/cv`, `GET /api/profiles/employee/matches`
- Jobs: `POST/GET /api/jobs`, `GET/PUT/DELETE /api/jobs/{job_id}`, `POST /api/jobs/{job_id}/apply`
- Tests: `GET /api/tests/job/{job_id}`, `POST /api/tests/job/{job_id}/submit`
- Rankings: `GET /api/rankings/job/{job_id}`
- Admin: `GET /api/admin/users`, `GET /api/admin/jobs`, `GET /api/admin/analytics`

## Sample Data

- SQL sample: `/database/sample_data.sql`
- Seeder script:
  ```bash
  python -m backend.seed
  ```

## Deployment (VPS)

- Use PostgreSQL and set `DATABASE_URL`
- Add Alembic (or equivalent) for schema migrations in production
- Run via `uvicorn` behind `nginx` (or systemd + reverse proxy)
- Restrict CORS origins for production using `CORS_ORIGINS`
- Rotate `SECRET_KEY` and keep `.env` private
