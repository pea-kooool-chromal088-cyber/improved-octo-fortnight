from typing import Dict, Any, Tuple
from src.application.use_cases.user_onboarding import UserOnboardingUseCase
from src.application.use_cases.get_main_menu import GetMainMenuUseCase
from src.domain.repositories.user_state_repository import UserStateRepository
from src.domain.entities.user_state import UserState


async def handle_message(
    update_data: Dict[str, Any],
    user_onboarding_use_case: UserOnboardingUseCase,
    get_main_menu_use_case: GetMainMenuUseCase,
    user_state_repository: UserStateRepository
) -> Dict[str, Any]:
    """
    Handle incoming message from Telegram
    
    Args:
        update_data: Telegram update object
        user_onboarding_use_case: Onboarding use case
        get_main_menu_use_case: Main menu use case
        user_state_repository: User state repository
        
    Returns:
        Response to send back to Telegram
    """
    # Check if this is a message update
    if 'message' not in update_data:
        return {"error": "No message in update"}
    
    message = update_data['message']
    user_id = str(message['from']['id'])
    user_input = message.get('text', '')
    
    # Get current user state
    current_state = await user_state_repository.get_user_state(user_id)
    
    # Determine current step
    if current_state:
        current_step = current_state.current_step
    else:
        # New user, start with main menu which will trigger onboarding
        current_step = 'main_menu'
    
    # Handle special commands
    if user_input == '/start':
        # For /start command, go to main menu
        message_text, keyboard = await get_main_menu_use_case.execute(user_id)
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
    elif current_step == 'main_menu':
        # Handle main menu interactions
        message_text, keyboard = await get_main_menu_use_case.execute(user_id)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }
    else:
        # Default response for unknown states
        message_text, keyboard = await get_main_menu_use_case.execute(user_id)
        
        return {
            "chat_id": user_id,
            "text": message_text,
            "reply_markup": {"inline_keyboard": keyboard}
        }