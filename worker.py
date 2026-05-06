import time
import threading
from concurrent.futures import ThreadPoolExecutor
from database import SessionLocal
import models

def process_jobs(worker_id: int):
    """
    This function runs continuously in a background thread.
    It constantly looks for PENDING jobs and processes them.
    """
    print(f"Worker {worker_id} started and waiting for jobs...")
    
    # We use a while True loop so the worker stays alive forever
    while True:
        # Every time the loop runs, we open a fresh database session
        db = SessionLocal()
        
        try:
            # THE MAGIC HAPPENS HERE: 
            # We look for 1 PENDING job and lock it, skipping over any rows 
            # that other workers have already locked.
            job = db.query(models.Job)\
                    .filter(models.Job.status == "PENDING")\
                    .with_for_update(skip_locked=True)\
                    .first()

            if not job:
                # If no jobs are available, sleep for 2 seconds to avoid overloading the database
                db.rollback()
                time.sleep(2)
                continue

            # 1. We found a job! Mark it as PROCESSING so others know it's taken
            print(f"[Worker {worker_id}] Picked up Job {job.id} - Payload: {job.payload}")
            job.status = "PROCESSING"
            db.commit()

            # 2. Simulate doing actual hard work (like sending an email or generating a PDF)
            time.sleep(5) 

            # 3. Work is done! Mark it as COMPLETED
            job.status = "COMPLETED"
            db.commit()
            print(f"[Worker {worker_id}] Successfully finished Job {job.id}")

        except Exception as e:
            # If the job crashes, catch the error and mark it as FAILED
            print(f"[Worker {worker_id}] Error processing job: {e}")
            db.rollback()
            if 'job' in locals() and job:
                job.status = "FAILED"
                db.commit()
                
        finally:
            # Always close the session so we don't leak database connections
            db.close()

def start_workers(num_workers: int = 3):
    """
    Spins up multiple worker threads using ThreadPoolExecutor.
    """
    print(f"Starting {num_workers} concurrent workers...")
    
    # ThreadPoolExecutor manages our pool of worker threads automatically
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for i in range(1, num_workers + 1):
            # Submit the process_jobs function to be run in a background thread
            executor.submit(process_jobs, i)

if __name__ == "__main__":
    # When we run `python worker.py`, this block executes
    start_workers(num_workers=3)