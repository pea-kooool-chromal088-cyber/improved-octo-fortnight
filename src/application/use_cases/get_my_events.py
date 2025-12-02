from typing import Dict, Any
from src.domain.repositories.event_repository import EventRepository
from src.domain.repositories.registration_repository import RegistrationRepository


class GetMyEventsUseCase:
    """Use case for getting user's registered events"""
    
    def __init__(self, event_repository: EventRepository,
                 registration_repository: RegistrationRepository):
        self.event_repository = event_repository
        self.registration_repository = registration_repository
    
    def execute(self, user_id: str) -> Dict[str, Any]:
        """Execute the use case to get user's events"""
        registrations = self.registration_repository.get_user_registrations(user_id)
        
        if not registrations:
            return {
                "message": "You haven't registered for any events yet.",
                "events": [],
                "next_step": "main_menu",
                "keyboard": [
                    [{"text": "🎯 Browse Events", "callback_data": "browse_events"}],
                    [{"text": "📋 My Events", "callback_data": "my_events"}],
                    [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
                ]
            }
        
        event_ids = [reg.event_id for reg in registrations]
        events = []
        
        for event_id in event_ids:
            event = self.event_repository.get_event_by_id(event_id)
            if event and event.is_in_future():  # Only show future events
                events.append(event)
        
        if not events:
            return {
                "message": "You have no upcoming events. Your registered events may have already passed.",
                "events": [],
                "next_step": "main_menu",
                "keyboard": [
                    [{"text": "🎯 Browse Events", "callback_data": "browse_events"}],
                    [{"text": "📋 My Events", "callback_data": "my_events"}],
                    [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
                ]
            }
        
        message = "📋 Your Upcoming Events:\n\n"
        keyboard = []
        
        for event in events:
            formatted_date = event.date.strftime('%Y-%m-%d %H:%M')
            message += f"• <b>{event.name}</b>\n  Date: {formatted_date}\n  ID: {event.event_id}\n\n"
            keyboard.append([{
                "text": f"Unregister: {event.name[:15]}...", 
                "callback_data": f"unregister_{event.event_id}"
            }])
        
        keyboard.append([{"text": "Back to Main Menu", "callback_data": "main_menu"}])
        
        return {
            "message": message.strip(),
            "events": events,
            "next_step": "my_events",
            "keyboard": keyboard
        }