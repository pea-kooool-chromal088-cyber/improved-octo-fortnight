from typing import List
from datetime import datetime
from src.domain.entities.registration import Registration
from src.domain.repositories.registration_repository import RegistrationRepository
from src.infrastructure.database.connection import DatabaseConnection


class SqliteRegistrationRepository(RegistrationRepository):
    """SQLite implementation of registration repository"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def register_user(self, registration: Registration) -> Registration:
        """Register user for an event"""
        conn = self.db.get_connection()
        conn.execute(
            """
            INSERT INTO registrations (user_id, event_id, created_at)
            VALUES (?, ?, ?)
            """,
            (registration.user_id, registration.event_id, 
             registration.created_at.isoformat() if registration.created_at else datetime.now().isoformat())
        )
        conn.commit()
        return registration
    
    def unregister_user(self, user_id: str, event_id: str) -> bool:
        """Unregister user from an event"""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "DELETE FROM registrations WHERE user_id = ? AND event_id = ?", 
            (user_id, event_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    
    def is_registered(self, user_id: str, event_id: str) -> bool:
        """Check if user is registered for an event"""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT 1 FROM registrations WHERE user_id = ? AND event_id = ? LIMIT 1", 
            (user_id, event_id)
        )
        row = cursor.fetchone()
        return row is not None
    
    def get_user_registrations(self, user_id: str) -> List[Registration]:
        """Get all registrations for a user"""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM registrations WHERE user_id = ? ORDER BY created_at ASC", 
            (user_id,)
        )
        rows = cursor.fetchall()
        
        registrations = []
        for row in rows:
            registrations.append(Registration(
                user_id=row['user_id'],
                event_id=row['event_id'],
                created_at=datetime.fromisoformat(row['created_at'])
            ))
        
        return registrations
    
    def get_event_registrations(self, event_id: str) -> List[Registration]:
        """Get all registrations for an event"""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM registrations WHERE event_id = ? ORDER BY created_at ASC", 
            (event_id,)
        )
        rows = cursor.fetchall()
        
        registrations = []
        for row in rows:
            registrations.append(Registration(
                user_id=row['user_id'],
                event_id=row['event_id'],
                created_at=datetime.fromisoformat(row['created_at'])
            ))
        
        return registrations