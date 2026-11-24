
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
import re

import jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from model.user import User
from repository.user_repository import UserRepository
from repository.refresh_token_repository import RefreshTokenRepository
from repository.password_reset_token_repository import (
    PasswordResetTokenRepository
)
from service.email_service import EmailService


load_dotenv()


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

JWT_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "20")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30")
)

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "PASSWORD_RESET_TOKEN_EXPIRE_MINUTES",
        "15"
    )
)

FRONTEND_RESET_PASSWORD_URL = os.getenv(
    "FRONTEND_RESET_PASSWORD_URL"
)


class UserService:

    def __init__(self, db: Session):

        self.db = db

        self.repository = UserRepository(db)

        self.refresh_token_repository = (
            RefreshTokenRepository(db)
        )

        self.password_reset_token_repository = (
            PasswordResetTokenRepository(db)
        )

        self.email_service = EmailService()

    # =========================================================
    # PASSWORD HASHING
    # =========================================================

    def hash_password(self, password: str) -> str:

        salt = secrets.token_bytes(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100_000
        )

        return (
            salt.hex()
            + ":"
            + password_hash.hex()
        )

    def verify_password(
        self,
        password: str,
        stored_password: str
    ) -> bool:

        try:
            salt_hex, hash_hex = stored_password.split(":")

            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)

            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                100_000
            )

            return secrets.compare_digest(
                password_hash,
                stored_hash
            )

        except (ValueError, TypeError):
            return False

    # =========================================================
    # STRONG PASSWORD VALIDATION
    # =========================================================

    @staticmethod
    def validate_strong_password(password: str):

        if len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters long."
            )

        if not re.search(r"[a-z]", password):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"[A-Z]", password):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"\d", password):
            raise ValueError(
                "Password must contain at least one number."
            )

        if not re.search(r"[!@#$%^&*_\-]", password):
            raise ValueError(
                "Password must contain at least one special character."
            )

    # =========================================================
    # EMAIL VALIDATION
    # =========================================================

    @staticmethod
    def validate_email(email: str):

        if not email or not email.strip():
            raise ValueError("Email is required")

        email = email.strip()

        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(pattern, email):
            raise ValueError(
                "Please enter a valid email address."
            )

    # =========================================================
    # REGISTER
    # =========================================================

    def register(
        self,
        name: str,
        password: str,
        email: str,
        phone: str
    ):

        if not name.strip():
            raise ValueError(
                "Name is required"
            )

        if not password:
            raise ValueError(
                "Password is required"
            )

        self.validate_strong_password(password)

        self.validate_email(email)
        email = email.strip()

        if not phone.strip():
            raise ValueError(
                "Phone is required"
            )

        existing_email = (
            self.repository.get_by_email(email)
        )

        if existing_email:
            raise ValueError(
                "Email already exists"
            )

        existing_phone = (
            self.repository.get_by_phone(phone)
        )

        if existing_phone:
            raise ValueError(
                "Phone already exists"
            )

        hashed_password = self.hash_password(
            password
        )

        user = User(
            name=name,
            password=hashed_password,
            email=email,
            phone=phone,
            role="user"
        )

        try:
            return self.repository.create(user)

        except Exception as error:
            self.repository.db.rollback()
            raise error

    # =========================================================
    # ACCESS TOKEN
    # =========================================================

    def create_access_token(
        self,
        user_id: int
    ) -> str:

        now = datetime.now(timezone.utc)

        expire = (
            now
            + timedelta(
                minutes=JWT_EXPIRE_MINUTES
            )
        )

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": expire
        }

        token = jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        return token

    # =========================================================
    # REFRESH TOKEN
    # =========================================================

    def create_refresh_token(
        self,
        user_id: int
    ) -> str:

        raw_token = secrets.token_urlsafe(64)

        token_hash = hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

        now = datetime.now(timezone.utc)

        expires_at = (
            now
            + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        self.refresh_token_repository.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=now
        )

        return raw_token

    # =========================================================
    # LOGIN
    # =========================================================

    def login(
        self,
        email: str,
        password: str
    ):

        user = self.repository.get_by_email(email)

        if not user:
            raise ValueError(
                "Invalid email or password"
            )

        if not self.verify_password(password, user.password):
            raise ValueError(
                "Invalid email or password"
            )

        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)

        # Record successful login
        from service.audit_log_service import AuditLogService

        audit_service = AuditLogService(self.db)

        audit_service.log_action(
            user_id=user.id,
            action="LOGIN",
            entity="user",
            entity_id=user.id,
            description="User logged in successfully",
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRE_MINUTES * 60
        }

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(
        self,
        refresh_token: str
    ):

        if not refresh_token:
            raise ValueError(
                "Refresh token is required"
            )

        token_hash = hashlib.sha256(
            refresh_token.encode("utf-8")
        ).hexdigest()

        stored_token = (
            self.refresh_token_repository
            .get_by_token_hash(token_hash)
        )

        if not stored_token:
            raise ValueError(
                "Invalid refresh token"
            )

        if stored_token.revoked:
            raise ValueError(
                "Refresh token has been revoked"
            )

        now = datetime.now(timezone.utc)

        expires_at = stored_token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at <= now:

            self.refresh_token_repository.revoke(
                stored_token.id
            )

            raise ValueError(
                "Refresh token has expired"
            )

        # Revoke old refresh token
        self.refresh_token_repository.revoke(
            stored_token.id
        )

        # Create new tokens
        access_token = self.create_access_token(
            stored_token.user_id
        )

        new_refresh_token = (
            self.create_refresh_token(
                stored_token.user_id
            )
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRE_MINUTES * 60
        }

    # =========================================================
    # LOGOUT
    # =========================================================

    def logout(
        self,
        refresh_token: str
    ):

        if not refresh_token:
            raise ValueError(
                "Refresh token is required"
            )

        token_hash = hashlib.sha256(
            refresh_token.encode("utf-8")
        ).hexdigest()

        stored_token = (
            self.refresh_token_repository
            .get_by_token_hash(token_hash)
        )

        if not stored_token:
            raise ValueError(
                "Invalid refresh token"
            )

        self.refresh_token_repository.revoke(
            stored_token.id
        )

        return True

    # =========================================================
    # FORGOT PASSWORD
    # =========================================================

    def forgot_password(
        self,
        email: str
    ):

        if not email.strip():
            raise ValueError(
                "Email is required"
            )

        user = self.repository.get_by_email(
            email
        )

        # Don't reveal whether the email exists.
        if not user:
            return

        # Delete previous active tokens
        self.password_reset_token_repository \
            .delete_active_tokens_by_user(
                user.id
            )

        # Generate raw token
        raw_token = secrets.token_urlsafe(64)

        # Store only hash in database
        token_hash = hashlib.sha256(
            raw_token.encode("utf-8")
        ).hexdigest()

        now = datetime.now(timezone.utc)

        expires_at = (
            now
            + timedelta(
                minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
            )
        )

        self.password_reset_token_repository.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=now
        )

        if not FRONTEND_RESET_PASSWORD_URL:
            raise RuntimeError(
                "FRONTEND_RESET_PASSWORD_URL "
                "is not configured"
            )

        reset_url = (
            FRONTEND_RESET_PASSWORD_URL
            + "?token="
            + raw_token
        )

        self.email_service.send_password_reset_email(
            recipient_email=user.email,
            reset_url=reset_url
        )

    # =========================================================
    # RESET PASSWORD
    # =========================================================

    def reset_password(
        self,
        token: str,
        new_password: str
    ):

        if not token:
            raise ValueError(
                "Reset token is required"
            )

        if not new_password:
            raise ValueError(
                "New password is required"
            )

        self.validate_strong_password(new_password)

        token_hash = hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        reset_token = (
            self.password_reset_token_repository
            .get_by_token_hash(token_hash)
        )

        if not reset_token:
            raise ValueError(
                "Invalid reset token"
            )

        if reset_token.used:
            raise ValueError(
                "Reset token has already been used"
            )

        now = datetime.now(timezone.utc)

        expires_at = reset_token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at <= now:
            raise ValueError(
                "Reset token has expired"
            )

        user = self.repository.get_by_id(
            reset_token.user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        # Hash new password
        user.password = self.hash_password(
            new_password
        )

        self.repository.update(user)

        # Token can no longer be used
        self.password_reset_token_repository \
            .mark_as_used(
                reset_token.id
            )

        # Invalidate all active sessions
        self.refresh_token_repository \
            .revoke_all_by_user(
                user.id
            )

        # Delete other active reset tokens
        self.password_reset_token_repository \
            .delete_active_tokens_by_user(
                user.id
            )

        return True

    # =========================================================
    # VERIFY JWT
    # =========================================================

    def verify_token(
        self,
        token: str
    ):

        try:
            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[JWT_ALGORITHM]
            )

            user_id = payload.get("sub")

            if not user_id:
                raise ValueError(
                    "Invalid token"
                )

            try:
                user_id = int(user_id)

            except (ValueError, TypeError):
                raise ValueError(
                    "Invalid token"
                )

            user = self.repository.get_by_id(
                user_id
            )

            if not user:
                raise ValueError(
                    "User not found"
                )

            return user

        except jwt.ExpiredSignatureError:
            raise ValueError(
                "Access token has expired"
            )

        except jwt.InvalidTokenError:
            raise ValueError(
                "Invalid access token"
            )

    # =========================================================
    # GET USER
    # =========================================================

    def get_user(self, user_id: int):

        user = self.repository.get_by_id(user_id)

        if not user:
            raise ValueError(
                "User not found"
            )

        return user

    # =========================================================
    # GET ALL USERS
    # =========================================================

    def get_all_users(self):

        return self.repository.get_all()

    # =========================================================
    # UPDATE USER
    # =========================================================

    def update_user(
        self,
        user_id: int,
        name: str,
        password: str,
        email: str,
        phone: str
    ):

        user = self.repository.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        # Validate email format
        self.validate_email(email)
        email = email.strip()

        # Check email ownership/conflict
        existing_email = (
            self.repository.get_by_email(email)
        )

        if (
            existing_email
            and existing_email.id != user_id
        ):
            raise ValueError(
                "Email already exists"
            )

        # Check phone ownership/conflict
        existing_phone = (
            self.repository.get_by_phone(phone)
        )

        if (
            existing_phone
            and existing_phone.id != user_id
        ):
            raise ValueError(
                "Phone already exists"
            )

        user.name = name
        user.email = email
        user.phone = phone

        # Only update password if a new one is provided
        if password:

            self.validate_strong_password(password)

            user.password = self.hash_password(
                password
            )

            # Password change should invalidate
            # existing refresh tokens.
            self.refresh_token_repository \
                .revoke_all_by_user(
                    user.id
                )

        return self.repository.update(user)

    # =========================================================
    # DELETE USER
    # =========================================================

    def delete_user(
        self,
        user_id: int
    ):

        user = self.repository.get_by_id(
            user_id
        )

        if not user:
            raise ValueError(
                "User not found"
            )

        self.repository.delete(user_id)

        return True
