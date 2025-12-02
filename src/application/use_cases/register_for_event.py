from typing import Dict, Any
from src.domain.entities.registration import Registration
from src.domain.repositories.event_repository import EventRepository
from src.domain.repositories.registration_repository import RegistrationRepository


class RegisterForEventUseCase:
    """Use case for registering for an event"""
    
    def __init__(self, event_repository: EventRepository, 
                 registration_repository: RegistrationRepository):
        self.event_repository = event_repository
        self.registration_repository = registration_repository
    
    def execute(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Execute the use case to register for an event"""
        # Check if event exists
        event = self.event_repository.get_event_by_id(event_id)
        if not event:
            return {
                "success": False,
                "message": "Event not found",
                "next_step": "browse_events",
                "keyboard": []
            }
        
        # Check if event is in the future
        if not event.is_in_future():
            return {
                "success": False,
                "message": "Cannot register for past events",
                "next_step": "browse_events",
                "keyboard": []
            }
        
        # Check if user is already registered
        if self.registration_repository.is_registered(user_id, event_id):
            return {
                "success": False,
                "message": "You are already registered for this event",
                "next_step": "browse_events",
                "keyboard": []
            }
        
        # Create registration
        registration = Registration.create(user_id=user_id, event_id=event_id)
        self.registration_repository.register_user(registration)
        
        return {
            "success": True,
            "message": f"Successfully registered for event: {event.name}",
            "next_step": "main_menu",
            "keyboard": [
                [{"text": "🎯 Browse Events", "callback_data": "browse_events"}],
                [{"text": "📋 My Events", "callback_data": "my_events"}],
                [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
            ]
        }