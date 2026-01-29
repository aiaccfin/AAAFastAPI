from pydantic import BaseModel
from typing import Optional

class BizEntity(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
