from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from model.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        created_at: datetime
    ):
        token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
            created_at=created_at
        )

        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return token

    def get_by_token_hash(self, token_hash: str):
        statement = (
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token_hash == token_hash
            )
        )

        return self.db.scalar(statement)

    def mark_as_used(self, token_id: int):
        token = self.db.get(
            PasswordResetToken,
            token_id
        )

        if token:
            token.used = True
            self.db.commit()

        return token

    def delete_active_tokens_by_user(self, user_id: int):
        statement = (
            delete(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used.is_(False)
            )
        )

        self.db.execute(statement)
        self.db.commit()

    def delete_expired_tokens(self, current_time: datetime):
        statement = (
            delete(PasswordResetToken)
            .where(
                PasswordResetToken.expires_at < current_time
            )
        )

        self.db.execute(statement)
        self.db.commit()