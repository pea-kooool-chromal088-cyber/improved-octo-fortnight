from fastapi import FastAPI, Request
import json
from src.application.use_cases.user_onboarding import UserOnboardingUseCase
from src.application.use_cases.get_main_menu import GetMainMenuUseCase
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository
from src.infrastructure.repositories.sqlite_user_state_repository import SqliteUserStateRepository
from src.presentation.telegram.handlers.message_handlers import handle_message


app = FastAPI()

# Initialize database and repositories
db_connection = DatabaseConnection()
user_repository = SqliteUserRepository(db_connection)
user_state_repository = SqliteUserStateRepository(db_connection)

# Initialize use cases
user_onboarding_use_case = UserOnboardingUseCase(user_repository, user_state_repository)
get_main_menu_use_case = GetMainMenuUseCase(user_repository, user_state_repository)


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