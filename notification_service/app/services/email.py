import smtplib

from email.message import EmailMessage

from app.core.config import settings


def send_email(
    recipient: str,
    subject: str,
    message: str
):

    email = EmailMessage()

    email["From"] = settings.SMTP_FROM_EMAIL
    email["To"] = recipient
    email["Subject"] = subject

    email.set_content(message)

    if settings.SMTP_USE_SSL and settings.SMTP_USE_TLS:
        raise ValueError(
            "SMTP SSL and STARTTLS cannot be enabled together"
        )

    if settings.SMTP_USE_SSL:

        with smtplib.SMTP_SSL(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=20
        ) as server:

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
            )

            server.send_message(email)

    else:

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=20
        ) as server:

            server.ehlo()

            if settings.SMTP_USE_TLS:
                server.starttls()
                server.ehlo()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
            )

            server.send_message(email)

    return True