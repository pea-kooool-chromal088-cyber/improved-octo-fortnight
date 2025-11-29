from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user_state import UserState


class UserStateRepository(ABC):
    """Interface for user state repository"""
    
    @abstractmethod
    async def get_user_state(self, user_id: str) -> Optional[UserState]:
        """Get user state by ID"""
        pass
    
    @abstractmethod
    async def save_user_state(self, user_state: UserState) -> None:
        """Save user state to database"""
        pass
    
    @abstractmethod
    async def update_user_state(self, user_state: UserState) -> None:
        """Update existing user state"""
        pass