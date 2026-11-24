from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class PasswordResetToken(Base):

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="password_reset_tokens"
    )

    def __repr__(self):

        return (
            f"PasswordResetToken("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"used={self.used}, "
            f"expires_at='{self.expires_at}'"
            f")"
        )