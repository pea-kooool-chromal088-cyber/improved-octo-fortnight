import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.domain.entities.user import User
from src.domain.entities.user_state import UserState
from src.application.use_cases.user_onboarding import UserOnboardingUseCase
from src.application.use_cases.get_main_menu import GetMainMenuUseCase
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository
from src.infrastructure.repositories.sqlite_user_state_repository import SqliteUserStateRepository


@pytest.mark.asyncio
async def test_user_entity_creation():
    """Test creating a valid user entity"""
    user = User(
        user_id="123456789",
        first_name="Иван",
        last_name="Иванов",
        birth_year=1990
    )
    
    assert user.user_id == "123456789"
    assert user.first_name == "Иван"
    assert user.last_name == "Иванов"
    assert user.birth_year == 1990
    assert user.is_admin is False


@pytest.mark.asyncio
async def test_user_entity_validation():
    """Test user entity validation"""
    # Test empty first name
    with pytest.raises(ValueError):
        User(
            user_id="123456789",
            first_name="",
            last_name="Иванов",
            birth_year=1990
        )
    
    # Test empty last name
    with pytest.raises(ValueError):
        User(
            user_id="123456789",
            first_name="Иван",
            last_name="",
            birth_year=1990
        )
    
    # Test invalid birth year
    with pytest.raises(ValueError):
        User(
            user_id="123456789",
            first_name="Иван",
            last_name="Иванов",
            birth_year=1800  # Too old
        )


@pytest.mark.asyncio
async def test_user_state_entity():
    """Test user state entity"""
    user_state = UserState(
        user_id="123456789",
        current_step="enter_first_name",
        context='{"temp": "data"}'
    )
    
    assert user_state.user_id == "123456789"
    assert user_state.current_step == "enter_first_name"
    assert user_state.context_data == {"temp": "data"}
    
    # Test updating context
    new_state = user_state.update_context({"new": "value"})
    assert new_state.context_data == {"temp": "data", "new": "value"}


@pytest.mark.asyncio
async def test_user_onboarding_use_case_execute():
    """Test user onboarding use case execute method with mocked repositories"""
    # Create mocks for repositories
    mock_user_repo = AsyncMock()
    mock_user_state_repo = AsyncMock()
    
    use_case = UserOnboardingUseCase(mock_user_repo, mock_user_state_repo)
    
    # Test validation of invalid input
    message, next_step, keyboard = await use_case.execute("123456789", "enter_first_name", "")
    
    assert "Пожалуйста, введите значение" in message
    assert next_step == "enter_first_name"  # Should stay in the same step


@pytest.mark.asyncio
async def test_get_main_menu_use_case():
    """Test get main menu use case"""
    mock_user_repo = AsyncMock()
    mock_user_state_repo = AsyncMock()
    
    use_case = GetMainMenuUseCase(mock_user_repo, mock_user_state_repo)
    
    # Mock a user
    mock_user = User(
        user_id="123456789",
        first_name="Иван",
        last_name="Иванов",
        birth_year=1990
    )
    
    mock_user_repo.get_user.return_value = mock_user
    
    message, keyboard = await use_case.execute("123456789")
    
    assert "Иван Иванов" in message
    assert len(keyboard) == 4  # Main menu has 4 buttons


@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    db = DatabaseConnection(":memory:")  # Use in-memory database for testing
    
    conn = db.get_connection()
    assert conn is not None
    
    # Test table creation
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    result = cursor.fetchone()
    assert result is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_states';")
    result = cursor.fetchone()
    assert result is not None


if __name__ == "__main__":
    pytest.main([__file__])