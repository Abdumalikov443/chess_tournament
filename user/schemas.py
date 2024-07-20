from typing import Optional
from pydantic import BaseModel, Field


class SignUpModel(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    is_staff: Optional[bool] = False

    # Example
    class Config:           
        orm_mode = True     
        json_schema_extra = {
            'example': {
                'username': "admin", 
                'email': 'admin@gmail.com',
                'password': 'password12345',
                'is_staff': 'True',
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = "72bbaec3bc58aae4034dced4504b67896043c31b605e742d982dbb9f72c19e4e"
    # authjwt_token_location: set = {"cookies"}
    # authjwt_cookie_csrf_protect: bool = False


class LoginModel(BaseModel):
    username_or_email: str
    password: str

