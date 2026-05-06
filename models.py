from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    
    # status can be: PENDING, PROCESSING, COMPLETED, FAILED
    # We add index=True because our workers will constantly query WHERE status = 'PENDING'
    status = Column(String(20), default="PENDING", index=True)
    
    # payload represents the actual work to be done (e.g., "Send email to user@test.com")
    payload = Column(String, nullable=False)
    
    # Audit timestamps: Every senior engineer adds these to track when jobs are created/finished
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 