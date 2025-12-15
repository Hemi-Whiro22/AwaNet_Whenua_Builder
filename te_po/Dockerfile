# Te Pō - Kitenga Whiro Backend
# Māori Intelligence Engine - FastAPI Backend Service
# Runs standalone on Render or any Docker-compatible host

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    libtesseract-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set locale for Māori text support
ENV LANG=mi_NZ.UTF-8 \
    LC_ALL=mi_NZ.UTF-8 \
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire te_po application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/heartbeat || exit 1

# Expose port
EXPOSE 10000

# Run the FastAPI application
CMD ["uvicorn", "te_po.core.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "4"]
