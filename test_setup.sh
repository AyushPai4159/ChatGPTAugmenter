#!/bin/bash

# Test setup script for ChatGPT Augmenter
# Run this to test the setup process locally

echo "🧪 Testing ChatGPT Augmenter Setup..."
echo "====================================="

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Please run this script from the root directory of the project"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "📋 Checking Python dependencies..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Test the backend directory
cd backend

echo "🔍 Checking data files..."
if [ -f "data/conversations.json" ]; then
    echo "✅ conversations.json found ($(wc -l < data/conversations.json) lines)"
else
    echo "❌ conversations.json not found!"
    exit 1
fi

echo "🧹 Cleaning up any existing setup..."
cd bashFiles
if sh delete.sh; then
    echo "✅ Cleanup completed"
else
    echo "⚠️ Cleanup had issues (may be normal)"
fi

echo "📥 Running setup scripts..."
if sh load.sh; then
    echo "✅ Setup scripts completed successfully"
else
    echo "❌ Setup scripts failed!"
    exit 1
fi

cd ..

echo "🔍 Checking if model was created..."
if [ -f "my_model_dir/config.json" ]; then
    echo "✅ Model directory created successfully!"
    echo "📄 Model config:"
    head -10 my_model_dir/config.json
else
    echo "❌ Model directory not created or missing config.json"
    echo "Contents of backend directory:"
    ls -la
    if [ -d "my_model_dir" ]; then
        echo "Contents of my_model_dir:"
        ls -la my_model_dir/
    fi
    exit 1
fi

echo "🔍 Checking if embeddings were created..."
if [ -f "data/doc_embeddings.npy" ]; then
    echo "✅ Document embeddings created successfully!"
    echo "📊 Embeddings file size: $(ls -lh data/doc_embeddings.npy | awk '{print $5}')"
else
    echo "❌ Document embeddings not created"
    exit 1
fi

echo ""
echo "🎉 Setup test completed successfully!"
echo "Your setup is working correctly and should work in Docker too."
