
from sentence_transformers import SentenceTransformer, util
import torch


class SearchServiceException(Exception):
    """Custom exception for search service errors"""
    pass


class SearchService:


     # ROOT FUNCTION HERE
    @staticmethod
    def search_documents_and_extract_results(query, top_k, model, data, doc_embeddings, keys):
        """Search for similar documents based on the query"""
        if not all([model, data, doc_embeddings.all(), keys]):
            raise SearchServiceException("model or data not loaded")
        
        try:  
            cos_package = SearchService.query_doc_similarity_scores_UNCHANGED(query, top_k, model, doc_embeddings, keys) #custom function

            cos_scores = cos_package['cos_scores']
            top_indices = cos_package['top_indices']
            
            results = SearchService.create_results_from_scores_UNCHANGED(cos_scores, top_indices, data, keys) #custom function
            
            return {"results": results, "query": query, "total_results": len(results)}
            
        except Exception:
            raise SearchServiceException("error in searching documents and extracting results")
    
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

    
   





