
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from controller.auth import get_current_user
from model.database import get_db
from model.roles import ROLES
from model.user import User
from service.user_service import UserService
from service.authorization_service import AuthorizationService
from service.audit_log_service import AuditLogService


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# Request Models
# =========================

class RegisterRequest(BaseModel):
    name: str
    password: str
    email: str
    phone: str


class CreateUserRequest(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    role: str = "user"


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    password: str | None = None


class RoleUpdate(BaseModel):
    role: str


# =========================
# Helper Functions
# =========================

def user_to_dict(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role
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
    entity_id: int,
    description: str
):
    audit_service = AuditLogService(db)

    audit_service.log_action(
        user_id=current_user.id,
        action=action,
        section="panel",
        entity="user",
        entity_id=entity_id,
        description=description,
        ip_address=get_client_ip(request)
    )


# =========================
# Public Register
# =========================

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    service = UserService(db)

    try:
        user = service.register(
            name=data.name,
            password=data.password,
            email=data.email,
            phone=data.phone
        )

        return {
            "message": "User registered successfully",
            "user": user_to_dict(user)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Admin Create User
# Only Superadmin
# =========================

@router.post("/")
def create_user(
    data: CreateUserRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_add(current_user.role)

    if data.role not in ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    service = UserService(db)

    try:
        user = service.register(
            name=data.name,
            password=data.password,
            email=data.email,
            phone=data.phone
        )

        user.role = data.role
        user = service.repository.update(user)

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="CREATE",
            entity_id=user.id,
            description=f"User created: {user.name}, role: {user.role}"
        )

        return {
            "message": "User created successfully",
            "user": user_to_dict(user)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Login
# =========================

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    service = UserService(db)

    try:
        return service.login(
            email=data.email,
            password=data.password
        )

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error)
        )


# =========================
# Refresh Token
# =========================

@router.post("/refresh")
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):
    service = UserService(db)

    try:
        return service.refresh(
            data.refresh_token
        )

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error)
        )


# =========================
# Logout
# =========================

@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db)
):
    service = UserService(db)

    try:
        service.logout(
            data.refresh_token
        )

        return {
            "message": "Logged out successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Forgot Password
# =========================

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    service = UserService(db)

    try:
        service.forgot_password(
            data.email
        )

        return {
            "message": "Password reset email sent"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Reset Password
# =========================

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    service = UserService(db)

    try:
        service.reset_password(
            token=data.token,
            new_password=data.new_password
        )

        return {
            "message": "Password reset successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Get My Profile
# =========================

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return user_to_dict(current_user)


# =========================
# Get All Users
# =========================

@router.get("/")
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    if current_user.role == "user":
        raise HTTPException(
            status_code=403,
            detail="Users can only view their own information"
        )

    service = UserService(db)

    users = service.get_all_users()

    return [
        user_to_dict(user)
        for user in users
    ]


# =========================
# Get User By ID
# =========================

@router.get("/{user_id}")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(current_user.role)

    if current_user.role == "user" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own information"
        )

    service = UserService(db)

    try:
        user = service.get_user(user_id)

        return user_to_dict(user)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# =========================
# Update User
# Admin and Superadmin
# =========================

@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_update(current_user.role)

    service = UserService(db)

    try:
        user = service.get_user(user_id)

        if (
            current_user.role == "admin"
            and user.role in {"admin", "superadmin"}
        ):
            raise HTTPException(
                status_code=403,
                detail="Admin cannot update this account"
            )

        old_name = user.name

        updated_user = service.update_user(
            user_id=user_id,
            name=data.name if data.name is not None else user.name,
            password=data.password or "",
            email=data.email if data.email is not None else user.email,
            phone=data.phone if data.phone is not None else user.phone
        )

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="UPDATE",
            entity_id=updated_user.id,
            description=f"User information updated: {old_name}"
        )

        if data.password:
            write_audit_log(
                db=db,
                current_user=current_user,
                request=request,
                action="PASSWORD_CHANGE",
                entity_id=updated_user.id,
                description=f"Password changed for user: {updated_user.name}"
            )

        return {
            "message": "User updated successfully",
            "user": user_to_dict(updated_user)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Delete User
# Admin and Superadmin
# =========================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_delete(current_user.role)

    service = UserService(db)

    try:
        user = service.get_user(user_id)

        if user.id == current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You cannot delete your own account"
            )

        if (
            current_user.role == "admin"
            and user.role in {"admin", "superadmin"}
        ):
            raise HTTPException(
                status_code=403,
                detail="Admin cannot delete this account"
            )

        deleted_user_name = user.name
        deleted_user_role = user.role

        service.delete_user(user_id)

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="DELETE",
            entity_id=user_id,
            description=(
                f"User deleted: {deleted_user_name}, "
                f"role: {deleted_user_role}"
            )
        )

        return {
            "message": "User deleted successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# =========================
# Change User Role
# Only Superadmin
# =========================

@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    data: RoleUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_superadmin(
        current_user.role
    )

    if data.role not in ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    service = UserService(db)

    try:
        user = service.get_user(user_id)

        if (
            user.id == current_user.id
            and data.role != "superadmin"
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot change your own superadmin role"
            )

        old_role = user.role
        user.role = data.role

        updated_user = service.repository.update(user)

        write_audit_log(
            db=db,
            current_user=current_user,
            request=request,
            action="CHANGE_ROLE",
            entity_id=updated_user.id,
            description=(
                f"User role changed: {old_role} -> {updated_user.role}"
            )
        )

        return {
            "message": "User role updated successfully",
            "user": user_to_dict(updated_user)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )
