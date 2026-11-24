from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from controller.auth import get_current_user
from model.database import get_db
from model.user import User
from service.home_service import HomeService
from service.authorization_service import AuthorizationService


router = APIRouter(
    prefix="/homes",
    tags=["Homes"]
)


# =========================
# Request Models
# =========================

class HomeCreate(BaseModel):
    address: str
    zip_code: str | None = None
    meters: float | None = None


class HomeUpdate(BaseModel):
    address: str | None = None
    zip_code: str | None = None
    meters: float | None = None


# =========================
# Helper
# =========================

def home_to_dict(home):
    return {
        "id": home.id,
        "user_id": home.user_id,
        "address": home.address,
        "zip_code": home.zip_code,
        "meters": home.meters
    }


# =========================
# Create Home
# =========================

@router.post("/")
def create_home(
    data: HomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_add(
        current_user.role
    )

    service = HomeService(db)

    try:
        home = service.create_home(
            user_id=current_user.id,
            address=data.address,
            zip_code=data.zip_code,
            meters=data.meters
        )

        return {
            "message": "Home created successfully",
            "home": home_to_dict(home)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Get My Homes
# =========================

@router.get("/me")
def get_my_homes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    service = HomeService(db)

    homes = service.get_homes_by_user(
        current_user.id
    )

    return [
        home_to_dict(home)
        for home in homes
    ]


# =========================
# Get Homes By User
# =========================

@router.get("/user/{user_id}")
def get_homes_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    # Normal user can only see their own homes
    if current_user.role == "user" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own homes"
        )

    service = HomeService(db)

    homes = service.get_homes_by_user(
        user_id
    )

    return [
        home_to_dict(home)
        for home in homes
    ]


# =========================
# Get All Homes
# =========================

@router.get("/")
def get_all_homes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    # Normal user cannot see all homes
    if current_user.role == "user":
        raise HTTPException(
            status_code=403,
            detail="Users can only view their own homes"
        )

    service = HomeService(db)

    homes = service.get_all_homes()

    return [
        home_to_dict(home)
        for home in homes
    ]


# =========================
# Get Home By ID
# =========================

@router.get("/{home_id}")
def get_home(
    home_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    service = HomeService(db)

    try:
        home = service.get_home(home_id)

        # Normal user can only see their own home
        if (
            current_user.role == "user"
            and home.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own home"
            )

        return home_to_dict(home)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# =========================
# Update Home
# =========================

@router.put("/{home_id}")
def update_home(
    home_id: int,
    data: HomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_update(
        current_user.role
    )

    service = HomeService(db)

    try:
        home = service.update_home(
            home_id=home_id,
            address=data.address,
            zip_code=data.zip_code,
            meters=data.meters
        )

        return {
            "message": "Home updated successfully",
            "home": home_to_dict(home)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Delete Home
# =========================

@router.delete("/{home_id}")
def delete_home(
    home_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_delete(
        current_user.role
    )

    service = HomeService(db)

    try:
        service.delete_home(home_id)

        return {
            "message": "Home deleted successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )