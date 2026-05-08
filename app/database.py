import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/taskqueue"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
)

SessionFactory = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()