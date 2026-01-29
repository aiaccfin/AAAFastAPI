# scripts/test_rls_simple.py
from app.db.connection.conn_rls import get_tenant_session_no_yield
from app.models.m_rls_product import Product
from sqlmodel import select, text, create_engine
from app.config import settings


def check_rls_configuration():
    """检查 RLS 配置状态"""
    print("🔧 检查 RLS 配置...")
    
    # 使用 uxai 用户连接检查
    engine = create_engine(settings.CFG['PG_RLS'], echo=False)
    
    try:
        with engine.connect() as conn:
            # 1. 检查 RLS 状态
            result = conn.execute(text("""
                SELECT tablename, rowsecurity 
                FROM pg_tables 
                WHERE tablename = 'products'
            """))
            rls_status = result.first()
            print(f"✅ RLS 状态: {rls_status[0]} - 启用={rls_status[1]}")
            
            # 2. 检查策略
            result = conn.execute(text("""
                SELECT policyname, cmd, qual 
                FROM pg_policies 
                WHERE tablename = 'products'
            """))
            policy = result.first()
            print(f"✅ 策略状态: {policy[0]} - 操作={policy[1]}")
            print(f"   条件: {policy[2]}")
            
            # 3. 检查当前用户权限
            result = conn.execute(text("""
                SELECT current_user, 
                       (SELECT rolbypassrls FROM pg_roles WHERE rolname = current_user) as can_bypass_rls
            """))
            user_info = result.first()
            print(f"✅ 当前用户: {user_info[0]} - 绕过RLS={user_info[1]}")
            
            # 4. 检查表权限
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.table_privileges 
                WHERE table_name = 'products' AND grantee = current_user
            """))
            perm_count = result.first()[0]
            print(f"✅ 表权限数量: {perm_count}")
            
            # 5. 测试设置租户上下文
            conn.execute(text("SET app.current_tenant = 'config_test'"))
            result = conn.execute(text("SELECT current_setting('app.current_tenant', true)"))
            tenant_setting = result.first()[0]
            print(f"✅ 租户上下文设置: {tenant_setting}")
            
            conn.execute(text("RESET app.current_tenant"))
            
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False
    
    return True


def test_rls_simple():
    print("🔍 测试 RLS 核心功能...")
    
    # 先检查配置
    if not check_rls_configuration():
        print("❌ 配置检查失败，停止测试")
        return
    
    print("\n" + "="*50)
    print("开始功能测试...")
    
    try:
        # 测试1: 用 acme 租户插入数据
        print("\n1. 用 acme_corp 租户插入数据...")
        session_acme = get_tenant_session_no_yield("acme_corp")
        
        # 验证会话的租户上下文
        result = session_acme.exec(text("SELECT current_setting('app.current_tenant', true)"))
        current_tenant = result.first()
        print(f"   会话租户上下文: {current_tenant}")
        
        product_acme = Product(
            tenant_id="acme_corp",  # 匹配 RLS 上下文
            product_code="ACME-001",
            product_name="Acme Product",
            unit_price=100.00,
        )
        session_acme.add(product_acme)
        session_acme.commit()
        print("✅ Acme 数据插入成功")
        
        # 验证数据插入
        products = session_acme.exec(select(Product)).all()
        print(f"   Acme 会话看到 {len(products)} 个产品")
        for p in products:
            print(f"     - {p.product_code}: {p.product_name} (租户: {p.tenant_id})")
        
        # 清理测试数据
        session_acme.exec(text("DELETE FROM products WHERE product_code = 'ACME-001'"))
        session_acme.commit()
        session_acme.close()
        
        print("🎉 RLS 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rls_simple()