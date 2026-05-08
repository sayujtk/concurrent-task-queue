from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(100), nullable=False, default="default")
    payload = Column(JSON, nullable=False, default={})
    status = Column(String(20), nullable=False, default="PENDING")
    priority = Column(Integer, nullable=False, default=0)

    attempts = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)

    scheduled_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())