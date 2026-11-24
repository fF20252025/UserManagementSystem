from sqlalchemy import select
from sqlalchemy.orm import Session

from model.account import Account


class AccountRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, account: Account):
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        return account

    def get_by_id(self, account_id: int):
        return self.db.get(Account, account_id)

    def get_all(self):
        statement = (
            select(Account)
            .order_by(Account.id)
        )

        return self.db.scalars(statement).all()

    def get_by_user_id(self, user_id: int):
        statement = (
            select(Account)
            .where(Account.user_id == user_id)
            .order_by(Account.id)
        )

        return self.db.scalars(statement).all()

    def get_by_bank_id(self, bank_id: int):
        statement = (
            select(Account)
            .where(Account.bank_id == bank_id)
            .order_by(Account.id)
        )

        return self.db.scalars(statement).all()

    def get_by_number(self, number: str):
        statement = (
            select(Account)
            .where(Account.number == number)
        )

        return self.db.scalar(statement)

    def update(self, account: Account):
        self.db.commit()
        self.db.refresh(account)

        return account

    def delete(self, account_id: int):
        account = self.get_by_id(account_id)

        if account:
            self.db.delete(account)
            self.db.commit()

        return account