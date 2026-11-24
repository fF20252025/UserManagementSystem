
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from controller.auth import get_current_user
from model.database import get_db
from model.user import User
from service.bank_service import BankService
from service.authorization_service import AuthorizationService
from service.audit_log_service import AuditLogService


router = APIRouter(
    prefix="/banks",
    tags=["Banks"]
)


# =========================
# Request Models
# =========================

class BankCreate(BaseModel):
    name: str
    services: str | None = None
    year: int | None = None


class BankUpdate(BaseModel):
    name: str | None = None
    services: str | None = None
    year: int | None = None


# =========================
# Helper Functions
# =========================

def bank_to_dict(bank):
    return {
        "id": bank.id,
        "name": bank.name,
        "services": bank.services,
        "year": bank.year
    }


def get_client_ip(request: Request):
    if request.client:
        return request.client.host
    return None


def write_audit_log(
    db: Session,
    current_user: User,
    request: Request,
    action: str,
    bank_id: int,
    description: str
):
    audit_service = AuditLogService(db)

    audit_service.log_action(
        user_id=current_user.id,
        section="banks",
        action=action,
        entity="bank",
        entity_id=bank_id,
        description=description,
        ip_address=get_client_ip(request)
    )


# =========================
# Create Bank
# =========================

@router.post("/")
def create_bank(
    data: BankCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_add(
        current_user.role
    )

    service = BankService(db)

    try:
        bank = service.create_bank(
            name=data.name,
            services=data.services,
            year=data.year
        )

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="CREATE",
            bank_id=bank.id,
            description=f"بانک جدید با نام {bank.name} ایجاد شد."
        )

        return {
            "message": "Bank created successfully",
            "bank": bank_to_dict(bank)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Get All Banks
# =========================

@router.get("/")
def get_all_banks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    service = BankService(db)

    banks = service.get_all_banks()

    return [
        bank_to_dict(bank)
        for bank in banks
    ]


# =========================
# Get Bank By ID
# =========================

@router.get("/{bank_id}")
def get_bank(
    bank_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    service = BankService(db)

    try:
        bank = service.get_bank(bank_id)

        return bank_to_dict(bank)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# =========================
# Update Bank
# =========================

@router.put("/{bank_id}")
def update_bank(
    bank_id: int,
    data: BankUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_update(
        current_user.role
    )

    service = BankService(db)

    try:
        bank = service.update_bank(
            bank_id=bank_id,
            name=data.name,
            services=data.services,
            year=data.year
        )

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="UPDATE",
            bank_id=bank.id,
            description=f"اطلاعات بانک {bank.name} ویرایش شد."
        )

        return {
            "message": "Bank updated successfully",
            "bank": bank_to_dict(bank)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Delete Bank
# =========================

@router.delete("/{bank_id}")
def delete_bank(
    bank_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_delete(
        current_user.role
    )

    service = BankService(db)

    try:
        # ابتدا اطلاعات بانک را می‌گیریم تا نام آن در گزارش ثبت شود
        bank = service.get_bank(bank_id)
        bank_name = bank.name

        service.delete_bank(bank_id)

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="DELETE",
            bank_id=bank_id,
            description=f"بانک {bank_name} حذف شد."
        )

        return {
            "message": "Bank deleted successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )
