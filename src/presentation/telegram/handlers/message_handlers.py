from typing import Dict, Any
from src.application.use_cases.user_onboarding import UserOnboardingUseCase
from src.application.use_cases.get_main_menu import GetMainMenuUseCase
from src.application.use_cases.create_event import CreateEventUseCase
from src.application.use_cases.get_events import GetEventsUseCase
from src.application.use_cases.register_for_event import RegisterForEventUseCase
from src.application.use_cases.get_my_events import GetMyEventsUseCase
from src.application.use_cases.unregister_from_event import UnregisterFromEventUseCase
from src.domain.repositories.user_state_repository import UserStateRepository
from src.domain.entities.user_state import UserState
import json


async def handle_message(
    update_data: Dict[str, Any],
    user_onboarding_use_case: UserOnboardingUseCase,
    get_main_menu_use_case: GetMainMenuUseCase,
    create_event_use_case: CreateEventUseCase,
    get_events_use_case: GetEventsUseCase,
    register_for_event_use_case: RegisterForEventUseCase,
    get_my_events_use_case: GetMyEventsUseCase,
    unregister_from_event_use_case: UnregisterFromEventUseCase,
    user_state_repository: UserStateRepository
) -> Dict[str, Any]:
    """
    Handle incoming message from Telegram
    
    Args:
        update_data: Telegram update object
        user_onboarding_use_case: Onboarding use case
        get_main_menu_use_case: Main menu use case
        create_event_use_case: Create event use case
        get_events_use_case: Get events use case
        register_for_event_use_case: Register for event use case
        get_my_events_use_case: Get my events use case
        unregister_from_event_use_case: Unregister from event use case
        user_state_repository: User state repository
        
    Returns:
        Response to send back to Telegram
    """
    # Check if this is a callback query (from inline buttons)
    if 'callback_query' in update_data:
        callback_query = update_data['callback_query']
        user_id = str(callback_query['from']['id'])
        callback_data = callback_query['data']
        message = callback_query.get('message', {})
    # Check if this is a message update
    elif 'message' in update_data:
        message = update_data['message']
        user_id = str(message['from']['id'])
        callback_data = message.get('text', '')
    else:
        return {"error": "No message or callback query in update"}

    # Get current user state
    current_state = await user_state_repository.get_user_state(user_id)
    
    # Determine current step
    if current_state:
        current_step = current_state.current_step
    else:
        # New user, start with main menu which will trigger onboarding
        current_step = 'main_menu'

    # Handle callback commands
    if callback_data.startswith('main_menu'):
        message_text, keyboard = await get_main_menu_use_case.execute(user_id)
        new_state = UserState(user_id=user_id, current_step='main_menu', context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif callback_data.startswith('browse_events'):
        result = get_events_use_case.execute(user_id)
        message_text = result['message']
        keyboard = result['keyboard']
        next_step = result['next_step']
        
        new_state = UserState(user_id=user_id, current_step=next_step, context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif callback_data.startswith('my_events'):
        result = get_my_events_use_case.execute(user_id)
        message_text = result['message']
        keyboard = result['keyboard']
        next_step = result['next_step']
        
        new_state = UserState(user_id=user_id, current_step=next_step, context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif callback_data.startswith('admin_menu'):
        # Create a simple admin menu
        user = get_main_menu_use_case.user_repository.get_user_by_id(user_id)
        if user and user.is_admin:
            message_text = "⚙️ Admin Menu:\n\nSelect an action:"
            keyboard = [
                [{"text": "➕ Create Event", "callback_data": "create_event"}],
                [{"text": "📊 All Events", "callback_data": "all_events"}],
                [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
            ]
            new_state = UserState(user_id=user_id, current_step='admin_menu', context=None)
            await user_state_repository.save_user_state(new_state)
            
            return {
                "chat_id": user_id,
                "text": message_text,
                "reply_markup": {"inline_keyboard": keyboard}
            }
        else:
            message_text = "You don't have admin privileges."
            keyboard = [
                [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
            ]
            return {
                "chat_id": user_id,
                "text": message_text,
                "reply_markup": {"inline_keyboard": keyboard}
            }
    elif callback_data.startswith('create_event'):
        # Check if user is admin
        user = get_main_menu_use_case.user_repository.get_user_by_id(user_id)
        if not (user and user.is_admin):
            message_text = "You don't have admin privileges to create events."
            keyboard = [
                [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
            ]
            return {
                "chat_id": user_id,
                "text": message_text,
                "reply_markup": {"inline_keyboard": keyboard}
            }
        
        # Start event creation process
        message_text = "Enter the event name:"
        keyboard = [[{"text": "Cancel", "callback_data": "admin_menu"}]]
        new_state = UserState(user_id=user_id, current_step='creating_event_name', context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif callback_data.startswith('register_'):
        # Extract event_id from callback_data (format: register_EVENTID)
        event_id = callback_data.split('_')[1]
        result = register_for_event_use_case.execute(user_id, event_id)
        message_text = result['message']
        keyboard = result.get('keyboard', [])
        
        # Set the next step based on the result
        next_step = result.get('next_step', 'main_menu')
        new_state = UserState(user_id=user_id, current_step=next_step, context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif callback_data.startswith('unregister_'):
        # Extract event_id from callback_data (format: unregister_EVENTID)
        event_id = callback_data.split('_')[1]
        result = unregister_from_event_use_case.execute(user_id, event_id)
        message_text = result['message']
        keyboard = result.get('keyboard', [])
        
        # Set the next step based on the result
        next_step = result.get('next_step', 'my_events')
        new_state = UserState(user_id=user_id, current_step=next_step, context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif callback_data.startswith('help'):
        message_text = "❓ Help:\n\nThis bot helps you manage and register for events.\n\nCommands:\n/start - Start the bot\n\nMenu options:\n🎯 Browse Events - View upcoming events\n📋 My Events - View your registered events\n⚙️ Admin Menu - Create events (admin only)"
        keyboard = [
            [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
        ]
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }

    # Handle text input based on current step
    user_input = message.get('text', '')

    # Handle special commands
    if user_input == '/start':
        # For /start command, go to main menu
        message_text, keyboard = await get_main_menu_use_case.execute(user_id)
        new_state = UserState(user_id=user_id, current_step='main_menu', context=None)
        await user_state_repository.save_user_state(new_state)
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }

    # Handle onboarding flow based on current step
    if current_step in ['enter_first_name', 'enter_last_name', 'enter_birth_year']:
        # Process onboarding step
        message_text, next_step, keyboard = await user_onboarding_use_case.execute(
            user_id, current_step, user_input
        )
        
        # Update user state with new step, preserving context if available
        new_state = UserState(user_id=user_id, current_step=next_step, context=current_state.context if current_state else None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    # Handle event creation steps
    elif current_step == 'creating_event_name':
        # Store the event name temporarily in context and ask for date
        context = {"event_name": user_input}
        message_text = "Enter the event date (YYYY-MM-DD HH:MM format):"
        keyboard = [[{"text": "Cancel", "callback_data": "admin_menu"}]]
        new_state = UserState(user_id=user_id, current_step='creating_event_date', context=str(context))
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif current_step == 'creating_event_date':
        # Get the stored event name from context
        try:
            context = json.loads(current_state.context) if current_state.context else {}
            event_name = context.get("event_name", "")
        except:
            event_name = ""
        
        if not event_name:
            message_text = "Error: Event name not found. Please start again."
            keyboard = [[{"text": "Back to Admin Menu", "callback_data": "admin_menu"}]]
            return {
                "chat_id": user_id,
                "text": message_text,
                "reply_markup": {"inline_keyboard": keyboard}
            }
        
        # Create the event
        result = create_event_use_case.execute(user_id, event_name, user_input)
        message_text = result['message']
        
        if result['success']:
            keyboard = [
                [{"text": "All Events", "callback_data": "all_events"}],
                [{"text": "Create Event", "callback_data": "create_event"}],
                [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
            ]
            next_step = result.get('next_step', 'admin_menu')
        else:
            keyboard = [[{"text": "Try Again", "callback_data": "create_event"}], [{"text": "Back", "callback_data": "admin_menu"}]]
            next_step = result.get('next_step', 'creating_event_date')
        
        new_state = UserState(user_id=user_id, current_step=next_step, context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif current_step == 'main_menu':
        # Handle main menu interactions
        message_text, keyboard = await get_main_menu_use_case.execute(user_id)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    elif current_step == 'admin_menu':
        # Handle admin menu interactions
        user = get_main_menu_use_case.user_repository.get_user_by_id(user_id)
        if user and user.is_admin:
            message_text = "⚙️ Admin Menu:\n\nSelect an action:"
            keyboard = [
                [{"text": "➕ Create Event", "callback_data": "create_event"}],
                [{"text": "📊 All Events", "callback_data": "all_events"}],
                [{"text": "Back to Main Menu", "callback_data": "main_menu"}]
            ]
            return {
                "chat_id": user_id,
                "text": message_text,
                "reply_markup": {"inline_keyboard": keyboard}
            }
    
    else:
        # Default response for unknown states
        message_text, keyboard = await get_main_menu_use_case.execute(user_id)
        new_state = UserState(user_id=user_id, current_step='main_menu', context=None)
        await user_state_repository.save_user_state(new_state)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }