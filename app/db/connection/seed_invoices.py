from sqlmodel import text
from app.db.connection.conn_rls import get_tenant_session_no_yield
from app.models.rls.m_invoice_rls import InvoiceDB
from datetime import datetime, timezone, timedelta


def check_if_invoice_seeded(tenant_id: str, session) -> bool:
    """检查租户是否已经初始化过发票数据"""
    result = session.exec(
        text(
            f"SELECT COUNT(*) FROM invoices_rls WHERE tenant_id = '{tenant_id}'")
    ).first()
    return result[0] > 0 if result else False


def seed_initial_invoice_data():
    """为示例租户初始化默认发票数据"""

    tenant_id = "550e8400-e29b-41d4-a716-446655440000"
    print(f"检查租户 {tenant_id} 的发票数据...")

    session = get_tenant_session_no_yield(tenant_id)

    try:
        # 检查是否已经初始化过
        if check_if_invoice_seeded(tenant_id, session):
            print(f"⏭️  {tenant_id} 已有发票数据，跳过初始化")
            return 0

        print(f"为租户 {tenant_id} 初始化发票数据...")

        # 发票1：已付款
        invoice1 = InvoiceDB(
            tenant_id=tenant_id,
            invoice_prefix="INV-",
            invoice_sequence=8001,
            issue_date=datetime(2024, 1, 15, tzinfo=timezone.utc),
            due_date=datetime(2024, 2, 15, tzinfo=timezone.utc),
            customer_id="550e8400-e29b-41d4-a716-446655440001",
            customer_name="ABC Company",
            customer_email="billing@abc.com",
            subtotal=100000,  # $1000.00
            discount_type="flat",
            discount_rate=0,
            discount_flat_amount=5000,

            discounted_subtotal=95000,  # $950.00
            tax_amount=12350,  # $123.50
            total_amount=107350,  # $1073.50
            amount_paid=107350,
            balance_due=0,
            status="paid",
            payment_status="paid",
            line_items=[
                {
                    "description": "Website Development",
                    "quantity": 1,
                    "unit_price": 100000,
                    "amount": 100000
                }
            ]
        )

        # 发票2：待付款
        invoice2 = InvoiceDB(
            tenant_id=tenant_id,
            invoice_prefix="INV-",
            invoice_sequence=8002,
            issue_date=datetime(2024, 1, 20, tzinfo=timezone.utc),
            due_date=datetime(2024, 2, 20, tzinfo=timezone.utc),
            customer_id="550e8400-e29b-41d4-a716-446655440002",
            customer_name="XYZ Corp",
            customer_email="accounts@xyz.com",
            subtotal=150000,  # $1500.00
            discount_type="percentage",
            discount_rate=10,
            discount_flat_amount=15000,
            discounted_subtotal=135000,  # $1350.00
            tax_amount=17550,  # $175.50
            total_amount=152550,  # $1525.50
            amount_paid=0,
            balance_due=152550,
            status="sent",
            payment_status="pending",
            line_items=[
                {
                    "description": "Mobile App Development",
                    "quantity": 1,
                    "unit_price": 150000,
                    "amount": 150000
                }
            ]
        )

        # 发票3：部分付款
        invoice3 = InvoiceDB(
            tenant_id=tenant_id,
            invoice_prefix="INV-",
            invoice_sequence=8003,
            issue_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
            due_date=datetime(2024, 3, 1, tzinfo=timezone.utc),
            customer_id="550e8400-e29b-41d4-a716-446655440003",
            customer_name="Global Consulting",
            customer_email="finance@global.com",
            subtotal=80000,  # $800.00
            discount_type=None,
            discount_rate=0,
            discount_flat_amount=0,
            discounted_subtotal=80000,  # $800.00
            tax_amount=10400,  # $104.00
            total_amount=90400,  # $904.00
            amount_paid=45200,  # 付了50%
            balance_due=45200,
            status="sent",
            payment_status="partial",
            line_items=[
                {
                    "description": "Technical Consulting",
                    "quantity": 40,
                    "unit_price": 2000,  # $20.00/小时
                    "amount": 80000
                }
            ]
        )

        session.add_all([invoice1, invoice2, invoice3])
        session.commit()
        print(f"✅ {tenant_id} 发票数据初始化完成")
        return 3

    except Exception as e:
        print(f"❌ {tenant_id} 初始化失败: {e}")
        session.rollback()
        return 0
    finally:
        session.close()


def create_invoice_seeds():
    """主发票种子数据函数"""
    print("开始检查并初始化发票种子数据...")
    seeded_count = seed_initial_invoice_data()

    if seeded_count > 0:
        print(f"✅ 发票种子数据初始化完成，创建了 {seeded_count} 张发票")
    else:
        print("⏭️  已有发票数据，无需初始化")

    return seeded_count
