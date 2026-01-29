from pydantic import BaseModel, Extra

class Receipt(BaseModel):
    class Config:
        extra = Extra.allow


# from pydantic import BaseModel, Field
# from typing import Optional, Dict, Any
# from datetime import datetime

# class Receipt(BaseModel):
#     data: Dict[str, Any] = Field(..., description="Arbitrary JSON data for the receipt")