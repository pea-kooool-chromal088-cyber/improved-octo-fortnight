from fastapi import FastAPI, Request
import json
from src.application.use_cases.user_onboarding import UserOnboardingUseCase
from src.application.use_cases.get_main_menu import GetMainMenuUseCase
from src.application.use_cases.create_event import CreateEventUseCase
from src.application.use_cases.get_events import GetEventsUseCase
from src.application.use_cases.register_for_event import RegisterForEventUseCase
from src.application.use_cases.get_my_events import GetMyEventsUseCase
from src.application.use_cases.unregister_from_event import UnregisterFromEventUseCase
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository
from src.infrastructure.repositories.sqlite_user_state_repository import SqliteUserStateRepository
from src.infrastructure.repositories.sqlite_event_repository import SqliteEventRepository
from src.infrastructure.repositories.sqlite_registration_repository import SqliteRegistrationRepository
from src.presentation.telegram.handlers.message_handlers import handle_message


app = FastAPI()

# Initialize database and repositories
db_connection = DatabaseConnection()
user_repository = SqliteUserRepository(db_connection)
user_state_repository = SqliteUserStateRepository(db_connection)
event_repository = SqliteEventRepository(db_connection)
registration_repository = SqliteRegistrationRepository(db_connection)

# Initialize use cases
user_onboarding_use_case = UserOnboardingUseCase(user_repository, user_state_repository)
get_main_menu_use_case = GetMainMenuUseCase(user_repository, user_state_repository)
create_event_use_case = CreateEventUseCase(event_repository, user_repository)
get_events_use_case = GetEventsUseCase(event_repository)
register_for_event_use_case = RegisterForEventUseCase(event_repository, registration_repository)
get_my_events_use_case = GetMyEventsUseCase(event_repository, registration_repository)
unregister_from_event_use_case = UnregisterFromEventUseCase(event_repository, registration_repository)


@app.post("/webhook")
async def webhook_handler(request: Request):
    """Handle incoming webhook requests from Telegram"""
    try:
        # Get JSON data from request
        json_data = await request.json()
        
        # Process the update
        response = await handle_message(
            json_data,
            user_onboarding_use_case,
            get_main_menu_use_case,
            create_event_use_case,
            get_events_use_case,
            register_for_event_use_case,
            get_my_events_use_case,
            unregister_from_event_use_case,
            user_state_repository
        )
        
        return {"status": "ok", "response": response}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "running", "message": "Telegram Bot Webhook is active"}