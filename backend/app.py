from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import torch
import os

app = Flask(__name__)

# Configure CORS to handle browser extension requests
def integrateCORS():
    print("Isolated component so CORS disabled")


integrateCORS()

# Global variables to store model and data
model = None
data = None
doc_embeddings = None
keys = None

def load_model_and_data():
    """Load the model and data on startup"""
    global model, data, doc_embeddings, keys
    
    try:
        # Load the sentence transformer model
        model_path = os.path.join(os.path.dirname(__file__), 'my_model_dir')
        model = SentenceTransformer(model_path)
        
        # Load the JSON data
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'output.json')
        with open(data_path, "r") as file:
            data = json.load(file)
        
        # Load precomputed embeddings
        embeddings_path = os.path.join(os.path.dirname(__file__), 'data', 'doc_embeddings.npy')
        doc_embeddings_np = np.load(embeddings_path)
        doc_embeddings = torch.tensor(doc_embeddings_np)
        
        # Get all keys
        keys = list(data.keys())
        
        print(f"✅ Model and data loaded successfully!")
        print(f"📊 Loaded {len(keys)} documents")
        print(f"🤖 Model: {model}")
        
    except Exception as e:
        print(f"❌ Error loading model and data: {e}")
        raise e

def search_documents(query, top_k=6):
    """Search for similar documents based on the query"""
    if not all([model, data, doc_embeddings.all(), keys]):
        return {"error": "Model or data not loaded"}
    
    try:
        # Encode the query
        query_embedding = model.encode(query, convert_to_tensor=True)
        
        # Calculate cosine similarities
        cos_scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)
        
        # Get top k results
        top_scores, top_indices = torch.topk(cos_scores, k=min(top_k, len(keys)))
        
        # Flatten scores for easier access
        cos_scores = cos_scores.flatten()
        
        # Prepare results
        results = []
        for idx in top_indices[0]:
            key = keys[idx]
            similarity = float(cos_scores[idx])
            content = data[key]
            
            results.append({
                "key": key,
                "similarity": similarity,
                "content": content
            })
        
        return {"results": results, "query": query, "total_results": len(results)}
        
    except Exception as e:
        return {"error": f"Search error: {str(e)}"}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/search', methods=['POST', 'OPTIONS'])
def search():
    """API endpoint for searching documents"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 6)
        
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        results = search_documents(query, top_k)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    is_loaded = all([model, data, doc_embeddings, keys])
    return jsonify({
        "status": "healthy" if is_loaded else "not_ready",
        "model_loaded": model is not None,
        "data_loaded": data is not None,
        "embeddings_loaded": doc_embeddings is not None,
        "total_documents": len(keys) if keys else 0
    })

if __name__ == '__main__':
    print("🚀 Starting Semantic Search Flask Application...")
    
    # Load model and data
    load_model_and_data()
    
    # Run the Flask app
    print("🌐 Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
