from typing import Dict, Any
from src.domain.repositories.event_repository import EventRepository
from src.domain.repositories.registration_repository import RegistrationRepository


class UnregisterFromEventUseCase:
    """Use case for unregistering from an event"""
    
    def __init__(self, event_repository: EventRepository,
                 registration_repository: RegistrationRepository):
        self.event_repository = event_repository
        self.registration_repository = registration_repository
    
    def execute(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Execute the use case to unregister from an event"""
        # Check if event exists
        event = self.event_repository.get_event_by_id(event_id)
        if not event:
            return {
                "success": False,
                "message": "Event not found",
                "next_step": "my_events",
                "keyboard": []
            }
        
        # Check if user is registered for the event
        if not self.registration_repository.is_registered(user_id, event_id):
            return {
                "success": False,
                "message": "You are not registered for this event",
                "next_step": "my_events",
                "keyboard": []
            }
        
        # Unregister user
        success = self.registration_repository.unregister_user(user_id, event_id)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully unregistered from event: {event.name}",
                "next_step": "my_events",
                "keyboard": [
                    [{"text": "📋 My Events", "callback_data": "my_events"}],
                    [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
                ]
            }
        else:
            return {
                "success": False,
                "message": "Failed to unregister from event",
                "next_step": "my_events",
                "keyboard": []
            }