import pytest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.delete import DeleteService, DeleteServiceException
from database.postgres import DatabaseServiceException, TableNotFoundException, UserNotFoundException


class TestDeleteService:
    """Test suite for DeleteService class with emphasis on exception handling and JSON fallback"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.test_uuid = "test-uuid-123"
        self.valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        self.empty_uuid = ""
        self.none_uuid = None
        self.invalid_uuid = 123  # Non-string UUID
        
        # Mock database successful deletion result
        self.mock_db_success_result = {
            "deleted_rows": 1,
            "success": True
        }
        
        # Mock database failure result 
        self.mock_db_failure_result = {
            "success": False,
            "error": "User not found in database",
            "error_type": "UserNotFoundException"
        }
        
        # Mock JSON file content
        self.mock_json_content = {
            self.test_uuid: {
                "conversations": ["Some conversation data"],
                "metadata": {"created": "2024-01-01"}
            }
        }

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR delete_service() ROOT FUNCTION - SUCCESSFUL DATABASE DELETION"""

    @patch('routes.delete.DeleteService.delete_from_database')
    def test_delete_service_database_success(self, mock_db_delete):
        """Test successful deletion from database (primary path)"""
        # Arrange
        mock_db_delete.return_value = {
            "success": True,
            "deleted_rows": 1,
            "message": "Successfully deleted from database"
        }
        
        # Act
        result = DeleteService.delete_service(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["uuid"] == self.test_uuid
        assert result["deleted_rows"] == 1
        assert result["status"] == "deleted_from_database"
        assert result["source"] == "database"
        assert "Successfully deleted data for UUID" in result["message"]
        assert "from database" in result["message"]
        mock_db_delete.assert_called_once_with(self.test_uuid)

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR delete_service() ROOT FUNCTION - DATABASE FAILURE WITH JSON FALLBACK"""

    @patch('routes.delete.DeleteService.delete_from_json_file')
    @patch('routes.delete.DeleteService.delete_from_database')
    def test_delete_service_database_failure_json_success(self, mock_db_delete, mock_json_delete):
        """Test database failure with successful JSON fallback"""
        # Arrange
        mock_db_delete.return_value = {
            "success": False,
            "error": "Table not found",
            "error_type": "TableNotFoundException"
        }
        mock_json_delete.return_value = {
            "success": True,
            "message": "Successfully deleted JSON file",
            "file_path": "/path/to/file.json"
        }
        
        # Act
        result = DeleteService.delete_service(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["uuid"] == self.test_uuid
        assert result["status"] == "deleted_from_json"
        assert result["source"] == "json_file"
        assert "from JSON file" in result["message"]
        assert result["file_path"] == "/path/to/file.json"
        mock_db_delete.assert_called_once_with(self.test_uuid)
        mock_json_delete.assert_called_once_with(self.test_uuid)

    @patch('routes.delete.DeleteService.delete_from_json_file')
    @patch('routes.delete.DeleteService.delete_from_database')
    def test_delete_service_both_database_and_json_fail(self, mock_db_delete, mock_json_delete):
        """Test when both database and JSON deletion fail"""
        # Arrange
        mock_db_delete.return_value = {
            "success": False,
            "error": "Database connection failed",
            "error_type": "DatabaseServiceException"
        }
        mock_json_delete.return_value = {
            "success": False,
            "error": "JSON file not found",
            "file_path": "/path/to/missing/file.json"
        }
        
        # Act
        result = DeleteService.delete_service(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert result["uuid"] == self.test_uuid
        assert result["status"] == "not_found_anywhere"
        assert "No data found for UUID" in result["message"]
        assert "in database or JSON files" in result["message"]
        assert result["database_error"] == "Database connection failed"
        assert result["json_error"] == "JSON file not found"

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR INPUT VALIDATION AND EDGE CASES"""

    def test_delete_service_empty_uuid(self):
        """Test deletion with empty UUID raises exception"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_service(self.empty_uuid)
        
        assert "UUID is required for deletion" in str(exc_info.value)

    def test_delete_service_none_uuid(self):
        """Test deletion with None UUID raises exception"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_service(self.none_uuid)
        
        assert "UUID is required for deletion" in str(exc_info.value)

    def test_delete_service_invalid_uuid_type(self):
        """Test deletion with non-string UUID raises exception"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_service(self.invalid_uuid)
        
        assert "UUID must be a string" in str(exc_info.value)

    @patch('routes.delete.DeleteService.delete_from_database')
    def test_delete_service_whitespace_uuid_stripped(self, mock_db_delete):
        """Test deletion with whitespace-padded UUID is properly stripped"""
        # Arrange
        whitespace_uuid = f"  {self.test_uuid}  "
        mock_db_delete.return_value = {
            "success": True,
            "deleted_rows": 1,
            "message": "Successfully deleted from database"
        }
        
        # Act
        result = DeleteService.delete_service(whitespace_uuid)
        
        # Assert
        assert result["success"] is True
        mock_db_delete.assert_called_once_with(self.test_uuid)  # Should be stripped

    @patch('routes.delete.DeleteService.delete_from_database')
    def test_delete_service_unexpected_exception_handling(self, mock_db_delete):
        """Test handling of unexpected exceptions during deletion"""
        # Arrange
        mock_db_delete.side_effect = RuntimeError("Unexpected system error")
        
        # Act & Assert
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_service(self.test_uuid)
        
        assert "Delete service failed: Unexpected system error" in str(exc_info.value)

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR delete_from_database() FUNCTION"""

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_from_database_success(self, mock_db_service):
        """Test successful database deletion"""
        # Arrange
        mock_db_service.return_value = {"deleted_rows": 1}
        
        # Act
        result = DeleteService.delete_from_database(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["deleted_rows"] == 1
        assert result["message"] == "Successfully deleted from database"
        mock_db_service.assert_called_once_with(self.test_uuid)

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_from_database_table_not_found(self, mock_db_service):
        """Test database deletion when table doesn't exist"""
        # Arrange
        mock_db_service.side_effect = TableNotFoundException("Table 'users' not found")
        
        # Act
        result = DeleteService.delete_from_database(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Table 'users' not found"
        assert result["error_type"] == "TableNotFoundException"

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_from_database_user_not_found(self, mock_db_service):
        """Test database deletion when user doesn't exist"""
        # Arrange
        mock_db_service.side_effect = UserNotFoundException("User not found in database")
        
        # Act
        result = DeleteService.delete_from_database(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "User not found in database"
        assert result["error_type"] == "UserNotFoundException"

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_from_database_general_db_exception(self, mock_db_service):
        """Test database deletion with general database exception"""
        # Arrange
        mock_db_service.side_effect = DatabaseServiceException("Connection timeout")
        
        # Act
        result = DeleteService.delete_from_database(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Connection timeout"
        assert result["error_type"] == "DatabaseServiceException"

    def test_delete_from_database_empty_uuid(self):
        """Test database deletion with empty UUID raises exception"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_from_database("")
        
        assert "User UUID is required for database deletion" in str(exc_info.value)

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR delete_from_json_file() FUNCTION"""

    @patch('routes.delete.DeleteService.execute_file_deletion')
    @patch('routes.delete.DeleteService.validate_json_file')
    @patch('routes.delete.DeleteService.get_json_file_path')
    def test_delete_from_json_file_success(self, mock_get_path, mock_validate, mock_execute):
        """Test successful JSON file deletion"""
        # Arrange
        test_file_path = "/path/to/test-uuid-123userData.json"
        mock_get_path.return_value = test_file_path
        mock_validate.return_value = {"valid": True}
        mock_execute.return_value = {
            "success": True,
            "message": "Successfully deleted JSON file"
        }
        
        # Act
        result = DeleteService.delete_from_json_file(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["message"] == "Successfully deleted JSON file"
        assert result["file_path"] == test_file_path
        mock_get_path.assert_called_once_with(self.test_uuid)
        mock_validate.assert_called_once_with(test_file_path, self.test_uuid)
        mock_execute.assert_called_once_with(test_file_path)

    @patch('routes.delete.DeleteService.validate_json_file')
    @patch('routes.delete.DeleteService.get_json_file_path')
    def test_delete_from_json_file_validation_failure(self, mock_get_path, mock_validate):
        """Test JSON file deletion when validation fails"""
        # Arrange
        test_file_path = "/path/to/missing/file.json"
        mock_get_path.return_value = test_file_path
        mock_validate.return_value = {
            "valid": False,
            "error": "JSON file not found"
        }
        
        # Act
        result = DeleteService.delete_from_json_file(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "JSON file not found"
        assert result["file_path"] == test_file_path

    def test_delete_from_json_file_empty_uuid(self):
        """Test JSON file deletion with empty UUID raises exception"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_from_json_file("")
        
        assert "User UUID is required for JSON file deletion" in str(exc_info.value)

    @patch('routes.delete.DeleteService.get_json_file_path')
    def test_delete_from_json_file_unexpected_exception(self, mock_get_path):
        """Test JSON file deletion with unexpected exception"""
        # Arrange
        mock_get_path.side_effect = RuntimeError("Filesystem error")
        
        # Act
        result = DeleteService.delete_from_json_file(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert "Unexpected error during JSON file deletion" in result["error"]
        assert "Filesystem error" in result["error"]

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR get_json_file_path() HELPER FUNCTION"""

    def test_get_json_file_path_construction(self):
        """Test JSON file path construction"""
        # Act
        result_path = DeleteService.get_json_file_path(self.test_uuid)
        
        # Assert
        assert result_path.endswith(f"{self.test_uuid}userData.json")
        assert "data/conversations" in result_path
        assert os.path.isabs(result_path)  # Should be absolute path

    def test_get_json_file_path_special_characters(self):
        """Test JSON file path construction with special characters"""
        # Arrange
        special_uuid = "test-uuid-with-@#$%"
        
        # Act
        result_path = DeleteService.get_json_file_path(special_uuid)
        
        # Assert
        assert result_path.endswith(f"{special_uuid}userData.json")

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR validate_json_file() HELPER FUNCTION"""

    @patch('builtins.open', new_callable=mock_open, read_data='{"test-uuid-123": {"data": "value"}}')
    @patch('os.path.isfile')
    @patch('os.path.exists')
    def test_validate_json_file_success(self, mock_exists, mock_isfile, mock_file):
        """Test successful JSON file validation"""
        # Arrange
        test_file_path = "/path/to/test-uuid-123userData.json"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        # Act
        result = DeleteService.validate_json_file(test_file_path, self.test_uuid)
        
        # Assert
        assert result["valid"] is True
        mock_exists.assert_called_once_with(test_file_path)
        mock_isfile.assert_called_once_with(test_file_path)

    @patch('os.path.exists')
    def test_validate_json_file_not_exists(self, mock_exists):
        """Test JSON file validation when file doesn't exist"""
        # Arrange
        test_file_path = "/path/to/missing/file.json"
        mock_exists.return_value = False
        
        # Act
        result = DeleteService.validate_json_file(test_file_path, self.test_uuid)
        
        # Assert
        assert result["valid"] is False
        assert "JSON file not found" in result["error"]

    @patch('os.path.isfile')
    @patch('os.path.exists')
    def test_validate_json_file_not_a_file(self, mock_exists, mock_isfile):
        """Test JSON file validation when path is not a file"""
        # Arrange
        test_file_path = "/path/to/directory"
        mock_exists.return_value = True
        mock_isfile.return_value = False
        
        # Act
        result = DeleteService.validate_json_file(test_file_path, self.test_uuid)
        
        # Assert
        assert result["valid"] is False
        assert "Path exists but is not a file" in result["error"]

    @patch('builtins.open', new_callable=mock_open, read_data='{"other-uuid": {"data": "value"}}')
    @patch('os.path.isfile')
    @patch('os.path.exists')
    def test_validate_json_file_uuid_not_found(self, mock_exists, mock_isfile, mock_file):
        """Test JSON file validation when UUID not found in file"""
        # Arrange
        test_file_path = "/path/to/file.json"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        # Act
        result = DeleteService.validate_json_file(test_file_path, self.test_uuid)
        
        # Assert
        assert result["valid"] is False
        assert f"UUID {self.test_uuid} not found in JSON file" in result["error"]

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json content')
    @patch('os.path.isfile')
    @patch('os.path.exists')
    def test_validate_json_file_invalid_json(self, mock_exists, mock_isfile, mock_file):
        """Test JSON file validation with invalid JSON format"""
        # Arrange
        test_file_path = "/path/to/invalid.json"
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        # Act
        result = DeleteService.validate_json_file(test_file_path, self.test_uuid)
        
        # Assert
        assert result["valid"] is False
        assert "Invalid JSON format" in result["error"]

    """--------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR execute_file_deletion() HELPER FUNCTION"""

    @patch('os.remove')
    def test_execute_file_deletion_success(self, mock_remove):
        """Test successful file deletion"""
        # Arrange
        test_file_path = "/path/to/file.json"
        
        # Act
        result = DeleteService.execute_file_deletion(test_file_path)
        
        # Assert
        assert result["success"] is True
        assert result["message"] == "Successfully deleted JSON file"
        mock_remove.assert_called_once_with(test_file_path)

    @patch('os.remove')
    def test_execute_file_deletion_os_error(self, mock_remove):
        """Test file deletion with OS error"""
        # Arrange
        test_file_path = "/path/to/file.json"
        mock_remove.side_effect = OSError("Permission denied")
        
        # Act
        result = DeleteService.execute_file_deletion(test_file_path)
        
        # Assert
        assert result["success"] is False
        assert "Failed to delete JSON file: Permission denied" in result["error"]
