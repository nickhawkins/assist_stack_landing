import sqlite3
import uuid
import datetime
import logging
from typing import Optional, Dict, Any
import json
import threading

logger = logging.getLogger(__name__)


class JobDatabase:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _init_db(self):
        """Initialize the database with required tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                display_name TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                error TEXT,
                result TEXT
            )
        """)
        
        conn.commit()
    
    def create_job(self, display_name: str, url: str, category: Optional[str] = None) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())
        now = datetime.datetime.utcnow().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO jobs (job_id, status, display_name, url, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (job_id, "pending", display_name, url, category, now, now))
        
        conn.commit()
        logger.info(f"Created job {job_id} for {display_name}")
        return job_id
    
    def update_job_status(self, job_id: str, status: str, error: Optional[str] = None, result: Optional[str] = None):
        """Update job status"""
        now = datetime.datetime.utcnow().isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE jobs 
            SET status = ?, updated_at = ?, error = ?, result = ?
            WHERE job_id = ?
        """, (status, now, error, result, job_id))
        
        conn.commit()
        logger.info(f"Updated job {job_id} status to {status}")
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def list_jobs(self, limit: int = 100) -> list:
        """List recent jobs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM jobs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]


# Global instance
job_db = JobDatabase()