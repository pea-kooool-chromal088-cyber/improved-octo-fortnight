from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.registration import Registration


class RegistrationRepository(ABC):
    """Interface for registration repository"""
    
    @abstractmethod
    def register_user(self, registration: Registration) -> Registration:
        """Register user for an event"""
        pass
    
    @abstractmethod
    def unregister_user(self, user_id: str, event_id: str) -> bool:
        """Unregister user from an event"""
        pass
    
    @abstractmethod
    def is_registered(self, user_id: str, event_id: str) -> bool:
        """Check if user is registered for an event"""
        pass
    
    @abstractmethod
    def get_user_registrations(self, user_id: str) -> List[Registration]:
        """Get all registrations for a user"""
        pass
    
    @abstractmethod
    def get_event_registrations(self, event_id: str) -> List[Registration]:
        """Get all registrations for an event"""
        pass