#!/bin/bash

echo "🚀 Starting Semantic Search Flask Application"
echo "============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first to avoid compatibility issues
echo "⬆️ Upgrading pip..."
pip install --upgrade pip --break-system-packages

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt --break-system-packages

# Check if required files exist
if [ ! -f "my_model_dir/config.json" ]; then
    echo "❌ Error: Model directory 'my_model_dir' not found or incomplete!"
    echo "Please ensure the model files are in the correct location."
    sh setup.sh
fi


echo "✅ All required files found!"
echo ""
echo "🌐 Starting Flask server..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python3 app.py
