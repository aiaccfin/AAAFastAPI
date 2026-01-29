import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Column, SQLModel, Field
from typing import Optional, Dict, Any
from app.models.m_mixin import BaseMixin

class UserBase(SQLModel):
    username: str
    extras: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))



class UserTable(UserBase, BaseMixin, table=True):
    __tablename__ = "user_rls"

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: uuid.UUID  
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_deleted: bool
    status: str
    extras: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))




# from sqlmodel import SQLModel, Field
# from typing import List, Optional, Dict, Any
# from datetime import datetime
# from sqlalchemy import Column
# from sqlalchemy.dialects.postgresql import JSONB
# import uuid

# # ------------------------------
# # Base model (shared fields)
# # ------------------------------
# class UserBase(SQLModel):
#     name: str
#     description: Optional[str] = None

#     tenant_ids: List[uuid.UUID] = Field(
#         default_factory=lambda: [uuid.UUID("00000000-0000-0000-0000-000000000000")],
#         sa_column=Column(JSONB, nullable=False)
#     )
#     roles: List[str] = Field(default_factory=lambda: ["88"], sa_column=Column(JSONB, nullable=False))
#     groups: List[str] = Field(default_factory=lambda: ["9999"], sa_column=Column(JSONB, nullable=False))

#     primary_tenant_id: uuid.UUID = Field(default=uuid.UUID("00000000-0000-0000-0000-000000000000"))
#     primary_role: str = Field(default="88")
#     primary_group: str = Field(default="9999")
#     email_verified: bool = Field(default=False)

#     status: str = Field(default="active")
#     is_deleted: bool = Field(default=False)

#     notes: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))


# # ------------------------------
# # Table model
# # ------------------------------
# class User(UserBase, table=True):
#     __tablename__ = "users"

#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     created_by: str = Field(default="admin")


# # ------------------------------
# # Create model
# # ------------------------------
# class UserCreate(UserBase):
#     """
#     Input model for creating a new user.
#     Excludes id, timestamps, created_by
#     """
#     pass


# # ------------------------------
# # Read model
# # ------------------------------
# class UserRead(UserBase):
#     """
#     Output model for reading user data.
#     Includes id and timestamps.
#     """
#     id: uuid.UUID
#     created_at: datetime
#     updated_at: datetime
#     created_by: str


# # ------------------------------
# # Update model
# # ------------------------------
# class UserUpdate(SQLModel):
#     """
#     Input model for updating a user.
#     All fields optional.
#     """
#     name: Optional[str] = None
#     description: Optional[str] = None
#     tenant_ids: Optional[List[uuid.UUID]] = None
#     roles: Optional[List[str]] = None
#     groups: Optional[List[str]] = None
#     primary_tenant_id: Optional[uuid.UUID] = None
#     primary_role: Optional[str] = None
#     primary_group: Optional[str] = None
#     email_verified: Optional[bool] = None
#     status: Optional[str] = None
#     is_deleted: Optional[bool] = None
#     notes: Optional[Dict[str, Any]] = None


# # from sqlmodel import SQLModel, Field, Relationship
# # from typing import List, Optional, Dict, Any
# # from datetime import datetime
# # from sqlalchemy.dialects.postgresql import JSONB
# # from sqlalchemy import Column, Text, CheckConstraint, text
# # from sqlalchemy.orm import sessionmaker
# # import uuid

# # class User(SQLModel, table=True):
# #     __tablename__ = "users"

# #     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
# #     name: str = Field(index=True)
# #     description: Optional[str] = None

# #     tenant_ids: List[uuid.UUID] = Field(
# #         default_factory=lambda: [uuid.UUID("00000000-0000-0000-0000-000000000000")],
# #         sa_column=Column(JSONB, nullable=False)
# #     )
# #     roles: List[str] = Field(default_factory=lambda: ["88"], sa_column=Column(JSONB, nullable=False))
# #     groups: List[str] = Field(default_factory=lambda: ["9999"], sa_column=Column(JSONB, nullable=False))

# #     primary_tenant_id: uuid.UUID = Field(default=uuid.UUID("00000000-0000-0000-0000-000000000000"))
# #     primary_role: str = Field(default="88")
# #     primary_group: str = Field(default="9999")
# #     email_verified: bool = Field(default=False)

# #     status: str = Field(default="active")
# #     is_deleted: bool = Field(default=False)

# #     created_at: datetime = Field(default_factory=datetime.utcnow)
# #     updated_at: datetime = Field(default_factory=datetime.utcnow)
# #     created_by: str = Field(default="admin")

# #     notes: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))


# # # class AuditLog(SQLModel, table=True):
# # #     __tablename__ = "audit_logs"
# # #     id: int | None = Field(default=None, primary_key=True)
# # #     tenant_id: str = Field(index=True) 
# # #     operation: str  # INSERT, UPDATE, DELETE
# # #     record_id: Optional[str]
# # #     data_before: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "jsonb"})
# # #     data_after: Optional[dict] = Field(default=None, sa_column_kwargs={"type_": "jsonb"})
# # #     created_at: datetime = Field(default_factory=datetime.utcnow)
# # #     created_by: Optional[str] = Field(default=None)
