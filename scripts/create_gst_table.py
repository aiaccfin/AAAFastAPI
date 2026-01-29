# scripts/create_gst_table.py
from sqlmodel import Session, SQLModel, create_engine, text
from app.config import settings
from app.models.m_rls_gst import GST


def create_gst_table():
    engine = create_engine(settings.CFG['PG_POSTGRES'], echo=True)

    # 创建表
    SQLModel.metadata.create_all(engine)
    print("✅ GST 表已创建")

    # 启用 RLS
    with Session(engine) as session:
        session.exec(text("ALTER TABLE gst ENABLE ROW LEVEL SECURITY;"))

        # 创建 RLS 策略
        session.exec(text("""
        CREATE POLICY gst_tenant_isolation ON gst
            FOR ALL 
            USING (tenant_id = current_setting('app.current_tenant')::VARCHAR);
        """))

        session.commit()
        print("✅ GST 表 RLS 已启用")


if __name__ == "__main__":
    create_gst_table()
