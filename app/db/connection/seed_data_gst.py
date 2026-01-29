from sqlmodel import text
from app.db.connection.conn_rls import get_tenant_session_no_yield
from app.models.rls.m_gst_rls import GSTTable
from datetime import datetime, timezone

def check_if_seeded(tenant_id: str, session) -> bool:
    """Check whether the tenant has already been initialized with data."""
    result = session.exec(
        text(f"SELECT COUNT(*) FROM gst62_rls WHERE tenant_id = '{tenant_id}'")
    ).first()
    return result[0] > 0 if result else False

def seed_initial_gst_data():
    """Initialize default tax rate data for the sample tenant."""
    
    tenant_id = "550e8400-e29b-41d4-a716-446655440000"
    print(f"Checking tax rate data for tenant {tenant_id}...")
    
    session = get_tenant_session_no_yield(tenant_id)
    
    try:
        # Check whether initialization has already been performed
        if check_if_seeded(tenant_id, session):
            print(f"⏭️  {tenant_id} already has data, skipping initialization")
            return 0
        
        print(f"Initializing tax rate data for tenant {tenant_id}...")
        
        # Canada GST
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
        
        # Ontario HST
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
        
        # British Columbia PST
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
        print(f"✅ Tax rate data initialization completed for {tenant_id}")
        return 1
        
    except Exception as e:
        print(f"❌ Initialization failed for {tenant_id}: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def create_seeds():
    """Main seed data function."""
    print("Starting seed data check and initialization...")
    seeded_count = seed_initial_gst_data()
    
    if seeded_count > 0:
        print("✅ Seed data initialization completed")
    else:
        print("⏭️  Data already exists, no initialization required")
    
    return seeded_count
