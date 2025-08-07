from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import zipfile
import subprocess
import tempfile
from datetime import datetime

from app.config import settings
from app.database import Job, JobFile, JobStatus, FileStatus

# Create Celery app
celery_app = Celery(
    "docx_converter",
    broker=settings.redis_url,
    backend=settings.redis_url
)

# Database setup for worker
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    return SessionLocal()

@celery_app.task
def process_job(job_id: str):
    """Process a conversion job by converting all DOCX files to PDF"""
    db = get_db_session()
    
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return f"Job {job_id} not found"
        
        # Update job status to IN_PROGRESS
        job.status = JobStatus.IN_PROGRESS
        db.commit()
        
        job_files = db.query(JobFile).filter(JobFile.job_id == job_id).all()
        
        # Create output directory for this job
        job_output_dir = os.path.join(settings.output_dir, job_id)
        os.makedirs(job_output_dir, exist_ok=True)
        
        converted_files = []
        failed_files = 0
        
        for job_file in job_files:
            try:
                # Update file status to IN_PROGRESS
                job_file.status = FileStatus.IN_PROGRESS
                db.commit()
                
                # Convert DOCX to PDF
                pdf_path = convert_docx_to_pdf(job_file.original_path, job_output_dir)
                
                if pdf_path and os.path.exists(pdf_path):
                    job_file.output_path = pdf_path
                    job_file.status = FileStatus.COMPLETED
                    job_file.completed_at = datetime.utcnow()
                    converted_files.append(pdf_path)
                else:
                    job_file.status = FileStatus.FAILED
                    job_file.error_message = "Conversion failed - output file not created"
                    failed_files += 1
                
            except Exception as e:
                job_file.status = FileStatus.FAILED
                job_file.error_message = str(e)
                failed_files += 1
            
            db.commit()
        
        # Create ZIP archive if we have any converted files
        if converted_files:
            archive_path = create_zip_archive(job_id, converted_files)
            job.archive_path = archive_path
        
        # Update job status
        if failed_files == len(job_files):
            job.status = JobStatus.FAILED
        else:
            job.status = JobStatus.COMPLETED
        
        job.completed_at = datetime.utcnow()
        db.commit()
        
        return f"Job {job_id} completed. {len(converted_files)} files converted, {failed_files} failed."
        
    except Exception as e:
        # Mark job as failed
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            db.commit()
        return f"Job {job_id} failed: {str(e)}"
    
    finally:
        db.close()

def convert_docx_to_pdf(docx_path: str, output_dir: str) -> str:
    """Convert a DOCX file to PDF using LibreOffice"""
    try:
        # Get the base filename without extension
        base_name = os.path.splitext(os.path.basename(docx_path))[0]
        pdf_filename = f"{base_name}.pdf"
        
        # Use LibreOffice to convert DOCX to PDF
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            docx_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"LibreOffice conversion failed: {result.stderr}")
        
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        if not os.path.exists(pdf_path):
            raise Exception("PDF file was not created")
        
        return pdf_path
        
    except subprocess.TimeoutExpired:
        raise Exception("Conversion timeout - file may be too large or complex")
    except Exception as e:
        raise Exception(f"Conversion error: {str(e)}")

def create_zip_archive(job_id: str, file_paths: list) -> str:
    """Create a ZIP archive containing all converted PDF files"""
    archive_filename = f"converted_files_{job_id}.zip"
    archive_path = os.path.join(settings.archive_dir, archive_filename)
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if os.path.exists(file_path):
                # Add file to zip with just the filename (not the full path)
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
    
    return archive_path

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)