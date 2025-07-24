from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import torch
import os
from routes.search import SearchService, SearchServiceException
from routes.health import HealthService, HealthServiceException

app = Flask(__name__)

"""-------------------------------------------------------------------------------------------------------"""

"""FRONTEND INTEGRATION FUNCTIONS"""



# Configure CORS to handle browser extension requests
def integrateCORS():
    print("Isolated component so CORS disabled")


integrateCORS()




"""-------------------------------------------------------------------------------------------------------"""

"""GLOBAL VARIABLES"""


# Global variables to store model and data
model = None
data = None
doc_embeddings = None
keys = None







"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""

"""SEARCH SERVICES"""


def searchExtractJsonParameters() -> list:
    data = request.get_json()
    query = data.get('query', '').strip()
    top_k = data.get('top_k', 6)
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    return {"query": query, "top_k": top_k}





@app.route('/search', methods=['POST', 'OPTIONS'])
def search_documents_and_extract_results():
    """API endpoint for searching documents given user query and returns a top 6 list of the closest queries and their responses"""
   
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        
        extract = searchExtractJsonParameters() #custom function
        query, top_k = extract['query'], 6
        results = SearchService.search_documents_and_extract_results(query, top_k, model, data, doc_embeddings, keys) # backend/routes/search.py
        
        return jsonify(results)
        
    except SearchServiceException as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500





"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""

"""HEALTH SERVICES"""




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
    
    try:
        # Use the health service
        health_status = HealthService.health_service(model, data, doc_embeddings, keys)
        return jsonify(health_status)
        
    except HealthServiceException as e:
        # Handle health service specific exceptions
        return jsonify({"error": str(e), "status": "error"}), 500
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"Health check failed: {str(e)}", "status": "error"}), 500



"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""

"""GENERAL INIT SERVICES and OTHER ROUTES"""



@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')



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






if __name__ == '__main__':
    print("🚀 Starting Semantic Search Flask Application...")
    
    # Load model and data
    load_model_and_data()
    
    # Run the Flask app
    print("🌐 Starting Flask server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
