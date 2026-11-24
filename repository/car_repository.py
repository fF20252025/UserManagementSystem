from sqlalchemy import select
from sqlalchemy.orm import Session

from model.car import Car


class CarRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, car: Car):
        self.db.add(car)
        self.db.commit()
        self.db.refresh(car)

        return car

    def get_by_id(self, car_id: int):
        return self.db.get(Car, car_id)

    def get_all(self):
        statement = (
            select(Car)
            .order_by(Car.id)
        )

        return self.db.scalars(statement).all()

    def get_by_user_id(self, user_id: int):
        statement = (
            select(Car)
            .where(Car.user_id == user_id)
            .order_by(Car.id)
        )

        return self.db.scalars(statement).all()

    def get_by_plate(self, plate: str):
        statement = (
            select(Car)
            .where(Car.plate == plate)
        )

        return self.db.scalar(statement)

    def update(self, car: Car):
        self.db.commit()
        self.db.refresh(car)

        return car

    def delete(self, car_id: int):
        car = self.get_by_id(car_id)

        if car:
            self.db.delete(car)
            self.db.commit()

        return car