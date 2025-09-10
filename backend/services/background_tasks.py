import asyncio
import logging
import re
from services.ai_service import ai_service
from services.job_db import job_db

logger = logging.getLogger(__name__)


def sanitize_display_name(display_name: str) -> str:
    """
    Sanitize display name to prevent path traversal and other security issues.
    
    Args:
        display_name: The raw display name from user input
        
    Returns:
        Sanitized display name safe for use in filenames and storage
    """
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', display_name)
    
    # Remove multiple spaces and trim
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Limit length
    sanitized = sanitized[:100]
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "Untitled"
    
    return sanitized


async def create_markdown_task_from_html(job_id: str, display_name: str, url: str, html_content: str, category: str = None):
    """
    Background task to process HTML content and convert it to Markdown using AI.
    
    Args:
        job_id: The job ID to update
        display_name: Display name for the content
        url: Source URL
        html_content: The full HTML content to process
        category: Optional category for the content
    """
    try:
        logger.info(f"Starting markdown creation task for job {job_id}")
        
        # Update job status to processing
        job_db.update_job_status(job_id, "processing")
        
        # Use AI service to convert HTML to Markdown
        markdown_content = ai_service.completion(html_content, url, display_name)
        
        # Update job as completed with result
        job_db.update_job_status(job_id, "completed", result=markdown_content)
        
        logger.info(f"Successfully completed markdown creation for job {job_id}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in markdown creation task for job {job_id}: {error_msg}")
        
        # Update job as failed
        job_db.update_job_status(job_id, "failed", error=error_msg)


async def create_markdown_task_from_url(job_id: str, display_name: str, url: str, category: str = None):
    """
    Background task to fetch URL with Playwright and convert to Markdown using AI.
    This is the fallback method when HTML is not provided.
    
    Args:
        job_id: The job ID to update
        display_name: Display name for the content
        url: URL to fetch
        category: Optional category for the content
    """
    try:
        logger.info(f"Starting URL fetch task for job {job_id}")
        
        # Update job status to processing
        job_db.update_job_status(job_id, "processing")
        
        # TODO: Implement Playwright fetching logic here
        # For now, we'll simulate this with a placeholder
        # This would include:
        # 1. Launch Playwright browser
        # 2. Navigate to URL
        # 3. Wait for page load
        # 4. Get page content
        # 5. Close browser
        
        # Placeholder implementation
        await asyncio.sleep(1)  # Simulate processing time
        
        # For now, just create a simple markdown indicating this is a URL-based fetch
        markdown_content = f"""# {display_name}

**Source:** {url}

*This content was fetched from the URL but Playwright implementation is pending.*

Please use the Chrome extension to collect HTML directly for better results.
"""
        
        # Update job as completed with result
        job_db.update_job_status(job_id, "completed", result=markdown_content)
        
        logger.info(f"Successfully completed URL fetch for job {job_id}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in URL fetch task for job {job_id}: {error_msg}")
        
        # Update job as failed
        job_db.update_job_status(job_id, "failed", error=error_msg)