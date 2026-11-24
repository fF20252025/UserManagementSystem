import os

import httpx


NOTIFICATION_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL",
    "http://127.0.0.1:8001"
)

NOTIFICATION_API_KEY = os.getenv(
    "NOTIFICATION_API_KEY"
)


def send_email(
    recipient: str,
    subject: str,
    message: str
):

    if not NOTIFICATION_API_KEY:
        raise RuntimeError(
            "Notification API key is not configured"
        )

    url = f"{NOTIFICATION_URL}/notifications/email"

    headers = {
        "X-API-Key": NOTIFICATION_API_KEY
    }

    payload = {
        "recipient": recipient,
        "subject": subject,
        "message": message
    }

    try:

        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except httpx.HTTPError as exc:

        raise RuntimeError(
            f"Notification service error: {exc}"
        ) from exc