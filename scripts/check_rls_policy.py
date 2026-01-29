# scripts/check_rls_policy.py
from sqlmodel import Session, text
from app.db.connection.conn_rls import engine


def check_rls_policy():
    with Session(engine) as session:
        # 检查 RLS 是否启用
        result = session.exec(
            text(
                """
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' AND tablename = 'products'
        """
            )
        )
        table_info = result.first()
        print(f"Products 表 RLS 状态: {table_info}")

        # 检查策略详情
        policies = session.exec(
            text(
                """
            SELECT schemaname, tablename, policyname, 
                   roles, cmd, qual, with_check
            FROM pg_policies 
            WHERE tablename = 'products'
        """
            )
        )

        print("\nProducts 表 RLS 策略:")
        for policy in policies:
            print(
                f"""
            策略名: {policy.policyname}
            命令: {policy.cmd}
            条件: {policy.qual}
            with_check: {policy.with_check}
            """
            )

        # 检查当前会话的租户设置
        current_tenant = session.exec(text("SHOW app.current_tenant")).first()
        print(f"当前会话的 app.current_tenant: {current_tenant}")


if __name__ == "__main__":
    check_rls_policy()
