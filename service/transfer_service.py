from sqlalchemy.orm import Session

from repository.transfer_repository import TransferRepository


class TransferService:

    def __init__(self, db: Session):
        self.repository = TransferRepository(db)

    # Get all transfers
    def get_all_transfers(self, limit=100, offset=0):
        return self.repository.get_all(
            limit=limit,
            offset=offset
        )

    # Get transfers by user
    def get_user_transfers(self, user_id, limit=100, offset=0):
        return self.repository.get_by_user_id(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

    # Search and paginate transfers
    def get_filtered_transfers(
        self,
        user_id=None,
        search=None,
        status=None,
        start_date=None,
        end_date=None,
        source_account_id=None,
        destination_account_id=None,
        page=1,
        page_size=20
    ):

        if page < 1:
            raise ValueError("Page must be greater than zero")

        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        if search:
            search = search.strip()

            if len(search) > 100:
                raise ValueError("Search text is too long")

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError("Start date cannot be after end date")

        if source_account_id is not None and source_account_id < 1:
            raise ValueError("Source account ID must be greater than zero")

        if destination_account_id is not None and destination_account_id < 1:
            raise ValueError("Destination account ID must be greater than zero")

        if status not in (None, "", "SUCCESS", "FAILED"):
            raise ValueError("Status must be SUCCESS or FAILED")

        return self.repository.get_filtered_transfers(
            user_id=user_id,
            search=search,
            status=status,
            start_date=start_date,
            end_date=end_date,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            page=page,
            page_size=page_size
        )

    # Get transfer by ID
    def get_transfer(self, transfer_id):

        transfer = self.repository.get_by_id(transfer_id)

        if not transfer:
            raise ValueError("Transfer not found")

        return transfer

    # Get transfer report with optional filters
    def get_transfer_report(
        self,
        user_id=None,
        start_date=None,
        end_date=None,
        source_account_id=None,
        destination_account_id=None,
        status=None
    ):

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError("Start date cannot be after end date")

        if source_account_id is not None and source_account_id < 1:
            raise ValueError("Source account ID must be greater than zero")

        if destination_account_id is not None and destination_account_id < 1:
            raise ValueError(
                "Destination account ID must be greater than zero"
            )

        if status not in (None, "", "ALL", "SUCCESS", "FAILED"):
            raise ValueError(
                "Status must be ALL, SUCCESS, or FAILED"
            )

        if status in ("", "ALL"):
            status = None

        return self.repository.get_transfer_report(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            status=status
        )