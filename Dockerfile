FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ffmpeg \
    wget \
    bash \
    gcc \
    libffi-dev \
    musl-dev \
    make \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip wheel \
    && pip install --no-cache-dir -r requirements.txt

# App source
COPY . .

# Render-required port
EXPOSE 8000

# Start Flask + Telegram bot
CMD bash -c "flask run --host=0.0.0.0 --port=${PORT:-8000} & python3 -m devgagan"