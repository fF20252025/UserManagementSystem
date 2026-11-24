from sqlalchemy import ForeignKey, Numeric, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    source_account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id"),
        nullable=False,
        index=True
    )

    destination_account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id"),
        nullable=False,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    amount: Mapped[float] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SUCCESS"
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    source_account = relationship(
        "Account",
        foreign_keys=[source_account_id]
    )

    destination_account = relationship(
        "Account",
        foreign_keys=[destination_account_id]
    )

    user = relationship("User")