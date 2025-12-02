from datetime import datetime
from typing import Dict, Any, Optional
from src.domain.entities.event import Event
from src.domain.repositories.event_repository import EventRepository
from src.domain.repositories.user_repository import UserRepository


class CreateEventUseCase:
    """Use case for creating events"""
    
    def __init__(self, event_repository: EventRepository, user_repository: UserRepository):
        self.event_repository = event_repository
        self.user_repository = user_repository
    
    def execute(self, user_id: str, event_name: str, event_date_str: str) -> Dict[str, Any]:
        """Execute the use case to create an event"""
        # Check if user is admin
        user = self.user_repository.get_user_by_id(user_id)
        if not user or not user.is_admin:
            return {
                "success": False,
                "message": "Only administrators can create events",
                "next_step": "admin_menu",
                "keyboard": []
            }
        
        # Validate event date
        try:
            event_date = datetime.fromisoformat(event_date_str.replace('Z', '+00:00'))
            if event_date <= datetime.now():
                return {
                    "success": False,
                    "message": "Event date must be in the future",
                    "next_step": "creating_event_date",
                    "keyboard": []
                }
        except ValueError:
            return {
                "success": False,
                "message": "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)",
                "next_step": "creating_event_date",
                "keyboard": []
            }
        
        # Create event
        event = Event.create(
            name=event_name,
            date=event_date,
            created_by=user_id
        )
        
        created_event = self.event_repository.create_event(event)
        
        return {
            "success": True,
            "message": f"Event '{created_event.name}' created successfully for {created_event.date.strftime('%Y-%m-%d %H:%M')}",
            "event_id": created_event.event_id,
            "next_step": "admin_menu",
            "keyboard": [
                [{"text": "All Events", "callback_data": "all_events"}],
                [{"text": "Create Event", "callback_data": "create_event"}],
                [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
            ]
        }