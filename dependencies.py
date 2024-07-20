from fastapi import Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from db import SessionLocal
from user.models import User



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


def get_current_user(db: db_dependency, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter a valid access token")
    
    current_user = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user