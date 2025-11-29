from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user import User


class UserRepository(ABC):
    """Interface for user repository"""
    
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def save_user(self, user: User) -> None:
        """Save user to database"""
        pass
    
    @abstractmethod
    async def update_user(self, user: User) -> None:
        """Update existing user"""
        pass