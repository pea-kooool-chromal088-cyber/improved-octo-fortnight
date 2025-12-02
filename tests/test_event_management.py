import pytest
import asyncio
from datetime import datetime, timedelta
from src.domain.entities.event import Event
from src.domain.entities.registration import Registration
from src.domain.repositories.event_repository import EventRepository
from src.domain.repositories.registration_repository import RegistrationRepository
from src.domain.repositories.user_repository import UserRepository
from src.application.use_cases.create_event import CreateEventUseCase
from src.application.use_cases.get_events import GetEventsUseCase
from src.application.use_cases.register_for_event import RegisterForEventUseCase
from src.application.use_cases.get_my_events import GetMyEventsUseCase
from src.application.use_cases.unregister_from_event import UnregisterFromEventUseCase
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_event_repository import SqliteEventRepository
from src.infrastructure.repositories.sqlite_registration_repository import SqliteRegistrationRepository
from src.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository


class TestEventManagementPhase3:
    """Phase 3 tests: Event Foundation"""
    
    @pytest.fixture
    def db_connection(self):
        # Use in-memory database for testing
        connection = DatabaseConnection(":memory:")
        yield connection
        connection.close()
    
    @pytest.fixture
    def repositories(self, db_connection):
        event_repo = SqliteEventRepository(db_connection)
        registration_repo = SqliteRegistrationRepository(db_connection)
        user_repo = SqliteUserRepository(db_connection)
        return {
            "event_repo": event_repo,
            "registration_repo": registration_repo,
            "user_repo": user_repo
        }
    
    @pytest.fixture
    def use_cases(self, repositories):
        create_event_use_case = CreateEventUseCase(
            repositories["event_repo"], 
            repositories["user_repo"]
        )
        get_events_use_case = GetEventsUseCase(repositories["event_repo"])
        register_for_event_use_case = RegisterForEventUseCase(
            repositories["event_repo"],
            repositories["registration_repo"]
        )
        
        return {
            "create_event": create_event_use_case,
            "get_events": get_events_use_case,
            "register_for_event": register_for_event_use_case
        }
    
    async def test_event_creation_happy_path(self, repositories, use_cases):
        """Phase 3 test: Admin creates an event"""
        # Create an admin user
        user_repo = repositories["user_repo"]
        user_repo.create_user("12345", "Admin", "User", 1990, is_admin=True)
        
        # Create event
        future_date = datetime.now() + timedelta(days=1)
        result = use_cases["create_event"].execute(
            user_id="12345",
            event_name="Test Event",
            event_date_str=future_date.isoformat()
        )
        
        assert result["success"] is True
        assert "Test Event" in result["message"]
        assert result["event_id"] is not None
        
        # Verify event was created in DB
        event = repositories["event_repo"].get_event_by_id(result["event_id"])
        assert event is not None
        assert event.name == "Test Event"
        assert event.created_by == "12345"
    
    async def test_non_admin_cannot_create_event(self, repositories, use_cases):
        """Phase 3 test: Non-admin cannot create event"""
        # Create a regular user
        user_repo = repositories["user_repo"]
        user_repo.create_user("54321", "Regular", "User", 1995, is_admin=False)
        
        # Try to create event as non-admin
        future_date = datetime.now() + timedelta(days=1)
        result = use_cases["create_event"].execute(
            user_id="54321",
            event_name="Test Event",
            event_date_str=future_date.isoformat()
        )
        
        assert result["success"] is False
        assert "administrators can create events" in result["message"]
    
    async def test_event_registration_happy_path(self, repositories, use_cases):
        """Phase 3 test: Register for event"""
        # Create user and event
        user_repo = repositories["user_repo"]
        user_repo.create_user("11111", "Test", "User", 1992, is_admin=False)
        
        future_date = datetime.now() + timedelta(days=1)
        event = Event.create("Test Event", future_date, "12345")
        event_repo = repositories["event_repo"]
        created_event = event_repo.create_event(event)
        
        # Register user for event
        result = use_cases["register_for_event"].execute(
            user_id="11111",
            event_id=created_event.event_id
        )
        
        assert result["success"] is True
        assert "registered for event" in result["message"]
        
        # Verify registration in DB
        registration_repo = repositories["registration_repo"]
        assert registration_repo.is_registered("11111", created_event.event_id) is True
    
    async def test_duplicate_registration(self, repositories, use_cases):
        """Phase 3 test: Cannot register twice for same event"""
        # Create user and event
        user_repo = repositories["user_repo"]
        user_repo.create_user("22222", "Test", "User", 1992, is_admin=False)
        
        future_date = datetime.now() + timedelta(days=1)
        event = Event.create("Test Event", future_date, "12345")
        event_repo = repositories["event_repo"]
        created_event = event_repo.create_event(event)
        
        # First registration - should succeed
        result1 = use_cases["register_for_event"].execute(
            user_id="22222",
            event_id=created_event.event_id
        )
        assert result1["success"] is True
        
        # Second registration - should fail
        result2 = use_cases["register_for_event"].execute(
            user_id="22222",
            event_id=created_event.event_id
        )
        assert result2["success"] is False
        assert "already registered" in result2["message"]
    
    async def test_get_events_returns_future_events(self, repositories, use_cases):
        """Phase 3 test: GetEventsUseCase returns future events"""
        # Create a future event
        future_date = datetime.now() + timedelta(days=1)
        event = Event.create("Future Event", future_date, "12345")
        event_repo = repositories["event_repo"]
        event_repo.create_event(event)
        
        # Create a past event (should not appear)
        past_date = datetime.now() - timedelta(days=1)
        past_event = Event.create("Past Event", past_date, "12345")
        event_repo.create_event(past_event)
        
        # Get events
        result = use_cases["get_events"].execute(user_id="99999")
        
        # Should only contain the future event
        assert len(result["events"]) == 1
        assert result["events"][0].name == "Future Event"


