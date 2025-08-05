from sentence_transformers import SentenceTransformer, util
import torch
import json
import base64
import numpy as np
import os
from database.postgres import DatabaseService, DatabaseServiceException



model = None

class SearchServiceException(Exception):
    """Custom exception for search service errors"""
    pass


class SearchService:
    """--------------------------------------------------------------------------------------------------------------"""
    """MAIN SEARCH FUNCTION"""
    
    @staticmethod
    def search_documents_and_extract_results(uuid, query, top_k, model):
        """
        Main function to search for similar documents based on the query
        
        Args:
            uuid (str): User's UUID
            query (str): Search query
            top_k (int): Number of top results to return
            model: SentenceTransformer model
            
        Returns:
            dict: Search results with similarity scores
            
        Raises:
            SearchServiceException: If search fails
        """
        try:
            # Validate inputs
            if not all([model, query, uuid]):
                raise SearchServiceException("Model, query, or uuid not provided")
            
            # Extract data from database
            database_extraction = SearchService.integrate_extraction(uuid)
            
            # Calculate similarity scores
            cos_package = SearchService.query_doc_similarity_scores_UNCHANGED(
                query, top_k, model, 
                database_extraction['doc_embeddings'], 
                database_extraction['keys']
            )
            
            # Extract scores and indices
            cos_scores = cos_package['cos_scores']
            top_indices = cos_package['top_indices']
            
            # Format results
            results = SearchService.create_results_from_scores_UNCHANGED(
                cos_scores, top_indices, 
                database_extraction['data'], 
                database_extraction['keys']
            )
            
            return {
                "results": results, 
                "query": query, 
                "total_results": len(results)
            }
            
        except Exception as e:
            if isinstance(e, SearchServiceException):
                raise
            raise SearchServiceException(f"Search operation failed: {str(e)}")

    """--------------------------------------------------------------------------------------------------------------"""
    """DATABASE EXTRACTION FUNCTIONS"""
    
    @staticmethod
    def integrate_extraction(uuid):
        """
        Extract data with preserved key ordering from database or JSON file
        
        Args:
            uuid (str): User's UUID
            
        Returns:
            dict: Dictionary containing embeddings, processed_data, and keys in correct order
            
        Raises:
            SearchServiceException: If data extraction fails
        """

        try:
            result = SearchService.integrate_database_extraction(uuid)
            return result
        except(SearchServiceException, ImportError) as db_error:
            print(f"❌ PostgreSQL load failed, falling back to JSON: {db_error}")
        

        try:
            result = SearchService.integrate_file_extraction(uuid) 
            return result
        except SearchServiceException as e:
            raise SearchServiceException(f"Database extraction failed (could be an invalid uuid): {str(e)}")

    
    @staticmethod
    def integrate_database_extraction(uuid):

        try:
            user_data = DatabaseService.load_user_data_from_database(uuid)
            data_source = "PostgreSQL"
            print(f"✅ Loaded data from PostgreSQL database")
            
            # Extract processed_data and key ordering
            processed_data = user_data['processed_data']
            keys = user_data['key_order']
            embeddings_bytes = user_data.get('embeddings')
            embedding_shape = user_data.get('embedding_shape')
            
            embeddings = SearchService.recreate_doc_embeddings_from_database(embeddings_bytes, embedding_shape)
            
            return {
                    "doc_embeddings": embeddings,
                    "data": processed_data,
                    "keys": keys  # Use preserved key ordering
            }
        except SearchServiceException:
            raise
        except DatabaseServiceException as e:
            raise SearchServiceException(e)
        except Exception as e:
            raise SearchServiceException(e)

    
    @staticmethod
    def recreate_doc_embeddings_from_database(embeddings_bytes, embedding_shape):
        #  Convert bytes back to numpy array with proper shape, then to torch tensor
        try:
            print(f"🔄 Loading embeddings from database bytes (shape: {embedding_shape})")
            embeddings_np = np.frombuffer(embeddings_bytes, dtype=np.float32)
            embeddings_np = embeddings_np.reshape(embedding_shape)
            embeddings = torch.from_numpy(embeddings_np.copy())  # Create writable copy
            # Ensure embeddings are on CPU
            embeddings = embeddings.cpu()
            return embeddings
        except Exception as e:
            raise SearchServiceException("recreating doc_embeddings failed, mostly likely a corrupt embedding_bytes or embedding_shape")
        



    @staticmethod
    def integrate_file_extraction(uuid):
        """
        Extract data from JSON file with key ordering preservation
        
        Args:
            uuid (str): User's UUID
            
        Returns:
            dict: Dictionary containing embeddings, processed_data, and keys in correct order
            
        Raises:
            SearchServiceException: If file extraction fails
        """
        # Load user data from JSON file
        try:
            user_data = SearchService.load_user_data_from_file(uuid)
            print(f"✅ Loaded data from JSON file")
            
            # Extract processed_data and key ordering
            if 'processed_data' in user_data:
                processed_data = user_data.get('processed_data')
                # Use explicit key ordering if available, otherwise use dict keys
                keys = user_data.get('key_order', list(processed_data.keys()))
            else:
                # Fallback for old data format
                processed_data = user_data
                keys = list(processed_data.keys())

            if 'keys' in user_data:
                keys = user_data.get('keys')
            else:
                keys = list(processed_data.keys())
            
            # Try to get embeddings from database info first, then fallback to user_data
            embeddings = SearchService.recreate_doc_embeddings_from_file(uuid, user_data)
            
            return {
                "doc_embeddings": embeddings,
                "data": processed_data,
                "keys": keys  # Use preserved key ordering
            }
        except SearchServiceException:
            raise
        except Exception as e:
            raise SearchServiceException(e)

    
    @staticmethod
    def load_user_data_from_file(uuid):
        """
        Load user data from userData.json file
        
        Args:
            uuid (str): User's UUID
            
        Returns:
            dict: User data from JSON file
            
        Raises:
            SearchServiceException: If file loading fails
        """
        try:
            # Define the file path
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data/conversations', f'{uuid}userData.json')
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise SearchServiceException("userData.json file not found, possibly because conversations.json wasn't initially extracted")
            
            # Load the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data_file = json.load(f)
            
            # Check if UUID exists in the data
            if uuid not in user_data_file:
                raise SearchServiceException(f"Data for user UUID {uuid} not found")
            
            return user_data_file[uuid]
            
        except Exception as e:
            if isinstance(e, SearchServiceException):
                raise
            raise SearchServiceException(f"Failed to load user data: {str(e)}")


    @staticmethod
    def recreate_doc_embeddings_from_file(uuid, user_data):
       
        if user_data and 'embeddings' in user_data:
            # Decode from base64 in user_data
            print(f"🔄 Loading embeddings from base64 in user_data")
            embeddings_b64 = user_data['embeddings']
            embeddings_bytes = base64.b64decode(embeddings_b64)
            embeddings_np = np.frombuffer(embeddings_bytes, dtype=np.float32)
            
            # Try to infer shape from processed_data if no explicit shape
            if 'processed_data' in user_data:
                num_docs = len(user_data['processed_data'])
                embedding_dim = len(embeddings_np) // num_docs
                embeddings_np = embeddings_np.reshape(num_docs, embedding_dim)
                print(f"🔄 Inferred embedding shape: ({num_docs}, {embedding_dim})")
            
            embeddings = torch.from_numpy(embeddings_np)
            # Ensure embeddings are on CPU
            embeddings = embeddings.cpu()

            return embeddings
        else:
            print(f"❌ No embeddings found - checked database and user_data")
            raise SearchServiceException(f"No embeddings found in database, file, or user data for UUID {uuid}")

        
    
    # @staticmethod
    # def decode_embeddings_from_base64(embeddings_b64, num_docs):
    #     """
    #     Decode base64 embeddings back to PyTorch tensor
        
    #     Args:
    #         embeddings_b64 (str): Base64 encoded embeddings
    #         num_docs (int): Number of documents for reshaping
            
    #     Returns:
    #         torch.Tensor: Decoded embeddings tensor
            
    #     Raises:
    #         SearchServiceException: If decoding fails
    #     """
    #     try:
    #         # Decode base64 to bytes
    #         embeddings_bytes = base64.b64decode(embeddings_b64)
            
    #         # Convert bytes to numpy array
    #         embeddings_np = np.frombuffer(embeddings_bytes, dtype=np.float32)
            
    #         # Reshape embeddings (assuming 2D: num_docs x embedding_dim)
    #         embedding_dim = len(embeddings_np) // num_docs
    #         embeddings_np = embeddings_np.reshape(num_docs, embedding_dim)
            
    #         # Convert to PyTorch tensor
    #         embeddings = torch.from_numpy(embeddings_np)
            
    #         return embeddings
            
    #     except Exception as e:
    #         raise SearchServiceException(f"Failed to decode embeddings: {str(e)}")

    """--------------------------------------------------------------------------------------------------------------"""
    """SIMILARITY SCORING FUNCTIONS"""
    
    @staticmethod
    def query_doc_similarity_scores_UNCHANGED(query, top_k, model, doc_embeddings, keys):
        """
        Calculate similarity scores between query and documents
        
        Args:
            query (str): Search query
            top_k (int): Number of top results
            model: SentenceTransformer model
            doc_embeddings (torch.Tensor): Document embeddings
            keys (list): Document keys
            
        Returns:
            dict: Similarity scores and top indices
            
        Raises:
            SearchServiceException: If similarity scoring fails
        """
        try:
            # Encode the query
            query_embedding = SearchService.encode_query_to_embedding(query, model)
            
            # Calculate cosine similarities
            cos_scores = SearchService.calculate_cosine_similarities(query_embedding, doc_embeddings)
            
            # Get top k results
            result = SearchService.get_top_k_results(cos_scores, top_k, keys)
            
            return result
            
        except Exception as e:
            if isinstance(e, SearchServiceException):
                raise
            raise SearchServiceException(f"Error in creating similarity scores: {str(e)}")
    
    @staticmethod
    def encode_query_to_embedding(query, model):
        """
        Encode search query to embedding vector
        
        Args:
            query (str): Search query
            model: SentenceTransformer model
            
        Returns:
            torch.Tensor: Query embedding
            
        Raises:
            SearchServiceException: If query encoding fails
        """
        query_embedding = model.encode(query, convert_to_tensor=True)
        # Always ensure the query embedding is on CPU
        query_embedding = query_embedding.cpu()
        return query_embedding
        
            
    
    
    @staticmethod
    def calculate_cosine_similarities(query_embedding, doc_embeddings):
        """
        Calculate cosine similarities between query and documents
        
        Args:
            query_embedding (torch.Tensor): Query embedding
            doc_embeddings (torch.Tensor): Document embeddings
            
        Returns:
            torch.Tensor: Cosine similarity scores
            
        Raises:
            SearchServiceException: If similarity calculation fails
        """
        # Ensure both tensors are on the same device (CPU)
        query_embedding = query_embedding.cpu()
        doc_embeddings = doc_embeddings.cpu()
        
        cos_scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)
        return cos_scores
    
    @staticmethod
    def get_top_k_results(cos_scores, top_k, keys):
        """
        Get top k results from similarity scores
        
        Args:
            cos_scores (torch.Tensor): Cosine similarity scores
            top_k (int): Number of top results to return
            keys (list): Document keys
            
        Returns:
            dict: Top scores and indices
       
        """
        # Get top k results
        top_scores, top_indices = torch.topk(cos_scores, k=min(top_k, len(keys)))
        
        # Flatten scores for easier access
        cos_scores = cos_scores.flatten()
        
        return {'cos_scores': cos_scores, 'top_indices': top_indices}
            
        

    """--------------------------------------------------------------------------------------------------------------"""
    """RESULT FORMATTING FUNCTIONS"""
    
    @staticmethod
    def create_results_from_scores_UNCHANGED(cos_scores, top_indices, data, keys):
        """
        Create formatted results from similarity scores
        
        Args:
            cos_scores (torch.Tensor): Similarity scores
            top_indices (torch.Tensor): Top result indices
            data (dict): Document data
            keys (list): Document keys
            
        Returns:
            list: Formatted search results
            
        Raises:
            SearchServiceException: If result creation fails
        """
        try:
            results = []
            
            for idx in top_indices[0]:
                result = SearchService.format_single_result(idx, cos_scores, keys, data)
                results.append(result)
            
            return results
            
        except Exception as e:
            if isinstance(e, SearchServiceException):
                raise
            raise SearchServiceException(f"Error in preparing results array: {str(e)}")
    
    @staticmethod
    def format_single_result(idx, cos_scores, keys, data):
        """
        Format a single search result
        
        Args:
            idx (int): Document index
            cos_scores (torch.Tensor): Similarity scores
            keys (list): Document keys
            data (dict): Document data
            
        Returns:
            dict: Formatted result
            
        Raises:
            SearchServiceException: If result formatting fails
        """
        try:
            key = keys[idx]
            similarity = float(cos_scores[idx])
            content = data[key]
            
            return {
                "key": key,
                "similarity": similarity,
                "content": content
            }
        except IndexError:
            raise SearchServiceException("idx is out of bounds for keys array given")
            
        









