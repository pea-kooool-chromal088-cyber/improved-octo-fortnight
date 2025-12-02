from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Registration:
    """Registration entity"""
    user_id: str
    event_id: str
    created_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, user_id: str, event_id: str) -> 'Registration':
        """Create a new registration"""
        return cls(
            user_id=user_id,
            event_id=event_id,
            created_at=datetime.now()
        )