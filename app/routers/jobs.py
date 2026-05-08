from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job
from app.schemas import JobCreate, JobResponse, JobListResponse, StatsResponse
from typing import Optional
from sqlalchemy import func


router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(type=job.type, payload=job.payload)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    pending = db.query(Job).filter(Job.status == "PENDING").count()
    running = db.query(Job).filter(Job.status == "RUNNING").count()
    success = db.query(Job).filter(Job.status == "SUCCESS").count()
    failed = db.query(Job).filter(Job.status == "FAILED").count()

    avg_duration = (
        db.query(func.avg(func.extract("epoch", Job.finished_at - Job.started_at)))
        .filter(Job.status == "SUCCESS", Job.started_at.isnot(None), Job.finished_at.isnot(None))
        .scalar()
    )

    return {
        "pending_count": pending,
        "running_count": running,
        "success_count": success,
        "failed_count": failed,
        "avg_duration_seconds": float(avg_duration or 0.0),
    }

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/", response_model=JobListResponse)
def list_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    jobs = query.order_by(Job.created_at.desc()).limit(limit).all()
    return {"jobs": jobs}

