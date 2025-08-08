# Multi-stage Dockerfile for ChatGPT Augmenter
# Stage 1: Build React frontend
FROM node:18-alpine AS react-builder

# Set working directory for React app
WORKDIR /app/react-app

# Copy package files
COPY react-app/package*.json ./

# Install dependencies
RUN npm install

# Copy React source code
COPY react-app/ ./

# Build the React app for production
RUN npm run build

# Stage 2: Build Flask backend with Python
FROM python:3.11-slim AS backend-base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for backend
WORKDIR /app/backend

# Copy requirements first for better Docker layer caching
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./

# Stage 3: Production stage with both frontend and backend
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app
ENV PORT=80

# Install system dependencies and Node.js for serving React app
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install serve globally for React app
RUN npm install -g serve

# Create app directory
WORKDIR /app

# Copy Python dependencies from backend stage
COPY --from=backend-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-base /usr/local/bin /usr/local/bin

# Copy backend code
COPY --from=backend-base /app/backend ./backend

# Copy built React app from react-builder stage
COPY --from=react-builder /app/react-app/build ./react-app/build

# Create gunicorn configuration
RUN echo 'bind = "0.0.0.0:8000"\n\
workers = 4\n\
worker_class = "sync"\n\
worker_connections = 1000\n\
max_requests = 1000\n\
max_requests_jitter = 100\n\
timeout = 30\n\
keepalive = 2\n\
preload_app = True\n\
accesslog = "-"\n\
errorlog = "-"\n\
loglevel = "info"' > /app/backend/gunicorn.conf.py

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting ChatGPT Augmenter services..."\n\
\n\
# Start React app on port 3000 in background\n\
echo "Starting React frontend on port 3000..."\n\
cd /app/react-app && serve -s build -l 3000 &\n\
REACT_PID=$!\n\
\n\
# Start Flask backend with gunicorn on port 8000\n\
echo "Starting Flask backend on port 8000..."\n\
cd /app/backend && gunicorn --config gunicorn.conf.py app:app &\n\
FLASK_PID=$!\n\
\n\
# Function to handle shutdown\n\
shutdown() {\n\
    echo "Shutting down services..."\n\
    kill $REACT_PID 2>/dev/null || true\n\
    kill $FLASK_PID 2>/dev/null || true\n\
    wait\n\
    exit 0\n\
}\n\
\n\
# Trap signals\n\
trap shutdown SIGTERM SIGINT\n\
\n\
# Wait for both processes\n\
echo "Both services started successfully!"\n\
echo "React frontend: http://localhost:3000"\n\
echo "Flask backend: http://localhost:8000"\n\
\n\
# Keep the container running\n\
wait' > /app/start.sh

# Make startup script executable
RUN chmod +x /app/start.sh

# Create necessary directories
RUN mkdir -p /app/backend/data/conversations

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health && curl -f http://localhost:3000 || exit 1

# Start both services
CMD ["/app/start.sh"]