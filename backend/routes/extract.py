import json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import base64
import os
from database.postgres import DatabaseService, DatabaseServiceException


class ExtractServiceException(Exception):
    """Custom exception for extract service errors"""
    pass


class ExtractService:


    """--------------------------------------------------------------------------------------------------------------"""
    """ROOT FUNCTION"""

    @staticmethod
    def extract_service(conversations_data, user_uuid, model):
        """
        Main service function for extracting and processing conversations
        
        Args:
            conversations_data (list): Raw conversation data
            user_uuid (str): User's UUID
            model: SentenceTransformer model
            
        Returns:
            dict: Processing result with database save confirmation
            
        Raises:
            ExtractServiceException: If any step fails
        """
        try:

            if not model:
                raise ExtractServiceException("Model not available for creating embeddings")
            if not conversations_data:
                raise ExtractServiceException("No conversation data available for processing")
            if not user_uuid:
                raise ExtractServiceException("User UUID is required")


            # Step 1: Process conversations (similar to exportData())
            print(f"🔄 Processing conversations for user {user_uuid[:8]}...")
            processed_data = ExtractService.process_conversations(conversations_data, user_uuid)
            
            # Step 2: Create embeddings
            print(f"🧠 Creating embeddings for {len(processed_data)} documents...")
            embeddings, keys = ExtractService.create_embeddings(processed_data, model)
            
            # Step 3: Save to database (mock)
            print(f"💾 Saving to database...")
            db_result = ExtractService.save_data(user_uuid, processed_data, keys, embeddings)
            
            return {
                "success": True,
                "message": f"Successfully processed {len(processed_data)} conversation segments",
                "total_documents": len(processed_data),
                "embeddings_shape": list(embeddings.shape),
                "database_result": db_result
            }
            
        except Exception as e:
            if isinstance(e, ExtractServiceException):
                raise
            raise ExtractServiceException(f"Extract service failed: {str(e)}")

    """--------------------------------------------------------------------------------------------------------------"""
    """PROCESS ALL CONVERSATIONS"""


    #SUBROOT FUNCTION
    @staticmethod
    def process_conversations(conversations_data, user_uuid):
        """
        Process conversations data similar to parseJson.py exportData() function
        
        Args:
            conversations_data (list): Raw conversation data from ChatGPT export
            user_uuid (str): User's UUID for identification
            
        Returns:
            dict: Processed conversation data
            
        Raises:
            ExtractServiceException: If processing fails
        """
        # Early parameter validation
        
            
        docs = ExtractService.extract_conversation_tree(conversations_data, user_uuid)
        if not docs:
            raise ExtractServiceException("No valid conversations found in the data. Make sure to check you uploaded the right conversations.json file")
        return docs





    @staticmethod
    def extract_conversation_tree(conversations_data, user_uuid) -> dict:
        # Early parameter validation

        if not isinstance(conversations_data, list):
            raise ExtractServiceException("Conversations data must be a list")

        docs = {}
            
        for point in conversations_data:
            if 'mapping' not in point:
                continue
                
            pointers = point['mapping']
            keys = pointers.keys()
            user = "dummy"
            
            for key in keys:
                value = pointers[key]
                if value.get('message') is not None:
                    content = value['message']['content']
                    text = ""
                    
                    if 'parts' in content and content['parts']:
                        text = str(content['parts'][0])
                    elif 'text' in content:
                        text = str(content['text'])
                    
                    if text.strip():  # Only process non-empty text
                        role = value['message']['author']['role']
                        if role == "user":
                            user = text
                        elif role != "system":
                            # Only add to docs if the response text is non-empty
                            if user.strip() and user != "dummy":
                                docs[user] = text
        
        return docs


    """--------------------------------------------------------------------------------------------------------------"""
    """CREATING EMBEDDINGS FOR CONVERSATIONS"""

    #SUBROOT FUNCTION
    @staticmethod
    def create_embeddings(processed_data, model):
        """
        Create embeddings from processed conversation data
        
        Args:
            processed_data (dict): Processed conversation data
            model: SentenceTransformer model
            
        Returns:
            torch.Tensor: Document embeddings
            
        Raises:
            ExtractServiceException: If embedding creation fails
        """
        texts = list(processed_data.keys())
        if not texts:
            raise ExtractServiceException("No text found in processed data for embedding creation")
        
        # Create embeddings
        embeddings = model.encode(texts, convert_to_tensor=True)
        
        return embeddings, texts
            
        



    """--------------------------------------------------------------------------------------------------------------"""
    """SAVE ALL DATA TO DATABASE"""


    #SUBROOT FUNCTION
    @staticmethod
    def save_data(user_uuid, processed_data, keys, embeddings):
        """
        Save data to database with fallback to file storage
        
        Args:
            user_uuid (str): User's UUID
            processed_data (dict): Processed conversation data
            keys (list): Ordered list of document keys
            embeddings (torch.Tensor): Document embeddings
            
        Returns:
            dict: Save operation result
            
        Raises:
            ExtractServiceException: If both database and file save fail
        """
        # Early parameter validation
        
        if embeddings is None:
            raise ExtractServiceException("Embeddings are required for saving")
        
        # Try database save first
        try:
            return ExtractService.save_data_to_database(user_uuid, processed_data, keys, embeddings)
        except (ImportError, ExtractServiceException) as db_error:
            print(f"Database save failed, falling back to file: {db_error}")
        
        # Fallback to file save
        try:
            return ExtractService.save_data_to_file(user_uuid, processed_data, keys, embeddings)
        except Exception as file_error:
            raise ExtractServiceException(f"Both database and file save failed. File error: {str(file_error)}")



    @staticmethod
    def save_data_to_database(user_uuid, processed_data, keys, embeddings):
                   
        try:
            # Convert embeddings tensor to bytes for PostgreSQL
            embeddings_bytes = ExtractService.convert_tensor_to_bytes(embeddings)
            # Get embedding shape for reconstruction
            embedding_shape = ExtractService.create_embedding_shape(embeddings)

            key_order = keys  # Explicit key ordering

            db_result = DatabaseService.execute_save_query(user_uuid, processed_data, key_order, embeddings_bytes, embedding_shape)
            return {
                "success": True,
                "user_uuid": user_uuid,
                "file_path": db_result.get("file_path", "PostgreSQL database"),
                "total_documents": len(processed_data),
                "key_order_saved": db_result.get("key_order_saved", 0),
                "embeddings_saved": db_result.get("embeddings_saved", 0),
                "database_result": db_result
            }
        except DatabaseServiceException as e:
            #Re-raise any database related exceptions
            raise ExtractServiceException("Database error " + str(e))
        except Exception as e:
            raise ExtractServiceException(f"Unknown error for database upload: {str(e)}")

    @staticmethod
    def convert_tensor_to_bytes(embeddings):
        """
        Convert tensor to bytes for lossless storage
        
        Args:
            embeddings (torch.Tensor): Embeddings tensor
            
        Returns:
            bytes: Binary representation of embeddings
            
        Raises:
            ExtractServiceException: If tensor conversion fails
        """
            
        embeddings_np = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings
        embeddings_bytes = embeddings_np.tobytes()
        return embeddings_bytes
        
    
    @staticmethod
    def create_embedding_shape(embeddings):
        """
        Get the shape of embeddings tensor
        
        Args:
            embeddings (torch.Tensor): Embeddings tensor
            
        Returns:
            tuple: Shape of the embeddings tensor
            
        Raises:
            ExtractServiceException: If shape extraction fails
        """
            
        embeddings_np = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings
        return embeddings_np.shape
        

    
    @staticmethod
    def save_data_to_file(user_uuid, processed_data, keys, embeddings):
        """
        Save data to JSON file with base64 encoded embeddings
        
        Args:
            user_uuid (str): User's UUID
            processed_data (dict): Processed conversation data
            keys (list): Ordered list of document keys
            embeddings (torch.Tensor): Document embeddings
            
        Returns:
            dict: Save operation result
            
        Raises:
            ExtractServiceException: If file save fails
        """
        try:
            # Convert embeddings to base64 for JSON storage
            embeddings_b64 = ExtractService.convert_tensor_to_base64(embeddings)
            user_data = {
                user_uuid: {
                    "embeddings": embeddings_b64,
                    "processed_data": processed_data,
                    "key_order": keys  # Preserve key ordering like database storage
                }
            }
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data/conversations', f'{user_uuid}userData.json')
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save to JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)

            return {
                "success": True,
                "user_uuid": user_uuid,
                "file_path": file_path,
                "total_documents": len(processed_data)
            }
        except ExtractServiceException:
            # Re-raise tensor conversion errors
            raise
        except Exception as e:
            raise ExtractServiceException(f"Failed to save data to file: {str(e)}")


    @staticmethod
    def convert_tensor_to_base64(embeddings):
        """
        Convert tensor to base64 for JSON storage compatibility
        
        Args:
            embeddings (torch.Tensor): Embeddings tensor
            
        Returns:
            str: Base64 encoded embeddings
            
        Raises:
            ExtractServiceException: If tensor conversion fails
        """
        
        embeddings_np = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings
        embeddings_bytes = embeddings_np.tobytes()
        embeddings_b64 = base64.b64encode(embeddings_bytes).decode('utf-8')
        return embeddings_b64
        

        
