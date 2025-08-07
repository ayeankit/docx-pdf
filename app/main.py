from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from app.database import get_db, create_tables, Job, JobFile, JobStatus, FileStatus
from app.models import JobResponse, JobStatusResponse, FileStatusResponse
from app.worker import process_job
from app.config import settings

app = FastAPI(
    title="Bulk Document Conversion Service",
    description="Convert DOCX files to PDF in bulk with asynchronous processing",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    create_tables()
    # Ensure storage directories exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.archive_dir, exist_ok=True)

@app.post("/api/v1/jobs", response_model=JobResponse, status_code=202)
async def submit_job(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit a new conversion job with multiple DOCX files.
    
    - **files**: List of DOCX files to convert
    
    Returns a job_id for tracking the conversion progress.
    """
    if len(files) > settings.max_files_per_job:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum allowed: {settings.max_files_per_job}"
        )
    
    # Validate file types and sizes
    for file in files:
        if not file.filename.lower().endswith('.docx'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Only DOCX files are allowed."
            )
        
        # Check file size (this is approximate as we haven't read the full content yet)
        if hasattr(file, 'size') and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file.filename}. Maximum size: {settings.max_file_size} bytes"
            )
    
    # Create job record
    job = Job(file_count=len(files))
    db.add(job)
    db.commit()
    db.refresh(job)
    
    job_upload_dir = os.path.join(settings.upload_dir, str(job.id))
    os.makedirs(job_upload_dir, exist_ok=True)
    
    # Save uploaded files and create file records
    job_files = []
    for file in files:
        file_path = os.path.join(job_upload_dir, file.filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > settings.max_file_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large: {file.filename}. Maximum size: {settings.max_file_size} bytes"
                )
            buffer.write(content)
        
        # Create file record
        job_file = JobFile(
            job_id=job.id,
            filename=file.filename,
            original_path=file_path
        )
        db.add(job_file)
        job_files.append(job_file)
    
    db.commit()
    
    # Queue the job for processing
    process_job.delay(str(job.id))
    
    return JobResponse(job_id=str(job.id), file_count=len(files))

@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a conversion job.
    
    - **job_id**: The unique identifier of the job
    
    Returns the current status and progress of the job.
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    job = db.query(Job).filter(Job.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_files = db.query(JobFile).filter(JobFile.job_id == job_uuid).all()
    
    files_status = [
        FileStatusResponse(
            filename=jf.filename,
            status=jf.status,
            error_message=jf.error_message
        )
        for jf in job_files
    ]
    
    download_url = None
    if job.status == JobStatus.COMPLETED and job.archive_path:
        download_url = f"/api/v1/jobs/{job_id}/download"
    
    return JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        created_at=job.created_at,
        download_url=download_url,
        files=files_status
    )

@app.get("/api/v1/jobs/{job_id}/download")
async def download_results(job_id: str, db: Session = Depends(get_db)):
    """
    Download the converted files as a ZIP archive.
    
    - **job_id**: The unique identifier of the completed job
    
    Returns the ZIP file containing all converted PDFs.
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    job = db.query(Job).filter(Job.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not completed yet")
    
    if not job.archive_path or not os.path.exists(job.archive_path):
        raise HTTPException(status_code=404, detail="Archive file not found")
    
    return FileResponse(
        job.archive_path,
        media_type="application/zip",
        filename=f"converted_files_{job_id}.zip"
    )

@app.get("/api/v1/jobs/{job_id}/files")
async def list_job_files(job_id: str, db: Session = Depends(get_db)):
    """
    List all files in a job with their download links.
    
    - **job_id**: The unique identifier of the job
    
    Returns a list of files with their status and download URLs.
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    job = db.query(Job).filter(Job.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_files = db.query(JobFile).filter(JobFile.job_id == job_uuid).all()
    
    files_info = []
    for jf in job_files:
        download_url = None
        if jf.status == FileStatus.COMPLETED and jf.output_path:
            download_url = f"/api/v1/jobs/{job_id}/files/{jf.filename}/download"
        
        files_info.append({
            "filename": jf.filename,
            "status": jf.status,
            "error_message": jf.error_message,
            "download_url": download_url
        })
    
    return {
        "job_id": str(job.id),
        "job_status": job.status,
        "files": files_info
    }

@app.get("/api/v1/jobs/{job_id}/files/{filename}/download")
async def download_individual_pdf(job_id: str, filename: str, db: Session = Depends(get_db)):
    """
    Download a specific converted PDF file directly.
    
    - **job_id**: The unique identifier of the job
    - **filename**: The name of the file to download (without .pdf extension)
    
    Returns the individual PDF file.
    """
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    job = db.query(Job).filter(Job.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Find the specific file
    job_file = db.query(JobFile).filter(
        JobFile.job_id == job_uuid,
        JobFile.filename == filename
    ).first()
    
    if not job_file:
        raise HTTPException(status_code=404, detail="File not found in this job")
    
    if job_file.status != FileStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="File conversion is not completed yet")
    
    if not job_file.output_path or not os.path.exists(job_file.output_path):
        raise HTTPException(status_code=404, detail="Converted PDF file not found")
    
    # Get the original filename without extension and add .pdf
    original_name = os.path.splitext(job_file.filename)[0]
    pdf_filename = f"{original_name}.pdf"
    
    return FileResponse(
        job_file.output_path,
        media_type="application/pdf",
        filename=pdf_filename
    )

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI page"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)