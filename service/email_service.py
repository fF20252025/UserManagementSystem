import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    SMTP_USERNAME
)


class EmailService:

    def __init__(self):

        if not SMTP_HOST:
            raise RuntimeError(
                "SMTP_HOST is not configured in .env"
            )

        if not SMTP_USERNAME:
            raise RuntimeError(
                "SMTP_USERNAME is not configured in .env"
            )

        if not SMTP_PASSWORD:
            raise RuntimeError(
                "SMTP_PASSWORD is not configured in .env"
            )

    def send_password_reset_email(
        self,
        recipient_email,
        reset_url
    ):

        subject = "Password Reset - Havaleh"

        text_body = f"""
Hello,

We received a request to reset your Havaleh account password.

Click the link below to reset your password:

{reset_url}

This link will expire in 15 minutes.

If you did not request a password reset, you can safely ignore this email.

Best regards,
Havaleh Team
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Password Reset</title>
</head>

<body>

    <h2>Password Reset</h2>

    <p>
        We received a request to reset your Havaleh account password.
    </p>

    <p>
        Click the button below to reset your password:
    </p>

    <p>
        <a
            href="{reset_url}"
            style="
                display: inline-block;
                padding: 12px 20px;
                background-color: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 6px;
            "
        >
            Reset Password
        </a>
    </p>

    <p>
        This link will expire in <strong>15 minutes</strong>.
    </p>

    <p>
        If you did not request a password reset,
        you can safely ignore this email.
    </p>

    <br>

    <p>
        Best regards,<br>
        Havaleh Team
    </p>

</body>
</html>
"""

        message = MIMEMultipart("alternative")

        message["Subject"] = subject
        message["From"] = EMAIL_FROM
        message["To"] = recipient_email

        text_part = MIMEText(
            text_body,
            "plain",
            "utf-8"
        )

        html_part = MIMEText(
            html_body,
            "html",
            "utf-8"
        )

        message.attach(text_part)
        message.attach(html_part)

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD
            )

            server.sendmail(
                EMAIL_FROM,
                recipient_email,
                message.as_string()
            )