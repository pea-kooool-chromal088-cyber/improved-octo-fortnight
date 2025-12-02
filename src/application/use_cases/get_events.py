from typing import Dict, Any
from src.domain.repositories.event_repository import EventRepository


class GetEventsUseCase:
    """Use case for getting events"""
    
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository
    
    def execute(self, user_id: str) -> Dict[str, Any]:
        """Execute the use case to get events"""
        events = self.event_repository.get_future_events()
        
        if not events:
            return {
                "message": "No upcoming events available.",
                "events": [],
                "next_step": "main_menu",
                "keyboard": [
                    [{"text": "🎯 Browse Events", "callback_data": "browse_events"}],
                    [{"text": "📋 My Events", "callback_data": "my_events"}],
                    [{"text": "⚙️ Admin Menu", "callback_data": "admin_menu"}],
                    [{"text": "❓ Help", "callback_data": "help"}]
                ]
            }
        
        message = "🎯 Upcoming Events:\n\n"
        keyboard = []
        
        for event in events:
            formatted_date = event.date.strftime('%Y-%m-%d %H:%M')
            message += f"• <b>{event.name}</b>\n  Date: {formatted_date}\n  ID: {event.event_id}\n\n"
            keyboard.append([{
                "text": f"Register: {event.name[:20]}...", 
                "callback_data": f"register_{event.event_id}"
            }])
        
        keyboard.append([{"text": "Back to Main Menu", "callback_data": "main_menu"}])
        
        return {
            "message": message.strip(),
            "events": events,
            "next_step": "browse_events",
            "keyboard": keyboard
        }