# scripts/test_rls_simple.py
from app.db.connection.conn_rls import get_tenant_session_no_yield
from app.models.m_rls_product import Product
from sqlmodel import select


def test_rls_simple():
    print("🔍 测试 RLS 核心功能...")

    # 测试1: 用 acme 租户插入数据
    print("\n1. 用 acme_corp 租户插入数据...")
    session_acme = get_tenant_session_no_yield("acme_corp")

    product_acme = Product(
        tenant_id="acme_corp",  # 匹配 RLS 上下文
        product_code="ACME-001",
        product_name="Acme Product",
        unit_price=100.00,
    )
    session_acme.add(product_acme)
    session_acme.commit()
    print("✅ Acme 数据插入成功")


if __name__ == "__main__":
    test_rls_simple()
