
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from model.database import get_db
from controller.auth import get_current_user
from service.audit_log_service import AuditLogService
from service.authorization_service import AuthorizationService


router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.get("/")
def get_all_logs(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    AuthorizationService.require_superadmin(current_user.role)

    service = AuditLogService(db)

    return service.get_all_logs(
        limit=limit,
        offset=offset,
    )


@router.get("/{user_id}")
def get_user_logs(
    user_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    AuthorizationService.require_superadmin(current_user.role)

    service = AuditLogService(db)

    return service.get_user_logs(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
