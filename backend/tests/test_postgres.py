import pytest
import json
import psycopg
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.postgres import DatabaseService, DatabaseServiceException, TableNotFoundException, UserNotFoundException


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
    """TESTS FOR EXCEPTION HANDLING - TableNotFoundException and UserNotFoundException"""

    @patch('database.postgres.DatabaseService._execute_delete_query')
    def test_delete_user_data_table_not_found_exception(self, mock_execute):
        """Test delete_user_data when table doesn't exist"""
        # Arrange
        mock_execute.side_effect = TableNotFoundException("Table 'users' does not exist in the database")
        
        # Act & Assert
        with pytest.raises(TableNotFoundException) as exc_info:
            DatabaseService.delete_user_data(self.test_uuid)
        
        assert "Table 'users' does not exist in the database" in str(exc_info.value)
        assert isinstance(exc_info.value, DatabaseServiceException)  # Should inherit from base exception
        mock_execute.assert_called_once_with(self.test_uuid)

    @patch('database.postgres.DatabaseService._execute_delete_query')
    def test_delete_user_data_user_not_found_exception(self, mock_execute):
        """Test delete_user_data when user doesn't exist"""
        # Arrange
        mock_execute.side_effect = UserNotFoundException(f"User with UUID '{self.test_uuid}' not found in the users table")
        
        # Act & Assert
        with pytest.raises(UserNotFoundException) as exc_info:
            DatabaseService.delete_user_data(self.test_uuid)
        
        assert f"User with UUID '{self.test_uuid}' not found in the users table" in str(exc_info.value)
        assert isinstance(exc_info.value, DatabaseServiceException)  # Should inherit from base exception
        mock_execute.assert_called_once_with(self.test_uuid)

    @patch('database.postgres.DatabaseService._execute_delete_query')
    def test_delete_user_data_general_database_exception(self, mock_execute):
        """Test delete_user_data with general database exception"""
        # Arrange
        mock_execute.side_effect = DatabaseServiceException("Connection timeout")
        
        # Act & Assert
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.delete_user_data(self.test_uuid)
        
        assert "Connection timeout" in str(exc_info.value)
        mock_execute.assert_called_once_with(self.test_uuid)

    @patch('database.postgres.DatabaseService._execute_delete_query')
    def test_delete_user_data_unexpected_exception_wrapping(self, mock_execute):
        """Test delete_user_data wraps unexpected exceptions"""
        # Arrange
        mock_execute.side_effect = RuntimeError("Unexpected system error")
        
        # Act & Assert
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.delete_user_data(self.test_uuid)
        
        assert "Failed to delete user data: Unexpected system error" in str(exc_info.value)
        mock_execute.assert_called_once_with(self.test_uuid)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR _execute_delete_query() - DETAILED EXCEPTION SCENARIOS"""

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_execute_delete_query_table_does_not_exist(self, mock_get_conn):
        """Test _execute_delete_query when users table doesn't exist"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Mock table existence check to return False
        self.mock_cursor.fetchone.return_value = [False]  # Table doesn't exist
        
        # Act & Assert
        with pytest.raises(TableNotFoundException) as exc_info:
            DatabaseService._execute_delete_query(self.test_uuid)
        
        assert "Table 'users' does not exist in the database" in str(exc_info.value)

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_execute_delete_query_user_does_not_exist(self, mock_get_conn):
        """Test _execute_delete_query when user doesn't exist"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Mock sequence: table exists (True), then user count is 0
        self.mock_cursor.fetchone.side_effect = [[True], [0]]  # Table exists, but user count is 0
        
        # Act & Assert
        with pytest.raises(UserNotFoundException) as exc_info:
            DatabaseService._execute_delete_query(self.test_uuid)
        
        assert f"User with UUID '{self.test_uuid}' not found in the users table" in str(exc_info.value)

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_execute_delete_query_successful_deletion(self, mock_get_conn):
        """Test _execute_delete_query successful deletion"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Mock sequence: table exists (True), user exists (1), deletion successful
        self.mock_cursor.fetchone.side_effect = [[True], [1]]  # Table exists, user exists
        self.mock_cursor.rowcount = 1  # One row deleted
        
        # Act
        result = DatabaseService._execute_delete_query(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["deleted_rows"] == 1
        assert result["uuid"] == self.test_uuid
        self.mock_connection.commit.assert_called_once()

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_execute_delete_query_database_execution_error(self, mock_get_conn):
        """Test _execute_delete_query with database execution error"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Mock table check succeeds, but user check fails with database error
        self.mock_cursor.fetchone.side_effect = [[True]]  # Table exists
        self.mock_cursor.execute.side_effect = [None, psycopg.Error("Database connection lost")]
        
        # Act & Assert
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService._execute_delete_query(self.test_uuid)
        
        assert "Database delete execution failed" in str(exc_info.value)
        self.mock_connection.rollback.assert_called_once()

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_execute_delete_query_connection_error(self, mock_get_conn):
        """Test _execute_delete_query with connection error"""
        # Arrange
        mock_get_conn.side_effect = psycopg.Error("Unable to connect to database")
        
        # Act & Assert
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService._execute_delete_query(self.test_uuid)
        
        assert "Database delete execution failed" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR EXCEPTION INHERITANCE AND BEHAVIOR"""

    def test_table_not_found_exception_inheritance(self):
        """Test TableNotFoundException inherits from DatabaseServiceException"""
        # Act
        exception = TableNotFoundException("Test table error")
        
        # Assert
        assert isinstance(exception, DatabaseServiceException)
        assert isinstance(exception, Exception)
        assert str(exception) == "Test table error"

    def test_user_not_found_exception_inheritance(self):
        """Test UserNotFoundException inherits from DatabaseServiceException"""
        # Act
        exception = UserNotFoundException("Test user error")
        
        # Assert
        assert isinstance(exception, DatabaseServiceException)
        assert isinstance(exception, Exception)
        assert str(exception) == "Test user error"

    def test_custom_exceptions_are_distinguishable(self):
        """Test that custom exceptions can be caught separately"""
        # Test that we can catch TableNotFoundException specifically
        try:
            raise TableNotFoundException("Table error")
        except TableNotFoundException as e:
            assert str(e) == "Table error"
        except Exception:
            pytest.fail("Should have caught TableNotFoundException specifically")

        # Test that we can catch UserNotFoundException specifically
        try:
            raise UserNotFoundException("User error")
        except UserNotFoundException as e:
            assert str(e) == "User error"
        except Exception:
            pytest.fail("Should have caught UserNotFoundException specifically")

    """----------------------------------------------------------------------------------------------------------------------------"""
    """INTEGRATION TESTS FOR EXCEPTION HANDLING WORKFLOWS"""

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_integration_full_delete_workflow_table_missing(self, mock_get_conn):
        """Test complete delete workflow when table is missing"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        self.mock_cursor.fetchone.return_value = [False]  # Table doesn't exist
        
        # Act & Assert - Should raise TableNotFoundException through the full stack
        with pytest.raises(TableNotFoundException) as exc_info:
            DatabaseService.delete_user_data(self.test_uuid)
        
        assert "Table 'users' does not exist" in str(exc_info.value)

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_integration_full_delete_workflow_user_missing(self, mock_get_conn):
        """Test complete delete workflow when user is missing"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Table exists, but user doesn't
        self.mock_cursor.fetchone.side_effect = [[True], [0]]
        
        # Act & Assert - Should raise UserNotFoundException through the full stack
        with pytest.raises(UserNotFoundException) as exc_info:
            DatabaseService.delete_user_data(self.test_uuid)
        
        assert f"User with UUID '{self.test_uuid}' not found" in str(exc_info.value)

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_integration_full_delete_workflow_success(self, mock_get_conn):
        """Test complete successful delete workflow"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Table exists, user exists, deletion succeeds
        self.mock_cursor.fetchone.side_effect = [[True], [1]]
        self.mock_cursor.rowcount = 1
        
        # Act
        result = DatabaseService.delete_user_data(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["deleted_rows"] == 1
        assert result["uuid"] == self.test_uuid

    """----------------------------------------------------------------------------------------------------------------------------"""
    """EDGE CASES FOR EXCEPTION HANDLING"""

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_execute_delete_query_multiple_users_with_same_uuid(self, mock_get_conn):
        """Test _execute_delete_query when multiple users have same UUID (edge case)"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Table exists, multiple users found (should still work)
        self.mock_cursor.fetchone.side_effect = [[True], [2]]  # 2 users with same UUID
        self.mock_cursor.rowcount = 2  # Two rows deleted
        
        # Act
        result = DatabaseService._execute_delete_query(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["deleted_rows"] == 2  # Should delete all matching rows

    @patch('database.postgres.DatabaseService.get_database_connection')
    def test_execute_delete_query_zero_rows_affected_but_user_exists(self, mock_get_conn):
        """Test edge case where user exists but delete affects 0 rows"""
        # Arrange
        mock_get_conn.return_value = self.mock_connection
        # Table exists, user exists, but somehow delete affects 0 rows
        self.mock_cursor.fetchone.side_effect = [[True], [1]]
        self.mock_cursor.rowcount = 0  # No rows actually deleted (edge case)
        
        # Act
        result = DatabaseService._execute_delete_query(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["deleted_rows"] == 0
        assert result["uuid"] == self.test_uuid

    def test_delete_user_data_empty_string_uuid(self):
        """Test delete_user_data with empty string UUID"""
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.delete_user_data("")
        
        assert "User UUID is required for deletion" in str(exc_info.value)

    def test_delete_user_data_whitespace_only_uuid(self):
        """Test delete_user_data with whitespace-only UUID"""
        with pytest.raises(DatabaseServiceException) as exc_info:
            DatabaseService.delete_user_data("   ")
        
        # This should pass the empty check and reach the database level
        # where it would be handled as a legitimate UUID (even if invalid)
        # The actual behavior depends on implementation details

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