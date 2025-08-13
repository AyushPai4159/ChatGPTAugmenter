import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.extract import ExtractService, ExtractServiceException
from database.postgres import DatabaseServiceException


class TestExtractService:
    """Test suite for ExtractService class"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.mock_model = Mock()
        self.mock_model.encode.return_value = torch.tensor([[0.1, 0.2], [0.3, 0.4]])
        
        self.test_uuid = "test-uuid-123"
        self.test_conversations = [
            {
                "mapping": {
                    "1": {
                        "message": {
                            "content": {"parts": ["How do I learn Python?"]},
                            "author": {"role": "user"}
                        }
                    },
                    "2": {
                        "message": {
                            "content": {"parts": ["Start with basics"]},
                            "author": {"role": "assistant"}
                        }
                    }
                }
            }
        ]
        self.test_processed_data = {"How do I learn Python?": "Start with basics"}

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR EXTRACT_SERVICE() ROOT FUNCTION"""

    @patch('routes.extract.ExtractService.save_data')
    @patch('routes.extract.ExtractService.create_embeddings')
    @patch('routes.extract.ExtractService.process_conversations')
    def test_integration_extract_service_success(self, mock_process, mock_embeddings, mock_save):
        """Test successful extract_service execution"""
        # Setup mocks
        mock_process.return_value = self.test_processed_data
        mock_embeddings.return_value = (torch.tensor([[0.1, 0.2]]), ["How do I learn Python?"])
        mock_save.return_value = {"success": True, "file_path": "/test/path"}
        
        # Execute
        result = ExtractService.extract_service(self.test_conversations, self.test_uuid, self.mock_model)
        
        # Verify
        assert result["success"] is True
        assert result["user_uuid"] == self.test_uuid
        assert result["total_documents"] == 1
        assert "embeddings_shape" in result
        
        # Verify method calls
        mock_process.assert_called_once_with(self.test_conversations, self.test_uuid)
        mock_embeddings.assert_called_once_with(self.test_processed_data, self.mock_model)
        mock_save.assert_called_once()

    def test_unit_extract_service_no_model(self):
        """Test extract_service with missing model"""
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.extract_service(self.test_conversations, self.test_uuid, None)
        assert "Model not available" in str(exc_info.value)

    def test_unit_extract_service_no_conversations(self):
        """Test extract_service with missing conversations"""
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.extract_service(None, self.test_uuid, self.mock_model)
        assert "No conversation data available" in str(exc_info.value)

    @patch('routes.extract.ExtractService.process_conversations')
    def test_unit_extract_service_process_conversations_failure(self, mock_process):
        """Test extract_service when process_conversations fails"""
        mock_process.side_effect = ExtractServiceException("Processing failed")
        
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.extract_service(self.test_conversations, self.test_uuid, self.mock_model)
        assert "Processing failed" in str(exc_info.value)

    @patch('routes.extract.ExtractService.create_embeddings')
    @patch('routes.extract.ExtractService.process_conversations')
    def test_unit_extract_service_create_embeddings_failure(self, mock_process, mock_embeddings):
        """Test extract_service when create_embeddings fails"""
        mock_process.return_value = self.test_processed_data
        mock_embeddings.side_effect = Exception("Embedding creation failed")
        
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.extract_service(self.test_conversations, self.test_uuid, self.mock_model)
        assert "Extract service failed" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR PROCESS_CONVERSATIONS() SUBROOT FUNCTION"""

    @patch('routes.extract.ExtractService.extract_conversation_tree')
    def test_integration_process_conversations_success(self, mock_extract):
        """Test successful process_conversations execution"""
        mock_extract.return_value = self.test_processed_data
        
        result = ExtractService.process_conversations(self.test_conversations, self.test_uuid)
        
        assert result == self.test_processed_data
        mock_extract.assert_called_once_with(self.test_conversations, self.test_uuid)


    @patch('routes.extract.ExtractService.extract_conversation_tree')
    def test_unit_process_conversations_empty_result(self, mock_extract):
        """Test process_conversations when extract_conversation_tree returns empty"""
        mock_extract.return_value = {}
        
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.process_conversations(self.test_conversations, self.test_uuid)
        assert "No valid conversations found" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR EXTRACT_CONVERSATION_TREE() CHILD FUNCTION"""

    def test_unit_extract_conversation_tree_success(self):
        """Test successful extract_conversation_tree execution"""
        result = ExtractService.extract_conversation_tree(self.test_conversations, self.test_uuid)
        
        assert isinstance(result, dict)
        assert "How do I learn Python?" in result
        assert result["How do I learn Python?"] == "Start with basics"


    def test_unit_extract_conversation_tree_invalid_type(self):
        """Test extract_conversation_tree with invalid data type"""
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.extract_conversation_tree("invalid", self.test_uuid)
        assert "Conversations data must be a list" in str(exc_info.value)

   

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR CREATE_EMBEDDINGS() SUBROOT FUNCTION"""

    def test_unit_create_embeddings_success(self):
        """Test successful create_embeddings execution"""
        embeddings, keys = ExtractService.create_embeddings(self.test_processed_data, self.mock_model)
        
        assert isinstance(embeddings, torch.Tensor)
        assert keys == ["How do I learn Python?"]
        self.mock_model.encode.assert_called_once()


    def test_unit_create_embeddings_empty_data(self):
        """Test create_embeddings with empty data"""
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.create_embeddings({}, self.mock_model)
        assert "No text found in processed data" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR SAVE_DATA() SUBROOT FUNCTION"""

    @patch('routes.extract.ExtractService.save_data_to_database')
    def test_integration_save_data_database_success(self, mock_db_save):
        """Test successful save_data to database"""
        mock_db_save.return_value = {"success": True, "file_path": "database"}
        
        result = ExtractService.save_data(
            self.test_uuid, self.test_processed_data, ["key1"], torch.tensor([[0.1, 0.2]])
        )
        
        assert result["success"] is True
        mock_db_save.assert_called_once()

    @patch('routes.extract.ExtractService.save_data_to_file')
    @patch('routes.extract.ExtractService.save_data_to_database')
    def test_integration_save_data_fallback_to_file(self, mock_db_save, mock_file_save):
        """Test save_data fallback from database to file"""
        mock_db_save.side_effect = ExtractServiceException("DB error")
        mock_file_save.return_value = {"success": True, "file_path": "/test/file"}
        
        result = ExtractService.save_data(
            self.test_uuid, self.test_processed_data, ["key1"], torch.tensor([[0.1, 0.2]])
        )
        
        assert result["success"] is True
        mock_db_save.assert_called_once()
        mock_file_save.assert_called_once()


    def test_unit_save_data_no_embeddings(self):
        """Test save_data with no embeddings"""
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.save_data(self.test_uuid, self.test_processed_data, ["key1"], None)
        assert "Embeddings are required" in str(exc_info.value)

    @patch('routes.extract.ExtractService.save_data_to_file')
    @patch('routes.extract.ExtractService.save_data_to_database')
    def test_unit_save_data_both_methods_fail(self, mock_db_save, mock_file_save):
        """Test save_data when both database and file save fail"""
        mock_db_save.side_effect = ExtractServiceException("DB error")
        mock_file_save.side_effect = Exception("File error")
        
        with pytest.raises(ExtractServiceException) as exc_info:
            ExtractService.save_data(
                self.test_uuid, self.test_processed_data, ["key1"], torch.tensor([[0.1, 0.2]])
            )
        assert "Both database and file save failed" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR SAVE_DATA_TO_DATABASE() CHILD FUNCTION"""

    @patch('routes.extract.ExtractService.create_embedding_shape')
    @patch('routes.extract.ExtractService.convert_tensor_to_bytes')
    @patch('routes.extract.DatabaseService.execute_save_query')
    def test_integration_save_data_to_database_success(self, mock_db_query, mock_convert_bytes, mock_shape):
        """Test successful save_data_to_database execution"""
        mock_convert_bytes.return_value = b"test_bytes"
        mock_shape.return_value = (1, 2)
        mock_db_query.return_value = {"embeddings_saved": 1, "key_order_saved": 1}
        
        result = ExtractService.save_data_to_database(
            self.test_uuid, self.test_processed_data, ["key1"], torch.tensor([[0.1, 0.2]])
        )
        
        assert result["success"] is True
        assert result["user_uuid"] == self.test_uuid
        mock_db_query.assert_called_once()

    @patch('routes.extract.DatabaseService.execute_save_query')
    def test_unit_save_data_to_database_db_exception(self, mock_db_query):
        """Test save_data_to_database when database throws exception"""
        mock_db_query.side_effect = DatabaseServiceException("DB connection failed")
        
        with pytest.raises(ExtractServiceException):
            ExtractService.save_data_to_database(
                self.test_uuid, self.test_processed_data, ["key1"], torch.tensor([[0.1, 0.2]])
            )

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR SAVE_DATA_TO_FILE() CHILD FUNCTION"""

    @patch('routes.extract.ExtractService.convert_tensor_to_base64')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('routes.extract.json.dump')
    @patch('routes.extract.os.makedirs')
    def test_integration_save_data_to_file_success(self, mock_makedirs, mock_json, mock_open, mock_convert):
        """Test successful save_data_to_file execution"""
        mock_convert.return_value = "base64_string"
        
        result = ExtractService.save_data_to_file(
            self.test_uuid, self.test_processed_data, ["key1"], torch.tensor([[0.1, 0.2]])
        )
        
        assert result["success"] is True
        assert result["user_uuid"] == self.test_uuid
        mock_makedirs.assert_called_once()
        mock_json.assert_called_once()

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR HELPER FUNCTIONS"""

    def test_unit_convert_tensor_to_bytes_success(self):
        """Test successful convert_tensor_to_bytes execution"""
        tensor = torch.tensor([[0.1, 0.2]])
        result = ExtractService.convert_tensor_to_bytes(tensor)
        
        assert isinstance(result, bytes)


    def test_unit_create_embedding_shape_success(self):
        """Test successful create_embedding_shape execution"""
        tensor = torch.tensor([[0.1, 0.2], [0.3, 0.4]])
        result = ExtractService.create_embedding_shape(tensor)
        
        assert result == (2, 2)


    def test_unit_convert_tensor_to_base64_success(self):
        """Test successful convert_tensor_to_base64 execution"""
        tensor = torch.tensor([[0.1, 0.2]])
        result = ExtractService.convert_tensor_to_base64(tensor)
        
        assert isinstance(result, str)


# ===== PYTEST FIXTURES =====

@pytest.fixture
def mock_sentence_transformer():
    """Fixture for mock SentenceTransformer model"""
    model = Mock()
    model.encode.return_value = torch.tensor([[0.1, 0.2], [0.3, 0.4]])
    return model

@pytest.fixture
def sample_conversation_data():
    """Fixture for sample conversation data"""
    return [
        {
            "mapping": {
                "1": {
                    "message": {
                        "content": {"parts": ["Test question"]},
                        "author": {"role": "user"}
                    }
                },
                "2": {
                    "message": {
                        "content": {"parts": ["Test answer"]},
                        "author": {"role": "assistant"}
                    }
                }
            }
        }
    ]
