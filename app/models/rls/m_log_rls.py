from sqlmodel import SQLModel, Field, Column
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)

    tenant_id: str = Field(index=True)
    user_id: Optional[int] = Field(default=None)
    role_id: Optional[int] = Field(default=None)
    
    table_name: str
    operation: str  # INSERT, UPDATE, DELETE

    data_before: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    data_after: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default="mouren")


# class AuditLog(SQLModel, table=True):
#     __tablename__ = "audit_logs"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     tenant_id: str = Field(index=True)
#     role_id: Optional[int] = Field(default=None)
#     table_name: str
#     operation: str

#     data_before: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
#     data_after: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))

#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     created_by: Optional[str] = Field(default=None)


# from sqlmodel import SQLModel, Field
# from typing import Optional, Dict, Any
# from datetime import datetime
# from sqlalchemy import Column
# from sqlalchemy.dialects.postgresql import JSONB
# from pydantic import BaseModel


# # -----------------------------
# # Base Model (shared fields)
# # -----------------------------
# class AuditLogBase(SQLModel):
#     operation: str                               # INSERT / UPDATE / DELETE

#     # JSON snapshots
#     data_before: Optional[Dict[str, Any]] = Field(
#         default=None,
#         sa_column=Column(JSONB)
#     )

#     data_after: Optional[Dict[str, Any]] = Field(
#         default=None,
#         sa_column=Column(JSONB)
#     )


# # -----------------------------
# # DB Table Model (actual table)
# # -----------------------------
# class AuditLog(AuditLogBase, table=True):
#     __tablename__ = "audit_log"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     tenant_id: str = Field(index=True)
#     role_id: Optional[int] = Field(default=None)      # <-- added
#     table_name: str  

#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     created_by: Optional[str] = Field(default=None)


# # -----------------------------
# # Request / Response Models
# # -----------------------------
# class AuditLogCreate(AuditLogBase):
#     """User cannot set metadata manually"""
#     pass


# class AuditLogRead(AuditLogBase):
#     id: int
#     tenant_id: str
#     created_at: datetime
#     created_by: Optional[str]
