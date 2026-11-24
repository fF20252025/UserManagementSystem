from sqlalchemy import select
from sqlalchemy.orm import Session

from model.bank import Bank


class BankRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, bank: Bank):
        self.db.add(bank)
        self.db.commit()
        self.db.refresh(bank)

        return bank

    def get_by_id(self, bank_id: int):
        return self.db.get(Bank, bank_id)

    def get_all(self):
        statement = (
            select(Bank)
            .order_by(Bank.id)
        )

        return self.db.scalars(statement).all()

    def update(self, bank: Bank):
        self.db.commit()
        self.db.refresh(bank)

        return bank

    def delete(self, bank_id: int):
        bank = self.get_by_id(bank_id)

        if bank:
            self.db.delete(bank)
            self.db.commit()

        return bank