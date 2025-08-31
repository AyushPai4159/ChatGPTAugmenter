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



# Install system dependencies including cron and sudo
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    ca-certificates \
    cron \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application contents (excluding venv and __pycache__ via .dockerignore)
COPY backend/ ./

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

# Setup crontab for daily data cleanup at 5 AM EST (10 AM UTC)
RUN echo '# Daily data cleanup at 5 AM EST (10 AM UTC)' > /app/cleanup-crontab \
    && echo '0 10 * * * find /app/data -type f -not -name "dummy.txt" -delete 2>/dev/null' >> /app/cleanup-crontab \
    && echo '# Log cleanup completion' >> /app/cleanup-crontab \
    && echo '1 10 * * * echo "$(date): Data cleanup completed" >> /app/cleanup.log' >> /app/cleanup-crontab \
    && chmod 644 /app/cleanup-crontab

# Create startup script that runs both cron and gunicorn
RUN echo '#!/bin/bash' > /app/start.sh \
    && echo 'set -e' >> /app/start.sh \
    && echo '' >> /app/start.sh \
    && echo '# Install crontab as root' >> /app/start.sh \
    && echo 'sudo crontab /app/cleanup-crontab' >> /app/start.sh \
    && echo '' >> /app/start.sh \
    && echo '# Start cron daemon as root' >> /app/start.sh \
    && echo 'sudo service cron start' >> /app/start.sh \
    && echo '' >> /app/start.sh \
    && echo '# Start gunicorn as appuser' >> /app/start.sh \
    && echo 'exec gunicorn --config gunicorn.conf.py app:app' >> /app/start.sh \
    && chmod +x /app/start.sh

# Give appuser sudo access for cron management (needed for container startup)
RUN echo 'appuser ALL=(ALL) NOPASSWD: /usr/sbin/service cron start, /usr/bin/crontab' > /etc/sudoers.d/appuser \
    && chmod 440 /etc/sudoers.d/appuser

# Switch to non-root user
USER appuser

# Expose port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application with cron and gunicorn
CMD ["/app/start.sh"]