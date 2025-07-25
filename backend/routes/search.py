
from sentence_transformers import SentenceTransformer, util
import torch
import json
import base64
import numpy as np
import os


class SearchServiceException(Exception):
    """Custom exception for search service errors"""
    pass


class SearchService:


     # ROOT FUNCTION HERE
    @staticmethod
    def search_documents_and_extract_results(uuid, query, top_k, model):
        """Search for similar documents based on the query"""
        if not all([model, query, uuid]):
            raise SearchServiceException("model, query, or uuid not loaded")
        
        
        database_extraction = SearchService.integrate_database_extraction(uuid, query)  
        cos_package = SearchService.query_doc_similarity_scores_UNCHANGED(query, top_k, model, database_extraction['doc_embeddings'], database_extraction['keys']) #custom function

        cos_scores = cos_package['cos_scores']
        top_indices = cos_package['top_indices']
        
        results = SearchService.create_results_from_scores_UNCHANGED(cos_scores, top_indices, database_extraction['data'], database_extraction['keys']) #custom function
        
        return {"results": results, "query": query, "total_results": len(results)}
            
        

    
    @staticmethod
    def integrate_database_extraction(uuid, query):
        """
        Extract data from userData.json for a specific user UUID
        
        Args:
            uuid (str): User's UUID
            query (str): Search query (for reference)
            
        Returns:
            dict: Dictionary containing embeddings, processed_data, and keys
            
        Raises:
            SearchServiceException: If data extraction fails
        """
        try:
            # Define the file path
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'userData.json')
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise SearchServiceException("userData.json file not found")
            
            # Load the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data_file = json.load(f)
            
            # Check if UUID exists in the data
            if uuid not in user_data_file:
                raise SearchServiceException(f"Data for user UUID {uuid} not found")
            
            user_data = user_data_file[uuid]
            
            # Extract processed_data
            processed_data = user_data['processed_data']
            
            # Extract and decode embeddings from base64
            embeddings_b64 = user_data['embeddings']
            embeddings_bytes = base64.b64decode(embeddings_b64)
            embeddings_np = np.frombuffer(embeddings_bytes, dtype=np.float32)
            
            # Reshape embeddings (assuming 2D: num_docs x embedding_dim)
            num_docs = len(processed_data)
            embedding_dim = len(embeddings_np) // num_docs
            embeddings_np = embeddings_np.reshape(num_docs, embedding_dim)
            
            # Convert to PyTorch tensor
            embeddings = torch.from_numpy(embeddings_np)
            
            # Extract keys from processed_data
            keys = list(processed_data.keys())
            
            return {
                "doc_embeddings": embeddings,
                "data": processed_data,
                "keys": keys
            }
            
        except Exception as e:
            if isinstance(e, SearchServiceException):
                raise
            raise SearchServiceException(f"Database extraction failed: {str(e)}")

    
    @staticmethod
    def query_doc_similarity_scores_UNCHANGED(query, top_k, model, doc_embeddings, keys):

        try:
            # Encode the query
            query_embedding = model.encode(query, convert_to_tensor=True)
            # Calculate cosine similarities
            cos_scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)
            # Get top k results
            top_scores, top_indices = torch.topk(cos_scores, k=min(top_k, len(keys)))
            # Flatten scores for easier access
            cos_scores = cos_scores.flatten()
            return {'cos_scores' : cos_scores, 'top_indices' : top_indices}
        except Exception:
            raise SearchServiceException('error in creating cos_scores')
            

    @staticmethod
    def create_results_from_scores_UNCHANGED(cos_scores, top_indices, data, keys):

        try:
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
            return results
        except Exception:
            raise SearchServiceException('error in preparing results array')

    
   





