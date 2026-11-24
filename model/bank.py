from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class Bank(Base):

    __tablename__ = "bank"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    services: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    accounts = relationship(
        "Account",
        back_populates="bank"
    )

    def __repr__(self):

        return (
            f"Bank("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"year={self.year}"
            f")"
        )