from sqlmodel import Session, SQLModel, create_engine, text
from typing import Generator

from app.config import settings

# Import your specific RLS models
from app.models.rls import m_gst_rls
from app.models.rls import m_log_rls
from app.models.rls import m_user_rls

engine = create_engine(settings.CFG['PG_AIACC'], echo=False)
engine_rls_crud = create_engine(settings.CFG['PG_RLS'], echo=False)
engine_rls_create = create_engine(settings.CFG['PG_RLS_POSTGRES'], echo=False)

# def create_log_audit_function():
#     """Create or replace the log_audit() function in PostgreSQL"""
#     with Session(engine_rls_create) as session:
#         session.exec(text("""
#             CREATE OR REPLACE FUNCTION log_audit()
#             RETURNS TRIGGER AS $$
#             DECLARE
#                 rec_before JSONB;
#                 rec_after JSONB;
#             BEGIN
#                 IF TG_OP = 'INSERT' THEN
#                     rec_before := NULL;
#                     rec_after := to_jsonb(NEW);
#                 ELSIF TG_OP = 'UPDATE' THEN
#                     rec_before := to_jsonb(OLD);
#                     rec_after := to_jsonb(NEW);
#                 ELSIF TG_OP = 'DELETE' THEN
#                     rec_before := to_jsonb(OLD);
#                     rec_after := NULL;
#                 END IF;

#                 INSERT INTO audit_logs(
#                     table_name,
#                     operation,
#                     tenant_id,
#                     role_id,
#                     data_before,
#                     data_after,
#                     created_at,
#                     created_by
#                 ) VALUES (
#                     TG_TABLE_NAME,
#                     TG_OP,
#                     current_setting('app.current_tenant', true),
#                     current_setting('app.current_role_id', true)::INT,
#                     rec_before,
#                     rec_after,
#                     now(),
#                     current_setting('app.current_user', true)
#                 );

#                 RETURN NEW;
#             END;
#             $$ LANGUAGE plpgsql;
#         """))
#         session.commit()
#         print("✅ log_audit() function created or replaced")


# def attach_audit_triggers(RLS_TABLES):
#     """Attach triggers to all tables that require auditing"""
#     with Session(engine_rls_create) as session:
#         for table in RLS_TABLES:
#             table_name = table.name
#             trigger_name = f"{table_name}_audit_trigger"
#             session.exec(text(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};"))
#             session.exec(text(f"""
#                 CREATE TRIGGER {trigger_name}
#                 AFTER INSERT OR UPDATE OR DELETE ON {table_name}
#                 FOR EACH ROW
#                 EXECUTE FUNCTION log_audit();
#             """))
#             print(f"✅ Trigger attached to {table_name}")
#         session.commit()


def create_log_audit_function():
    with Session(engine_rls_create) as session:
        session.exec(text("""
        CREATE OR REPLACE FUNCTION log_audit()
        RETURNS TRIGGER AS $$
        DECLARE
            rec_before JSONB;
            rec_after JSONB;
        BEGIN
            IF TG_OP = 'INSERT' THEN
                rec_before := NULL;
                rec_after := to_jsonb(NEW);
            ELSIF TG_OP = 'UPDATE' THEN
                rec_before := to_jsonb(OLD);
                rec_after := to_jsonb(NEW);
            ELSIF TG_OP = 'DELETE' THEN
                rec_before := to_jsonb(OLD);
                rec_after := NULL;
            END IF;

            INSERT INTO audit_logs(
                tenant_id,
                user_id,
    
                table_name,
                operation,

                data_before,
                data_after,
                created_at,
                created_by

            ) VALUES (
                current_setting('app.current_tenant_id', true),
                current_setting('app.current_user_id', true)::INT,
                TG_TABLE_NAME,
                TG_OP,
                rec_before,
                rec_after,
                now(),
                current_setting('app.current_user', true)
            );

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """))
        session.commit()
        print("✅ log_audit() function created or replaced")
        
        
def attach_audit_triggers(RLS_TABLES):
    """tables: list of SQLAlchemy Table objects"""
    with Session(engine_rls_create) as session:
        for table in RLS_TABLES:
            table_name = table.name
            trigger_name = f"{table_name}_audit_trigger"

            session.exec(text(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table_name}"))
            session.exec(text(f"""
                CREATE TRIGGER {trigger_name}
                AFTER INSERT OR UPDATE OR DELETE ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION log_audit();
            """))
            print(f"✅ Trigger attached to {table_name}")

        session.commit()
