import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/docx_converter")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    
    # Storage paths - use environment variable or default to local paths
    upload_dir: str = os.getenv("UPLOAD_DIR", "./storage/uploads")
    output_dir: str = os.getenv("OUTPUT_DIR", "./storage/outputs")
    archive_dir: str = os.getenv("ARCHIVE_DIR", "./storage/archives")
    
    # File size limits
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_files_per_job: int = 1000
    
    class Config:
        env_file = ".env"

settings = Settings()