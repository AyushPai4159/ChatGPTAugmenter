#!/bin/bash

# Startup script for ChatGPT Augmenter
# Can be used both in Docker and local development

echo "🚀 Starting ChatGPT Augmenter..."

# Set environment variables if not already set
export FLASK_APP=${FLASK_APP:-backend/app.py}
export PYTHONPATH=${PYTHONPATH:-$(pwd)}

# Check if we're in Docker (production mode)
if [ "$FLASK_ENV" = "production" ]; then
    echo "🐳 Running in Docker production mode"
    
    # Start Flask backend
    echo "🔧 Starting Flask backend on port 5000..."
    cd backend && python app.py &
    FLASK_PID=$!
    
    # Wait for Flask to start
    echo "⏳ Waiting for Flask backend to start..."
    sleep 5
    
    # Serve React frontend using Python's built-in server
    echo "🌐 Starting React frontend on port 3000..."
    cd ../frontend/build && python -m http.server 3000 &
    REACT_PID=$!
    
    # Function to cleanup on exit
    cleanup() {
        echo "🛑 Shutting down services..."
        kill $FLASK_PID $REACT_PID 2>/dev/null
        exit 0
    }
    
    # Set up signal handlers
    trap cleanup SIGTERM SIGINT
    
    echo "✅ Services started successfully!"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend:  http://localhost:5000"
    echo "   - Health:   http://localhost:5000/health"
    
    # Wait for processes
    wait
    
else
    echo "💻 Running in development mode"
    
    # In development, just start Flask (React will be started separately)
    echo "🔧 Starting Flask backend in development mode..."
    cd backend && python app.py
fi
