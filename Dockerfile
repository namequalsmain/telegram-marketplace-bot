# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Don't generate .pyc, flush stdout immediately (good for docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python deps first (better layer caching — only rebuilds on requirements change)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source
COPY . .

# Run as non-root for safety
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Entrypoint: apply migrations, then start the bot
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
