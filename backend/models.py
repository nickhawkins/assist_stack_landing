from pydantic import BaseModel
from typing import Optional


class CreateHTMLRequest(BaseModel):
    display_name: str
    url: str
    html: str
    category: Optional[str] = None


class CreateURLRequest(BaseModel):
    display_name: str
    url: str
    category: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    display_name: str
    url: str
    category: Optional[str] = None
    created_at: str
    updated_at: str
    error: Optional[str] = None
    result: Optional[str] = None