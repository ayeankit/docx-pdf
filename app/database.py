from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
import os

from app.config import settings

# Get database URL with fallback
def get_database_url():
    # Check for Railway's DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Railway provides DATABASE_URL, but we need to ensure it's PostgreSQL
        if database_url.startswith("postgres://"):
            # Convert postgres:// to postgresql:// for SQLAlchemy
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    
    # Fallback to settings
    return settings.database_url

# Create engine with proper error handling
def create_database_engine():
    database_url = get_database_url()
    print(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
    return create_engine(database_url)

# Lazy initialization
_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_database_engine()
    return _engine

def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

Base = declarative_base()

class JobStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class FileStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    file_count = Column(Integer, default=0)
    archive_path = Column(String, nullable=True)

class JobFile(Base):
    __tablename__ = "job_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    output_path = Column(String, nullable=True)
    status = Column(Enum(FileStatus), default=FileStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print(f"Database URL: {get_database_url().split('@')[1] if '@' in get_database_url() else 'localhost'}")
        raise