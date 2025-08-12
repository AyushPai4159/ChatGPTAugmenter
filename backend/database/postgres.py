import psycopg
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class DatabaseServiceException(Exception):
    """Custom exception for database service errors"""
    pass


class TableNotFoundException(DatabaseServiceException):
    """Exception raised when the users table doesn't exist"""
    pass


class UserNotFoundException(DatabaseServiceException):
    """Exception raised when the specified user UUID doesn't exist in the table"""
    pass


class DatabaseService:
    """PostgreSQL database service for ChatGPT Augmenter"""
    
    # Database connection parameters - loaded from .env file in database directory
    CONNECTION_PARAMS = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    """--------------------------------------------------------------------------------------------------------------"""
    """CONNECTION MANAGEMENT FUNCTIONS"""
    
    @staticmethod
    def get_database_connection():
        """
        Establish connection to PostgreSQL database
        
        Returns:
            psycopg.Connection: Database connection
            
        Raises:
            DatabaseServiceException: If connection fails
        """
        if not DatabaseService._validate_connection_params():
            raise DatabaseServiceException("Invalid connection parameters")
            
        try:
            return DatabaseService._attempt_connection()
        except Exception as e:
            if isinstance(e, DatabaseServiceException):
                raise
            raise DatabaseServiceException(f"Database connection failed: {str(e)}")
    
    @staticmethod
    def _validate_connection_params():
        """Validate that all required connection parameters are present"""
        required_params = ["host", "port", "dbname", "user", "password"]
        return all(param in DatabaseService.CONNECTION_PARAMS and 
                  DatabaseService.CONNECTION_PARAMS[param] for param in required_params)
    
    @staticmethod
    def _attempt_connection():
        """Attempt connection using multiple connection string formats"""
        connection_attempts = DatabaseService._get_connection_strings()
        
        for i, conn_string in enumerate(connection_attempts, 1):
            try:
                conn = psycopg.connect(conn_string)
                return conn
            except psycopg.Error as attempt_error:
                if i == len(connection_attempts):
                    raise DatabaseServiceException(f"All connection methods failed. Last error: {attempt_error}")
    
    @staticmethod
    def _get_connection_strings():
        """Generate different connection string formats to try"""
        params = DatabaseService.CONNECTION_PARAMS
        return [
            f"host={params['host']} port={params['port']} dbname={params['dbname']} user={params['user']} password={params['password']}",
            f"host={params['host']} port={params['port']} dbname={params['dbname']} user={params['user']} password={params['password']} sslmode=disable",
            f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['dbname']}",
        ]
    
    @staticmethod
    def ensure_table_exists():
        """
        Create users table if it doesn't exist
        
        Raises:
            DatabaseServiceException: If table creation fails
        """
        try:
            DatabaseService._execute_table_creation()
        except Exception as e:
            if isinstance(e, DatabaseServiceException):
                raise
            raise DatabaseServiceException(f"Table creation failed: {str(e)}")
    
    @staticmethod
    def _execute_table_creation():
        """Execute the table creation SQL"""
        conn = None
        cur = None
        
        try:
            conn = DatabaseService.get_database_connection()
            cur = conn.cursor()
            
            create_table_query = DatabaseService._get_table_creation_query()
            cur.execute(create_table_query)
            conn.commit()
            
        finally:
            DatabaseService._close_connection(cur, conn)
    
    @staticmethod
    def _get_table_creation_query():
        """Get the SQL query for table creation"""
        return """
        CREATE TABLE IF NOT EXISTS users (
            uuid TEXT PRIMARY KEY,
            data JSONB,
            key_order JSONB,
            embeddings BYTEA,
            embedding_shape JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    
    @staticmethod
    def _close_connection(cursor, connection):
        """Safely close database cursor and connection"""
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    """--------------------------------------------------------------------------------------------------------------"""
    """SAVE OPERATIONS (for routes/extract.py)"""
    
    @staticmethod
    def execute_save_query(user_uuid, processed_data, key_order, embeddings, embedding_shape):
        """
        Execute the database save query (stores processed data, key ordering, and embeddings with shape)
        
        Args:
            user_uuid (str): User's UUID
            processed_data (dict): Processed conversation data (will be converted to JSON)
            key_order (list): List of keys in their preserved order
            embeddings (bytes): Embeddings data converted to bytes
            embedding_shape (tuple): Original shape of the embeddings array
            
        Returns:
            dict: Query execution result
            
        Raises:
            DatabaseServiceException: If query execution fails
        """
        try:
            if not user_uuid:
                raise DatabaseServiceException("User UUID is required")
            
            # Validate and prepare data
            prepared_data = DatabaseService._prepare_save_data(
                processed_data, key_order, embeddings, embedding_shape
            )
            
            # Execute save operation
            return DatabaseService._execute_user_save(user_uuid, prepared_data)
            
        except Exception as e:
            if isinstance(e, DatabaseServiceException):
                raise
            raise DatabaseServiceException(f"Database save operation failed: {str(e)}")
    
    @staticmethod
    def _prepare_save_data(processed_data, key_order, embeddings, embedding_shape):
        """Prepare and validate data for database save"""
        try:
            # Ensure processed_data is a valid dict
            if processed_data is None:
                processed_data = {}
            elif not isinstance(processed_data, dict):
                processed_data = {"data": processed_data}
            
            # Ensure key_order is a valid list
            if key_order is None:
                key_order = []
            elif not isinstance(key_order, list):
                key_order = list(key_order) if hasattr(key_order, '__iter__') else [key_order]
            
            # Ensure embedding_shape is valid
            if embedding_shape is None:
                embedding_shape = []
            elif not isinstance(embedding_shape, (list, tuple)):
                embedding_shape = list(embedding_shape) if hasattr(embedding_shape, '__iter__') else [embedding_shape]
            else:
                embedding_shape = list(embedding_shape)
            
            return {
                'data_json': DatabaseService._convert_to_json(processed_data),
                'key_order_json': DatabaseService._convert_to_json(key_order),
                'embeddings': embeddings,
                'embedding_shape_json': DatabaseService._convert_to_json(embedding_shape)
            }
        except Exception as e:
            raise DatabaseServiceException(f"Failed to prepare data for database save: {str(e)}")
    
    @staticmethod
    def _convert_to_json(data):
        """Convert data to JSON string safely"""
        try:
            if data is None:
                return json.dumps(None)
            elif isinstance(data, str):
                # If it's already a string, try to parse it to validate JSON, then re-serialize
                try:
                    parsed = json.loads(data)
                    return json.dumps(parsed)
                except json.JSONDecodeError:
                    # If it's not valid JSON, treat it as a regular string
                    return json.dumps(data)
            elif isinstance(data, (dict, list, int, float, bool)):
                return json.dumps(data)
            else:
                # For any other type, convert to string first
                return json.dumps(str(data))
        except Exception as e:
            # Fallback: convert to string and wrap in JSON
            return json.dumps(str(data))
    
    @staticmethod
    def _execute_user_save(user_uuid, prepared_data):
        """Execute the actual database save operation"""
        conn = None
        cur = None
        
        try:
            conn = DatabaseService.get_database_connection()
            cur = conn.cursor()
            
            # Ensure table exists before inserting
            DatabaseService.ensure_table_exists()
            
            # Execute upsert query
            user_query = DatabaseService._get_upsert_query()
            cur.execute(user_query, (
                user_uuid,
                prepared_data['data_json'],
                prepared_data['key_order_json'],
                prepared_data['embeddings'],
                prepared_data['embedding_shape_json']
            ))
            conn.commit()
            
            return DatabaseService._create_save_result(user_uuid, prepared_data, cur.rowcount)
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseServiceException(f"Database save execution failed: {str(e)}")
            
        finally:
            DatabaseService._close_connection(cur, conn)
    
    @staticmethod
    def _get_upsert_query():
        """Get the SQL query for user data upsert"""
        return """
        INSERT INTO users (uuid, data, key_order, embeddings, embedding_shape) 
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (uuid) DO UPDATE SET 
            data = EXCLUDED.data,
            key_order = EXCLUDED.key_order,
            embeddings = EXCLUDED.embeddings,
            embedding_shape = EXCLUDED.embedding_shape,
            created_at = CURRENT_TIMESTAMP;
        """
    
    @staticmethod
    def _create_save_result(user_uuid, prepared_data, rows_affected):
        """Create the result object for save operation"""
        return {
            "rows_affected": rows_affected,
            "operation": "upsert",
            "file_path": f"PostgreSQL database (user: {user_uuid})",
            "key_order_saved": len(json.loads(prepared_data['key_order_json'])),
            "embeddings_saved": len(prepared_data['embeddings']) if prepared_data['embeddings'] else 0,
            "embedding_shape": json.loads(prepared_data['embedding_shape_json'])
        }

    """--------------------------------------------------------------------------------------------------------------"""
    """LOAD OPERATIONS (for routes/search.py)"""
    
    @staticmethod
    def load_user_data_from_database(uuid):
        """
        Load user data from PostgreSQL database (processed data, key ordering, and embeddings)
        
        Args:
            uuid (str): User's UUID
            
        Returns:
            dict: User data from database including key ordering and embeddings
            
        Raises:
            DatabaseServiceException: If data loading fails
        """
        try:
            if not uuid:
                raise DatabaseServiceException("User UUID is required")
            
            # Execute load query
            raw_data = DatabaseService._execute_user_load(uuid)
            
            # Process and return formatted data
            return DatabaseService._process_loaded_data(raw_data)
            
        except Exception as e:
            if isinstance(e, DatabaseServiceException):
                raise
            raise DatabaseServiceException(f"Failed to load user data: {str(e)}")
    
    @staticmethod
    def _execute_user_load(uuid):
        """Execute the database load query"""
        conn = None
        cur = None
        
        try:
            conn = DatabaseService.get_database_connection()
            cur = conn.cursor()
            
            # Query for user data, key ordering, embeddings, and shape
            user_query = "SELECT data, key_order, embeddings, embedding_shape FROM users WHERE uuid = %s;"
            cur.execute(user_query, (uuid,))
            user_result = cur.fetchone()
            
            if not user_result:
                raise DatabaseServiceException(f"Data for user UUID {uuid} not found in database")
            
            return user_result
            
        finally:
            DatabaseService._close_connection(cur, conn)
    
    @staticmethod
    def _process_loaded_data(raw_data):
        """Process raw database data into structured format"""
        data_json, key_order_json, embeddings_bytes, embedding_shape_json = raw_data
        
        return {
            "processed_data": DatabaseService._parse_processed_data(data_json),
            "key_order": DatabaseService._parse_key_order(key_order_json),
            "embeddings": embeddings_bytes,
            "embedding_shape": DatabaseService._parse_embedding_shape(embedding_shape_json)
        }
    
    @staticmethod
    def _parse_processed_data(data_json):
        """Parse processed data from database JSON"""
        if isinstance(data_json, str):
            processed_data = json.loads(data_json)
        elif isinstance(data_json, dict):
            processed_data = data_json
        else:
            # Try to convert to dict or fallback
            try:
                processed_data = dict(data_json)
            except:
                processed_data = {"data": data_json}
        
        
        return dict(processed_data)
    
    @staticmethod
    def _parse_key_order(key_order_json):
        """Parse key ordering from database JSON"""
        if isinstance(key_order_json, str):
            return json.loads(key_order_json)
        elif isinstance(key_order_json, list):
            return key_order_json
        else:
            return []
    
    @staticmethod
    def _parse_embedding_shape(embedding_shape_json):
        """Parse embedding shape from database JSON"""
        if isinstance(embedding_shape_json, str):
            return json.loads(embedding_shape_json)
        elif isinstance(embedding_shape_json, list):
            return tuple(embedding_shape_json)
        else:
            return None

    """--------------------------------------------------------------------------------------------------------------"""
    """UTILITY OPERATIONS (for database management)"""
    
    @staticmethod
    def get_user_count():
        """
        Get total number of users in database
        
        Returns:
            int: Total user count
            
        Raises:
            DatabaseServiceException: If query fails
        """
        try:
            return DatabaseService._execute_count_query()
        except Exception as e:
            raise DatabaseServiceException(f"Failed to get user count: {str(e)}")
    
    @staticmethod
    def _execute_count_query():
        """Execute the user count query"""
        conn = None
        cur = None
        
        try:
            conn = DatabaseService.get_database_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM users;")
            count = cur.fetchone()[0]
            
            return count
            
        finally:
            DatabaseService._close_connection(cur, conn)
    
    @staticmethod
    def get_database_size():
        """
        Get database size in human-readable format
        
        Returns:
            str: Database size
            
        Raises:
            DatabaseServiceException: If query fails
        """
        try:
            return DatabaseService._execute_size_query()
        except Exception as e:
            raise DatabaseServiceException(f"Failed to get database size: {str(e)}")
    
    @staticmethod
    def _execute_size_query():
        """Execute the database size query"""
        conn = None
        cur = None
        
        try:
            conn = DatabaseService.get_database_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT pg_size_pretty(pg_database_size('test'));")
            size = cur.fetchone()[0]
            
            return size
            
        finally:
            DatabaseService._close_connection(cur, conn)
    
    @staticmethod
    def list_all_users():
        """
        List all users in database
        
        Returns:
            list: List of (uuid, created_at) tuples
            
        Raises:
            DatabaseServiceException: If query fails
        """
        try:
            return DatabaseService._execute_list_users_query()
        except Exception as e:
            raise DatabaseServiceException(f"Failed to list users: {str(e)}")
    
    @staticmethod
    def _execute_list_users_query():
        """Execute the list users query"""
        conn = None
        cur = None
        
        try:
            conn = DatabaseService.get_database_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT uuid, created_at FROM users ORDER BY created_at DESC;")
            users = cur.fetchall()
            
            return users
            
        finally:
            DatabaseService._close_connection(cur, conn)
    
    @staticmethod
    def delete_user_data(uuid):
        """
        Delete user data from database
        
        Args:
            uuid (str): User's UUID to delete
            
        Returns:
            dict: Deletion result
            
        Raises:
            TableNotFoundException: If the users table doesn't exist
            UserNotFoundException: If the specified user UUID doesn't exist
            DatabaseServiceException: If deletion fails for other reasons
        """
        try:
            if not uuid:
                raise DatabaseServiceException("User UUID is required for deletion")
            
            return DatabaseService._execute_delete_query(uuid)
            
        except (TableNotFoundException, UserNotFoundException):
            # Re-raise specific exceptions without wrapping them
            raise
        except Exception as e:
            if isinstance(e, DatabaseServiceException):
                raise
            raise DatabaseServiceException(f"Failed to delete user data: {str(e)}")
    
    @staticmethod
    def _execute_delete_query(uuid):
        """Execute the delete user query"""
        conn = None
        cur = None
        
        try:
            conn = DatabaseService.get_database_connection()
            cur = conn.cursor()
            
            # First check if the users table exists
            table_check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
            """
            cur.execute(table_check_query)
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                raise TableNotFoundException(f"Table 'users' does not exist in the database")
            
            # Check if the user exists before attempting to delete
            user_check_query = "SELECT COUNT(*) FROM users WHERE uuid = %s;"
            cur.execute(user_check_query, (uuid,))
            user_count = cur.fetchone()[0]
            
            if user_count == 0:
                raise UserNotFoundException(f"User with UUID '{uuid}' not found in the users table")
            
            # Proceed with deletion if user exists
            delete_query = "DELETE FROM users WHERE uuid = %s;"
            cur.execute(delete_query, (uuid,))
            conn.commit()
            
            return {
                "success": True,
                "deleted_rows": cur.rowcount,
                "uuid": uuid
            }
            
        except (TableNotFoundException, UserNotFoundException):
            # Re-raise our custom exceptions without wrapping them
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseServiceException(f"Database delete execution failed: {str(e)}")
            
        finally:
            DatabaseService._close_connection(cur, conn)






