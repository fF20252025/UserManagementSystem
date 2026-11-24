from datetime import date

from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    phone: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user"
    )

    accounts = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    cars = relationship(
        "Car",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    homes = relationship(
        "Home",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"User("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"email='{self.email}', "
            f"phone='{self.phone}', "
            f"birth_date='{self.birth_date}', "
            f"role='{self.role}'"
            f")"
        )