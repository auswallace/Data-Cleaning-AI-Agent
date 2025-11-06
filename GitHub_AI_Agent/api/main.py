"""
FastAPI REST API for Data Cleaning Agent
Provides multiple upload methods: file, URL, paste data
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import pandas as pd
import io
import logging
from pathlib import Path
import uuid
from datetime import datetime

from ..agents.simple_cleaning_agent import SimpleCleaningAgent
from ..config.settings import (
    MAX_FILE_SIZE_BYTES,
    ALLOWED_EXTENSIONS,
    UPLOAD_DIR,
    CLEANED_DIR
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Data Cleaning API",
    description="Autonomous data cleaning with AI agents",
    version="2.0.0"
)

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (in production, use Redis/database)
jobs: Dict[str, Dict[str, Any]] = {}


class PasteDataRequest(BaseModel):
    """Request model for pasted CSV data"""
    data: str
    filename: Optional[str] = "pasted_data.csv"


class URLRequest(BaseModel):
    """Request model for URL-based data"""
    url: HttpUrl


class JobResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str  # pending, processing, completed, failed
    message: str
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None


@app.get("/")
def root():
    """API health check"""
    return {
        "status": "online",
        "service": "AI Data Cleaning API",
        "version": "2.0.0",
        "endpoints": {
            "upload_file": "POST /api/upload",
            "paste_data": "POST /api/paste",
            "from_url": "POST /api/url",
            "job_status": "GET /api/jobs/{job_id}",
            "download": "GET /api/download/{job_id}"
        }
    }


@app.post("/api/upload", response_model=JobResponse)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload a file for cleaning

    Supports: CSV, Excel (.xlsx, .xls), Parquet, JSON
    Max size: configured in settings
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_FILE_SIZE_BYTES / 1024 / 1024} MB"
        )

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "filename": file.filename,
        "created_at": datetime.now().isoformat()
    }

    # Process in background
    background_tasks.add_task(process_dataframe, job_id, content, file_ext)

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"File {file.filename} uploaded successfully. Processing started."
    )


@app.post("/api/paste", response_model=JobResponse)
async def paste_data(
    request: PasteDataRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Paste CSV data directly (copy-paste from Excel, Google Sheets, etc.)
    """
    if not request.data.strip():
        raise HTTPException(status_code=400, detail="No data provided")

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "filename": request.filename,
        "created_at": datetime.now().isoformat()
    }

    # Process in background
    background_tasks.add_task(process_pasted_data, job_id, request.data)

    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Pasted data received. Processing started."
    )


@app.post("/api/url", response_model=JobResponse)
async def from_url(
    request: URLRequest,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Load data from a URL (supports CSV, Excel, JSON, Parquet)
    """
    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "url": str(request.url),
        "created_at": datetime.now().isoformat()
    }

    # Process in background
    background_tasks.add_task(process_url, job_id, str(request.url))

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"Loading data from {request.url}. Processing started."
    )


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str):
    """Get status of a cleaning job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobResponse(
        job_id=job_id,
        status=job["status"],
        message=job.get("message", ""),
        progress=job.get("progress"),
        result=job.get("result")
    )


@app.get("/api/download/{job_id}")
def download_cleaned_data(job_id: str):
    """Download cleaned dataset"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    file_path = CLEANED_DIR / f"{job_id}.csv"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Cleaned file not found")

    return FileResponse(
        path=file_path,
        filename=f"cleaned_{job.get('filename', 'data.csv')}",
        media_type="text/csv"
    )


# Background processing functions

async def process_dataframe(job_id: str, content: bytes, file_ext: str):
    """Process uploaded file"""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10

        # Load DataFrame based on file type
        if file_ext == ".csv":
            df = pd.read_csv(io.BytesIO(content))
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(io.BytesIO(content))
        elif file_ext == ".json":
            df = pd.read_json(io.BytesIO(content))
        elif file_ext == ".parquet":
            df = pd.read_parquet(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        jobs[job_id]["progress"] = 30

        # Run agent
        agent = SimpleCleaningAgent(df)
        result = agent.run()

        jobs[job_id]["progress"] = 90

        # Save cleaned data
        output_path = CLEANED_DIR / f"{job_id}.csv"
        result["cleaned_df"].to_csv(output_path, index=False)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = result["report"]
        jobs[job_id]["message"] = "Cleaning completed successfully"

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)


async def process_pasted_data(job_id: str, data: str):
    """Process pasted CSV data"""
    try:
        jobs[job_id]["status"] = "processing"
        df = pd.read_csv(io.StringIO(data))

        # Run agent
        agent = SimpleCleaningAgent(df)
        result = agent.run()

        # Save cleaned data
        output_path = CLEANED_DIR / f"{job_id}.csv"
        result["cleaned_df"].to_csv(output_path, index=False)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result["report"]
        jobs[job_id]["message"] = "Cleaning completed successfully"

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)


async def process_url(job_id: str, url: str):
    """Process data from URL"""
    try:
        jobs[job_id]["status"] = "processing"

        # Determine file type from URL
        if url.endswith(".csv"):
            df = pd.read_csv(url)
        elif url.endswith((".xlsx", ".xls")):
            df = pd.read_excel(url)
        elif url.endswith(".json"):
            df = pd.read_json(url)
        elif url.endswith(".parquet"):
            df = pd.read_parquet(url)
        else:
            # Try CSV as default
            df = pd.read_csv(url)

        # Run agent
        agent = SimpleCleaningAgent(df)
        result = agent.run()

        # Save cleaned data
        output_path = CLEANED_DIR / f"{job_id}.csv"
        result["cleaned_df"].to_csv(output_path, index=False)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result["report"]
        jobs[job_id]["message"] = "Cleaning completed successfully"

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
