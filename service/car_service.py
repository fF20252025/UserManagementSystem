from sqlalchemy.orm import Session

from model.car import Car
from repository.car_repository import CarRepository


class CarService:
    def __init__(self, db: Session):
        self.repository = CarRepository(db)

    def create_car(
        self,
        user_id,
        model,
        plate,
        color,
        year
    ):
        if not model or not model.strip():
            raise ValueError("Car model is required")

        if not plate or not plate.strip():
            raise ValueError("Car plate is required")

        existing_car = self.repository.get_by_plate(plate)

        if existing_car:
            raise ValueError("Car plate already exists")

        if year is not None and year < 0:
            raise ValueError("Invalid year")

        car = Car(
            user_id=user_id,
            model=model,
            plate=plate,
            color=color,
            year=year
        )

        try:
            return self.repository.create(car)
        except Exception as error:
            self.repository.db.rollback()
            raise error

    def get_car(self, car_id):
        car = self.repository.get_by_id(car_id)

        if not car:
            raise ValueError("Car not found")

        return car

    def get_all_cars(self):
        return self.repository.get_all()

    def get_cars_by_user(self, user_id):
        return self.repository.get_by_user_id(user_id)

    def update_car(
        self,
        car_id,
        model,
        plate,
        color,
        year
    ):
        car = self.repository.get_by_id(car_id)

        if not car:
            raise ValueError("Car not found")

        if not model or not model.strip():
            raise ValueError("Car model is required")

        if not plate or not plate.strip():
            raise ValueError("Car plate is required")

        existing_car = self.repository.get_by_plate(plate)

        if existing_car and existing_car.id != car_id:
            raise ValueError("Car plate already exists")

        if year is not None and year < 0:
            raise ValueError("Invalid year")

        car.model = model
        car.plate = plate
        car.color = color
        car.year = year

        return self.repository.update(car)

    def delete_car(self, car_id):
        car = self.repository.get_by_id(car_id)

        if not car:
            raise ValueError("Car not found")

        self.repository.delete(car_id)

        return True