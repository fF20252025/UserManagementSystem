from sqlalchemy.orm import Session

from model.audit_log import AuditLog
from repository.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session):
        self.repository = AuditLogRepository(db)

    def log_action(
        self,
        user_id: int | None,
        action: str,
        section: str = "panel",
        entity: str | None = None,
        entity_id: int | None = None,
        description: str | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:

        log = AuditLog(
            user_id=user_id,
            section=section,
            action=action,
            entity=entity,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
        )

        return self.repository.create(log)

    def get_all_logs(self, limit: int = 100, offset: int = 0):
        return self.repository.get_all(
            limit=limit,
            offset=offset
        )

    def get_user_logs(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ):
        return self.repository.get_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset
        )