from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.base import Base


DATABASE_URL = "sqlite:///./havaleh.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_tables():

    # Import models so SQLAlchemy knows all tables
    from model.audit_log import AuditLog
    from model.user import User
    from model.bank import Bank
    from model.account import Account
    from model.car import Car
    from model.home import Home
    from model.refresh_token import RefreshToken
    from model.password_reset_token import PasswordResetToken
    from model.transfer import Transfer

    Base.metadata.create_all(bind=engine)