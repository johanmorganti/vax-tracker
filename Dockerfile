FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (better layer caching — only reruns on requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY data/ data/
COPY templates/ templates/
COPY static/ static/

EXPOSE 5002

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "2", "app:create_app()"]
