# scripts/debug_rls_detailed.py
from sqlmodel import Session, text
from app.db.connection.conn_rls import engine, get_tenant_session_no_yield
from app.models.m_rls_product import Product


def debug_rls_detailed():
    print("🔍 详细诊断 RLS 问题...")

    # 用不同租户创建会话
    session_acme = get_tenant_session_no_yield("acme_corp")
    session_xyz = get_tenant_session_no_yield("xyz_inc")

    try:
        # 1. 先清理可能存在的测试数据
        session_acme.exec(text("DELETE FROM products"))
        session_acme.commit()

        # 2. 插入测试数据
        print("\n1. 插入测试数据...")
        product_acme = Product(
            tenant_id="acme_corp",
            product_code="ACME-001",
            product_name="Acme Product",
            unit_price=100.00,
        )
        session_acme.add(product_acme)
        session_acme.commit()
        print("✅ Acme 数据插入成功")

        product_xyz = Product(
            tenant_id="xyz_inc",
            product_code="XYZ-001",
            product_name="XYZ Product",
            unit_price=200.00,
        )
        session_xyz.add(product_xyz)
        session_xyz.commit()
        print("✅ XYZ 数据插入成功")

        # 3. 检查实际插入的数据
        print("\n2. 检查数据库中的实际数据...")
        with Session(engine) as admin_session:  # 无 RLS 限制的会话
            all_products = admin_session.exec(
                text("SELECT id, tenant_id, product_code FROM products")
            ).all()
            print("数据库中的所有产品:")
            for p in all_products:
                print(f"  - ID: {p[0]}, 租户: {p[1]}, 代码: {p[2]}")

        # 4. 测试查询隔离
        print("\n3. 测试查询隔离...")

        # Acme 会话的查询
        products_acme = session_acme.exec(
            text("SELECT id, tenant_id, product_code FROM products")
        ).all()
        print(f"Acme 会话看到 {len(products_acme)} 个产品:")
        for p in products_acme:
            print(f"  - ID: {p[0]}, 租户: {p[1]}, 代码: {p[2]}")

        # XYZ 会话的查询
        products_xyz = session_xyz.exec(
            text("SELECT id, tenant_id, product_code FROM products")
        ).all()
        print(f"XYZ 会话看到 {len(products_xyz)} 个产品:")
        for p in products_xyz:
            print(f"  - ID: {p[0]}, 租户: {p[1]}, 代码: {p[2]}")

        # 5. 检查策略的实际执行
        print("\n4. 检查 RLS 策略执行...")
        explain_acme = session_acme.exec(text("EXPLAIN SELECT * FROM products")).all()
        print("Acme 会话的查询计划:")
        for line in explain_acme:
            print(f"  - {line[0]}")

        explain_xyz = session_xyz.exec(text("EXPLAIN SELECT * FROM products")).all()
        print("XYZ 会话的查询计划:")
        for line in explain_xyz:
            print(f"  - {line[0]}")

    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        raise
    finally:
        # 清理
        with Session(engine) as admin_session:
            admin_session.exec(text("DELETE FROM products"))
            admin_session.commit()
        session_acme.close()
        session_xyz.close()


if __name__ == "__main__":
    debug_rls_detailed()
