from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    user_id: str
    first_name: str
    last_name: str
    birth_year: int
    is_admin: bool = False
    
    def __post_init__(self):
        # Validate user data
        if not self.first_name.strip():
            raise ValueError("First name cannot be empty")
        if not self.last_name.strip():
            raise ValueError("Last name cannot be empty")
        if self.birth_year < 1900 or self.birth_year > 2024:
            raise ValueError("Birth year must be between 1900 and 2024")