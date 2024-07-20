import datetime
from sqlalchemy import or_
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, status
from werkzeug.security import generate_password_hash, check_password_hash

from user.models import User
from db import db_dependency
from user.schemas import LoginModel, SignUpModel


user = APIRouter(
    prefix="/user",
    tags=["user"]
)


@user.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(db: db_dependency, user: SignUpModel):
    db_email = db.query(User).filter(User.username == user.email).first()
    if db_email is not None:
        return HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail='This email already exists!')
    
    db_username = db.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail='This username already exists!') 
    
    
    new_user = User(
        full_name = user.full_name,
        username = user.username,
        email = user.email,
        password = generate_password_hash(user.password),
        is_staff = user.is_staff
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    response = {
        "success": True,
        "status_code": 201,
        "message": "User created succesfully!",
        "data":{
            "id": new_user.id,
            "full_name": new_user.full_name,
            "username": new_user.username,
            "email": new_user.email,
            "is_staff": new_user.is_staff
        }
    }
    return response



@user.post("/login", status_code=status.HTTP_200_OK)
async def login(db: db_dependency,
                user: LoginModel,
                Authorize: AuthJWT = Depends()):
    # query for login with username or email
    db_user = db.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email
        )
    ).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_lifetime = datetime.timedelta(minutes=60)
        refresh_lifetime = datetime.timedelta(days=3)
        access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)

        token = {
            'access': access_token,
            'refresh': refresh_token
        }

        response = {
            'success': True,
            'status_code': 200,
            'message': 'User successfully logged in',
            'data': token
        }

        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")


# Create new access token via help of refresh token
@user.post('/login/refresh')
async def refresh_token(db: db_dependency, Authorize: AuthJWT = Depends()):
    try:
        access_lifetime = datetime.timedelta(minutes=60)
        Authorize.jwt_refresh_token_required()            
        user = Authorize.get_jwt_subject()      

        current_user = db.query(User).filter(User.username==user).first()
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        new_access_token = Authorize.create_access_token(subject=current_user.username, expires_time=access_lifetime)
        response = {
            'success': True,
            'status_code': 201,
            'message': 'New access token is created',
            'data': {
                'acces_token': new_access_token}
        }
        return jsonable_encoder(response)
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh token")
    


