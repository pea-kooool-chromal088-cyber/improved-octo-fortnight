from dataclasses import dataclass
from typing import Optional
import json
from datetime import datetime


@dataclass
class UserState:
    user_id: str
    current_step: str
    context: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        # Validate current_step
        valid_steps = [
            'main_menu', 
            'enter_first_name', 
            'enter_last_name', 
            'enter_birth_year'
        ]
        if self.current_step not in valid_steps:
            raise ValueError(f"Invalid step: {self.current_step}. Must be one of {valid_steps}")
    
    @property
    def context_data(self) -> dict:
        """Get context as a dictionary, return empty dict if context is None"""
        if self.context:
            return json.loads(self.context)
        return {}
    
    def update_context(self, data: dict) -> 'UserState':
        """Return a new UserState with updated context"""
        updated_context = self.context_data.copy()
        updated_context.update(data)
        return UserState(
            user_id=self.user_id,
            current_step=self.current_step,
            context=json.dumps(updated_context),
            updated_at=self.updated_at
        )