# model_base
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

from sqlmodel import Field, SQLModel


class AllBase(SQLModel):
    id:     Optional[int] = Field(default=None, primary_key=True)  # Auto-increment ID
    biz_id: Optional[int]
    status: Optional[str]
    note:   Optional[str]  # Optional if the field allows NULL
    info:   Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Timestamp with timezone

