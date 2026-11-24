
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from controller.auth import get_current_user
from model.database import get_db
from model.user import User
from service.account_service import AccountService
from service.audit_log_service import AuditLogService
from service.authorization_service import AuthorizationService


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


# =========================
# Request Models
# =========================

class AccountCreate(BaseModel):
    number: str
    balance: Decimal = Decimal("0")
    bank_id: int


class AccountUpdate(BaseModel):
    number: str | None = None
    balance: Decimal | None = None
    bank_id: int | None = None


class TransferRequest(BaseModel):
    source_account_id: int
    destination_account_id: int
    amount: Decimal


# =========================
# Helpers
# =========================

def account_to_dict(account):
    return {
        "id": account.id,
        "user_id": account.user_id,
        "number": account.number,
        "balance": account.balance,
        "bank_id": account.bank_id
    }


def get_client_ip(request: Request):
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


def write_audit_log(
    db: Session,
    current_user: User,
    request: Request,
    action: str,
    account=None,
    description: str | None = None
):
    service = AuditLogService(db)

    service.log_action(
        user_id=current_user.id,
        action=action,
        section="accounts",
        entity="account",
        entity_id=account.id if account else None,
        description=description,
        ip_address=get_client_ip(request)
    )


# =========================
# Create Account
# =========================

@router.post("/")
def create_account(
    data: AccountCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_add(current_user.role)

    service = AccountService(db)

    try:
        account = service.create_account(
            number=data.number,
            balance=data.balance,
            bank_id=data.bank_id,
            user_id=current_user.id
        )

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="CREATE",
            account=account,
            description=(
                f"حساب بانکی {account.number} "
                f"برای کاربر {current_user.id} ایجاد شد"
            )
        )

        return {
            "message": "Account created successfully",
            "account": account_to_dict(account)
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# =========================
# Get My Accounts
# =========================

@router.get("/me")
def get_my_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    service = AccountService(db)

    try:
        accounts = service.get_accounts_by_user(current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return [account_to_dict(account) for account in accounts]


# =========================
# Transfer
# =========================

@router.post("/transfer")
def transfer(
    data: TransferRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # فقط این سه نقش اجازه انتقال دارند.
    if current_user.role not in {"user", "admin", "superadmin"}:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to transfer money"
        )

    service = AccountService(db)

    try:
        result = service.transfer(
            from_account_id=data.source_account_id,
            to_account_id=data.destination_account_id,
            amount=data.amount,
            current_user_id=current_user.id,
            current_user_role=current_user.role
        )

        source_account = result["from_account"]
        destination_account = result["to_account"]

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="TRANSFER",
            account=source_account,
            description=(
                f"انتقال مبلغ {result['amount']} "
                f"از حساب {source_account.number} "
                f"به حساب {destination_account.number} "
                f"انجام شد"
            )
        )

        return {
            "message": "Transfer completed successfully",
            "result": {
                "from_account": account_to_dict(source_account),
                "to_account": account_to_dict(destination_account),
                "amount": result["amount"],
                "transfer_id": result["transfer"].id
            }
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# =========================
# Get Accounts By User
# =========================

@router.get("/user/{user_id}")
def get_accounts_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    if current_user.role == "user" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own accounts"
        )

    service = AccountService(db)

    try:
        accounts = service.get_accounts_by_user(user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return [account_to_dict(account) for account in accounts]


# =========================
# Get Accounts By Bank
# =========================

@router.get("/bank/{bank_id}")
def get_accounts_by_bank(
    bank_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    if current_user.role == "user":
        raise HTTPException(
            status_code=403,
            detail="Users cannot view accounts by bank"
        )

    service = AccountService(db)

    try:
        accounts = service.get_accounts_by_bank(bank_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return [account_to_dict(account) for account in accounts]


# =========================
# Get All Accounts
# =========================

@router.get("/")
def get_all_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    if current_user.role == "user":
        raise HTTPException(
            status_code=403,
            detail="Users can only view their own accounts"
        )

    service = AccountService(db)
    accounts = service.get_all_accounts()

    return [account_to_dict(account) for account in accounts]


# =========================
# Get Account By ID
# =========================

@router.get("/{account_id}")
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    service = AccountService(db)

    try:
        account = service.get_account(account_id)

        if (
            current_user.role == "user"
            and account.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own account"
            )

        return account_to_dict(account)

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


# =========================
# Update Account
# =========================

@router.put("/{account_id}")
def update_account(
    account_id: int,
    data: AccountUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_update(current_user.role)

    service = AccountService(db)

    try:
        account = service.update_account(
            account_id=account_id,
            number=data.number,
            balance=data.balance,
            bank_id=data.bank_id
        )

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="UPDATE",
            account=account,
            description=f"اطلاعات حساب {account.number} ویرایش شد"
        )

        return {
            "message": "Account updated successfully",
            "account": account_to_dict(account)
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# =========================
# Delete Account
# =========================

@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_delete(current_user.role)

    service = AccountService(db)

    try:
        account = service.get_account(account_id)
        account_number = account.number

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="DELETE",
            account=account,
            description=f"حساب {account_number} حذف شد"
        )

        service.delete_account(account_id)

        return {
            "message": "Account deleted successfully"
        }

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
