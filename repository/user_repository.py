from sqlalchemy import select
from sqlalchemy.orm import Session

from model.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_id(self, user_id: int):
        return self.db.get(User, user_id)

    def get_all(self):
        statement = (
            select(User)
            .order_by(User.id)
        )

        return self.db.scalars(statement).all()

    def get_by_email(self, email: str):
        statement = (
            select(User)
            .where(User.email == email)
        )

        return self.db.scalar(statement)

    def get_by_phone(self, phone: str):
        statement = (
            select(User)
            .where(User.phone == phone)
        )

        return self.db.scalar(statement)

    def update(self, user: User):
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete(self, user_id: int):
        user = self.get_by_id(user_id)

        if user:
            self.db.delete(user)
            self.db.commit()

        return user