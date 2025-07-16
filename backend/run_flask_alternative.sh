#!/bin/bash

echo "🔧 Alternative Flask Setup Script"
echo "================================="

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "🗑️ Removing existing virtual environment..."
    rm -rf venv
fi

# Create fresh virtual environment
echo "📦 Creating fresh virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and setuptools first
echo "⬆️ Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Install packages one by one to avoid conflicts
echo "📚 Installing Flask..."
pip install Flask

echo "📚 Installing PyTorch..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "📚 Installing transformers..."
pip install transformers

echo "📚 Installing sentence-transformers..."
pip install sentence-transformers

echo "📚 Installing numpy..."
pip install numpy

echo "✅ Installation complete!"

# Check if required files exist
if [ ! -f "my_model_dir/config.json" ]; then
    echo "❌ Error: Model directory 'my_model_dir' not found or incomplete!"
    echo "Please ensure the model files are in the correct location."
    exit 1
fi

if [ ! -f "data/output.json" ]; then
    echo "❌ Error: Data file 'data/output.json' not found!"
    echo "Please ensure the data files are in the correct location."
    exit 1
fi

if [ ! -f "data/doc_embeddings.npy" ]; then
    echo "❌ Error: Embeddings file 'data/doc_embeddings.npy' not found!"
    echo "Please ensure the embeddings file is in the correct location."
    exit 1
fi

echo "✅ All required files found!"
echo ""
echo "🌐 Starting Flask server..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python3 app.py
