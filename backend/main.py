from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.rate_limit import RateLimitMiddleware
from backend.routers.admin_router import router as admin_router
from backend.routers.auth_router import router as auth_router
from backend.routers.jobs_router import router as jobs_router
from backend.routers.profiles_router import router as profiles_router
from backend.routers.rankings_router import router as rankings_router
from backend.routers.tests_router import router as tests_router
from database.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Recruitment Platform", version="1.0.0")
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(jobs_router)
app.include_router(tests_router)
app.include_router(rankings_router)
app.include_router(admin_router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "ai-recruitment-platform"}
