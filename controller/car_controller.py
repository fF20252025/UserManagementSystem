from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from controller.auth import get_current_user
from model.database import get_db
from model.user import User
from service.car_service import CarService
from service.authorization_service import AuthorizationService


router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)


# =========================
# Request Models
# =========================

class CarCreate(BaseModel):
    model: str
    plate: str
    color: str | None = None
    year: int | None = None


class CarUpdate(BaseModel):
    model: str | None = None
    plate: str | None = None
    color: str | None = None
    year: int | None = None


# =========================
# Helper
# =========================

def car_to_dict(car):
    return {
        "id": car.id,
        "user_id": car.user_id,
        "model": car.model,
        "plate": car.plate,
        "color": car.color,
        "year": car.year
    }


# =========================
# Create Car
# =========================

@router.post("/")
def create_car(
    data: CarCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_add(
        current_user.role
    )

    service = CarService(db)

    try:
        car = service.create_car(
            user_id=current_user.id,
            model=data.model,
            plate=data.plate,
            color=data.color,
            year=data.year
        )

        return {
            "message": "Car created successfully",
            "car": car_to_dict(car)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Get My Cars
# =========================

@router.get("/me")
def get_my_cars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    service = CarService(db)

    cars = service.get_cars_by_user(
        current_user.id
    )

    return [
        car_to_dict(car)
        for car in cars
    ]


# =========================
# Get Cars By User
# =========================

@router.get("/user/{user_id}")
def get_cars_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    # Normal user can only see their own cars
    if current_user.role == "user" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own cars"
        )

    service = CarService(db)

    cars = service.get_cars_by_user(
        user_id
    )

    return [
        car_to_dict(car)
        for car in cars
    ]


# =========================
# Get All Cars
# =========================

@router.get("/")
def get_all_cars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    # Normal user cannot see all cars
    if current_user.role == "user":
        raise HTTPException(
            status_code=403,
            detail="Users can only view their own cars"
        )

    service = CarService(db)

    cars = service.get_all_cars()

    return [
        car_to_dict(car)
        for car in cars
    ]


# =========================
# Get Car By ID
# =========================

@router.get("/{car_id}")
def get_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_get(
        current_user.role
    )

    service = CarService(db)

    try:
        car = service.get_car(car_id)

        # Normal user can only see their own car
        if (
            current_user.role == "user"
            and car.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own car"
            )

        return car_to_dict(car)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# =========================
# Update Car
# =========================

@router.put("/{car_id}")
def update_car(
    car_id: int,
    data: CarUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_update(
        current_user.role
    )

    service = CarService(db)

    try:
        car = service.update_car(
            car_id=car_id,
            model=data.model,
            plate=data.plate,
            color=data.color,
            year=data.year
        )

        return {
            "message": "Car updated successfully",
            "car": car_to_dict(car)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# Delete Car
# =========================

@router.delete("/{car_id}")
def delete_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthorizationService.require_delete(
        current_user.role
    )

    service = CarService(db)

    try:
        service.delete_car(car_id)

        return {
            "message": "Car deleted successfully"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )