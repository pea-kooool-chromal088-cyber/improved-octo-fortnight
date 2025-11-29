from typing import Dict, List, Optional, Tuple
from src.domain.entities.user import User
from src.domain.entities.user_state import UserState
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.user_state_repository import UserStateRepository


class UserOnboardingUseCase:
    """Use case for user onboarding process"""
    
    def __init__(
        self, 
        user_repository: UserRepository, 
        user_state_repository: UserStateRepository
    ):
        self.user_repository = user_repository
        self.user_state_repository = user_state_repository
    
    async def execute(
        self, 
        user_id: str, 
        current_step: str, 
        user_input: str
    ) -> Tuple[str, str, List[List[Dict[str, str]]]]:
        """
        Execute onboarding use case
        
        Args:
            user_id: Telegram user ID
            current_step: Current step in the onboarding process
            user_input: Text input from user
            
        Returns:
            Tuple of (message, next_step, keyboard)
        """
        # Validate the input based on the current step
        validation_result = self._validate_input(current_step, user_input)
        
        if not validation_result[0]:  # If validation fails
            error_message = validation_result[1]
            return error_message, current_step, self._get_error_keyboard()
        
        # If validation passes, update user data and state
        if current_step == 'enter_first_name':
            return await self._handle_first_name(user_id, user_input)
        elif current_step == 'enter_last_name':
            return await self._handle_last_name(user_id, user_input)
        elif current_step == 'enter_birth_year':
            return await self._handle_birth_year(user_id, user_input)
        else:
            # Default to main menu if step is not recognized
            return "Добро пожаловать! Выберите действие:", "main_menu", self._get_main_menu_keyboard()
    
    def _validate_input(self, step: str, user_input: str) -> Tuple[bool, str]:
        """Validate user input based on the current step"""
        user_input = user_input.strip()
        
        if not user_input:
            return False, "Пожалуйста, введите значение."
        
        if step == 'enter_first_name':
            if not user_input.replace(" ", "").isalpha():
                return False, "Имя должно содержать только буквы."
            if len(user_input) > 50:
                return False, "Имя слишком длинное (максимум 50 символов)."
            return True, ""
        
        elif step == 'enter_last_name':
            if not user_input.replace(" ", "").isalpha():
                return False, "Фамилия должна содержать только буквы."
            if len(user_input) > 50:
                return False, "Фамилия слишком длинная (максимум 50 символов)."
            return True, ""
        
        elif step == 'enter_birth_year':
            try:
                year = int(user_input)
                if year < 1900 or year > 2024:
                    return False, "Год рождения должен быть между 1900 и 2024."
                return True, ""
            except ValueError:
                return False, "Пожалуйста, введите год рождения числом."
        
        return True, ""  # For other steps, assume valid
    
    async def _handle_first_name(self, user_id: str, first_name: str) -> Tuple[str, str, List[List[Dict[str, str]]]]:
        """Handle first name input"""
        # Get current user state
        current_state = await self.user_state_repository.get_user_state(user_id)
        
        # Update context with first name
        import json
        if current_state and current_state.context:
            context_data = json.loads(current_state.context)
        else:
            context_data = {}
        
        context_data["first_name"] = first_name
        
        # Save updated state
        await self.user_state_repository.save_user_state(
            UserState(user_id=user_id, current_step='enter_last_name', context=json.dumps(context_data))
        )
        
        return "Введите вашу фамилию:", "enter_last_name", self._get_cancel_keyboard()
    
    async def _handle_last_name(self, user_id: str, last_name: str) -> Tuple[str, str, List[List[Dict[str, str]]]]:
        """Handle last name input"""
        # Get current user state
        current_state = await self.user_state_repository.get_user_state(user_id)
        
        # Update context with last name
        import json
        if current_state and current_state.context:
            context_data = json.loads(current_state.context)
        else:
            context_data = {}
        context_data["last_name"] = last_name
        
        # Save updated state
        await self.user_state_repository.save_user_state(
            UserState(user_id=user_id, current_step='enter_birth_year', context=json.dumps(context_data))
        )
        
        return "Введите ваш год рождения:", "enter_birth_year", self._get_cancel_keyboard()
    
    async def _handle_birth_year(self, user_id: str, birth_year: str) -> Tuple[str, str, List[List[Dict[str, str]]]]:
        """Handle birth year input and complete onboarding"""
        # Get current user state and context
        current_state = await self.user_state_repository.get_user_state(user_id)
        
        context_data = {}
        if current_state and current_state.context:
            import json
            context_data = json.loads(current_state.context)
        
        # Create user object
        user = User(
            user_id=user_id,
            first_name=context_data.get("first_name", ""),
            last_name=context_data.get("last_name", ""),
            birth_year=int(birth_year)
        )
        
        # Save user to database
        await self.user_repository.save_user(user)
        
        # Update user state to main menu
        await self.user_state_repository.save_user_state(
            UserState(user_id=user_id, current_step='main_menu', context=None)
        )
        
        return "Онбординг завершен! Добро пожаловать!", "main_menu", self._get_main_menu_keyboard()
    
    def _get_cancel_keyboard(self) -> List[List[Dict[str, str]]]:
        """Get keyboard with cancel button"""
        return [[{"text": "Отмена", "callback_data": "cancel"}]]
    
    def _get_error_keyboard(self) -> List[List[Dict[str, str]]]:
        """Get keyboard for error states"""
        return [[{"text": "Повторить ввод", "callback_data": "retry"}]]
    
    def _get_main_menu_keyboard(self) -> List[List[Dict[str, str]]]:
        """Get main menu keyboard"""
        return [
            [{"text": "🎯 Ближайшие события", "callback_data": "events"}],
            [{"text": "📋 Мои события", "callback_data": "my_events"}],
            [{"text": "⚙️ Админ меню", "callback_data": "admin"}],
            [{"text": "❓ Справка", "callback_data": "help"}]
        ]