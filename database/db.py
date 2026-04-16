from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_optional_columns() -> None:
    inspector = inspect(engine)
    if "applications" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("applications")}
    if "test_started_at" not in columns:
        col_type = "TIMESTAMP" if engine.dialect.name == "postgresql" else "DATETIME"
        ddl = f"ALTER TABLE applications ADD COLUMN test_started_at {col_type} NULL"
        with engine.begin() as conn:
            conn.execute(text(ddl))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
