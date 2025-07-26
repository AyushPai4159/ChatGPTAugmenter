
from routes.search import SearchService, SearchServiceException



class HealthServiceException(Exception):
    """Custom exception for health service errors"""
    pass


class HealthService:

    """--------------------------------------------------------------------------------------------------------------"""
    """MAIN HEALTH FUNCTION"""

    @staticmethod
    def health_service(model, uuid):
        """
        Service function for health check
        
        Args:
            model: The sentence transformer model
            data: The document data
            doc_embeddings: The document embeddings tensor
            keys: List of document keys
            
        Returns:
            dict: Health status
            
        Raises:
            HealthServiceException: If health check fails
        """
        return HealthService.check_health(model, uuid)
    @staticmethod
    def check_health(model, uuid):
        """
        Check the health status of the application
        
        Args:
            model: The sentence transformer model
            data: The document data
            doc_embeddings: The document embeddings tensor
            keys: List of document keys
            
        Returns:
            dict: Health status information
            
        Raises:
            HealthServiceException: If health check fails
        """
        try:
            
            data_dict = SearchService.integrate_database_extraction(uuid)
            data = data_dict['data']
            doc_embeddings = data_dict['doc_embeddings']
            keys = data_dict['keys']

            model_loaded = model is not None
            data_loaded = data is not None
            embeddings_loaded = doc_embeddings is not None
            keys_available = keys is not None and len(keys) > 0
            
            # Determine overall health status
            is_healthy = all([model_loaded, data_loaded, embeddings_loaded, keys_available])
            
            # Get document count safely
            total_documents = len(keys) if keys else 0
            
            return {
                "uuid" : uuid,
                "status": "healthy" if is_healthy else "not_ready",
                "model_loaded": model_loaded,
                "data_loaded": data_loaded,
                "embeddings_loaded": embeddings_loaded,
                "keys_available": keys_available,
                "total_documents": total_documents,
                "ready_for_search": is_healthy
            }
            
        except Exception as e:
            raise HealthServiceException(f"Health check failed: {str(e)}")


