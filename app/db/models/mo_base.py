# app/db/base.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from decimal import Decimal

import uuid


from sqlalchemy import Boolean, DateTime, String, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlmodel import Float, Integer



class Base(DeclarativeBase):
    pass

class BaseMixin:
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False,)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[Optional[str]] = mapped_column(String, default="create_user")
    updated_by: Mapped[Optional[str]] = mapped_column(String, default="update_user")
    deleted_by: Mapped[Optional[str]] = mapped_column(String, default="delete_user")

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)
    date_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)


class TenantMixin:
    tenant_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), index=True, nullable=False)
