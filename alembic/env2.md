import os, sys
sys.path.append(os.path.abspath(os.getcwd()))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from sqlmodel import SQLModel
# from app.models.rls.m_invoice_embedding import InvoiceEmbeddingDB

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata
print("------------------------------------------------------------------------ALEMBIC SEES TABLES:", list(target_metadata.tables.keys()))
print("------------------------------------------------------------------------")

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# --- FIX FOR SQLMODEL AUTOSTRING ---
from alembic.autogenerate.render import renderers
from sqlmodel.sql.sqltypes import AutoString

@renderers.dispatch_for(AutoString)
def render_autostring(type_, autogen_context):
    return "sa.String()"
# -----------------------------------

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
