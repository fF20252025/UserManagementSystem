
from sqlalchemy.orm import Session

from model.audit_log import AuditLog
from model.user import User


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def _serialize_logs(self, rows):
        result = []

        for log, user_name, user_role in rows:
            result.append({
                "id": log.id,
                "user_id": log.user_id,
                "user_name": user_name,
                "user_role": user_role,
                "section": log.section,
                "action": log.action,
                "entity": log.entity,
                "entity_id": log.entity_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            })

        return result

    def get_all(self, limit: int = 100, offset: int = 0):
        rows = (
            self.db.query(
                AuditLog,
                User.name.label("user_name"),
                User.role.label("user_role")
            )
            .outerjoin(
                User,
                AuditLog.user_id == User.id
            )
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return self._serialize_logs(rows)

    def get_by_user(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ):
        rows = (
            self.db.query(
                AuditLog,
                User.name.label("user_name"),
                User.role.label("user_role")
            )
            .outerjoin(
                User,
                AuditLog.user_id == User.id
            )
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return self._serialize_logs(rows)
