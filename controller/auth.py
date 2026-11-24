from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from model.database import get_db
from service.user_service import UserService


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    user_service = UserService(db)

    try:
        user = user_service.verify_token(token)
        return user

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"}
        )