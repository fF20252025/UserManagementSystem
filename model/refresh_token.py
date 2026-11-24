from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

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

    revoked: Mapped[bool] = mapped_column(
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
        back_populates="refresh_tokens"
    )

    def __repr__(self):

        return (
            f"RefreshToken("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"revoked={self.revoked}, "
            f"expires_at='{self.expires_at}'"
            f")"
        )