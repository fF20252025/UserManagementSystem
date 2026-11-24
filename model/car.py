from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class Car(Base):

    __tablename__ = "cars"

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

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    plate: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    color: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="cars"
    )

    def __repr__(self):

        return (
            f"Car("
            f"id={self.id}, "
            f"model='{self.model}', "
            f"plate='{self.plate}', "
            f"user_id={self.user_id}"
            f")"
        )