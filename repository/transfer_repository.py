from datetime import datetime, time, timedelta

from sqlalchemy import select, func, or_, case
from sqlalchemy.orm import Session, aliased, selectinload

from model.transfer import Transfer
from model.account import Account


class TransferRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, transfer: Transfer):
        self.db.add(transfer)
        self.db.flush()
        return transfer

    # Get transfer by ID
    def get_by_id(self, transfer_id: int):
        statement = (
            select(Transfer)
            .options(
                selectinload(Transfer.source_account),
                selectinload(Transfer.destination_account)
            )
            .where(Transfer.id == transfer_id)
        )

        return self.db.scalars(statement).first()

    # Get all transfers
    def get_all(self, limit=100, offset=0):
        statement = (
            select(Transfer)
            .options(
                selectinload(Transfer.source_account),
                selectinload(Transfer.destination_account)
            )
            .order_by(
                Transfer.created_at.desc(),
                Transfer.id.desc()
            )
            .limit(limit)
            .offset(offset)
        )

        return self.db.scalars(statement).all()

    # Get transfers by user
    def get_by_user_id(self, user_id: int, limit=100, offset=0):
        statement = (
            select(Transfer)
            .options(
                selectinload(Transfer.source_account),
                selectinload(Transfer.destination_account)
            )
            .where(Transfer.user_id == user_id)
            .order_by(
                Transfer.created_at.desc(),
                Transfer.id.desc()
            )
            .limit(limit)
            .offset(offset)
        )

        return self.db.scalars(statement).all()

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
        SourceAccount = aliased(Account)
        DestinationAccount = aliased(Account)

        filters = []

        if user_id is not None:
            filters.append(Transfer.user_id == user_id)

        if source_account_id is not None:
            filters.append(Transfer.source_account_id == source_account_id)

        if destination_account_id is not None:
            filters.append(
                Transfer.destination_account_id == destination_account_id
            )

        if search:
            search = search.strip()

            search_conditions = [
                SourceAccount.number.ilike(f"%{search}%"),
                DestinationAccount.number.ilike(f"%{search}%")
            ]

            if search.isdigit():
                search_conditions.append(
                    Transfer.id == int(search)
                )

            filters.append(or_(*search_conditions))

        if status:
            filters.append(Transfer.status == status)

        if start_date:
            start_datetime = datetime.combine(start_date, time.min)
            filters.append(Transfer.created_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(
                end_date + timedelta(days=1),
                time.min
            )
            filters.append(Transfer.created_at < end_datetime)

        count_statement = (
            select(func.count(Transfer.id))
            .select_from(Transfer)
            .outerjoin(
                SourceAccount,
                Transfer.source_account_id == SourceAccount.id
            )
            .outerjoin(
                DestinationAccount,
                Transfer.destination_account_id == DestinationAccount.id
            )
            .where(*filters)
        )

        total = self.db.scalar(count_statement) or 0

        offset = (page - 1) * page_size

        statement = (
            select(Transfer)
            .options(
                selectinload(Transfer.source_account),
                selectinload(Transfer.destination_account)
            )
            .outerjoin(
                SourceAccount,
                Transfer.source_account_id == SourceAccount.id
            )
            .outerjoin(
                DestinationAccount,
                Transfer.destination_account_id == DestinationAccount.id
            )
            .where(*filters)
            .order_by(
                Transfer.created_at.desc(),
                Transfer.id.desc()
            )
            .limit(page_size)
            .offset(offset)
        )

        items = self.db.scalars(statement).all()

        return items, total

    # Calculate today's successful transfers
    def get_today_total_by_user(self, user_id: int):

        now = datetime.now()

        start_of_day = datetime.combine(now.date(), time.min)
        start_of_next_day = start_of_day + timedelta(days=1)

        statement = (
            select(func.coalesce(func.sum(Transfer.amount), 0))
            .where(
                Transfer.user_id == user_id,
                Transfer.status == "SUCCESS",
                Transfer.created_at >= start_of_day,
                Transfer.created_at < start_of_next_day
            )
        )

        result = self.db.scalar(statement)

        return result or 0

    # Build date filters for reports
    def _get_report_filters(
        self,
        user_id=None,
        start_date=None,
        end_date=None,
        source_account_id=None,
        destination_account_id=None,
        status=None
    ):
        filters = []

        if user_id is not None:
            filters.append(Transfer.user_id == user_id)

        if source_account_id is not None:
            filters.append(Transfer.source_account_id == source_account_id)

        if destination_account_id is not None:
            filters.append(
                Transfer.destination_account_id == destination_account_id
            )

        if status == "SUCCESS":
            filters.append(Transfer.status == "SUCCESS")
        elif status == "FAILED":
            filters.append(Transfer.status != "SUCCESS")

        if start_date:
            start_datetime = datetime.combine(start_date, time.min)
            filters.append(Transfer.created_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(
                end_date + timedelta(days=1),
                time.min
            )
            filters.append(Transfer.created_at < end_datetime)

        return filters

    # Get overall transfer statistics
    def get_transfer_summary(
        self,
        user_id=None,
        start_date=None,
        end_date=None,
        source_account_id=None,
        destination_account_id=None,
        status=None
    ):
        filters = self._get_report_filters(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            status=status
        )

        statement = (
            select(
                func.count(Transfer.id).label("total_count"),

                func.coalesce(
                    func.sum(Transfer.amount), 0
                ).label("total_amount"),

                func.sum(
                    case(
                        (Transfer.status == "SUCCESS", 1),
                        else_=0
                    )
                ).label("success_count"),

                func.coalesce(
                    func.sum(
                        case(
                            (Transfer.status == "SUCCESS", Transfer.amount),
                            else_=0
                        )
                    ),
                    0
                ).label("success_amount"),

                func.sum(
                    case(
                        (Transfer.status != "SUCCESS", 1),
                        else_=0
                    )
                ).label("failed_count"),

                func.coalesce(
                    func.sum(
                        case(
                            (Transfer.status != "SUCCESS", Transfer.amount),
                            else_=0
                        )
                    ),
                    0
                ).label("failed_amount")
            )
            .where(*filters)
        )

        result = self.db.execute(statement).one()

        return {
            "total_count": result.total_count or 0,
            "total_amount": result.total_amount or 0,
            "success_count": result.success_count or 0,
            "success_amount": result.success_amount or 0,
            "failed_count": result.failed_count or 0,
            "failed_amount": result.failed_amount or 0
        }

    # Get daily transfer statistics
    def get_daily_transfer_statistics(
        self,
        user_id=None,
        start_date=None,
        end_date=None,
        source_account_id=None,
        destination_account_id=None,
        status=None
    ):
        filters = self._get_report_filters(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            status=status
        )

        date_column = func.date(Transfer.created_at)

        statement = (
            select(
                date_column.label("report_date"),
                func.count(Transfer.id).label("total_count"),
                func.coalesce(
                    func.sum(Transfer.amount), 0
                ).label("total_amount"),
                func.sum(
                    case(
                        (Transfer.status == "SUCCESS", 1),
                        else_=0
                    )
                ).label("success_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (Transfer.status == "SUCCESS", Transfer.amount),
                            else_=0
                        )
                    ),
                    0
                ).label("success_amount"),
                func.sum(
                    case(
                        (Transfer.status != "SUCCESS", 1),
                        else_=0
                    )
                ).label("failed_count")
            )
            .where(*filters)
            .group_by(date_column)
            .order_by(date_column.asc())
        )

        results = self.db.execute(statement).all()

        return [
            {
                "date": row.report_date,
                "total_count": row.total_count or 0,
                "total_amount": row.total_amount or 0,
                "success_count": row.success_count or 0,
                "success_amount": row.success_amount or 0,
                "failed_count": row.failed_count or 0
            }
            for row in results
        ]

    # Get monthly transfer statistics
    def get_monthly_transfer_statistics(
        self,
        user_id=None,
        start_date=None,
        end_date=None,
        source_account_id=None,
        destination_account_id=None,
        status=None
    ):
        filters = self._get_report_filters(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            status=status
        )

        month_column = func.strftime(
            "%Y-%m",
            Transfer.created_at
        )

        statement = (
            select(
                month_column.label("report_month"),
                func.count(Transfer.id).label("total_count"),
                func.coalesce(
                    func.sum(Transfer.amount), 0
                ).label("total_amount"),
                func.sum(
                    case(
                        (Transfer.status == "SUCCESS", 1),
                        else_=0
                    )
                ).label("success_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (Transfer.status == "SUCCESS", Transfer.amount),
                            else_=0
                        )
                    ),
                    0
                ).label("success_amount"),
                func.sum(
                    case(
                        (Transfer.status != "SUCCESS", 1),
                        else_=0
                    )
                ).label("failed_count")
            )
            .where(*filters)
            .group_by(month_column)
            .order_by(month_column.asc())
        )

        results = self.db.execute(statement).all()

        return [
            {
                "month": row.report_month,
                "total_count": row.total_count or 0,
                "total_amount": row.total_amount or 0,
                "success_count": row.success_count or 0,
                "success_amount": row.success_amount or 0,
                "failed_count": row.failed_count or 0
            }
            for row in results
        ]

    # Get complete transfer report
    def get_transfer_report(
        self,
        user_id=None,
        start_date=None,
        end_date=None,
        source_account_id=None,
        destination_account_id=None,
        status=None
    ):
        report_filters = {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "status": status
        }

        return {
            "summary": self.get_transfer_summary(**report_filters),
            "daily": self.get_daily_transfer_statistics(**report_filters),
            "monthly": self.get_monthly_transfer_statistics(**report_filters)
        }