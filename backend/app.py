from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import torch
import os
from routes.search import SearchService, SearchServiceException
from routes.extract import extract_service, ExtractServiceException
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

"""-------------------------------------------------------------------------------------------------------"""

"""EXTRACT SERVICES"""

@app.route('/extract', methods=['POST', 'OPTIONS'])
def extract():
    """API endpoint for extracting UUID, conversations.json, and creating doc_embeddings to be sent to database"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        request_data = request.get_json()
        
        # Extract UUID and conversation data from request
        user_uuid = request_data.get('uuid')
        conversations_data = request_data.get('data')
        
        # Validate required fields
        if not user_uuid:
            return jsonify({"error": "UUID is required"}), 400
        
        if not conversations_data:
            return jsonify({"error": "Conversation data is required"}), 400
        
        # Use the extract service to process the data
        result = extract_service(conversations_data, user_uuid, model)
        
        return jsonify(result)
        
    except ExtractServiceException as e:
        # Handle extract service specific exceptions
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"Server error: {str(e)}"}), 500








"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""

"""SEARCH SERVICES"""


def searchExtractJsonParameters(data) -> dict:
    query = data.get('query', '').strip()
    uuid = data.get('uuid', '').strip()
    if not query or not uuid:
        raise SearchServiceException("Query and uuid cannot be empty")
    return {"uuid": uuid, "query": query}





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
        
        extract = searchExtractJsonParameters(request.get_json()) #custom function
        uuid = extract['uuid']
        query = extract['query'] 
        top_k = 6
        results = SearchService.search_documents_and_extract_results(uuid, query, top_k, model) # backend/routes/search.py
        
        return jsonify(results)
        
    except SearchServiceException as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



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
