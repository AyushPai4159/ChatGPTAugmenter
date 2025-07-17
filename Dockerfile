# Use official Python base image
FROM python:3.11-slim

# Create and set working directory
WORKDIR /app

# Install system dependencies (required for some ML packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy frontend extension code for reference (optional)
COPY extension/ ./extension/

# Set working directory to backend code
WORKDIR /app/backend

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
