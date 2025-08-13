import os
import json
from database.postgres import DatabaseService, DatabaseServiceException, TableNotFoundException, UserNotFoundException


class DeleteServiceException(Exception):
    """Custom exception for delete service errors"""
    pass


class DeleteService:


    """--------------------------------------------------------------------------------------------------------------"""
    """ROOT FUNCTION"""

    @staticmethod
    def delete_service(user_uuid):
        """
        Main service function for deleting user data from database with JSON fallback
        
        Args:
            user_uuid (str): User's UUID to delete
            
        Returns:
            dict: Delete operation result
            
        Raises:
            DeleteServiceException: If deletion fails
        """
        try:
            # Validate input parameters
            if not user_uuid:
                raise DeleteServiceException("UUID is required for deletion")
            
            if not isinstance(user_uuid, str):
                raise DeleteServiceException("UUID must be a string")
            
            user_uuid = user_uuid.strip()
            
            # Step 1: Attempt to delete from database first
            print(f"🗑️  Attempting database deletion for user {user_uuid[:8]}...")
            db_result = DeleteService.delete_from_database(user_uuid)
            
            if db_result["success"]:
                return {
                    "success": True,
                    "message": f"Successfully deleted data for UUID: {user_uuid} from database",
                    "uuid": user_uuid,
                    "deleted_rows": db_result.get('deleted_rows', 0),
                    "status": "deleted_from_database",
                    "source": "database"
                }
            
            # Step 2: Fallback to JSON file deletion
            print(f"🗂️  Database deletion failed, attempting JSON file deletion for user {user_uuid[:8]}...")
            json_result = DeleteService.delete_from_json_file(user_uuid)
            
            if json_result["success"]:
                return {
                    "success": True,
                    "message": f"Successfully deleted data for UUID: {user_uuid} from JSON file",
                    "uuid": user_uuid,
                    "status": "deleted_from_json",
                    "source": "json_file",
                    "file_path": json_result.get("file_path")
                }
            else:
                return {
                    "success": False,
                    "message": f"No data found for UUID: {user_uuid} in database or JSON files",
                    "uuid": user_uuid,
                    "status": "not_found_anywhere",
                    "database_error": db_result.get("error"),
                    "json_error": json_result.get("error")
                }
            
        except Exception as e:
            if isinstance(e, DeleteServiceException):
                raise
            raise DeleteServiceException(f"Delete service failed: {str(e)}")

    """--------------------------------------------------------------------------------------------------------------"""
    """DELETE FROM DATABASE"""

    # SUBROOT FUNCTION
    @staticmethod
    def delete_from_database(user_uuid):
        """
        Delete user data from PostgreSQL database
        
        Args:
            user_uuid (str): User's UUID to delete
            
        Returns:
            dict: Database deletion result
            
        Raises:
            DeleteServiceException: If database operation fails unexpectedly
        """
        # Early parameter validation
        if not user_uuid:
            raise DeleteServiceException("User UUID is required for database deletion")
        
        try:
            delete_result = DatabaseService.delete_user_data(user_uuid)
            
            return {
                "success": True,
                "deleted_rows": delete_result.get('deleted_rows', 0),
                "message": "Successfully deleted from database"
            }
            
        except (TableNotFoundException, UserNotFoundException) as specific_error:
            # Expected cases where database doesn't have the data
            return {
                "success": False,
                "error": str(specific_error),
                "error_type": type(specific_error).__name__
            }
            
        except DatabaseServiceException as db_error:
            # Other database-specific errors
            return {
                "success": False,
                "error": str(db_error),
                "error_type": "DatabaseServiceException"
            }

    """--------------------------------------------------------------------------------------------------------------"""
    """DELETE FROM JSON FILE"""

    # SUBROOT FUNCTION
    @staticmethod
    def delete_from_json_file(user_uuid):
        """
        Delete user data from JSON file as fallback
        
        Args:
            user_uuid (str): User's UUID to delete
            
        Returns:
            dict: JSON file deletion result
        """
        # Early parameter validation
        if not user_uuid:
            raise DeleteServiceException("User UUID is required for JSON file deletion")
        
        try:
            # Step 1: Construct and validate file path
            json_file_path = DeleteService.get_json_file_path(user_uuid)
            
            # Step 2: Validate file existence and format
            validation_result = DeleteService.validate_json_file(json_file_path, user_uuid)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "file_path": json_file_path
                }
            
            # Step 3: Delete the file
            deletion_result = DeleteService.execute_file_deletion(json_file_path)
            
            return {
                "success": deletion_result["success"],
                "message": deletion_result.get("message"),
                "error": deletion_result.get("error"),
                "file_path": json_file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during JSON file deletion: {str(e)}",
                "file_path": json_file_path if 'json_file_path' in locals() else "unknown"
            }

    @staticmethod
    def get_json_file_path(user_uuid):
        """
        Construct the JSON file path for the given UUID
        
        Args:
            user_uuid (str): User's UUID
            
        Returns:
            str: Complete file path to the JSON file
        """
        return os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'data', 
            'conversations',
            f'{user_uuid}userData.json'
        )

    @staticmethod
    def validate_json_file(json_file_path, user_uuid):
        """
        Validate JSON file existence, format, and UUID presence
        
        Args:
            json_file_path (str): Path to the JSON file
            user_uuid (str): User's UUID to check for
            
        Returns:
            dict: Validation result with success status and error message
        """
        # Check if the JSON file exists
        if not os.path.exists(json_file_path):
            print(f"❌ JSON file not found: {json_file_path}")
            return {
                "valid": False,
                "error": f"JSON file not found: {json_file_path}"
            }
        
        # Verify it's actually a file (not a directory)
        if not os.path.isfile(json_file_path):
            print(f"❌ Path exists but is not a file: {json_file_path}")
            return {
                "valid": False,
                "error": f"Path exists but is not a file: {json_file_path}"
            }
        
        # Try to read and validate the JSON file
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check if the UUID exists in the JSON file
                if user_uuid not in data:
                    return {
                        "valid": False,
                        "error": f"UUID {user_uuid} not found in JSON file"
                    }
                    
            return {"valid": True}
            
        except json.JSONDecodeError:
            return {
                "valid": False,
                "error": f"Invalid JSON format in file: {json_file_path}"
            }
        except Exception as read_error:
            return {
                "valid": False,
                "error": f"Error reading JSON file: {str(read_error)}"
            }

    @staticmethod
    def execute_file_deletion(json_file_path):
        """
        Execute the actual file deletion from the operating system
        
        Args:
            json_file_path (str): Path to the JSON file to delete
            
        Returns:
            dict: Deletion result with success status and message
        """
        try:
            os.remove(json_file_path)
            print(f"✅ Successfully deleted JSON file: {json_file_path}")
            
            return {
                "success": True,
                "message": f"Successfully deleted JSON file"
            }
            
        except OSError as delete_error:
            return {
                "success": False,
                "error": f"Failed to delete JSON file: {str(delete_error)}"
            }


