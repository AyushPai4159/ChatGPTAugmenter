# Optimized Dockerfile for Flask backend with React app
# Works with combined repository structure (no separate backend/ directory)

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV FLASK_ENV=production
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app

# Database environment variables (can be overridden at runtime)
ENV DB_HOST=host.docker.internal
ENV DB_PORT=5432
ENV DB_NAME=test
ENV DB_USER=ayushpai
ENV DB_PASSWORD=pai2004

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application contents (excluding venv and __pycache__ via .dockerignore)
COPY . ./

# Remove any accidentally copied venv and __pycache__ directories
RUN find /app -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true \
    && find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /app -type f -name "*.pyc" -delete 2>/dev/null || true

# Create necessary directories and set permissions
RUN mkdir -p /app/data/conversations \
    && chmod -R 755 /app \
    && chown -R appuser:appuser /app

# Run preload script to download and save SentenceTransformer model
RUN cd /app/pythonFiles && python preload.py

# Ensure model directory has correct permissions
RUN chown -R appuser:appuser /app/my_model_dir

# Create gunicorn configuration for port 8080
RUN echo 'bind = "0.0.0.0:8080"' > /app/gunicorn.conf.py \
    && echo 'workers = 1' >> /app/gunicorn.conf.py \
    && echo 'worker_class = "sync"' >> /app/gunicorn.conf.py \
    && echo 'timeout = 30' >> /app/gunicorn.conf.py \
    && echo 'preload_app = True' >> /app/gunicorn.conf.py \
    && echo 'accesslog = "-"' >> /app/gunicorn.conf.py \
    && echo 'errorlog = "-"' >> /app/gunicorn.conf.py

# Switch to non-root user
USER appuser

# Expose port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]