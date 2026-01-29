# scripts/check_rls_ownership.py
from sqlmodel import Session, text
from app.db.connection.conn_rls import engine


def check_rls_ownership():
    with Session(engine) as session:
        # 检查表所有者和当前用户
        result = session.exec(
            text(
                """
            SELECT 
                tablename,
                tableowner,
                rowsecurity,
                (SELECT current_user) as current_user,
                (SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user) as can_bypass_rls
            FROM pg_tables 
            WHERE schemaname = 'public' AND tablename = 'products'
        """
            )
        ).first()

        print("表所有者和权限信息:")
        print(f"  表名: {result[0]}")
        print(f"  所有者: {result[1]}")
        print(f"  RLS 启用: {result[2]}")
        print(f"  当前用户: {result[3]}")
        print(f"  可绕过RLS: {result[4]}")

        # 检查策略对当前用户是否可见
        policies = session.exec(
            text(
                """
            SELECT 
                policyname,
                roles,
                (SELECT current_user IN (SELECT unnest(roles))) as applies_to_current_user
            FROM pg_policies 
            WHERE tablename = 'products'
        """
            )
        ).all()

        print("\n策略应用情况:")
        for policy in policies:
            print(f"  策略: {policy.policyname}")
            print(f"  应用角色: {policy.roles}")
            print(f"  对当前用户生效: {policy.applies_to_current_user}")


if __name__ == "__main__":
    check_rls_ownership()
