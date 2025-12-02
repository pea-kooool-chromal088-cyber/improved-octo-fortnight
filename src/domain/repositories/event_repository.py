from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.event import Event


class EventRepository(ABC):
    """Interface for event repository"""
    
    @abstractmethod
    def create_event(self, event: Event) -> Event:
        """Create a new event"""
        pass
    
    @abstractmethod
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        pass
    
    @abstractmethod
    def get_all_events(self) -> List[Event]:
        """Get all events"""
        pass
    
    @abstractmethod
    def get_future_events(self) -> List[Event]:
        """Get all future events"""
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        pass