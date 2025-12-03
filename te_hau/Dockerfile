FROM mcr.microsoft.com/devcontainers/python:1-3.12

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/workspace:/workspace/shared"
WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    git curl wget make locales \
    && locale-gen en_US.UTF-8

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

COPY requirements.txt .
RUN python3 -m venv .venv
RUN /bin/bash -c "source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

CMD ["bash", "-c", "source .venv/bin/activate && uvicorn app:app --host 0.0.0.0 --port 8020"]
