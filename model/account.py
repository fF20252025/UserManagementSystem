from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class Account(Base):

    __tablename__ = "account"

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

    number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    balance: Mapped[float] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0
    )

    bank_id: Mapped[int] = mapped_column(
        ForeignKey(
            "bank.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    user = relationship(
        "User",
        back_populates="accounts"
    )

    bank = relationship(
        "Bank",
        back_populates="accounts"
    )

    def __repr__(self):

        return (
            f"Account("
            f"id={self.id}, "
            f"number='{self.number}', "
            f"balance={self.balance}, "
            f"user_id={self.user_id}, "
            f"bank_id={self.bank_id}"
            f")"
        )