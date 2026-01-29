# scripts/enable_rls_for_tables.py
from sqlmodel import Session, text
from app.config import settings
from app.db import connection.conn_rls


def enable_rls_for_table(table_name: str):
    """为指定表启用 RLS 并创建策略"""
    with Session(connection.conn_rls.engine) as session:
        try:
            # 1. 启用 RLS
            session.exec(text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"))

            # 2. 删除现有策略（如果存在）
            session.exec(
                text(
                    f"""
            DROP POLICY IF EXISTS {table_name}_tenant_isolation ON {table_name};
            """
                )
            )

            # 3. 创建新的租户隔离策略
            session.exec(
                text(
                    f"""
            CREATE POLICY {table_name}_tenant_isolation ON {table_name}
                FOR ALL USING (tenant_id = current_setting('app.current_tenant')::VARCHAR);
            """
                )
            )

            session.commit()
            print(f"✅ RLS 已为 {table_name} 表启用")

        except Exception as e:
            session.rollback()
            print(f"❌ 为 {table_name} 启用 RLS 失败: {e}")
            raise


def setup_all_tables_rls():
    """为所有表启用 RLS"""
    tables = ["product"]  # 添加你所有的表名

    for table in tables:
        enable_rls_for_table(table)


if __name__ == "__main__":
    setup_all_tables_rls()
