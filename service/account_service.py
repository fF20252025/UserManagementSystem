from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from model.account import Account
from model.transfer import Transfer

from repository.account_repository import AccountRepository
from repository.user_repository import UserRepository
from repository.bank_repository import BankRepository
from repository.transfer_repository import TransferRepository


class AccountService:

    USER_MAX_TRANSFER = Decimal("10000000")
    USER_DAILY_TRANSFER_LIMIT = Decimal("30000000")

    def __init__(self, db: Session):
        self.db = db

        self.repository = AccountRepository(db)
        self.user_repository = UserRepository(db)
        self.bank_repository = BankRepository(db)
        self.transfer_repository = TransferRepository(db)

    # Create Account
    def create_account(self, user_id, number, balance, bank_id):
        if not number or not number.strip():
            raise ValueError("Account number is required")

        number = number.strip()

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        bank = self.bank_repository.get_by_id(bank_id)
        if not bank:
            raise ValueError("Bank not found")

        existing_account = self.repository.get_by_number(number)

        if existing_account:
            raise ValueError("Account number already exists")

        if balance is None:
            balance = Decimal("0")

        try:
            balance = Decimal(str(balance))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Invalid balance")

        if not balance.is_finite() or balance < 0:
            raise ValueError("Balance cannot be negative")

        if balance.as_tuple().exponent < -2:
            raise ValueError(
                "Balance cannot have more than two decimal places"
            )

        account = Account(
            user_id=user_id,
            number=number,
            balance=balance,
            bank_id=bank_id
        )

        try:
            return self.repository.create(account)
        except Exception:
            self.repository.db.rollback()
            raise

    # Get Account
    def get_account(self, account_id):
        account = self.repository.get_by_id(account_id)

        if not account:
            raise ValueError("Account not found")

        return account

    # Get All Accounts
    def get_all_accounts(self):
        return self.repository.get_all()

    # Get Accounts By User
    def get_accounts_by_user(self, user_id):
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        return self.repository.get_by_user_id(user_id)

    # Get Accounts By Bank
    def get_accounts_by_bank(self, bank_id):
        bank = self.bank_repository.get_by_id(bank_id)

        if not bank:
            raise ValueError("Bank not found")

        return self.repository.get_by_bank_id(bank_id)

    # Update Account
    def update_account(self, account_id, number, balance, bank_id):
        account = self.repository.get_by_id(account_id)

        if not account:
            raise ValueError("Account not found")

        if number is None or not number.strip():
            raise ValueError("Account number is required")

        number = number.strip()

        existing_account = self.repository.get_by_number(number)

        if existing_account and existing_account.id != account_id:
            raise ValueError("Account number already exists")

        bank = self.bank_repository.get_by_id(bank_id)

        if not bank:
            raise ValueError("Bank not found")

        if balance is None:
            raise ValueError("Balance is required")

        try:
            balance = Decimal(str(balance))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Invalid balance")

        if not balance.is_finite() or balance < 0:
            raise ValueError("Balance cannot be negative")

        if balance.as_tuple().exponent < -2:
            raise ValueError(
                "Balance cannot have more than two decimal places"
            )

        account.number = number
        account.balance = balance
        account.bank_id = bank_id

        try:
            return self.repository.update(account)
        except Exception:
            self.repository.db.rollback()
            raise

    # Delete Account
    def delete_account(self, account_id):
        account = self.repository.get_by_id(account_id)

        if not account:
            raise ValueError("Account not found")

        try:
            self.repository.delete(account_id)
        except Exception:
            self.repository.db.rollback()
            raise

        return True

    # Transfer
    def transfer(
        self,
        from_account_id,
        to_account_id,
        amount,
        current_user_id,
        current_user_role
    ):
        # ---------------------------------
        # Validate source/destination
        # ---------------------------------

        if from_account_id == to_account_id:
            raise ValueError(
                "Source and destination accounts must be different"
            )

        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Invalid transfer amount")

        if not amount.is_finite():
            raise ValueError("Invalid transfer amount")

        if amount <= 0:
            raise ValueError(
                "Transfer amount must be greater than zero"
            )

        if amount.as_tuple().exponent < -2:
            raise ValueError(
                "Transfer amount cannot have more than two decimal places"
            )

        from_account = self.repository.get_by_id(from_account_id)

        if not from_account:
            raise ValueError("Source account not found")

        to_account = self.repository.get_by_id(to_account_id)

        if not to_account:
            raise ValueError("Destination account not found")

        # ---------------------------------
        # User ownership check
        # ---------------------------------

        if current_user_role == "user":

            if from_account.user_id != current_user_id:
                raise ValueError(
                    "You can only transfer from your own account"
                )

            # ---------------------------------
            # Per-transfer limit
            # ---------------------------------

            if amount > self.USER_MAX_TRANSFER:
                raise ValueError(
                    "Maximum transfer amount for users is 10000000"
                )

            # ---------------------------------
            # Daily transfer limit
            # ---------------------------------

            today_total = Decimal(
                str(
                    self.transfer_repository.get_today_total_by_user(
                        current_user_id
                    )
                )
            )

            if today_total + amount > self.USER_DAILY_TRANSFER_LIMIT:
                raise ValueError(
                    "Daily transfer limit of 30000000 exceeded"
                )

        # ---------------------------------
        # Balance check
        # ---------------------------------

        if from_account.balance < amount:
            raise ValueError("Insufficient balance")

        # ---------------------------------
        # Perform transfer
        # ---------------------------------

        try:
            from_account.balance -= amount
            to_account.balance += amount

            # Create transfer record
            transfer = Transfer(
                source_account_id=from_account.id,
                destination_account_id=to_account.id,
                user_id=current_user_id,
                amount=amount,
                status="SUCCESS"
            )

            self.transfer_repository.create(transfer)

            # Commit everything together
            self.db.commit()

            self.db.refresh(from_account)
            self.db.refresh(to_account)
            self.db.refresh(transfer)

        except Exception:
            self.db.rollback()
            raise

        return {
            "from_account": from_account,
            "to_account": to_account,
            "amount": amount,
            "transfer": transfer
        }