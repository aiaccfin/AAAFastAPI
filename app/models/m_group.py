from pydantic import BaseModel
from typing import List, Optional

class Group(BaseModel):
    id: Optional[str] = None
    name: str
    biz_entities: List[str] = []  # List of BizEntity IDs
    users: List[str] = []  # List of User IDs
