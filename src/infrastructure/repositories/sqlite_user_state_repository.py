import sqlite3
from typing import Optional
from datetime import datetime
from src.domain.entities.user_state import UserState
from src.domain.repositories.user_state_repository import UserStateRepository
from src.infrastructure.database.connection import DatabaseConnection


class SqliteUserStateRepository(UserStateRepository):
    """SQLite implementation of user state repository"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
    
    async def get_user_state(self, user_id: str) -> Optional[UserState]:
        """Get user state by ID"""
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT user_id, current_step, context, updated_at FROM user_states WHERE user_id = ?",
            (user_id,)
        )
        
        row = cursor.fetchone()
        if row:
            return UserState(
                user_id=row['user_id'],
                current_step=row['current_step'],
                context=row['context'],
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
        return None
    
    async def save_user_state(self, user_state: UserState) -> None:
        """Save user state to database"""
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_states 
            (user_id, current_step, context) 
            VALUES (?, ?, ?)
        """, (
            user_state.user_id,
            user_state.current_step,
            user_state.context
        ))
        
        conn.commit()
    
    async def update_user_state(self, user_state: UserState) -> None:
        """Update existing user state"""
        # For SQLite, save and update are the same operation (upsert)
        await self.save_user_state(user_state)