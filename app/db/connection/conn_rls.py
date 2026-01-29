from sqlmodel import Session, SQLModel, create_engine, text
from typing import Generator

from app.config import settings

# Import your specific RLS models
from app.models.rls import (m_gst_rls, m_log_rls, m_invoice_rls, 
                            m_generic_rls, m_journal_entry_rls, m_user_rls, m_partner_rls, m_global_type_rls, 
                            m_journal_header_rls, m_journal_line_rls, 
                            m_payment_allocation_rls, m_payment_rls, m_tenant_rls, m_tenant_sequence_rls,
                            m_coa_rls, m_gst_agency_rls,
                            m_product_category_rls, m_product_rls, m_bill_rls, m_bill_payment_rls, m_bill_payment_allocation_rls)
from app.db.connection.generate_trigger_function import create_log_audit_function, attach_audit_triggers
from app.models.rls.m_tenant_sequence_rls import TenantSequenceDB


engine = create_engine(settings.CFG['PG_AIACC'], echo=False)
engine_rls_crud = create_engine(settings.CFG['PG_RLS'], echo=False)
engine_rls_create = create_engine(settings.CFG['PG_RLS_POSTGRES'], echo=False)

# Hardcoded list of ALL RLS tables
RLS_TABLES = [
    m_user_rls.UserTable.__table__,
    m_generic_rls.GenericStore.__table__,
    m_gst_rls.GSTTable.__table__,
    m_partner_rls.Partner.__table__,
    m_global_type_rls.TypeDB.__table__,

    m_invoice_rls.InvoiceDB.__table__,
    m_payment_allocation_rls.PaymentAllocationDB.__table__,
    m_payment_rls.PaymentDB.__table__,
    m_tenant_sequence_rls.TenantSequenceDB.__table__,
    m_journal_header_rls.JournalHeaderDB.__table__,
    m_journal_line_rls.JournalLineDB.__table__,
    m_coa_rls.COADB.__table__,
    m_gst_agency_rls.TaxAgency.__table__,
    m_product_rls.Product.__table__,
    m_product_category_rls.ProductCategory.__table__,
    m_bill_rls.BillDB.__table__,
    m_bill_payment_rls.BillPaymentDB.__table__, 
    m_bill_payment_allocation_rls.BillPaymentAllocationDB.__table__,

    # m_log_rls.AuditLog.__table__,
    # m_journal_entry_rls.JournalEntry.__table__,
]
ALLOWED_ROLE_IDS = ["111", "112"]


def create_db_and_tables():
    # Create ALL tables in the main AI engine
    # SQLModel.metadata.create_all(engine)

    # Create ONLY specific RLS tables in the RLS engine
    # Use checkfirst=True to skip if tables already exist
    # Note: Index creation errors are handled separately
    from sqlalchemy.exc import ProgrammingError
    
    try:
        SQLModel.metadata.create_all(engine_rls_create, tables=RLS_TABLES, checkfirst=True)
    except ProgrammingError as e:
        # If it's an index/constraint already exists error, log and continue
        error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "already exists" in error_str.lower() or "duplicate" in error_str.lower():
            print(f"⚠️  Database objects already exist (skipping): {error_str.split('[')[0] if '[' in error_str else error_str[:80]}")
            # Continue execution - tables/indexes already exist, which is fine
        else:
            # Re-raise if it's a different ProgrammingError
            raise
    except Exception as e:
        # Re-raise any other exceptions
        raise

    # Enable RLS for ALL created tables
    enable_rls_policies()

    # 2️⃣ Create invoice sequence (if it doesn't exist)
    create_invoice_sequence()
    
    # 2️⃣ Create log_audit() function
    # create_log_audit_function()

    # 3️⃣ Attach triggers to all tables
    # attach_audit_triggers(RLS_TABLES=RLS_TABLES)


