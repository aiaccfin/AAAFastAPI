from pydantic import BaseModel
from typing import List, Optional

class Role(BaseModel):
    id: Optional[str] = None
    name: str  # e.g., "Supervisor", "Manager", "Regular User"
    modules: List[str] = []  # List of allowed modules
