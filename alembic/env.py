from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os, sys

sys.path.append(os.path.abspath(os.getcwd()))

from app.db.models.mo_transaction import Transaction

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

TRACK_TABLES = {"transactions", }

def include_object(object, name, type_, reflected, compare_to):
    return type_ != "table" or name in TRACK_TABLES

target_metadata = Transaction.metadata  # metadata can be shared

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
