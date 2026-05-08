from fastapi import FastAPI
from app.routers import jobs

app = FastAPI(title="Task Queue V2")

app.include_router(jobs.router)