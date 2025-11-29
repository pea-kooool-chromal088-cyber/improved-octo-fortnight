import sqlite3
from typing import Optional
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.connection import DatabaseConnection


class SqliteUserRepository(UserRepository):
    """SQLite implementation of user repository"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, first_name, last_name, birth_year, is_admin FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        row = cursor.fetchone()
        if row:
            return User(
                user_id=row['user_id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                birth_year=row['birth_year'],
                is_admin=bool(row['is_admin'])
            )
        return None
    
    async def save_user(self, user: User) -> None:
        """Save user to database"""
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (user_id, first_name, last_name, birth_year, is_admin) 
            VALUES (?, ?, ?, ?, ?)
        """, (
            user.user_id,
            user.first_name,
            user.last_name,
            user.birth_year,
            user.is_admin
        ))
        
        conn.commit()
    
    async def update_user(self, user: User) -> None:
        """Update existing user"""
        # For SQLite, save and update are the same operation (upsert)
        await self.save_user(user)