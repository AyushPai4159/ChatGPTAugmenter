# Semantic Search Flask Application

A beautiful web application that provides semantic search functionality using SentenceTransformers. This Flask app converts your existing `sentenceTransform.py` script into a user-friendly web interface.

## 🌟 Features

- **Beautiful UI**: Modern, responsive design with glassmorphism effects
- **Real-time Search**: Fast semantic search with similarity scoring
- **Configurable Results**: Choose how many results to display (3, 5, 10, or 20)
- **Health Monitoring**: Built-in health check endpoint
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

## 📋 Prerequisites

Make sure you have the following files in your directory:
- `my_model_dir/` - Your trained SentenceTransformer model
- `data/output.json` - Your document data
- `data/doc_embeddings.npy` - Precomputed document embeddings

## 🚀 Quick Start

### Option 1: Using the startup script (Recommended)
```bash
./run_flask.sh
```

### Option 2: Manual setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 🌐 Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Enter your search query in the search box
3. Select the number of results you want (3, 5, 10, or 20)
4. Click "🔍 Search" to find similar documents
5. View results with similarity scores and content

## 📁 File Structure

```
testFolder/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html         # Web interface template
├── requirements.txt       # Python dependencies
├── run_flask.sh          # Startup script
├── my_model_dir/         # SentenceTransformer model
├── data/
│   ├── output.json       # Document data
│   └── doc_embeddings.npy # Precomputed embeddings
└── pythonFiles/
    └── sentenceTransform.py # Original script
```

## 🔧 API Endpoints

- `GET /` - Main web interface
- `POST /search` - Search endpoint (JSON API)
- `GET /health` - Health check endpoint

### Search API Example

```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query", "top_k": 5}'
```

## 🎨 Features

- **Semantic Search**: Uses AI to understand the meaning behind your queries
- **Similarity Scoring**: Shows how closely each result matches your query
- **Real-time Results**: Fast search with loading indicators
- **Beautiful Design**: Modern UI with gradient backgrounds and glassmorphism
- **Responsive Layout**: Works on all device sizes
- **Error Handling**: Graceful error messages and validation

## 🛠️ Customization

You can customize the application by:
- Modifying the CSS in `templates/index.html` for different styling
- Adjusting the search parameters in `app.py`
- Adding new API endpoints for additional functionality
- Changing the default number of results or adding more options

## 📊 Performance

The application loads the model and embeddings once at startup for optimal performance. Subsequent searches are very fast as they only need to:
1. Encode the query
2. Calculate cosine similarities
3. Return the top results

## 🐛 Troubleshooting

**Model not found error**:
- Ensure `my_model_dir/` contains your SentenceTransformer model files

**Data not found error**:
- Verify `data/output.json` and `data/doc_embeddings.npy` exist

**Port already in use**:
- Change the port in `app.py`: `app.run(port=5001)`

**Memory issues**:
- The application loads everything into memory for speed. For large datasets, consider implementing lazy loading.

## 📝 License

This application is built on top of your existing semantic search functionality and can be used according to your project's licensing terms.
