import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import URL

from database.base import Base
import database.models


load_dotenv()

config = context.config

database_url = os.getenv("DATABASE_URL")
database_password = os.getenv("DATABASE_PASSWORD")

if not database_url:
    raise RuntimeError("DATABASE_URL is not configured.")

if not database_password:
    raise RuntimeError("DATABASE_PASSWORD is not configured.")

database_url = URL.create(
    "postgresql+psycopg",
    username="postgres",
    password=database_password,
    host="localhost",
    port=5432,
    database="wastesense",
)

config.set_main_option(
    "sqlalchemy.url",
    database_url.render_as_string(hide_password=False),
)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


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


def run_migrations_online() -> None:
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
