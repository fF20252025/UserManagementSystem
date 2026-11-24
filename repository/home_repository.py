from sqlalchemy import select
from sqlalchemy.orm import Session

from model.home import Home


class HomeRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, home: Home):
        self.db.add(home)
        self.db.commit()
        self.db.refresh(home)

        return home

    def get_by_id(self, home_id: int):
        return self.db.get(Home, home_id)

    def get_all(self):
        statement = (
            select(Home)
            .order_by(Home.id)
        )

        return self.db.scalars(statement).all()

    def get_by_user_id(self, user_id: int):
        statement = (
            select(Home)
            .where(Home.user_id == user_id)
            .order_by(Home.id)
        )

        return self.db.scalars(statement).all()

    def update(self, home: Home):
        self.db.commit()
        self.db.refresh(home)

        return home

    def delete(self, home_id: int):
        home = self.get_by_id(home_id)

        if home:
            self.db.delete(home)
            self.db.commit()

        return home