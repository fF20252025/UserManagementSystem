
from math import ceil
from datetime import date
from io import BytesIO

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from controller.auth import get_current_user
from model.database import get_db
from model.user import User
from service.transfer_service import TransferService
from service.authorization_service import AuthorizationService
from service.date_service import DateService


router = APIRouter(
    prefix="/transfers",
    tags=["Transfers"]
)


# =========================
# Date Parsing
# =========================

def parse_date_filters(
    start_date: str | None,
    end_date: str | None,
    calendar: str = "gregorian"
):
    """
    Convert incoming Jalali or Gregorian dates
    into Gregorian Python date objects.

    Database dates remain Gregorian.
    """

    try:
        normalized_calendar = DateService.normalize_calendar(
            calendar
        )

        parsed_start_date = DateService.parse_date(
            start_date,
            calendar=normalized_calendar
        )

        parsed_end_date = DateService.parse_date(
            end_date,
            calendar=normalized_calendar
        )

        if (
            parsed_start_date
            and parsed_end_date
            and parsed_start_date > parsed_end_date
        ):
            raise ValueError(
                "تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد."
            )

        return parsed_start_date, parsed_end_date

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Transfer Serialization
# =========================

def transfer_to_dict(transfer):
    return {
        "id": transfer.id,
        "user_id": transfer.user_id,
        "source_account_id": transfer.source_account_id,
        "source_account_number": (
            transfer.source_account.number
            if transfer.source_account
            else None
        ),
        "destination_account_id": transfer.destination_account_id,
        "destination_account_number": (
            transfer.destination_account.number
            if transfer.destination_account
            else None
        ),
        "amount": transfer.amount,
        "status": transfer.status,
        "description": transfer.description,
        "created_at": transfer.created_at
    }


# =========================
# Excel Creation
# =========================

def create_transfers_excel(transfers):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Transfer History"

    headers = [
        "Transfer ID",
        "User ID",
        "Source Account ID",
        "Source Account Number",
        "Destination Account ID",
        "Destination Account Number",
        "Amount",
        "Status",
        "Description",
        "Created At"
    ]

    worksheet.append(headers)

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="1F4E78"
    )

    for cell in worksheet[1]:
        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )
        cell.fill = header_fill
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    for transfer in transfers:
        worksheet.append([
            transfer.id,
            transfer.user_id,
            transfer.source_account_id,
            (
                transfer.source_account.number
                if transfer.source_account
                else None
            ),
            transfer.destination_account_id,
            (
                transfer.destination_account.number
                if transfer.destination_account
                else None
            ),
            float(transfer.amount),
            transfer.status,
            transfer.description,
            (
                transfer.created_at.replace(tzinfo=None)
                if transfer.created_at
                else None
            )
        ])

    column_widths = {
        "A": 15,
        "B": 15,
        "C": 20,
        "D": 25,
        "E": 25,
        "F": 30,
        "G": 18,
        "H": 15,
        "I": 40,
        "J": 25
    }

    for column, width in column_widths.items():
        worksheet.column_dimensions[column].width = width

    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="center")

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


# =========================
# Get Transfer Report
# =========================

@router.get("/report")
def get_transfer_report(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    calendar: str = Query(default="gregorian"),
    source_account_id: int | None = Query(default=None, ge=1),
    destination_account_id: int | None = Query(default=None, ge=1),
    status: str | None = Query(default=None, max_length=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    parsed_start_date, parsed_end_date = parse_date_filters(
        start_date,
        end_date,
        calendar
    )

    service = TransferService(db)

    user_id = (
        current_user.id
        if current_user.role == "user"
        else None
    )

    try:
        report = service.get_transfer_report(
            user_id=user_id,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            status=status
        )

        return report

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Export Filtered Transfer Report to Excel
# =========================

@router.get("/report/export/excel")
def export_transfer_report_excel(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    calendar: str = Query(default="gregorian"),
    source_account_id: int | None = Query(default=None, ge=1),
    destination_account_id: int | None = Query(default=None, ge=1),
    status: str | None = Query(default=None, max_length=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    parsed_start_date, parsed_end_date = parse_date_filters(
        start_date,
        end_date,
        calendar
    )

    service = TransferService(db)

    user_id = (
        current_user.id
        if current_user.role == "user"
        else None
    )

    try:
        all_transfers = []

        page_size = 100
        page = 1

        while True:
            transfers, total = service.get_filtered_transfers(
                user_id=user_id,
                start_date=parsed_start_date,
                end_date=parsed_end_date,
                source_account_id=source_account_id,
                destination_account_id=destination_account_id,
                status=(
                    None
                    if status in (None, "", "ALL")
                    else status
                ),
                page=page,
                page_size=page_size
            )

            all_transfers.extend(transfers)

            if len(all_transfers) >= total or not transfers:
                break

            page += 1

        excel_file = create_transfers_excel(all_transfers)

        filename = "transfer_report.xlsx"

        return StreamingResponse(
            excel_file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                )
            }
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Get Transfer History
# =========================

@router.get("/")
def get_transfers(
    search: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=20),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    calendar: str = Query(default="gregorian"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    parsed_start_date, parsed_end_date = parse_date_filters(
        start_date,
        end_date,
        calendar
    )

    service = TransferService(db)

    user_id = (
        current_user.id
        if current_user.role == "user"
        else None
    )

    try:
        transfers, total = service.get_filtered_transfers(
            user_id=user_id,
            search=search,
            status=status,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            page=page,
            page_size=page_size
        )

        total_pages = ceil(total / page_size) if total else 0

        return {
            "items": [
                transfer_to_dict(transfer)
                for transfer in transfers
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Export Transfer History to Excel
# =========================

@router.get("/export/excel")
def export_transfers_excel(
    search: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=20),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    calendar: str = Query(default="gregorian"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    parsed_start_date, parsed_end_date = parse_date_filters(
        start_date,
        end_date,
        calendar
    )

    service = TransferService(db)

    user_id = (
        current_user.id
        if current_user.role == "user"
        else None
    )

    try:
        transfers, total = service.get_filtered_transfers(
            user_id=user_id,
            search=search,
            status=status,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            page=1,
            page_size=100
        )

        all_transfers = list(transfers)

        total_pages = ceil(total / 100) if total else 0

        for page in range(2, total_pages + 1):
            page_transfers, _ = service.get_filtered_transfers(
                user_id=user_id,
                search=search,
                status=status,
                start_date=parsed_start_date,
                end_date=parsed_end_date,
                page=page,
                page_size=100
            )

            all_transfers.extend(page_transfers)

        excel_file = create_transfers_excel(all_transfers)

        filename = "transfer_history.xlsx"

        return StreamingResponse(
            excel_file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                )
            }
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Get Transfer By ID
# =========================

@router.get("/{transfer_id}")
def get_transfer(
    transfer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    service = TransferService(db)

    try:
        transfer = service.get_transfer(transfer_id)

        if (
            current_user.role == "user"
            and transfer.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own transfers"
            )

        return transfer_to_dict(transfer)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )
