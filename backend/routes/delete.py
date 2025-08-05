import os
import sys
from database.postgres import DatabaseService, DatabaseServiceException


class DeleteServiceException(Exception):
    """Custom exception for delete service errors"""
    pass


class DeleteService:
    """Delete service for ChatGPT Augmenter - handles data deletion operations"""
    
    @staticmethod
    def delete_data_from_uuid(uuid):
        """
        Delete user data from database using UUID
        
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
            
            # Attempt to delete from database
            try:
                delete_result = DatabaseService.delete_user_data(uuid)
                
                # Check if any rows were actually deleted
                if delete_result.get('deleted_rows', 0) == 0:
                    return {
                        "success": False,
                        "message": f"No data found for UUID: {uuid}",
                        "uuid": uuid,
                        "deleted_rows": 0,
                        "status": "not_found"
                    }
                
                # Success case
                return {
                    "success": True,
                    "message": f"Successfully deleted data for UUID: {uuid}",
                    "uuid": uuid,
                    "deleted_rows": delete_result.get('deleted_rows', 0),
                    "status": "deleted"
                }
                
            except DatabaseServiceException as db_error:
                # Handle database-specific errors
                if "not found" in str(db_error).lower():
                    return {
                        "success": False,
                        "message": f"No data found for UUID: {uuid}",
                        "uuid": uuid,
                        "deleted_rows": 0,
                        "status": "not_found"
                    }
                else:
                    raise DeleteServiceException(f"Database deletion failed: {str(db_error)}")
            
        except DeleteServiceException:
            # Re-raise delete service exceptions
            raise
        except Exception as e:
            # Handle any other unexpected errors
            raise DeleteServiceException(f"Delete operation failed: {str(e)}")
    
    @staticmethod
    def verify_deletion(uuid):
        """
        Verify that user data has been successfully deleted
        
        Args:
            uuid (str): User's UUID to verify
            
        Returns:
            dict: Verification result
            
        Raises:
            DeleteServiceException: If verification fails
        """
        try:
            if not uuid:
                raise DeleteServiceException("UUID is required for verification")
            
            # Try to load the user data to see if it still exists
            try:
                DatabaseService.load_user_data_from_database(uuid)
                # If we get here, data still exists
                return {
                    "verified": False,
                    "message": f"Data still exists for UUID: {uuid}",
                    "uuid": uuid,
                    "status": "still_exists"
                }
            except DatabaseServiceException as e:
                if "not found" in str(e).lower():
                    # Data not found means deletion was successful
                    return {
                        "verified": True,
                        "message": f"Deletion verified - no data found for UUID: {uuid}",
                        "uuid": uuid,
                        "status": "deleted_verified"
                    }
                else:
                    # Some other database error
                    raise DeleteServiceException(f"Verification failed: {str(e)}")
                    
        except DeleteServiceException:
            raise
        except Exception as e:
            raise DeleteServiceException(f"Deletion verification failed: {str(e)}")
    
    @staticmethod
    def get_deletion_summary():
        """
        Get summary of deletion operations (useful for admin/monitoring)
        
        Returns:
            dict: Summary of database state
            
        Raises:
            DeleteServiceException: If summary retrieval fails
        """
        try:
            # Get current user count
            user_count = DatabaseService.get_user_count()
            
            # Get database size
            try:
                db_size = DatabaseService.get_database_size()
            except:
                db_size = "Unable to determine"
            
            return {
                "total_users": user_count,
                "database_size": db_size,
                "status": "active"
            }
            
        except Exception as e:
            raise DeleteServiceException(f"Failed to get deletion summary: {str(e)}")
