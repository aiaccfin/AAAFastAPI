# scripts/seed_invoices_data.py
from app.db.connection.conn_rls import get_tenant_session_no_yield
from app.models.rls.m_invoice_rls import InvoiceDB
from datetime import datetime, timedelta

def seed_invoices_data():
    """初始化示例发票数据"""
    
    tenants = ["acme_corp", "xyz_inc"]
    
    for tenant_id in tenants:
        print(f"为租户 {tenant_id} 初始化发票数据...")
        session = get_tenant_session_no_yield(tenant_id)
        
        try:
            # 示例发票1
            invoice1 = InvoiceDB(
                tenant_id=tenant_id,
                invoice_number=f"INV-2024-001",
                invoice_date=datetime(2024, 1, 15),
                due_date=datetime(2024, 2, 15),
                customer_id="CUST-001",
                customer_name="ABC Company",
                customer_email="billing@abc.com",
                customer_address={
                    "street": "123 Main St",
                    "city": "Toronto",
                    "province": "ON",
                    "postal_code": "M1M 1M1"
                },
                subtotal=1000.00,
                tax_amount=130.00,
                total_amount=1130.00,
                amount_paid=0.00,
                balance_due=1130.00,
                status="sent",
                payment_status="pending",
                line_items=[
                    {
                        "description": "Website Development",
                        "quantity": 1,
                        "unit_price": 1000.00,
                        "amount": 1000.00,
                        "tax_rate": 0.13
                    }
                ],
                tax_breakdown={
                    "HST": {"rate": 0.13, "amount": 130.00}
                },
                payment_terms={
                    "net_days": 30,
                    "late_fee_rate": 0.02
                }
            )
            
            # 示例发票2（已付款）
            invoice2 = InvoiceDB(
                tenant_id=tenant_id,
                invoice_number=f"INV-2024-002",
                invoice_date=datetime(2024, 1, 10),
                due_date=datetime(2024, 2, 10),
                customer_id="CUST-002", 
                customer_name="XYZ Corp",
                subtotal=500.00,
                tax_amount=65.00,
                total_amount=565.00,
                amount_paid=565.00,
                balance_due=0.00,
                status="paid",
                payment_status="paid",
                line_items=[
                    {
                        "description": "Monthly Maintenance",
                        "quantity": 1,
                        "unit_price": 500.00,
                        "amount": 500.00
                    }
                ]
            )
            
            session.add_all([invoice1, invoice2])
            session.commit()
            print(f"✅ {tenant_id} 发票数据初始化完成")
            
        except Exception as e:
            print(f"❌ {tenant_id} 初始化失败: {e}")
            session.rollback()
        finally:
            session.close()

if __name__ == "__main__":
    seed_invoices_data()