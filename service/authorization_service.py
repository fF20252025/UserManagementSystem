from fastapi import HTTPException


class AuthorizationService:

    @staticmethod
    def can_get(role: str) -> bool:
        return role in {
            "superadmin",
            "admin",
            "operator",
            "user"
        }

    @staticmethod
    def can_add(role: str) -> bool:
        return role == "superadmin"

    @staticmethod
    def can_update(role: str) -> bool:
        return role in {
            "superadmin",
            "admin"
        }

    @staticmethod
    def can_delete(role: str) -> bool:
        return role in {
            "superadmin",
            "admin"
        }

    @staticmethod
    def require_get(role: str):
        if not AuthorizationService.can_get(role):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view this resource"
            )

    @staticmethod
    def require_add(role: str):
        if not AuthorizationService.can_add(role):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to add this resource"
            )

    @staticmethod
    def require_update(role: str):
        if not AuthorizationService.can_update(role):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this resource"
            )

    @staticmethod
    def require_delete(role: str):
        if not AuthorizationService.can_delete(role):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this resource"
            )

    @staticmethod
    def require_superadmin(role: str):
        if role != "superadmin":
            raise HTTPException(
                status_code=403,
                detail="Superadmin permission required"
            )