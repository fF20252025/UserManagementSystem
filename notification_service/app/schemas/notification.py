from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class EmailNotificationRequest(BaseModel):

    recipient: EmailStr

    subject: str = Field(
        min_length=1,
        max_length=255
    )

    message: str = Field(
        min_length=1
    )


class NotificationResponse(BaseModel):

    id: int

    recipient: str

    subject: str

    channel: str

    status: str

    error_message: str | None

    created_at: datetime

    sent_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )