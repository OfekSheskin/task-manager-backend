import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# A serverless host answers each request in a short-lived process, so a connection
# pool kept in memory is rarely reused and mostly holds slots open on the database.
# There, every request opens its own connection and the provider's pooler does the
# pooling; a long-running server keeps the normal pool with a liveness check, which
# matters against a database that suspends when idle.
engine_options = {"poolclass": NullPool} if os.getenv("VERCEL") else {"pool_pre_ping": True}

engine = create_engine(settings.sqlalchemy_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
