from typing import Optional
from sqlmodel import Field, SQLModel


class COABase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment ID
    coa_id: int
    biz_type: int
    account_type: str
    account_subtype: str
    parent_account: str
    sub_account: str
    status: str
    coa_note: Optional[str]  # Optional if the field allows NULL

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "coa_id": 1100,
                "biz_type": 11,
                "account_type": "Assets",
                "account_subtype": "Cash and Bank",
                "parent_account": "1000 Cash and Cash Equivalents",
                "sub_account": "1030 Short-Term Investments",
                "status": "Deleted",
                "coa_note": "Short-term investments"
            }
        }


class COA_Standard(COABase, table=True):  # Table for database
    pass


class COACreate(COABase):  # Used for request body
    pass


class COARead(COABase):  # Used for response models
    pass


class COAUpdate(SQLModel):  # Used for partial updates
    coa_id: Optional[int] = None
    biz_type: Optional[int] = None
    account_type: Optional[str] = None
    account_subtype: Optional[str] = None
    parent_account: Optional[str] = None
    sub_account: Optional[str] = None
    coa_note: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "coa_id": 1100,
                "account_type": "Assets",
                "coa_note": "Updated note"
            }
        }
