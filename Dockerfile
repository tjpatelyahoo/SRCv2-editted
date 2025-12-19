FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ffmpeg \
    python3-pip \
    gcc \
    libffi-dev \
    musl-dev \
    make \
    g++ \
    cmake \
    aria2 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy source
COPY . .

# Install Python deps
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Start app
CMD ["python3", "main.py"]