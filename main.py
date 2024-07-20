from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT


from dependencies import get_current_user
from user.models import User
from user.schemas import Settings
from user.router import user
from player.router import player
from tournaments.router import tournament



@AuthJWT.load_config
def get_config():
    return Settings()


app = FastAPI()

app.include_router(user)
app.include_router(player)
app.include_router(tournament)



@app.get("/")
async def root():
    return {"message": "hello"}

