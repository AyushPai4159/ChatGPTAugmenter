import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.delete import DeleteService, DeleteServiceException
from database.postgres import DatabaseServiceException


class TestDeleteService:
    """Test suite for DeleteService class"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.test_uuid = "test-uuid-123"
        self.valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        self.empty_uuid = ""
        self.none_uuid = None
        self.invalid_uuid = 123  # Non-string UUID
        
        self.mock_delete_result = {
            "deleted_rows": 1,
            "success": True
        }
        
        self.mock_zero_delete_result = {
            "deleted_rows": 0,
            "success": False
        }

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR DELETE_DATA_FROM_UUID() ROOT FUNCTION"""

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_integration_delete_service_success(self, mock_delete):
        """Test successful deletion with valid UUID"""
        # Arrange
        mock_delete.return_value = self.mock_delete_result
        
        # Act
        result = DeleteService.delete_data_from_uuid(self.test_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["uuid"] == self.test_uuid
        assert result["deleted_rows"] == 1
        assert result["status"] == "deleted"
        assert "Successfully deleted data" in result["message"]
        mock_delete.assert_called_once_with(self.test_uuid)

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_integration_delete_service_no_data_found(self, mock_delete):
        """Test deletion when no data exists for UUID"""
        # Arrange
        mock_delete.return_value = self.mock_zero_delete_result
        
        # Act
        result = DeleteService.delete_data_from_uuid(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert result["uuid"] == self.test_uuid
        assert result["deleted_rows"] == 0
        assert result["status"] == "not_found"
        assert "No data found" in result["message"]
        mock_delete.assert_called_once_with(self.test_uuid)

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_integration_delete_service_database_error_not_found(self, mock_delete):
        """Test deletion when database raises not found error"""
        # Arrange
        mock_delete.side_effect = DatabaseServiceException("User not found in database")
        
        # Act
        result = DeleteService.delete_data_from_uuid(self.test_uuid)
        
        # Assert
        assert result["success"] is False
        assert result["uuid"] == self.test_uuid
        assert result["deleted_rows"] == 0
        assert result["status"] == "not_found"
        assert "No data found" in result["message"]

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_integration_delete_service_database_error_general(self, mock_delete):
        """Test deletion when database raises general error"""
        # Arrange
        mock_delete.side_effect = DatabaseServiceException("Database connection failed")
        
        # Act & Assert
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_data_from_uuid(self.test_uuid)
        
        assert "Database deletion failed" in str(exc_info.value)

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_integration_delete_service_unexpected_error(self, mock_delete):
        """Test deletion when unexpected error occurs"""
        # Arrange
        mock_delete.side_effect = Exception("Unexpected error")
        
        # Act & Assert
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_data_from_uuid(self.test_uuid)
        
        assert "Delete operation failed" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR INPUT VALIDATION"""

    def test_delete_empty_uuid(self):
        """Test deletion with empty UUID"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_data_from_uuid(self.empty_uuid)
        
        assert "UUID is required for deletion" in str(exc_info.value)

    def test_delete_none_uuid(self):
        """Test deletion with None UUID"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_data_from_uuid(self.none_uuid)
        
        assert "UUID is required for deletion" in str(exc_info.value)

    def test_delete_invalid_uuid_type(self):
        """Test deletion with non-string UUID"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_data_from_uuid(self.invalid_uuid)
        
        assert "UUID must be a string" in str(exc_info.value)

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_whitespace_uuid(self, mock_delete):
        """Test deletion with whitespace-padded UUID"""
        # Arrange
        whitespace_uuid = "  " + self.test_uuid + "  "
        mock_delete.return_value = self.mock_delete_result
        
        # Act
        result = DeleteService.delete_data_from_uuid(whitespace_uuid)
        
        # Assert
        assert result["success"] is True
        mock_delete.assert_called_once_with(self.test_uuid)  # Should be stripped

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR VERIFY_DELETION() FUNCTION"""

    @patch('routes.delete.DatabaseService.load_user_data_from_database')
    def test_verify_deletion_success(self, mock_load):
        """Test verification when data has been successfully deleted"""
        # Arrange
        mock_load.side_effect = DatabaseServiceException("User not found")
        
        # Act
        result = DeleteService.verify_deletion(self.test_uuid)
        
        # Assert
        assert result["verified"] is True
        assert result["uuid"] == self.test_uuid
        assert result["status"] == "deleted_verified"
        assert "Deletion verified" in result["message"]

    @patch('routes.delete.DatabaseService.load_user_data_from_database')
    def test_verify_deletion_data_still_exists(self, mock_load):
        """Test verification when data still exists"""
        # Arrange
        mock_load.return_value = {"some": "data"}  # Data still exists
        
        # Act
        result = DeleteService.verify_deletion(self.test_uuid)
        
        # Assert
        assert result["verified"] is False
        assert result["uuid"] == self.test_uuid
        assert result["status"] == "still_exists"
        assert "Data still exists" in result["message"]

    @patch('routes.delete.DatabaseService.load_user_data_from_database')
    def test_verify_deletion_database_error(self, mock_load):
        """Test verification when database error occurs"""
        # Arrange
        mock_load.side_effect = DatabaseServiceException("Connection failed")
        
        # Act & Assert
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.verify_deletion(self.test_uuid)
        
        assert "Verification failed" in str(exc_info.value)

    def test_verify_deletion_empty_uuid(self):
        """Test verification with empty UUID"""
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.verify_deletion(self.empty_uuid)
        
        assert "UUID is required for verification" in str(exc_info.value)

    @patch('routes.delete.DatabaseService.load_user_data_from_database')
    def test_verify_deletion_unexpected_error(self, mock_load):
        """Test verification when unexpected error occurs"""
        # Arrange
        mock_load.side_effect = Exception("Unexpected error")
        
        # Act & Assert
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.verify_deletion(self.test_uuid)
        
        assert "Deletion verification failed" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR GET_DELETION_SUMMARY() FUNCTION"""

    @patch('routes.delete.DatabaseService.get_database_size')
    @patch('routes.delete.DatabaseService.get_user_count')
    def test_get_deletion_summary_success(self, mock_user_count, mock_db_size):
        """Test successful retrieval of deletion summary"""
        # Arrange
        mock_user_count.return_value = 5
        mock_db_size.return_value = "10.5 MB"
        
        # Act
        result = DeleteService.get_deletion_summary()
        
        # Assert
        assert result["total_users"] == 5
        assert result["database_size"] == "10.5 MB"
        assert result["status"] == "active"

    @patch('routes.delete.DatabaseService.get_database_size')
    @patch('routes.delete.DatabaseService.get_user_count')
    def test_get_deletion_summary_db_size_error(self, mock_user_count, mock_db_size):
        """Test summary when database size retrieval fails"""
        # Arrange
        mock_user_count.return_value = 3
        mock_db_size.side_effect = Exception("Size calculation failed")
        
        # Act
        result = DeleteService.get_deletion_summary()
        
        # Assert
        assert result["total_users"] == 3
        assert result["database_size"] == "Unable to determine"
        assert result["status"] == "active"

    @patch('routes.delete.DatabaseService.get_user_count')
    def test_get_deletion_summary_user_count_error(self, mock_user_count):
        """Test summary when user count retrieval fails"""
        # Arrange
        mock_user_count.side_effect = Exception("Count failed")
        
        # Act & Assert
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.get_deletion_summary()
        
        assert "Failed to get deletion summary" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """EDGE CASE TESTS"""

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_with_special_characters_uuid(self, mock_delete):
        """Test deletion with UUID containing special characters"""
        # Arrange
        special_uuid = "test-uuid-with-@#$%^&*()"
        mock_delete.return_value = self.mock_delete_result
        
        # Act
        result = DeleteService.delete_data_from_uuid(special_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["uuid"] == special_uuid
        mock_delete.assert_called_once_with(special_uuid)

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_with_very_long_uuid(self, mock_delete):
        """Test deletion with very long UUID"""
        # Arrange
        long_uuid = "a" * 1000  # Very long string
        mock_delete.return_value = self.mock_delete_result
        
        # Act
        result = DeleteService.delete_data_from_uuid(long_uuid)
        
        # Assert
        assert result["success"] is True
        assert result["uuid"] == long_uuid
        mock_delete.assert_called_once_with(long_uuid)

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_result_without_deleted_rows_key(self, mock_delete):
        """Test when database result doesn't include deleted_rows key"""
        # Arrange
        mock_delete.return_value = {"success": True}  # Missing deleted_rows key
        
        # Act
        result = DeleteService.delete_data_from_uuid(self.test_uuid)
        
        # Assert
        assert result["success"] is False  # Should be False when deleted_rows is 0
        assert result["deleted_rows"] == 0
        assert result["status"] == "not_found"

    """----------------------------------------------------------------------------------------------------------------------------"""
    """INTEGRATION TESTS"""

    @patch('routes.delete.DatabaseService.load_user_data_from_database')
    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_full_delete_verify_workflow(self, mock_delete, mock_load):
        """Test complete deletion and verification workflow"""
        # Arrange
        mock_delete.return_value = self.mock_delete_result
        mock_load.side_effect = DatabaseServiceException("User not found")
        
        # Act - Delete
        delete_result = DeleteService.delete_data_from_uuid(self.test_uuid)
        
        # Act - Verify
        verify_result = DeleteService.verify_deletion(self.test_uuid)
        
        # Assert
        assert delete_result["success"] is True
        assert delete_result["status"] == "deleted"
        assert verify_result["verified"] is True
        assert verify_result["status"] == "deleted_verified"

    @patch('routes.delete.DatabaseService.get_database_size')
    @patch('routes.delete.DatabaseService.get_user_count')
    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_delete_with_summary_check(self, mock_delete, mock_user_count, mock_db_size):
        """Test deletion followed by summary check"""
        # Arrange
        mock_delete.return_value = self.mock_delete_result
        mock_user_count.return_value = 4  # One less after deletion
        mock_db_size.return_value = "8.2 MB"
        
        # Act
        delete_result = DeleteService.delete_data_from_uuid(self.test_uuid)
        summary_result = DeleteService.get_deletion_summary()
        
        # Assert
        assert delete_result["success"] is True
        assert summary_result["total_users"] == 4
        assert summary_result["database_size"] == "8.2 MB"

    """----------------------------------------------------------------------------------------------------------------------------"""
    """PERFORMANCE AND STRESS TESTS"""

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_multiple_deletions(self, mock_delete):
        """Test multiple deletion operations"""
        # Arrange
        mock_delete.return_value = self.mock_delete_result
        uuids = [f"uuid-{i}" for i in range(10)]
        
        # Act
        results = []
        for uuid in uuids:
            result = DeleteService.delete_data_from_uuid(uuid)
            results.append(result)
        
        # Assert
        assert len(results) == 10
        assert all(result["success"] for result in results)
        assert mock_delete.call_count == 10

    """----------------------------------------------------------------------------------------------------------------------------"""
    """ERROR HANDLING TESTS"""

    def test_delete_service_exception_inheritance(self):
        """Test that DeleteServiceException is properly inheriting from Exception"""
        exception = DeleteServiceException("Test error")
        assert isinstance(exception, Exception)
        assert str(exception) == "Test error"

    @patch('routes.delete.DatabaseService.delete_user_data')
    def test_exception_preservation(self, mock_delete):
        """Test that exceptions are properly preserved and re-raised"""
        # Arrange
        original_error = DatabaseServiceException("Original database error")
        mock_delete.side_effect = original_error
        
        # Act & Assert
        with pytest.raises(DeleteServiceException) as exc_info:
            DeleteService.delete_data_from_uuid(self.test_uuid)
        
        # The original error message should be preserved
        assert "Original database error" in str(exc_info.value)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
