from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from model.refresh_token import RefreshToken


class RefreshTokenRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
        created_at: datetime
    ):
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False,
            created_at=created_at
        )

        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return token

    def get_by_token_hash(self, token_hash: str):
        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash
            )
        )

        return self.db.scalar(statement)

    def revoke(self, token_id: int):
        token = self.db.get(
            RefreshToken,
            token_id
        )

        if token:
            token.revoked = True
            self.db.commit()

        return token

    def revoke_all_by_user(self, user_id: int):
        statement = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id
            )
            .values(revoked=True)
        )

        self.db.execute(statement)
        self.db.commit()

    def delete_expired(self, current_time: datetime):
        statement = (
            delete(RefreshToken)
            .where(
                RefreshToken.expires_at < current_time
            )
        )

        self.db.execute(statement)
        self.db.commit()