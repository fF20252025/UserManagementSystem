from logging.config import fileConfig

from alembic import context

from model.database import engine, DATABASE_URL
from model.base import Base

# Import all models
from model.audit_log import AuditLog
from model.user import User
from model.bank import Bank
from model.account import Account
from model.car import Car
from model.home import Home
from model.refresh_token import RefreshToken
from model.password_reset_token import PasswordResetToken
from model.transfer import Transfer

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()