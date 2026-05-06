from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# Database URL format: dialect+driver://username:password@host:port/database
# This matches the Docker container credentials you set up earlier.
DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/taskqueue"

# Create the database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Keep 10 connections permanently open and ready for our workers
    max_overflow=5,      # Allow up to 5 extra connections if traffic spikes
    pool_pre_ping=True   # Ping the database before executing to ensure the connection hasn't dropped
)

# Create a thread-safe session factory
# scoped_session is CRITICAL here. It guarantees that every single worker thread 
# gets its own isolated database transaction and they don't share/corrupt data.
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Base class that our database models will inherit from
Base = declarative_base()

# FastAPI Dependency to get a database session per API request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()