from sqlalchemy.orm import Session

from model.bank import Bank
from repository.bank_repository import BankRepository


class BankService:
    def __init__(self, db: Session):
        self.repository = BankRepository(db)

    def create_bank(self, name, services, year):
        if not name or not name.strip():
            raise ValueError("Bank name is required")

        if year is not None and year < 0:
            raise ValueError("Invalid year")

        bank = Bank(
            name=name,
            services=services,
            year=year
        )

        try:
            return self.repository.create(bank)
        except Exception as error:
            self.repository.db.rollback()
            raise error

    def get_bank(self, bank_id):
        bank = self.repository.get_by_id(bank_id)

        if not bank:
            raise ValueError("Bank not found")

        return bank

    def get_all_banks(self):
        return self.repository.get_all()

    def update_bank(self, bank_id, name, services, year):
        bank = self.repository.get_by_id(bank_id)

        if not bank:
            raise ValueError("Bank not found")

        if not name or not name.strip():
            raise ValueError("Bank name is required")

        if year is not None and year < 0:
            raise ValueError("Invalid year")

        bank.name = name
        bank.services = services
        bank.year = year

        return self.repository.update(bank)

    def delete_bank(self, bank_id):
        bank = self.repository.get_by_id(bank_id)

        if not bank:
            raise ValueError("Bank not found")

        self.repository.delete(bank_id)

        return True