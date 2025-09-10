from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from models import CreateHTMLRequest, CreateURLRequest, JobResponse, JobStatus
from services.background_tasks import create_markdown_task_from_html, create_markdown_task_from_url, sanitize_display_name
from services.job_db import job_db
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Assist Stack API",
    description="API for processing web content with AI",
    version="1.0.0"
)

# Add CORS middleware to allow Chrome extension access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/files/create_html", response_model=JobResponse)
async def create_html(request: CreateHTMLRequest, background_tasks: BackgroundTasks):
    """
    Create a markdown file from provided HTML content.
    
    This endpoint accepts HTML content directly from the Chrome extension,
    bypassing the need to fetch pages with Playwright.
    """
    try:
        # Validate required fields
        if not request.html:
            raise ValueError("No HTML supplied.")
        
        if not request.display_name:
            raise ValueError("Display name is required.")
        
        if not request.url:
            raise ValueError("URL is required.")
        
        # Sanitize display name
        sanitized_name = sanitize_display_name(request.display_name)
        
        # Create job in database
        job_id = job_db.create_job(
            display_name=sanitized_name,
            url=request.url,
            category=request.category
        )
        
        # Start background task to process HTML
        background_tasks.add_task(
            create_markdown_task_from_html,
            job_id=job_id,
            display_name=sanitized_name,
            url=request.url,
            html_content=request.html,
            category=request.category
        )
        
        logger.info(f"Created HTML processing job {job_id} for {sanitized_name}")
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="HTML content received and queued for processing"
        )
        
    except ValueError as e:
        logger.error(f"Validation error in create_html: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_html: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/files/create_url", response_model=JobResponse)
async def create_url(request: CreateURLRequest, background_tasks: BackgroundTasks):
    """
    Create a markdown file from a URL using Playwright (fallback method).
    
    This endpoint is maintained for backward compatibility when HTML is not provided.
    """
    try:
        # Validate required fields
        if not request.display_name:
            raise ValueError("Display name is required.")
        
        if not request.url:
            raise ValueError("URL is required.")
        
        # Sanitize display name
        sanitized_name = sanitize_display_name(request.display_name)
        
        # Create job in database
        job_id = job_db.create_job(
            display_name=sanitized_name,
            url=request.url,
            category=request.category
        )
        
        # Start background task to fetch URL
        background_tasks.add_task(
            create_markdown_task_from_url,
            job_id=job_id,
            display_name=sanitized_name,
            url=request.url,
            category=request.category
        )
        
        logger.info(f"Created URL processing job {job_id} for {sanitized_name}")
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="URL queued for processing with Playwright"
        )
        
    except ValueError as e:
        logger.error(f"Validation error in create_url: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_url: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a specific job."""
    try:
        job = job_db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatus(**job)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/jobs", response_model=List[JobStatus])
async def list_jobs(limit: int = 100):
    """List recent jobs."""
    try:
        jobs = job_db.list_jobs(limit=limit)
        return [JobStatus(**job) for job in jobs]
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Assist Stack API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")