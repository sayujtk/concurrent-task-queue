from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class JobCreate(BaseModel):
    type: str = "default"
    payload: dict = {}


class JobResponse(BaseModel):
    id: int
    type: str
    payload: dict
    status: str
    priority: int
    attempts: int
    max_retries: int
    scheduled_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    jobs: List[JobResponse]


class StatsResponse(BaseModel):
    pending_count: int
    running_count: int
    success_count: int
    failed_count: int
    avg_duration_seconds: float