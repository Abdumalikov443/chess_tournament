from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from user.models import Leaderboard, User
from db import db_dependency
from dependencies import get_current_user
from algorithm import generate_leaderboard, generate_matches, update_scores
from .models import Tournament, TournamentParticipant
from .schemas import MatchResult, TournamentCreate, TournamentParticipantCreate, MatchCreate


tournament = APIRouter(
    prefix="/tournament",
    tags=["tournament"]
)


@tournament.get("/list", status_code=status.HTTP_200_OK)
async def get_list_of_tournaments(db: db_dependency):
    tournaments = db.query(Tournament).all()
    custom_data=[
        {
            "id":t.id, 
            "name":t.name,
            "started_date": t.start_date,
            "end_date": t.end_date,
            "creator": t.creator.full_name,
            "participants": len(t.participants)
        }
        for t in tournaments
    ]
    return jsonable_encoder(custom_data)


@tournament.post("/create", status_code=status.HTTP_201_CREATED)
async def create_tournament(tournament: TournamentCreate, db: db_dependency, user: User=Depends(get_current_user)):
    if user.is_staff:
        existing_tournament = db.query(Tournament).filter_by(name=tournament.name).first()
        if existing_tournament:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tournament with this name already exists")

        new_tournament = Tournament(
            name=tournament.name, 
            start_date=tournament.start_date,
            end_date=tournament.end_date, 
            creator_id=user.id
        )

        db.add(new_tournament)
        db.commit()
        db.refresh(new_tournament)
        
        response={
            "success": True,
            "status_code": 201,
            "message": "Tournament successfully created",
            "data":{
                "id": new_tournament.id,
                "name": new_tournament.name,
                "start_date": new_tournament.start_date,
                "end_date": new_tournament.end_date,
                "creator_id": new_tournament.creator_id
            }
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not allowed to create Tournaments")


@tournament.post("/participant/add", status_code=status.HTTP_200_OK)
async def add_participant(participant: TournamentParticipantCreate, db: db_dependency, user: User=Depends(get_current_user)):
    if user.is_staff:
        t_participant = TournamentParticipant(
            tournament_id=participant.tournament_id, 
            player_id = participant.player_id
        )
        db.add(t_participant)
        db.commit()
        db.refresh(t_participant)

        response={
            "success": True,
            "status_code": 200,
            "message": f"{t_participant.player.name} has been added to the {t_participant.tournament.name} tournament",
            "data":{
                "tournament_id": t_participant.tournament_id,
                "player_id": t_participant.player_id
            }
        }
        return jsonable_encoder(response)
    

@tournament.get("/{t_id}/participant/list", status_code=status.HTTP_200_OK)
async def get_participants_by_tournament_id(db: db_dependency, t_id: int, user: User=Depends(get_current_user)):
    if user.is_staff:
        t_p = db.query(Tournament).filter(Tournament.id == t_id).first()
        if t_p:
            custom_data = [
                {
                    "participant_id": i.player.id,
                    "name": i.player.name,
                    "age": i.player.age,
                    "country": i.player.country
                }
                for i in t_p.participants
            ]
            return jsonable_encoder(custom_data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tournament is not found on this id --> {t_id}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to get tournament participants!")


@tournament.post("/{t_id}/generate_matches", status_code=status.HTTP_201_CREATED)
async def create_match(t_id: int, match: MatchCreate, db: db_dependency, user: User=Depends(get_current_user)):
    if user.is_staff:
        tournament = db.query(Tournament).filter_by(id=t_id).first()
        if not tournament:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")
    
        match_details = generate_matches(tournament_id=t_id, round_number=match.round_number, db=db)
    
        response={
            "success": True,
            "status_code": 201,
            "message": f"Match is created in {tournament.name} tournament",
            "data": match_details
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins allowed to generate matches")



@tournament.put("/{t_id}/update_scores")
async def update_tournament_scores(t_id: int, match_results: List[MatchResult], db: db_dependency, user: User = Depends(get_current_user)):
    if user.is_staff:
        tournament = db.query(Tournament).filter_by(id=t_id).first()
        if not tournament:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")
    
        update_scores(t_id, match_results, db)
        response = {
            "success": True,
            "status_code": 200,
            "message": f"Scores updated for tournament {tournament.name}",
            "data": match_results
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins allowed to update scores")
    
    

@tournament.get("/{t_id}/leaderboard", status_code=status.HTTP_200_OK)
async def get_leaderboard(t_id: int, db: db_dependency):
    tournament = db.query(Tournament).filter(Tournament.id == t_id).first()
    if not tournament:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tournament not found with id {t_id}")

    leaderboard = db.query(Leaderboard).filter_by(tournament_id=t_id).order_by(Leaderboard.points.desc()).all()
    
    response = [
        {
            "player_id": entry.player.id,
            "player_name": entry.player.name,
            "points": entry.points
        }
        for entry in leaderboard
    ]
    return jsonable_encoder(response)
