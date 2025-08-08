import os
import sys
import json
from database.postgres import DatabaseService, DatabaseServiceException, TableNotFoundException, UserNotFoundException


class DeleteServiceException(Exception):
    """Custom exception for delete service errors"""
    pass


class DeleteService:
    """Delete service for ChatGPT Augmenter - handles data deletion operations"""
    
    @staticmethod
    def delete_data_from_uuid(uuid):
        """
        Delete user data from database using UUID, with fallback to JSON file deletion
        
        Args:
            uuid (str): User's UUID to delete
            
        Returns:
            dict: Delete operation result
            
        Raises:
            DeleteServiceException: If deletion fails
        """
        try:
            # Validate input parameters
            if not uuid:
                raise DeleteServiceException("UUID is required for deletion")
            
            if not isinstance(uuid, str):
                raise DeleteServiceException("UUID must be a string")
            
            uuid = uuid.strip()
            
            # Attempt to delete from database first
            try:
                delete_result = DatabaseService.delete_user_data(uuid)
                
                return {
                    "success": True,
                    "message": f"Successfully deleted data for UUID: {uuid} from database",
                    "uuid": uuid,
                    "deleted_rows": delete_result.get('deleted_rows', 0),
                    "status": "deleted_from_database",
                    "source": "database"
                }
                
                
            except DatabaseServiceException as db_error:
                # Handle other database-specific errors
                print(f"Database deletion failed")
                print(f"Attempting JSON file deletion for UUID: {uuid}")
                
                json_result = DeleteService._delete_from_json_file(uuid)
                
                if json_result["success"]:
                    return {
                        "success": True,
                        "message": f"Successfully deleted data for UUID: {uuid} from JSON file",
                        "uuid": uuid,
                        "status": "deleted_from_json",
                        "source": "json_file",
                        "file_path": json_result.get("file_path")
                    }
                else:
                    return {
                        "success": False,
                        "message": f"No data found for UUID: {uuid} in database or JSON files",
                        "uuid": uuid,
                        "status": "not_found_anywhere",
                        "database_error": str(db_error),
                        "json_error": json_result.get("error")
                    }
            
        except DeleteServiceException:
            # Re-raise delete service exceptions
            raise
        except Exception as e:
            # Handle any other unexpected errors
            raise DeleteServiceException(f"Delete operation failed: {str(e)}")
    
    @staticmethod
    def _delete_from_json_file(uuid):
        """
        Delete user data from JSON file as fallback
        
        Args:
            uuid (str): User's UUID to delete
            
        Returns:
            dict: Result of JSON file deletion attempt
        """
        try:
            # Construct the JSON file path
            json_file_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 
                'data', 
                'conversations',
                f'{uuid}userData.json'
            )
            
            # Check if the JSON file exists
            if not os.path.exists(json_file_path):
                return {
                    "success": False,
                    "error": f"JSON file not found: {json_file_path}",
                    "file_path": json_file_path
                }
            
            # Verify it's actually a file (not a directory)
            if not os.path.isfile(json_file_path):
                return {
                    "success": False,
                    "error": f"Path exists but is not a file: {json_file_path}",
                    "file_path": json_file_path
                }
            
            # Try to read and validate the JSON file before deletion
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if the UUID exists in the JSON file
                    if uuid not in data:
                        return {
                            "success": False,
                            "error": f"UUID {uuid} not found in JSON file",
                            "file_path": json_file_path
                        }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": f"Invalid JSON format in file: {json_file_path}",
                    "file_path": json_file_path
                }
            except Exception as read_error:
                return {
                    "success": False,
                    "error": f"Error reading JSON file: {str(read_error)}",
                    "file_path": json_file_path
                }
            
            # Delete the JSON file from the operating system
            try:
                os.remove(json_file_path)
                print(f"✅ Successfully deleted JSON file: {json_file_path}")
                
                return {
                    "success": True,
                    "message": f"Successfully deleted JSON file for UUID: {uuid}",
                    "file_path": json_file_path
                }
                
            except OSError as delete_error:
                return {
                    "success": False,
                    "error": f"Failed to delete JSON file: {str(delete_error)}",
                    "file_path": json_file_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during JSON file deletion: {str(e)}",
                "file_path": json_file_path if 'json_file_path' in locals() else "unknown"
            }

