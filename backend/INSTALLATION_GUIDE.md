# Manual Installation Guide

If you're getting the `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'` error, follow these manual steps:

## Option 1: Try the updated automatic script
```bash
./run_flask.sh
```

## Option 2: Try the alternative script
```bash
./run_flask_alternative.sh
```

## Option 3: Manual step-by-step installation

### Step 1: Clean slate
```bash
# Remove any existing virtual environment
rm -rf venv

# Create fresh virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 2: Upgrade pip first
```bash
pip install --upgrade pip setuptools wheel
```

### Step 3: Install packages individually
```bash
# Install core dependencies
pip install Flask

# Install PyTorch (CPU version for compatibility)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install transformers
pip install transformers

# Install sentence-transformers
pip install sentence-transformers

# Install numpy
pip install numpy
```

### Step 4: Verify installation
```bash
python3 -c "import flask, torch, transformers, sentence_transformers, numpy; print('All packages imported successfully!')"
```

### Step 5: Run the app
```bash
python3 app.py
```

## Common Issues and Solutions

### Issue: `pkgutil.ImpImporter` error
**Solution**: This is usually caused by an old pip version. Always upgrade pip first:
```bash
pip install --upgrade pip setuptools wheel
```

### Issue: PyTorch installation fails
**Solution**: Use the CPU-only version for compatibility:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue: Virtual environment conflicts
**Solution**: Start fresh:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Issue: Permission errors
**Solution**: Make sure you're not using sudo and the scripts are executable:
```bash
chmod +x run_flask.sh
chmod +x run_flask_alternative.sh
```

## System Requirements

- Python 3.8 or higher
- At least 2GB of RAM (for loading the model)
- The required data files:
  - `my_model_dir/` (SentenceTransformer model)
  - `data/output.json` (document data)
  - `data/doc_embeddings.npy` (precomputed embeddings)

## Success Indicators

When everything works correctly, you should see:
```
✅ All required files found!

🌐 Starting Flask server...
📱 Open your browser and go to: http://localhost:5000
⏹️  Press Ctrl+C to stop the server

🚀 Starting Semantic Search Flask Application...
✅ Model and data loaded successfully!
📊 Loaded [number] documents
🤖 Model: SentenceTransformer(...)
🌐 Starting Flask server on http://localhost:5000
```
