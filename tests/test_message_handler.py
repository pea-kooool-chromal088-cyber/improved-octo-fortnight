import pytest
import asyncio
from src.presentation.telegram.handlers.message_handlers import handle_message
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository
from src.infrastructure.repositories.sqlite_user_state_repository import SqliteUserStateRepository
from src.application.use_cases.user_onboarding import UserOnboardingUseCase
from src.application.use_cases.get_main_menu import GetMainMenuUseCase


@pytest.mark.asyncio
async def test_message_handler_start_command():
    """Test message handler with /start command"""
    # Setup
    db = DatabaseConnection(":memory:")
    user_repo = SqliteUserRepository(db)
    user_state_repo = SqliteUserStateRepository(db)
    
    onboarding_use_case = UserOnboardingUseCase(user_repo, user_state_repo)
    main_menu_use_case = GetMainMenuUseCase(user_repo, user_state_repo)
    
    # Simulate Telegram update with /start command
    update_data = {
        "message": {
            "from": {"id": 123456789},
            "text": "/start"
        }
    }
    
    response = await handle_message(
        update_data,
        onboarding_use_case,
        main_menu_use_case,
        user_state_repo
    )
    
    assert "chat_id" in response
    assert "text" in response
    assert "reply_markup" in response
    assert response["chat_id"] == "123456789"


@pytest.mark.asyncio
async def test_message_handler_onboarding_flow():
    """Test message handler during onboarding flow"""
    # Setup
    db = DatabaseConnection(":memory:")
    user_repo = SqliteUserRepository(db)
    user_state_repo = SqliteUserStateRepository(db)
    
    onboarding_use_case = UserOnboardingUseCase(user_repo, user_state_repo)
    main_menu_use_case = GetMainMenuUseCase(user_repo, user_state_repo)
    
    user_id = "123456789"
    
    # Set initial state for onboarding
    from src.domain.entities.user_state import UserState
    await user_state_repo.save_user_state(
        UserState(user_id=user_id, current_step="enter_first_name", context=None)
    )
    
    # Simulate user sending their first name
    update_data = {
        "message": {
            "from": {"id": user_id},
            "text": "Иван"
        }
    }
    
    response = await handle_message(
        update_data,
        onboarding_use_case,
        main_menu_use_case,
        user_state_repo
    )
    
    assert "chat_id" in response
    assert "text" in response
    assert "reply_markup" in response
    assert response["chat_id"] == user_id
    assert "фамилию" in response["text"]  # Should ask for last name next


if __name__ == "__main__":
    pytest.main([__file__])