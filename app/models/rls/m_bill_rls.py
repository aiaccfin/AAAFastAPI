# app/models/rls/m_bill_rls.py
import uuid
from sqlmodel import SQLModel, Field
from sqlalchemy import Boolean
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from typing import ClassVar, Optional, Dict, Any, List, Literal
from datetime import datetime

from app.models.m_mixin import BaseMixin
from app.models.rls.m_journal_line_rls import JournalLineCreate


class BillBase(SQLModel):
    bill_rec: Literal["bill", "vendor_credit", "expense", "credit_card_credit", "_others"] = Field(
        default="bill",
        sa_column=Column(String(), nullable=False, server_default="bill")
    )

    extras: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB))

    issue_date: datetime  # 账单日期
    due_date: datetime  # 到期日期

    bill_number: Optional[str] = Field(default=None, index=True)

    payee_id: uuid.UUID = Field(default_factory=uuid.uuid4, index=True)
    payee_snapshot: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB))

    line_items: List[Dict[str, Any]] = Field(
        default=[], sa_column=Column(JSONB))  # 行项目
    subtotal: float = Field(default  =  0)  # 小计

    tax_amount: float = Field(default  =  0)  # 税额
    total_amount: float = Field(default  =  0)  # 总金额
    amount_credited: float = Field(default  =  0)  # 已抵扣金额
    amount_paid: float = Field(default  =  0)  # 已付金额
    balance_due: float = Field(default  =  0)  # 欠款金额

    # draft, sent, paid, overdue, cancelled
    status: str = Field(default="draft")
    # unpaid, partial, paid, overdue
    payment_status: str = Field(default="unpaid")

    mark_as_sent: bool = Field(
        default=False, sa_column=Column(Boolean))  # 标记是否已发送
    auto_apply: bool = Field(
        default=False, sa_column=Column(Boolean))  # 自动应用付款
    sent_at: Optional[datetime] = Field(default=None)  # 发送时间

    # JSONB 灵活数据
    tax_breakdown: Dict[str, Any] = Field(
        default={}, sa_column=Column(JSONB))  # 税费明细
    payment_terms: Dict[str, Any] = Field(
        default={}, sa_column=Column(JSONB))  # 付款条款
    shipping_info: Dict[str, Any] = Field(
        default={}, sa_column=Column(JSONB))  # 配送信息
    notes: Dict[str, Any] = Field(
        default={}, sa_column=Column(JSONB))  # 备注和自定义字段


class BillDB(BillBase, BaseMixin, table=True):
    __tablename__ = "bills_rls"

    class Config:
        indexes = [
            ("tenant_id", "status"),
            ("tenant_id", "issue_date"),
        ]


class BillCreate(BillBase):
    journal_lines: Optional[List["JournalLineCreate"]] = Field(default_factory=list)


class BillReadList(BillBase):
    id: uuid.UUID  # 🔥 改为 UUID
    bill_number: Optional[str]  # will be auto-exposed
    created_at: datetime
    updated_at: datetime


class BillUpdate(SQLModel):
    # General extras
    extras: Optional[Dict[str, Any]] = None

    # Dates
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    # Bill number
    bill_number: Optional[str] = None

    # Payee
    payee_id: Optional[uuid.UUID] = None
    payee_snapshot: Optional[Dict[str, Any]] = None

    # Line items
    line_items: Optional[List[Dict[str, Any]]] = None
    subtotal: Optional[float] = None

    # Tax and total
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    amount_credited: Optional[float] = None
    amount_paid: Optional[float] = None
    balance_due: Optional[float] = None

    # Status
    # 'Unpaid', 'Pending for approval', 'Overdue', 'Paid', 'Schedule for pay', 'Partially paid', 'Rejected', 'Pending payment', 'Draft', 'Scheduled', 'Voided', 'Closed'
    status: Optional[str] = None
    payment_status: Optional[str] = None    # unpaid, partial, paid, overdue

    # Flags / actions
    mark_as_sent: Optional[bool] = None
    auto_apply: Optional[bool] = None
    sent_at: Optional[datetime] = None

    # JSON fields
    tax_breakdown: Optional[Dict[str, Any]] = None
    payment_terms: Optional[Dict[str, Any]] = None
    shipping_info: Optional[Dict[str, Any]] = None
    notes: Optional[Dict[str, Any]] = None

    # Business metadata
    description: Optional[str] = None

    # Journal lines
    journal_lines: Optional[List["JournalLineCreate"]] = None


class BillDelete(SQLModel):
    is_deleted: bool = Field(default=True)


class BillRead(BillBase):
    id: uuid.UUID
    bill_number: Optional[str]
    created_at: datetime
    created_by: str
    updated_at: datetime
    is_deleted: bool

