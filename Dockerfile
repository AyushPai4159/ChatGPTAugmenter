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

# Build React app
RUN npm run build

# Stage 2: Python backend with served React app
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js and PostgreSQL dev libraries
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    procps \
    libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/

# Copy built React app from previous stage
COPY --from=react-builder /app/react-app/build ./frontend/build

# Also copy React source for development server
COPY react-app/ ./react-app/

# Install React dependencies in the final stage
RUN cd react-app && npm install

# Copy startup scripts from root directory
COPY backend.sh frontend.sh ./

# Make scripts executable (including backend bash scripts)
RUN chmod +x backend.sh && \
    chmod +x frontend.sh && \
    chmod +x backend/setup.sh && \
    chmod +x backend/run_flask.sh && \
    chmod +x backend/bashFiles/delete.sh && \
    chmod +x backend/bashFiles/load.sh

# Create a Docker startup script that uses your existing logic but adapted for Docker
RUN echo '#!/bin/bash\n\
\n\
echo "🐳 Starting ChatGPT Augmenter in Docker..."\n\
\n\
# Check if model directory exists (indicates if setup was run before)\n\
if [ ! -d "/app/backend/my_model_dir" ] || [ ! -f "/app/backend/my_model_dir/config.json" ]; then\n\
    echo "🔧 Model directory not found or incomplete. Running initial setup..."\n\
    \n\
    # Ensure we'\''re in the right directory\n\
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
        echo "⚠️  delete.sh had issues (may be normal if files don'\''t exist)"\n\
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
# Start Flask backend\n\
echo "🌐 Starting Flask backend on port 5001..."\n\
cd /app/backend && python app.py &\n\
BACKEND_PID=$!\n\
\n\
# Start React development server\n\
echo "🌐 Starting React development server on port 3000..."\n\
cd /app/react-app && HOST=0.0.0.0 PORT=3000 npm start &\n\
REACT_PID=$!\n\
\n\
# Wait a bit for both servers to start\n\
sleep 10\n\
\n\
# Check if Flask started successfully\n\
if kill -0 $BACKEND_PID 2>/dev/null; then\n\
    echo "✅ Flask process is running (PID: $BACKEND_PID)"\n\
else\n\
    echo "❌ Flask failed to start!"\n\
    kill $REACT_PID 2>/dev/null\n\
    exit 1\n\
fi\n\
\n\
# Check if React started successfully\n\
if kill -0 $REACT_PID 2>/dev/null; then\n\
    echo "✅ React process is running (PID: $REACT_PID)"\n\
else\n\
    echo "❌ React failed to start!"\n\
    kill $BACKEND_PID 2>/dev/null\n\
    exit 1\n\
fi\n\
\n\
# Cleanup function\n\
cleanup() {\n\
    echo "🛑 Shutting down services..."\n\
    kill $BACKEND_PID $REACT_PID 2>/dev/null\n\
    exit 0\n\
}\n\
\n\
# Set up signal handlers\n\
trap cleanup SIGTERM SIGINT\n\
\n\
echo "✅ Services started successfully!"\n\
echo "   - React Dev Server: http://localhost:3000"\n\
echo "   - Flask API: http://localhost:5001"\n\
echo "   - Health Check: http://localhost:5001/health"\n\
\n\
# Wait for process\n\
wait' > /app/docker_start.sh && chmod +x /app/docker_start.sh

# Expose ports
EXPOSE 3000 5001

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5m --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=3000
ENV WATCHPACK_POLLING=true

# Database environment variables (can be overridden at runtime)
ENV DB_HOST=host.docker.internal
ENV DB_PORT=5432
ENV DB_NAME=test
ENV DB_USER=ayushpai
ENV DB_PASSWORD=pai2004

# Start the application
CMD ["/app/docker_start.sh"]

