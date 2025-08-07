FROM python:3.11-slim

# Install system dependencies for document conversion
RUN apt-get update && apt-get install -y \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p /app/storage/uploads /app/storage/outputs /app/storage/archives

# Set permissions
RUN chmod -R 755 /app/storage

# Make startup script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

# Use the startup script
CMD ["/app/start.sh"]