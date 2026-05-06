from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import schemas

# This single line tells SQLAlchemy to look at models.py and automatically 
# execute the CREATE TABLE SQL commands in Postgres if the table doesn't exist yet!
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Concurrent Task Queue")

@app.post("/jobs", response_model=schemas.JobResponse)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    """
    Endpoint to submit a new job to the queue.
    """
    # 1. Create a Python object of the Job model with the user's payload
    db_job = models.Job(payload=job.payload)
    
    # 2. Add it to the database transaction
    db.add(db_job)
    
    # 3. Commit it to save to Postgres
    db.commit()
    
    # 4. Refresh to get the auto-generated ID and created_at timestamps
    db.refresh(db_job) 
    
    return db_job

@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to check the status of a specific job.
    """
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return db_job