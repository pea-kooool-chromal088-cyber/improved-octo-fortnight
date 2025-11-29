import sqlite3
from typing import Optional
import os


class DatabaseConnection:
    """Database connection manager for SQLite"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection, creating it if necessary"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self._create_tables()
        return self.connection
    
    def _create_tables(self) -> None:
        """Create required tables if they don't exist"""
        conn = self.get_connection()
        
        # Create users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birth_year INTEGER NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_states table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_states (
                user_id TEXT PRIMARY KEY,
                current_step TEXT NOT NULL,
                context TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    
    def close(self) -> None:
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __del__(self):
        """Cleanup on object deletion"""
        self.close()