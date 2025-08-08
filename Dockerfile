# Multi-stage Docker build for ChatGPT Augmenter
# Stage 1: Build React app
FROM node:18-alpine as react-builder

# Set working directory for React app
WORKDIR /app/react-app

# Copy package files
COPY react-app/package*.json ./

# Install dependencies
RUN npm install

# Copy React app source
COPY react-app/ ./

# Build React app for production
RUN npm run build

# Stage 2: Production server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Node.js for serve
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    procps \
    libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g serve \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies including gunicorn
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend files
COPY backend/ ./backend/

# Copy built React app from previous stage (only the build folder)
COPY --from=react-builder /app/react-app/build ./frontend/build

# Make backend scripts executable
RUN chmod +x backend/bashFiles/delete.sh && \
    chmod +x backend/bashFiles/load.sh

# Create production startup script
RUN echo '#!/bin/bash\n\
\n\
echo "🐳 Starting ChatGPT Augmenter in Production Mode..."\n\
\n\
# Check if model directory exists (indicates if setup was run before)\n\
if [ ! -d "/app/backend/my_model_dir" ] || [ ! -f "/app/backend/my_model_dir/config.json" ]; then\n\
    echo "🔧 Model directory not found or incomplete. Running initial setup..."\n\
    \n\
    # Ensure we are in the right directory\n\
    cd /app/backend\n\
    \n\
    # Run the setup scripts with error handling\n\
    echo "📦 Running setup scripts..."\n\
    cd bashFiles\n\
    \n\
    echo "🗑️  Running delete.sh..."\n\
    if sh delete.sh; then\n\
        echo "✅ delete.sh completed successfully"\n\
    else\n\
        echo "⚠️  delete.sh had issues (may be normal if files do not exist)"\n\
    fi\n\
    \n\
    echo "📥 Running load.sh..."\n\
    if sh load.sh; then\n\
        echo "✅ load.sh completed successfully"\n\
    else\n\
        echo "❌ load.sh failed!"\n\
        exit 1\n\
    fi\n\
    \n\
    cd ..\n\
    \n\
    # Verify the setup worked\n\
    if [ -f "my_model_dir/config.json" ]; then\n\
        echo "✅ Setup completed successfully! Model config found."\n\
    else\n\
        echo "❌ Setup failed! Model config not found."\n\
        echo "Contents of backend directory:"\n\
        ls -la\n\
        if [ -d "my_model_dir" ]; then\n\
            echo "Contents of my_model_dir:"\n\
            ls -la my_model_dir/\n\
        fi\n\
        exit 1\n\
    fi\n\
else\n\
    echo "🚀 Model directory found with config.json. Skipping setup..."\n\
fi\n\
\n\
# Start React frontend with serve (production static file server)\n\
echo "🌐 Starting React frontend with serve on port 3000..."\n\
cd /app/frontend && serve -s build -l 3000 -n &\n\
FRONTEND_PID=$!\n\
\n\
# Start Flask backend with gunicorn (production WSGI server)\n\
echo "🌐 Starting Flask backend with gunicorn on port 8000..."\n\
cd /app/backend && gunicorn --config gunicorn.conf.py app:app &\n\
BACKEND_PID=$!\n\
\n\
# Wait a bit for both servers to start\n\
sleep 15\n\
\n\
# Check if Flask started successfully\n\
if kill -0 $BACKEND_PID 2>/dev/null; then\n\
    echo "✅ Flask backend is running (PID: $BACKEND_PID)"\n\
else\n\
    echo "❌ Flask backend failed to start!"\n\
    kill $FRONTEND_PID 2>/dev/null\n\
    exit 1\n\
fi\n\
\n\
# Check if React frontend started successfully\n\
if kill -0 $FRONTEND_PID 2>/dev/null; then\n\
    echo "✅ React frontend is running (PID: $FRONTEND_PID)"\n\
else\n\
    echo "❌ React frontend failed to start!"\n\
    kill $BACKEND_PID 2>/dev/null\n\
    exit 1\n\
fi\n\
\n\
# Cleanup function\n\
cleanup() {\n\
    echo "🛑 Shutting down services..."\n\
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null\n\
    exit 0\n\
}\n\
\n\
# Set up signal handlers\n\
trap cleanup SIGTERM SIGINT\n\
\n\
echo "✅ Production services started successfully!"\n\
echo "   - React Frontend (serve): http://localhost:3000"\n\
echo "   - Flask Backend (gunicorn): http://localhost:8000"\n\
echo "   - Health Check: http://localhost:8000/health"\n\
\n\
# Wait for processes\n\
wait' > /app/docker_start.sh && chmod +x /app/docker_start.sh

# Expose ports
EXPOSE 3000 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5m --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Database environment variables (can be overridden at runtime)
ENV DB_HOST=host.docker.internal
ENV DB_PORT=5432
ENV DB_NAME=test
ENV DB_USER=ayushpai
ENV DB_PASSWORD=pai2004

# Start the application
CMD ["/app/docker_start.sh"]

