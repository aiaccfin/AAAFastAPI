from pydantic import BaseModel
from typing import Optional, Dict, Any

class DBLogModel(BaseModel):
    _id: Optional[str]
    request_id: Optional[str]
    user: Optional[str]
    client_ip: Optional[str]
    operation: Optional[str]
    collection: Optional[str]
    filter: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]
    timestamp: Optional[float]
