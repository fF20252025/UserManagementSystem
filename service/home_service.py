from sqlalchemy.orm import Session

from model.home import Home
from repository.home_repository import HomeRepository


class HomeService:
    def __init__(self, db: Session):
        self.repository = HomeRepository(db)

    def create_home(
        self,
        user_id,
        address,
        zip_code,
        meters
    ):
        if not address or not address.strip():
            raise ValueError("Address is required")

        if meters is not None and meters < 0:
            raise ValueError("Meters cannot be negative")

        home = Home(
            user_id=user_id,
            address=address,
            zip_code=zip_code,
            meters=meters
        )

        try:
            return self.repository.create(home)
        except Exception as error:
            self.repository.db.rollback()
            raise error

    def get_home(self, home_id):
        home = self.repository.get_by_id(home_id)

        if not home:
            raise ValueError("Home not found")

        return home

    def get_all_homes(self):
        return self.repository.get_all()

    def get_homes_by_user(self, user_id):
        return self.repository.get_by_user_id(user_id)

    def update_home(
        self,
        home_id,
        address,
        zip_code,
        meters
    ):
        home = self.repository.get_by_id(home_id)

        if not home:
            raise ValueError("Home not found")

        if not address or not address.strip():
            raise ValueError("Address is required")

        if meters is not None and meters < 0:
            raise ValueError("Meters cannot be negative")

        home.address = address
        home.zip_code = zip_code
        home.meters = meters

        return self.repository.update(home)

    def delete_home(self, home_id):
        home = self.repository.get_by_id(home_id)

        if not home:
            raise ValueError("Home not found")

        self.repository.delete(home_id)

        return True