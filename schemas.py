from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Base schema contains fields shared by both creation and responses
class JobBase(BaseModel):
    payload: str

# Schema for incoming JSON data when a user calls POST /jobs
# We only want them to provide the payload. The DB handles ID and Status.
class JobCreate(JobBase):
    pass

# Schema for outgoing JSON data when our API responds to the user
class JobResponse(JobBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    # This config is CRITICAL. It tells Pydantic: 
    # "Hey, you are going to receive a SQLAlchemy Database Model. Don't panic, 
    # just read the attributes off it and convert it into JSON."
    class Config:
        from_attributes = True