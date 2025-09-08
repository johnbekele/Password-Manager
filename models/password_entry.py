from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class PasswordEntry:
    id: int = 0
    website: str = ""
    username: str = ""
    email: str = ""
    password: str = ""
    notes: str = ""
    date_created: datetime = None
    date_modified: datetime = None
    
    def __post_init__(self):
        if self.date_created is None:
            self.date_created = datetime.now()
        if self.date_modified is None:
            self.date_modified = datetime.now()
    
    @property
    def masked_password(self) -> str:
        return '*' * len(self.password) if self.password else ''