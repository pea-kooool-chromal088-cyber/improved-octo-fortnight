from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Event:
    """Event entity"""
    event_id: str
    name: str
    date: datetime
    created_by: str
    created_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, name: str, date: datetime, created_by: str) -> 'Event':
        """Create a new event with a unique ID"""
        return cls(
            event_id=str(uuid.uuid4()),
            name=name,
            date=date,
            created_by=created_by,
            created_at=datetime.now()
        )
    
    def is_in_future(self) -> bool:
        """Check if event is in the future"""
        return self.date > datetime.now()