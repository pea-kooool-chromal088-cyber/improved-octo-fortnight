import pytest
import asyncio
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository
from src.infrastructure.repositories.sqlite_user_state_repository import SqliteUserStateRepository
from src.application.use_cases.user_onboarding import UserOnboardingUseCase
from src.application.use_cases.get_main_menu import GetMainMenuUseCase
from src.domain.entities.user import User
from src.domain.entities.user_state import UserState


@pytest.mark.asyncio
async def test_full_onboarding_flow():
    """Test the full onboarding flow with real database"""
    # Use in-memory database for testing
    db = DatabaseConnection(":memory:")
    
    # Create repositories
    user_repo = SqliteUserRepository(db)
    user_state_repo = SqliteUserStateRepository(db)
    
    # Create use cases
    onboarding_use_case = UserOnboardingUseCase(user_repo, user_state_repo)
    main_menu_use_case = GetMainMenuUseCase(user_repo, user_state_repo)
    
    user_id = "123456789"
    
    # Step 1: Start with entering first name
    await user_state_repo.save_user_state(
        UserState(user_id=user_id, current_step="enter_first_name", context=None)
    )
    
    # Step 2: Enter first name
    message, next_step, keyboard = await onboarding_use_case.execute(
        user_id, "enter_first_name", "Иван"
    )
    
    assert message == "Введите вашу фамилию:"
    assert next_step == "enter_last_name"
    
    # Check that state was updated
    current_state = await user_state_repo.get_user_state(user_id)
    assert current_state.current_step == "enter_last_name"
    
    # Step 3: Enter last name
    message, next_step, keyboard = await onboarding_use_case.execute(
        user_id, "enter_last_name", "Иванов"
    )
    
    assert message == "Введите ваш год рождения:"
    assert next_step == "enter_birth_year"
    
    # Step 4: Enter birth year
    message, next_step, keyboard = await onboarding_use_case.execute(
        user_id, "enter_birth_year", "1990"
    )
    
    assert message == "Онбординг завершен! Добро пожаловать!"
    assert next_step == "main_menu"
    
    # Check that user was saved to database
    saved_user = await user_repo.get_user(user_id)
    assert saved_user is not None
    assert saved_user.first_name == "Иван"
    assert saved_user.last_name == "Иванов"
    assert saved_user.birth_year == 1990
    
    # Check that state is now main_menu
    current_state = await user_state_repo.get_user_state(user_id)
    assert current_state.current_step == "main_menu"


@pytest.mark.asyncio
async def test_main_menu_use_case():
    """Test main menu use case"""
    # Use in-memory database for testing
    db = DatabaseConnection(":memory:")
    
    # Create repositories
    user_repo = SqliteUserRepository(db)
    user_state_repo = SqliteUserStateRepository(db)
    
    # Create use case
    main_menu_use_case = GetMainMenuUseCase(user_repo, user_state_repo)
    
    user_id = "123456789"
    
    # First, create and save a user
    user = User(
        user_id=user_id,
        first_name="Иван",
        last_name="Иванов",
        birth_year=1990
    )
    await user_repo.save_user(user)
    
    # Test main menu for existing user
    message, keyboard = await main_menu_use_case.execute(user_id)
    
    assert "Иван Иванов" in message
    assert len(keyboard) == 4  # Should have 4 menu buttons


if __name__ == "__main__":
    pytest.main([__file__])