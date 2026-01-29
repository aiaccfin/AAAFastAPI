from sqlmodel import Session, text, select
from sqlalchemy import func
from app.models.rls.m_invoice_rls import InvoiceDB

def get_next_sequence_value_global(db: Session, seq_name: str = "inv_seq") -> int:
    stmt = text("SELECT nextval(:seq_name)").bindparams(seq_name=seq_name)
    result = db.exec(stmt)
    next_val = result.scalar_one()
    return next_val

def get_next_sequence_value(db: Session, seq_name: str = "inv_seq") -> int:
    stmt = text("SELECT nextval(:seq_name)").bindparams(seq_name=seq_name)
    result = db.exec(stmt)
    next_val = result.scalar_one()
    return next_val


async def get_next_invoice_number_for_me_when_saving(session, tenant_id):
    result = await session.exec(
        select(func.max(InvoiceDB.invoice_sequence))
        .where(InvoiceDB.tenant_id == tenant_id)
    )
    last = result.one_or_none() or 0
    return last + 1



def get_next_invoice_number_for_me(db: Session, tenant_id: str) -> int:
    stmt = text("SELECT next_invoice_number(:tenant_id)")
    result = db.exec(stmt.bindparams(tenant_id=tenant_id))
    next_number = result.scalar_one()
    return next_number