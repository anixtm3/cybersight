import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fail loudly at startup instead of falling back to a guessable default.
    # A silent fallback here is how someone ends up running against the
    # wrong database, or worse, signing JWTs with a default secret elsewhere.
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and fill it in — "
        "do not hardcode a fallback here."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()