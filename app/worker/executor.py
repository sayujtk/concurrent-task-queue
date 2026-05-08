from datetime import datetime, timedelta
import math
from sqlalchemy.orm import Session
from app.models import Job
from app.worker.handlers import handle_job

def poll_and_execute(session: Session):
    job = (
        session.query(Job)
        .filter(
            Job.status == "PENDING",
            Job.scheduled_at <= datetime.utcnow()
        )
        .order_by(Job.priority.desc(), Job.scheduled_at.asc())
        .with_for_update(skip_locked=True)
        .first()
    )

    if job is None:
        return  # nothing to do

    try:
        job.status = "RUNNING"
        job.started_at = datetime.utcnow()
        session.commit()

        # execute
        handle_job(job)

        job.status = "SUCCESS"
        job.finished_at = datetime.utcnow()
        session.commit()

    except Exception as e:
        session.rollback()
        handle_failure(session, job, e)

def handle_failure(session: Session, job: Job, error: Exception):
    job.attempts += 1
    job.error_message = str(error)

    if job.attempts >= job.max_retries:
        job.status = "FAILED"
        job.finished_at = datetime.utcnow()
    else:
        backoff_seconds = math.pow(2, job.attempts)
        job.status = "PENDING"
        job.scheduled_at = datetime.utcnow() + timedelta(seconds=backoff_seconds)

    session.commit()