from typing import Optional
from sqlmodel import Field, SQLModel


class NaicsBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment ID
    industry_category_id: int
    industry_category_name: Optional[str]
    business_type_id: int
    business_type_name: Optional[str]
    business_subtype_id: Optional[int]
    business_subtype_name: Optional[str]
    status: Optional[str]
    note: Optional[str]  # Optional if the field allows NULL


class Naics_Standard(NaicsBase, table=True):  # Table for database
    pass


class NaicsCreate(NaicsBase):  # Used for request body
    pass


class NaicsRead(NaicsBase):  # Used for response models
    pass


class NaicsUpdate(SQLModel):  # Used for partial updates
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment ID
    industry_category_id: int
    industry_category_name: Optional[str]
    business_type_id: int
    business_type_name: Optional[str]
    business_subtype_id: Optional[str]
    business_subtype_name: Optional[str]
    status: Optional[str]
    note: Optional[str]  # Optional if the field allows NULL
