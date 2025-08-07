import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from io import BytesIO

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_docx_content():
    """Create a minimal DOCX file content for testing"""
    # This is a simplified DOCX structure - in real tests you'd use python-docx
    return b"PK\x03\x04" + b"fake docx content for testing" + b"\x00" * 100

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_submit_job_success(client, sample_docx_content):
    files = [
        ("files", ("test1.docx", BytesIO(sample_docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ("files", ("test2.docx", BytesIO(sample_docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
    ]
    
    response = client.post("/api/v1/jobs", files=files)
    assert response.status_code == 202
    
    data = response.json()
    assert "job_id" in data
    assert data["file_count"] == 2

def test_submit_job_invalid_file_type(client):
    files = [
        ("files", ("test.txt", BytesIO(b"test content"), "text/plain"))
    ]
    
    response = client.post("/api/v1/jobs", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_get_job_status_not_found(client):
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404

def test_get_job_status_invalid_uuid(client):
    response = client.get("/api/v1/jobs/invalid-uuid")
    assert response.status_code == 400

def test_download_job_not_found(client):
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000/download")
    assert response.status_code == 404