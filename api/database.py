import os
from contextlib import contextmanager
from sqlmodel import create_engine, Session

# Detect environment
IS_CI = os.getenv("GITHUB_ACTIONS") == "true"

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, echo=False)


def get_db_session():
    with Session(engine) as session:
        yield session


db_context = contextmanager(get_db_session)