class TestEventManagementPhase4:
    """Phase 4 tests: Personal Events"""
    
    @pytest.fixture
    def db_connection(self):
        # Use in-memory database for testing
        connection = DatabaseConnection(":memory:")
        yield connection
        connection.close()
    
    @pytest.fixture
    def repositories(self, db_connection):
        event_repo = SqliteEventRepository(db_connection)
        registration_repo = SqliteRegistrationRepository(db_connection)
        user_repo = SqliteUserRepository(db_connection)
        return {
            "event_repo": event_repo,
            "registration_repo": registration_repo,
            "user_repo": user_repo
        }
    
    @pytest.fixture
    def use_cases(self, repositories):
        create_event_use_case = CreateEventUseCase(
            repositories["event_repo"], 
            repositories["user_repo"]
        )
        get_events_use_case = GetEventsUseCase(repositories["event_repo"])
        register_for_event_use_case = RegisterForEventUseCase(
            repositories["event_repo"],
            repositories["registration_repo"]
        )
        get_my_events_use_case = GetMyEventsUseCase(
            repositories["event_repo"],
            repositories["registration_repo"]
        )
        unregister_from_event_use_case = UnregisterFromEventUseCase(
            repositories["event_repo"],
            repositories["registration_repo"]
        )
        
        return {
            "create_event": create_event_use_case,
            "get_events": get_events_use_case,
            "register_for_event": register_for_event_use_case,
            "get_my_events": get_my_events_use_case,
            "unregister_from_event": unregister_from_event_use_case
        }
    
    async def test_my_events_display(self, repositories, use_cases):
        """Phase 4 test: Display user's registered events"""
        # Create user and events
        user_repo = repositories["user_repo"]
        user_repo.create_user("33333", "Test", "User", 1992, is_admin=False)
        
        future_date = datetime.now() + timedelta(days=1)
        event1 = Event.create("Event 1", future_date, "12345")
        event2 = Event.create("Event 2", future_date, "12345")
        event_repo = repositories["event_repo"]
        created_event1 = event_repo.create_event(event1)
        created_event2 = event_repo.create_event(event2)
        
        # Register user for both events
        use_cases["register_for_event"].execute(
            user_id="33333",
            event_id=created_event1.event_id
        )
        use_cases["register_for_event"].execute(
            user_id="33333",
            event_id=created_event2.event_id
        )
        
        # Get user's events
        result = use_cases["get_my_events"].execute(user_id="33333")
        
        assert len(result["events"]) == 2
        event_names = [event.name for event in result["events"]]
        assert "Event 1" in event_names
        assert "Event 2" in event_names
    
    async def test_unregister_flow(self, repositories, use_cases):
        """Phase 4 test: Unregister from event flow"""
        # Create user and event
        user_repo = repositories["user_repo"]
        user_repo.create_user("44444", "Test", "User", 1992, is_admin=False)
        
        future_date = datetime.now() + timedelta(days=1)
        event = Event.create("Test Event", future_date, "12345")
        event_repo = repositories["event_repo"]
        created_event = event_repo.create_event(event)
        
        # Register user for event
        use_cases["register_for_event"].execute(
            user_id="44444",
            event_id=created_event.event_id
        )
        
        # Verify registration exists
        registration_repo = repositories["registration_repo"]
        assert registration_repo.is_registered("44444", created_event.event_id) is True
        
        # Unregister from event
        result = use_cases["unregister_from_event"].execute(
            user_id="44444",
            event_id=created_event.event_id
        )
        
        assert result["success"] is True
        assert "unregistered from event" in result["message"]
        
        # Verify registration is removed
        assert registration_repo.is_registered("44444", created_event.event_id) is False
        
        # Try to get user's events - should be empty
        my_events_result = use_cases["get_my_events"].execute(user_id="44444")
        assert len(my_events_result["events"]) == 0


if __name__ == "__main__":
    pytest.main([__file__])