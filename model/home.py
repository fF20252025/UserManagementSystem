from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from model.base import Base


class Home(Base):

    __tablename__ = "home"

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

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    zip_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    meters: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="homes"
    )

    def __repr__(self):

        return (
            f"Home("
            f"id={self.id}, "
            f"address='{self.address}', "
            f"user_id={self.user_id}"
            f")"
        )