from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from db import db_dependency
from user.models import User
from .models import Player
from .schemas import PlayerCreate, PlayerUpdate
from dependencies import get_current_user



player = APIRouter(
    prefix="/player",
    tags=["player"]
)


@player.get("/list", status_code=status.HTTP_200_OK)
async def list_all_players(db: db_dependency, user: User=Depends(get_current_user)):
    if user.is_staff:
        players = db.query(Player).all()
        custom_data=[
            {
                "id": player.id,
                "name":player.name, 
                "age": player.age,
                "country": player.country
            }
            for player in players
        ]
        return jsonable_encoder(custom_data)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can see list of players")    


@player.get("/{player_id}", status_code=status.HTTP_200_OK)
async def get_player_by_id(player_id: int, db: db_dependency, user: User=Depends(get_current_user)):
    if user.is_staff:
        player = db.query(Player).filter_by(id=player_id).first()
        response={
            "id": player.id,
            "name": player.name,
            "age": player.age,
            "country": player.country
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can view information player")



@player.post("/create", status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerCreate, db: db_dependency, user: User = Depends(get_current_user)):
    if user.is_staff:
        if player.age<=0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Age should be greater than 0")
        
        if not (1 <= player.rating <= 5):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating should be set between 1 and 5")
        
        db_player = Player(
            name=player.name,
            age=player.age,
            rating=player.rating,
            country=player.country
        )
        db.add(db_player)
        db.commit()
        db.refresh(db_player)

        response={
            "success": True,
            "status_code": 201, 
            "message": "Player created successfully",
            "data": {
                "id": db_player.id, 
                "name": db_player.name,
                "age": db_player.age,
                "rating": db_player.rating, 
                "country": db_player.country
            }
        }
        return jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can create a player!")



@player.put("/{player_id}/update", status_code=status.HTTP_200_OK)
async def update_player(player_id: int, player: PlayerUpdate, db: db_dependency, user: User=Depends(get_current_user)):
    if user.is_staff:
        db_player = db.query(Player).filter(Player.id == player_id).first()

        if db_player is None:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if player.age<=0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Age should be greater than 0")
        
        if not (1 <= player.rating <= 5):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating should be set between 1 and 5")       

        db_player.name = player.name
        db_player.age = player.age
        db_player.rating = player.rating
        db_player.country = player.country

        db.commit()
        db.refresh(db_player)

        response = {
        "success": True,
        "status_code": 200,
        "message": "Player info is updated successfully",
        "data": {
            "id": db_player.id,
            "name": db_player.name,
            "age": db_player.age,
            "rating": db_player.rating,
            "country":db_player.country
            }
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can create a player!")


@player.delete("/{player_id}/delete", status_code=status.HTTP_200_OK)
async def delete_player(player_id: int, db: db_dependency, user: User=Depends(get_current_user)):
    if user.is_staff:
        player = db.query(Player).filter_by(id=player_id).first()
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

        db.delete(player)
        db.commit()
        return {"message": "Player deleted"}
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins can delete players")