def enable_rls_policies():
    """Enable RLS and create policies for ALL RLS tables"""
    with Session(engine_rls_create) as session:
        for table in RLS_TABLES:
            table_name = table.name

            # Enable RLS for the table
            session.exec(
                text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"))

            # Drop policy if it exists
            session.exec(
                text(f"DROP POLICY IF EXISTS {table_name}_tenant_isolation ON {table_name};"))

            # Create RLS policy
            session.exec(text(f"""
            CREATE POLICY {table_name}_tenant_isolation ON {table_name}
                FOR ALL 
                USING (tenant_id = current_setting('app.current_tenant')::UUID);
            """))

            print(f"✅ RLS enabled for {table_name} table")

        session.commit()
        print("✅ RLS enabled for ALL tables")

# 🔥 修正：统一的会话管理函数



def get_super_session_factory():
    def _dependency():
        with Session(engine_rls_create) as session:
            yield session
    return _dependency
















def get_norls_session() -> Generator[Session, None, None]:
    """
    A session that does NOT use tenant RLS context.
    Uses the engine with superuser-level privileges (engine_rls_create),
    allowing unrestricted access to tables.
    """
    with Session(engine_rls_create) as session:
        yield session


def get_session() -> Generator[Session, None, None]:
    """用于 FastAPI 依赖注入的会话（无租户上下文）"""
    with Session(engine_rls_crud) as session:  # 使用 RLS 引擎
        yield session


def get_session_no_yield() -> Session:
    """直接返回会话对象（无租户上下文）"""
    return Session(engine_rls_crud)  # 使用 RLS 引擎


def get_tenant_session(tenant_id: str) -> Generator[Session, None, None]:
    """获取设置了 RLS 上下文的数据库会话（用于依赖注入）"""
    with Session(engine_rls_crud) as session:  # 使用 RLS 引擎
        session.exec(text(f"SET app.current_tenant = '{tenant_id}'"))
        try:
            yield session
        finally:
            # 清理上下文
            # session.exec(text("RESET app.current_tenant"))
            try:
                session.exec(text("RESET app.current_tenant"))
            except Exception:
                # suppress cleanup errors from aborted transactions
                session.rollback()


def get_tenant_session_no_yield(tenant_id: str) -> Session:
    """直接返回设置了租户上下文的会话对象"""
    session = Session(engine_rls_crud)  # 使用 RLS 引擎
    session.exec(text(f"SET app.current_tenant = '{tenant_id}'"))
    return session

# 删除重复的 get_session 和 get_session_user_id 函数

def create_invoice_sequence():
    """Ensure the invoice sequence exists (this will be used across all tenants)."""
    sequence_creation_query = """
    CREATE SEQUENCE IF NOT EXISTS invoice_seq
    START 1088 INCREMENT 1;
    """
    with Session(engine_rls_create) as session:
        session.execute(text(sequence_creation_query))
        session.commit()
    print("✅ Invoice sequence 'invoice_seq' created (or already exists).")





def get_tenant_role_session(tenant_id: str, role_id: int, user_id: int) -> Generator[Session, None, None]:
    """
    Get a tenant-aware session and set role context.
    No user_id included; auditing handled separately.
    """
    
    # if role_id not in ALLOWED_ROLE_IDS:
    #     raise HTTPException(status_code=403, detail=f"Role {role_id} not permitted")
    
    with Session(engine) as session:
        # Set RLS context
        session.exec(text(f"SET app.current_tenant_id = '{tenant_id}'"))
        # session.exec(text(f"SET app.current_user_id = {user_id}"))
        # Set role context (for authorization in SQL if needed)
        # session.exec(text(f"SET app.current_role_id = {role_id}"))
        try:
            yield session
        finally:
            # Clean up context (optional)
            session.exec(text("RESET app.current_tenant_id"))
            # session.exec(text("RESET app.current_user_id"))
            # session.exec(text("RESET app.current_role_id")) 


def tenant_role_session_dependency(tenant_id: str, role_id: int, user_id: int):
    """
    Factory to return a FastAPI dependency yielding a tenant+role scoped session.
    """
    def _dependency():
        yield from get_tenant_role_session(tenant_id, role_id, user_id)
    return _dependency


def tenant_session_dependency(tenant_id: str):
    """Return a FastAPI dependency for any tenant"""
    def _dependency():
        yield from get_tenant_session(tenant_id)
    return _dependency
