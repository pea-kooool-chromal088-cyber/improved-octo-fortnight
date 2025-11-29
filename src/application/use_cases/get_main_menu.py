from typing import Dict, List, Tuple
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.user_state_repository import UserStateRepository


class GetMainMenuUseCase:
    """Use case for getting main menu"""
    
    def __init__(
        self, 
        user_repository: UserRepository, 
        user_state_repository: UserStateRepository
    ):
        self.user_repository = user_repository
        self.user_state_repository = user_state_repository
    
    async def execute(self, user_id: str) -> Tuple[str, List[List[Dict[str, str]]]]:
        """
        Execute main menu use case
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Tuple of (message, keyboard)
        """
        # Check if user has completed onboarding
        user = await self.user_repository.get_user(user_id)
        
        if user:
            # User exists, show main menu
            message = f"Добро пожаловать, {user.first_name} {user.last_name}!"
        else:
            # User doesn't exist, prompt for onboarding
            message = "Для начала пройдите онбординг. Введите ваше имя:"
            
            # Update user state to start onboarding
            from src.domain.entities.user_state import UserState
            await self.user_state_repository.save_user_state(
                UserState(user_id=user_id, current_step='enter_first_name', context=None)
            )
        
        keyboard = self._get_main_menu_keyboard()
        return message, keyboard
    
    def _get_main_menu_keyboard(self) -> List[List[Dict[str, str]]]:
        """Get main menu keyboard"""
        return [
            [{"text": "🎯 Ближайшие события", "callback_data": "events"}],
            [{"text": "📋 Мои события", "callback_data": "my_events"}],
            [{"text": "⚙️ Админ меню", "callback_data": "admin"}],
            [{"text": "❓ Справка", "callback_data": "help"}]
        ]