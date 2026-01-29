# scripts/seed_gst_data.py
from app.db.connection.conn_rls import get_tenant_session_no_yield
from app.models.rls.m_gst_rls import GSTTable
from datetime import datetime, timezone

def seed_initial_gst_data():
    """为示例租户初始化默认税率数据"""
    
    tenants = ["acme_corp", "xyz_inc"]
    
    for tenant_id in tenants:
        print(f"为租户 {tenant_id} 初始化税率数据...")
        session = get_tenant_session_no_yield(tenant_id)
        
        try:
            # 加拿大 GST
            gst_ca = GSTTable(
                tenant_id=tenant_id,
                tax_code="GST",
                tax_name="Goods and Services Tax",
                tax_rate=0.05,
                effective_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                tax_data={
                    "country": "CA",
                    "description": "Federal goods and services tax",
                    "reporting_code": "GST",
                    "is_recoverable": True
                },
                jurisdiction_data={
                    "federal": True,
                    "provinces": ["all"],
                    "requires_registration": True
                }
            )
            
            # 安省 HST
            hst_on = GSTTable(
                tenant_id=tenant_id,
                tax_code="HST_ON",
                tax_name="Harmonized Sales Tax - Ontario", 
                tax_rate=0.13,
                effective_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                tax_data={
                    "country": "CA",
                    "province": "ON", 
                    "description": "Ontario HST (GST + PST)",
                    "components": {
                        "gst_rate": 0.05,
                        "pst_rate": 0.08
                    }
                },
                jurisdiction_data={
                    "federal": True,
                    "province": "ON",
                    "applies_to": ["goods", "services"]
                }
            )
            
            # BC省 PST
            pst_bc = GSTTable(
                tenant_id=tenant_id,
                tax_code="PST_BC", 
                tax_name="Provincial Sales Tax - BC",
                tax_rate=0.07,
                effective_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
                tax_data={
                    "country": "CA",
                    "province": "BC",
                    "description": "British Columbia provincial sales tax",
                    "applies_to_goods": True,
                    "applies_to_services": False
                }
            )
            
            session.add_all([gst_ca, hst_on, pst_bc])
            session.commit()
            print(f"✅ {tenant_id} 税率数据初始化完成")
            
        except Exception as e:
            print(f"❌ {tenant_id} 初始化失败: {e}")
            session.rollback()
        finally:
            session.close()

if __name__ == "__main__":
    seed_initial_gst_data()