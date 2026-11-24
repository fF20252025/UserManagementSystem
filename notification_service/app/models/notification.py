from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Notification(Base):

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    recipient: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="email"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        index=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    def __repr__(self):
        return (
            f"Notification("
            f"id={self.id}, "
            f"recipient='{self.recipient}', "
            f"status='{self.status}'"
            f")"
        )