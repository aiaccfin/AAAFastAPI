# scripts/create_rls_invoice_table.py
from sqlmodel import Session, SQLModel, create_engine, text
from app.config import settings
from app.models.rls.m_invoice_rls import InvoiceDB

def create_rls_invoice_table():
    # 使用 PG_POSTGRES 连接
    admin_engine = create_engine(settings.CFG['PG_POSTGRES'], echo=True)
    
    # 创建表
    SQLModel.metadata.create_all(admin_engine)
    print("✅ rls_invoice 表已创建")
    
    # 启用 RLS 和创建索引
    with Session(admin_engine) as session:
        # 启用 RLS
        session.exec(text("ALTER TABLE rls_invoice ENABLE ROW LEVEL SECURITY;"))
        
        # 创建 RLS 策略
        session.exec(text("""
        CREATE POLICY rls_invoice_tenant_isolation ON rls_invoice
            FOR ALL 
            USING (tenant_id = current_setting('app.current_tenant')::VARCHAR);
        """))
        
        # 创建索引
        session.exec(text("""
        CREATE INDEX idx_rls_invoice_tenant_number ON rls_invoice (tenant_id, invoice_number);
        """))
        session.exec(text("""
        CREATE INDEX idx_rls_invoice_tenant_status ON rls_invoice (tenant_id, status);
        """))
        session.exec(text("""
        CREATE INDEX idx_rls_invoice_tenant_date ON rls_invoice (tenant_id, invoice_date);
        """))
        
        session.commit()
        print("✅ rls_invoice 表 RLS 和索引已启用")

if __name__ == "__main__":
    create_rls_invoice_table()