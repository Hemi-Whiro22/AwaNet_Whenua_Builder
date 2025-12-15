FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    nodejs \
    npm \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash vscode

# Set working directory
WORKDIR /workspaces

# Install Python tools
RUN pip install --upgrade pip setuptools wheel && \
    pip install \
    fastapi \
    uvicorn \
    pydantic \
    python-dotenv \
    requests \
    pytest \
    pytest-cov

USER vscode
