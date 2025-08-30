from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import torch
import os
from routes.search import SearchService, SearchServiceException
from routes.extract import ExtractService, ExtractServiceException
from routes.health import HealthService, HealthServiceException
from routes.delete import DeleteService, DeleteServiceException
app = Flask(__name__)



"""-------------------------------------------------------------------------------------------------------"""

"""GLOBAL VARIABLES"""


# Global variables to store model and data
model = None

"""-------------------------------------------------------------------------------------------------------"""

"""FRONTEND INTEGRATION FUNCTIONS"""



# Configure CORS to handle browser extension requests



def integrateCORS():
    # More permissive CORS for development
    CORS(app, origins=["*"], supports_credentials=True)
    print("CORS is enabled for React app and browser extensions")


def load_model_and_data():
    """Load the model and data on startup"""
    global model
    
    try:
        # Load the sentence transformer model
        model_path = os.path.join(os.path.dirname(__file__), 'my_model_dir')
        model = SentenceTransformer(model_path, device='cpu')
        
        print(f"🤖 Model: {model}")
        print(f"🖥️  Model device: CPU (forced)")
        
    except Exception as e:
        print(f"❌ Error loading model and data: {e}")
        raise e


integrateCORS()

load_model_and_data()




"""-------------------------------------------------------------------------------------------------------"""

"""EXTRACT SERVICES"""



def extractJsonParameters(data) -> dict:
    # Extract UUID and conversation data from request
    user_uuid = data.get('uuid')
    conversations_data = data.get('data')
    # Validate required fields
    if not user_uuid:
        raise ExtractServiceException("UUID is required")
    if not conversations_data:
        raise ExtractServiceException("Conversation data is required")
    
    return {"user_uuid" : user_uuid, "conversations_data" : conversations_data}








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

    if not model:
        load_model_and_data()
    
    try:
        extract = extractJsonParameters(request.get_json())
        # Use the extract service to process the data
        result = ExtractService.extract_service(extract['conversations_data'], extract['user_uuid'], model)
        return jsonify(result)
        
    except ExtractServiceException as e:
        # Handle extract service specific exceptions
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"Server error: {str(e)}"}), 500








"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""

"""SEARCH SERVICES"""


def searchJsonParameters(data) -> dict:
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

    if not model:
        load_model_and_data()
    
    try:
        
        search = searchJsonParameters(request.get_json()) #custom function
        uuid = search['uuid']
        query = search['query'] 
        top_k = 6
        results = SearchService.search_documents_and_extract_results(uuid, query, top_k, model) # backend/routes/search.py
        
        return jsonify(results)
        
    except SearchServiceException as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""

"""DELETE SERVICES"""

@app.route('/delete/<uuid>', methods=['DELETE', 'OPTIONS'])
def delete_user_data(uuid):
    """API endpoint for deleting user data by UUID"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        return response

    # Validate UUID parameter
    if not uuid or uuid.strip() == '':
        return jsonify({"error": "UUID is required", "status": "error"}), 400
    
    try:
        
        # Use the delete service
        delete_result = DeleteService.delete_service(uuid)
        return jsonify(delete_result)
        
    except DeleteServiceException as e:
        # Handle delete service specific exceptions
        return jsonify({"error": str(e), "status": "error"}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"Delete operation failed: {str(e)}", "status": "error"}), 500



"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""
"""HEALTH SERVICES"""

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_no_uuid():
    """Health check endpoint when no UUID is provided"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    return jsonify({
        "error": "UUID is required. Please provide a UUID in the URL path: /health/<uuid>", 
        "status": "error"
    }), 400

@app.route('/health/<uuid>', methods=['GET', 'OPTIONS'])
def health(uuid):
    """Health check endpoint"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response

    # Validate UUID parameter
    if not uuid or uuid.strip() == '':
        return jsonify({"error": "UUID is required", "status": "error"}), 400
    
    try:
        # Use the health service
        health_status = HealthService.health_service(model, uuid)
        return jsonify(health_status)
        
    except HealthServiceException as e:
        # Handle health service specific exceptions
        return jsonify({"error": str(e), "status": "error"}), 500
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"Health check failed: {str(e)}", "status": "error"}), 500






"""--------------------------------------------------------------------------------------------------------------------------------------------------------"""


"""GENERAL INIT SERVICES and OTHER ROUTES"""












if __name__ == '__main__':
    print("🚀 Starting Semantic Search Flask Application...")
    
    # Load model and data
    load_model_and_data()
    
    # Run the Flask app
    print("🌐 Starting Flask server on http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)
