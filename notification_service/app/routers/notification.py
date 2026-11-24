import secrets

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    status
)

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.schemas.notification import (
    EmailNotificationRequest,
    NotificationResponse
)

from app.services.email_service import send_email
from app.core.config import settings


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def verify_api_key(
    x_api_key: str = Header(...)
):

    if not secrets.compare_digest(
        x_api_key,
        settings.INTERNAL_API_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )


@router.post(
    "/email",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)]
)
def send_email_notification(
    data: EmailNotificationRequest,
    db: Session = Depends(get_db)
):

    notification = Notification(
        recipient=str(data.recipient),
        subject=data.subject,
        message=data.message,
        channel="email",
        status="PENDING"
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    try:

        notification.status = "PROCESSING"
        db.commit()

        send_email(
            recipient=notification.recipient,
            subject=notification.subject,
            message=notification.message
        )

        notification.status = "SENT"

        notification.sent_at = datetime.now(timezone.utc)

        notification.error_message = None

        db.commit()
        db.refresh(notification)

    except Exception as exc:

        db.rollback()

        notification = db.get(
            Notification,
            notification.id
        )

        if notification is not None:

            notification.status = "FAILED"

            notification.error_message = str(exc)

            db.commit()
            db.refresh(notification)

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Email delivery failed"
        )

    return notification


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    dependencies=[Depends(verify_api_key)]
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):

    notification = db.get(
        Notification,
        notification_id
    )

    if notification is None:

        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return notification