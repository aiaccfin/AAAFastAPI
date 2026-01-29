# scripts/debug_session_setup.py
from app.db.connection.conn_rls import get_tenant_session_no_yield
from sqlmodel import text


def debug_session_setup():
    print("🔍 调试会话设置...")

    # 测试会话设置
    session = get_tenant_session_no_yield("acme_corp")

    try:
        # 检查当前租户设置
        result = session.exec(
            text("SELECT current_setting('app.current_tenant', true)")
        )
        current_tenant = result.first()
        print(f"✅ 当前会话的 app.current_tenant: {current_tenant}")

        # 如果没有设置，手动设置
        if not current_tenant:
            print("❌ app.current_tenant 未设置，正在设置...")
            session.exec(text("SET app.current_tenant = 'acme_corp'"))
            session.commit()

            # 再次检查
            result = session.exec(
                text("SELECT current_setting('app.current_tenant', true)")
            )
            current_tenant = result.first()
            print(f"✅ 设置后的 app.current_tenant: {current_tenant}")

    except Exception as e:
        print(f"❌ 检查设置失败: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    debug_session_setup()
