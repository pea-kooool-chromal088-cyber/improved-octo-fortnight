from typing import List, Optional
from datetime import datetime
from src.domain.entities.event import Event
from src.domain.repositories.event_repository import EventRepository
from src.infrastructure.database.connection import DatabaseConnection


class SqliteEventRepository(EventRepository):
    """SQLite implementation of event repository"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def create_event(self, event: Event) -> Event:
        """Create a new event"""
        conn = self.db.get_connection()
        conn.execute(
            """
            INSERT INTO events (event_id, name, date, created_by, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event.event_id, event.name, event.date.isoformat(), event.created_by, 
             event.created_at.isoformat() if event.created_at else datetime.now().isoformat())
        )
        conn.commit()
        return event
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM events WHERE event_id = ?", (event_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return Event(
            event_id=row['event_id'],
            name=row['name'],
            date=datetime.fromisoformat(row['date']),
            created_by=row['created_by'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    def get_all_events(self) -> List[Event]:
        """Get all events"""
        conn = self.db.get_connection()
        cursor = conn.execute("SELECT * FROM events ORDER BY date ASC")
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            events.append(Event(
                event_id=row['event_id'],
                name=row['name'],
                date=datetime.fromisoformat(row['date']),
                created_by=row['created_by'],
                created_at=datetime.fromisoformat(row['created_at'])
            ))
        
        return events
    
    def get_future_events(self) -> List[Event]:
        """Get all future events"""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM events WHERE date > ? ORDER BY date ASC", 
            (datetime.now().isoformat(),)
        )
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            events.append(Event(
                event_id=row['event_id'],
                name=row['name'],
                date=datetime.fromisoformat(row['date']),
                created_by=row['created_by'],
                created_at=datetime.fromisoformat(row['created_at'])
            ))
        
        return events
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
        conn.commit()
        return cursor.rowcount > 0