# ---------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------
FROM python:3.13-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building Python packages (e.g. gcc, libpq-dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies to user directory
COPY api/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------
# Stage 2: Final Runtime
# ---------------------------------------------------------------------
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# Install only runtime system dependencies (libpq for Postsgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY api/ /app/api
COPY frontend/ /app/frontend

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]