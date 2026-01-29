# scripts/test_rls.py
from app.db.connection.conn_rls import get_tenant_session_no_yield
from app.models.m_rls_product import Product


def test_rls():
    # 测试租户隔离
    session_acme = get_tenant_session_no_yield("acme_corp")
    session_xyz = get_tenant_session_no_yield("xyz_inc")

    # 为 acme 创建产品
    product_acme = Product(
        tenant_id="acme_corp",  # 这个值应该与 RLS 上下文匹配
        product_code="TEST-001",
        product_name="Test Product for Acme",
        unit_price=100.00,
    )
    session_acme.add(product_acme)
    session_acme.commit()

    # 尝试从 xyz 会话查询 - 应该看不到 acme 的数据
    products = session_xyz.exec(select(Product)).all()
    print(f"XYZ 租户看到的产品数量: {len(products)}")  # 应该是 0

    session_acme.close()
    session_xyz.close()


if __name__ == "__main__":
    test_rls()
