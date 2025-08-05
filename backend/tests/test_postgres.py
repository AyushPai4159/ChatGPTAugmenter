import pytest
import json
import psycopg
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.postgres import DatabaseService, DatabaseServiceException


class TestDatabaseService:
    """Test suite for DatabaseService class"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.test_uuid = "test-uuid-123"
        self.test_processed_data = {"How do I learn Python?": "Start with basics"}
        self.test_key_order = ["How do I learn Python?"]
        self.test_embeddings = b"test_embeddings_bytes"
        self.test_embedding_shape = (1, 4)
        
        self.mock_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        
        self.test_raw_data = (
            '{"How do I learn Python?": "Start with basics"}',  # data_json
            '["How do I learn Python?"]',                       # key_order_json
            b"test_embeddings_bytes",                           # embeddings_bytes
            '[1, 4]'                                           # embedding_shape_json
        )

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR EXECUTE_SAVE_QUERY() ROOT FUNCTION"""

    @patch('database.postgres.DatabaseService._execute_user_save')
    @patch('database.postgres.DatabaseService._prepare_save_data')
    def test_integration_execute_save_query_success(self, mock_prepare, mock_execute):
        """Test successful execute_save_query execution"""
        # Setup mocks
        mock_prepare.return_value = {
            'data_json': '{"test": "data"}',
            'key_order_json': '["test"]',
            'embeddings': self.test_embeddings,
            'embedding_shape_json': '[1, 4]'
        }
        mock_execute.return_value = {
            "rows_affected": 1,
            "operation": "upsert",
            "file_path": f"PostgreSQL database (user: {self.test_uuid})"
        }
        
        # Execute
        result = DatabaseService.execute_save_query(
            self.test_uuid, self.test_processed_data, self.test_key_order, 
            self.test_embeddings, self.test_embedding_shape
        )
        
        # Verify
        assert result["rows_affected"] == 1
        assert result["operation"] == "upsert"
        
        # Verify method calls
        mock_prepare.assert_called_once()
        mock_execute.assert_called_once_with(self.test_uuid, mock_prepare.return_value)

    def test_unit_execute_save_query_no_uuid(self):
        """Test execute_save_query with missing UUID"""
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.execute_save_query(
                None, self.test_processed_data, self.test_key_order, 
                self.test_embeddings, self.test_embedding_shape
            )
        assert "User UUID is required" in str(exc_info.value)

    @patch('database.postgres.DatabaseService._prepare_save_data')
    def test_unit_execute_save_query_prepare_failure(self, mock_prepare):
        """Test execute_save_query when data preparation fails"""
        mock_prepare.side_effect = Exception("Data preparation failed")
        
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.execute_save_query(
                self.test_uuid, self.test_processed_data, self.test_key_order,
                self.test_embeddings, self.test_embedding_shape
            )
        assert "Database save operation failed" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR LOAD_USER_DATA_FROM_DATABASE() ROOT FUNCTION"""

    @patch('database.postgres.DatabaseService._process_loaded_data')
    @patch('database.postgres.DatabaseService._execute_user_load')
    def test_integration_load_user_data_success(self, mock_execute, mock_process):
        """Test successful load_user_data_from_database execution"""
        # Setup mocks
        mock_execute.return_value = self.test_raw_data
        mock_process.return_value = {
            "processed_data": self.test_processed_data,
            "key_order": self.test_key_order,
            "embeddings": self.test_embeddings,
            "embedding_shape": self.test_embedding_shape
        }
        
        # Execute
        result = DatabaseService.load_user_data_from_database(self.test_uuid)
        
        # Verify
        assert result["processed_data"] == self.test_processed_data
        assert result["key_order"] == self.test_key_order
        assert result["embeddings"] == self.test_embeddings
        
        # Verify method calls
        mock_execute.assert_called_once_with(self.test_uuid)
        mock_process.assert_called_once_with(self.test_raw_data)

    def test_unit_load_user_data_no_uuid(self):
        """Test load_user_data_from_database with missing UUID"""
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.load_user_data_from_database(None)
        assert "User UUID is required" in str(exc_info.value)

    @patch('database.postgres.DatabaseService._execute_user_load')
    def test_unit_load_user_data_execute_failure(self, mock_execute):
        """Test load_user_data_from_database when execution fails"""
        mock_execute.side_effect = DatabaseServiceException("User not found")
        
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.load_user_data_from_database(self.test_uuid)
        assert "User not found" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR GET_DATABASE_CONNECTION() SUBROOT FUNCTION"""

    @patch('database.postgres.DatabaseService._attempt_connection')
    @patch('database.postgres.DatabaseService._validate_connection_params')
    def test_integration_get_database_connection_success(self, mock_validate, mock_attempt):
        """Test successful get_database_connection execution"""
        mock_validate.return_value = True
        mock_attempt.return_value = self.mock_connection
        
        result = DatabaseService.get_database_connection()
        
        assert result == self.mock_connection
        mock_validate.assert_called_once()
        mock_attempt.assert_called_once()

    @patch('database.postgres.DatabaseService._validate_connection_params')
    def test_unit_get_database_connection_invalid_params(self, mock_validate):
        """Test get_database_connection with invalid parameters"""
        mock_validate.return_value = False
        
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.get_database_connection()
        assert "Invalid connection parameters" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR UTILITY FUNCTIONS"""

    @patch('database.postgres.DatabaseService._execute_count_query')
    def test_integration_get_user_count_success(self, mock_execute):
        """Test successful get_user_count execution"""
        mock_execute.return_value = 5
        
        result = DatabaseService.get_user_count()
        
        assert result == 5
        mock_execute.assert_called_once()

    @patch('database.postgres.DatabaseService._execute_delete_query')
    def test_integration_delete_user_data_success(self, mock_execute):
        """Test successful delete_user_data execution"""
        mock_execute.return_value = {
            "success": True,
            "deleted_rows": 1,
            "uuid": self.test_uuid
        }
        
        result = DatabaseService.delete_user_data(self.test_uuid)
        
        assert result["success"] is True
        assert result["deleted_rows"] == 1
        mock_execute.assert_called_once_with(self.test_uuid)

    def test_unit_delete_user_data_no_uuid(self):
        """Test delete_user_data with missing UUID"""
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.delete_user_data(None)
        assert "User UUID is required for deletion" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR CHILD FUNCTIONS"""

    def test_unit_validate_connection_params_success(self):
        """Test successful _validate_connection_params execution"""
        result = DatabaseService._validate_connection_params()
        
        assert isinstance(result, bool)
        assert result is True  # Should be valid with default params

    def test_unit_prepare_save_data_success(self):
        """Test successful _prepare_save_data execution"""
        result = DatabaseService._prepare_save_data(
            self.test_processed_data, self.test_key_order, 
            self.test_embeddings, self.test_embedding_shape
        )
        
        assert "data_json" in result
        assert "key_order_json" in result
        assert "embeddings" in result
        assert "embedding_shape_json" in result
        assert result["embeddings"] == self.test_embeddings

    def test_unit_convert_to_json_dict(self):
        """Test successful _convert_to_json execution with dict"""
        test_dict = {"key": "value"}
        result = DatabaseService._convert_to_json(test_dict)
        
        assert isinstance(result, str)
        assert json.loads(result) == test_dict

    def test_unit_convert_to_json_list(self):
        """Test successful _convert_to_json execution with list"""
        test_list = ["item1", "item2"]
        result = DatabaseService._convert_to_json(test_list)
        
        assert isinstance(result, str)
        assert json.loads(result) == test_list

    def test_unit_process_loaded_data_success(self):
        """Test successful _process_loaded_data execution"""
        result = DatabaseService._process_loaded_data(self.test_raw_data)
        
        assert "processed_data" in result
        assert "key_order" in result
        assert "embeddings" in result
        assert "embedding_shape" in result
        assert result["embeddings"] == self.test_raw_data[2]

    def test_unit_parse_processed_data_json_string(self):
        """Test successful _parse_processed_data execution with JSON string"""
        test_json = '{"test": "data"}'
        result = DatabaseService._parse_processed_data(test_json)
        
        assert isinstance(result, dict)
        assert result["test"] == "data"

    def test_unit_parse_processed_data_dict(self):
        """Test successful _parse_processed_data execution with dict"""
        test_dict = {"test": "data"}
        result = DatabaseService._parse_processed_data(test_dict)
        
        assert isinstance(result, dict)
        assert result == test_dict

    def test_unit_parse_key_order_json_string(self):
        """Test successful _parse_key_order execution with JSON string"""
        test_json = '["key1", "key2"]'
        result = DatabaseService._parse_key_order(test_json)
        
        assert isinstance(result, list)
        assert result == ["key1", "key2"]

    def test_unit_parse_key_order_list(self):
        """Test successful _parse_key_order execution with list"""
        test_list = ["key1", "key2"]
        result = DatabaseService._parse_key_order(test_list)
        
        assert isinstance(result, list)
        assert result == test_list

    def test_unit_parse_embedding_shape_json_string(self):
        """Test successful _parse_embedding_shape execution with JSON string"""
        test_json = '[2, 4]'
        result = DatabaseService._parse_embedding_shape(test_json)
        
        assert isinstance(result, list)
        assert result == [2, 4]

    def test_unit_parse_embedding_shape_list(self):
        """Test successful _parse_embedding_shape execution with list"""
        test_list = [2, 4]
        result = DatabaseService._parse_embedding_shape(test_list)
        
        assert isinstance(result, tuple)
        assert result == (2, 4)

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_unit_execute_user_load_not_found(self, mock_get_conn):
        """Test _execute_user_load when user not found"""
        mock_get_conn.return_value = self.mock_connection
        self.mock_cursor.fetchone.return_value = None
        
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService._execute_user_load(self.test_uuid)
        assert f"Data for user UUID {self.test_uuid} not found in database" in str(exc_info.value)

    def test_unit_close_connection_success(self):
        """Test successful _close_connection execution"""
        # Should not raise any exceptions
        DatabaseService._close_connection(self.mock_cursor, self.mock_connection)
        
        self.mock_cursor.close.assert_called_once()
        self.mock_connection.close.assert_called_once()

    def test_unit_close_connection_none_values(self):
        """Test _close_connection with None values"""
        # Should not raise any exceptions
        DatabaseService._close_connection(None, None)


# ===== PYTEST FIXTURES =====

@pytest.fixture
def mock_database_connection():
    """Fixture for mock database connection"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

@pytest.fixture
def sample_user_data():
    """Fixture for sample user data"""
    return {
        "uuid": "test-uuid-123",
        "processed_data": {"How to learn Python?": "Start with basics"},
        "key_order": ["How to learn Python?"],
        "embeddings": b"test_embeddings",
        "embedding_shape": (1, 4)
    }