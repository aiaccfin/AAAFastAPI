from pydantic import BaseModel
from typing import List, Optional

class COA(BaseModel):
    coa_id: int
    biz_type: int
    account_type: str
    account_subtype: str
    parent_account: str
    sub_account: str
    coa_note: Optional[str]  # Optional if the field allows NULL
