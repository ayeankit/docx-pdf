# Bulk Document Conversion Service

A robust, scalable, and asynchronous web service that converts DOCX files to PDF format in bulk. The service handles large batches of files through a clean RESTful API with background processing.

## Architecture Overview

### Core Components

1. **FastAPI Web Service**: Handles HTTP requests and provides RESTful API endpoints
2. **Celery Workers**: Process document conversions asynchronously in the background
3. **Redis**: Message broker for task queuing and result storage
4. **PostgreSQL**: Persistent storage for job metadata and file status tracking
5. **Docker Volumes**: Shared file storage between containers

### Key Architectural Decisions

- **Asynchronous Processing**: Uses Celery with Redis to decouple API requests from long-running conversion tasks
- **Shared Storage**: Docker volumes ensure all containers can access uploaded files and generated outputs
- **Stateless Workers**: Multiple worker instances can process jobs concurrently for horizontal scalability
- **Database-Driven State**: Job and file status stored in PostgreSQL for reliability and consistency
- **LibreOffice Integration**: Uses headless LibreOffice for robust DOCX to PDF conversion

## Features

- ✅ Bulk file upload (up to 1000 files per job)
- ✅ Asynchronous background processing
- ✅ Real-time job status tracking
- ✅ Individual file status monitoring
- ✅ Automatic ZIP archive creation
- ✅ Robust error handling and recovery
- ✅ RESTful API with OpenAPI documentation
- ✅ Containerized deployment with Docker Compose
- ✅ Horizontal scalability support
- ✅ Comprehensive test coverage

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 2GB RAM available for containers

### Running the Service

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd docx-to-pdf-service
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Wait for services to be ready**
   The API will be available at `http://localhost:8000` once all health checks pass.

4. **Access the API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

5. **Monitor workers (optional)**
   - Flower UI: `http://localhost:5555`

### Development Setup

For local development without Docker:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up postgres redis
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Run the API server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Start Celery workers**
   ```bash
   celery -A app.worker worker --loglevel=info
   ```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Submit Conversion Job
```http
POST /api/v1/jobs
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -F "files=@document1.docx" \
  -F "files=@document2.docx" \
  -F "files=@document3.docx"
```

**Response (202 Accepted):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "file_count": 3
}
```

#### 2. Get Job Status
```http
GET /api/v1/jobs/{job_id}
```

**Response (200 OK):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "COMPLETED",
  "created_at": "2023-10-27T10:00:00Z",
  "download_url": "/api/v1/jobs/a1b2c3d4-e5f6-7890-1234-567890abcdef/download",
  "files": [
    {
      "filename": "document1.docx",
      "status": "COMPLETED"
    },
    {
      "filename": "document2.docx",
      "status": "COMPLETED"
    },
    {
      "filename": "document3.docx",
      "status": "FAILED",
      "error_message": "Invalid file format or corrupted DOCX."
    }
  ]
}
```

**Job Status Values:**
- `PENDING`: Job is queued for processing
- `IN_PROGRESS`: Job is currently being processed
- `COMPLETED`: All files processed successfully (or with partial failures)
- `FAILED`: Job failed completely

#### 3. Download Results
```http
GET /api/v1/jobs/{job_id}/download
```

**Response:** ZIP file containing all successfully converted PDF files.

#### 4. Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2023-10-27T10:00:00Z"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/docx_converter` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `52428800` (50MB) |
| `MAX_FILES_PER_JOB` | Maximum files per job | `1000` |

### File Size Limits

- **Maximum file size**: 50MB per file
- **Maximum files per job**: 1000 files
- **Supported formats**: DOCX only

## Error Handling

The service implements comprehensive error handling:

### File-Level Errors
- Invalid file format (non-DOCX files)
- Corrupted DOCX files
- Conversion timeouts (5 minutes per file)
- File size exceeded

### Job-Level Errors
- Too many files in a single job
- Database connection issues
- Storage volume full
- Worker unavailability

### Error Response Format
```json
{
  "detail": "Error description"
}
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/test_main.py -v
```

### Test Coverage
- API endpoint testing
- File upload validation
- Job status tracking
- Error handling scenarios

## Monitoring and Observability

### Flower Dashboard
Monitor Celery workers and tasks at `http://localhost:5555`

### Health Checks
- API health: `GET /health`
- Database connectivity: Automatic in Docker Compose
- Redis connectivity: Automatic in Docker Compose

### Logs
```bash
# View API logs
docker-compose logs api

# View worker logs
docker-compose logs worker

# Follow logs in real-time
docker-compose logs -f
```

## Scaling and Production Considerations

### Horizontal Scaling
```yaml
# Scale workers
docker-compose up --scale worker=4

# Scale API instances (requires load balancer)
docker-compose up --scale api=2
```

### Production Deployment
1. Use managed databases (AWS RDS, Google Cloud SQL)
2. Use managed Redis (AWS ElastiCache, Redis Cloud)
3. Implement proper logging and monitoring
4. Set up SSL/TLS termination
5. Configure resource limits and health checks
6. Use persistent volumes for file storage

### Performance Tuning
- Adjust Celery worker concurrency based on CPU cores
- Optimize LibreOffice conversion parameters
- Implement file cleanup policies
- Monitor disk space usage

## Security Considerations

- File type validation prevents malicious uploads
- File size limits prevent DoS attacks
- Temporary file cleanup prevents disk exhaustion
- Database parameterized queries prevent SQL injection
- No file execution - only conversion through LibreOffice

## Troubleshooting

### Common Issues

1. **"Job not found" errors**
   - Verify job_id format (must be valid UUID)
   - Check database connectivity

2. **Conversion failures**
   - Ensure DOCX files are not corrupted
   - Check LibreOffice installation in worker containers
   - Verify file permissions on shared volumes

3. **Worker not processing jobs**
   - Check Redis connectivity
   - Verify Celery worker logs
   - Ensure shared volumes are mounted correctly

4. **Download failures**
   - Verify job status is COMPLETED
   - Check archive file exists in storage
   - Ensure proper file permissions

### Debug Commands
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 worker

# Access container shell
docker-compose exec api bash

# Check Redis queue
docker-compose exec redis redis-cli monitor
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.# docx-pdf
