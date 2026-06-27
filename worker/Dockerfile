FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api
ENV PYTHONPATH=/app

# Run Celery worker against the FastAPI task module
CMD ["celery", "-A", "api.tasks", "worker", "--loglevel=info"]
