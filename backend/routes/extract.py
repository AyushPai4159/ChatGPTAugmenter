import json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import base64
import os


class ExtractServiceException(Exception):
    """Custom exception for extract service errors"""
    pass


class ExtractService:
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
        try:
            docs = {}
            
            if not isinstance(conversations_data, list):
                raise ExtractServiceException("Conversations data must be a list")
            
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
                                # Use UUID + timestamp or counter to create unique keys
                                docs[user] = text
            
            if not docs:
                raise ExtractServiceException("No valid conversations found in the data")
                
            return docs
            
        except Exception as e:
            if isinstance(e, ExtractServiceException):
                raise
            raise ExtractServiceException(f"Failed to process conversations: {str(e)}")
    
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
        try:
            if not model:
                raise ExtractServiceException("Model not available for creating embeddings")
            
            if not processed_data:
                raise ExtractServiceException("No processed data available for creating embeddings")
            
            texts = list(processed_data.values())
            
            # Create embeddings
            embeddings = model.encode(texts, convert_to_tensor=True)
            
            return embeddings
            
        except Exception as e:
            if isinstance(e, ExtractServiceException):
                raise
            raise ExtractServiceException(f"Failed to create embeddings: {str(e)}")
    
    @staticmethod
    def save_to_database(user_uuid, processed_data, embeddings):
        """
        Save data to database as JSON file with UUID as key and base64-encoded embeddings
        
        Args:
            user_uuid (str): User's UUID
            processed_data (dict): Processed conversation data
            embeddings (torch.Tensor): Document embeddings
            
        Returns:
            dict: Save operation result
            
        Raises:
            ExtractServiceException: If database save fails
        """
        try:
            
            
            # Convert embeddings tensor to numpy array and then to base64
            embeddings_np = embeddings.cpu().numpy() if hasattr(embeddings, 'cpu') else embeddings
            embeddings_bytes = embeddings_np.tobytes()
            embeddings_b64 = base64.b64encode(embeddings_bytes).decode('utf-8')
            
            # Create the data structure
            user_data = {
                user_uuid: {
                    "embeddings": embeddings_b64,
                    "processed_data": processed_data
                }
            }
            
            # Define the file path
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'userData.json')
            
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
            
        except Exception as e:
            raise ExtractServiceException(f"Database save failed: {str(e)}")


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
        # Step 1: Process conversations (similar to exportData())
        print(f"🔄 Processing conversations for user {user_uuid[:8]}...")
        processed_data = ExtractService.process_conversations(conversations_data, user_uuid)
        
        # Step 2: Create embeddings
        print(f"🧠 Creating embeddings for {len(processed_data)} documents...")
        embeddings = ExtractService.create_embeddings(processed_data, model)
        
        # Step 3: Save to database (mock)
        print(f"💾 Saving to database...")
        db_result = ExtractService.save_to_database(user_uuid, processed_data, embeddings)
        
        return {
            "success": True,
            "message": f"Successfully processed {len(processed_data)} conversation segments",
            "user_uuid": user_uuid,
            "total_documents": len(processed_data),
            "embeddings_shape": list(embeddings.shape),
            "database_result": db_result
        }
        
    except Exception as e:
        if isinstance(e, ExtractServiceException):
            raise
        raise ExtractServiceException(f"Extract service failed: {str(e)}")
