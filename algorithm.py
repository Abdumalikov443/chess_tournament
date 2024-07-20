from sqlalchemy.orm import Session
from typing import List, Tuple
from player.models import Player
from tournaments.models import Tournament, TournamentParticipant, Match
from fastapi import HTTPException, status

from tournaments.schemas import MatchCreate, MatchResult
from dependencies import db_dependency
from user.models import Leaderboard



def get_player_pairings(tournament_id: int, db: db_dependency) -> List[Tuple[Player, Player]]:
    participants = db.query(TournamentParticipant).filter_by(tournament_id=tournament_id).all()
    players = [p.player for p in participants]

    players.sort(key=lambda p: p.rating, reverse=True)
    
    # Create pairings
    pairings = []
    paired_players = set()
    for i in range(0, len(players), 2):
        p1 = players[i]
        if i + 1 < len(players):
            p2 = players[i + 1]
        else:
            p2 = None
        if p2 and (p1, p2) not in paired_players and (p2, p1) not in paired_players:
            pairings.append((p1, p2))
            paired_players.add((p1, p2))
            paired_players.add((p2, p1))
    
    return pairings


def generate_matches(tournament_id: int, round_number: int, db: db_dependency):
    pairings = get_player_pairings(tournament_id, db)
    match_details = []

    for player1, player2 in pairings:
        new_match = Match(
            tournament_id=tournament_id,
            round_number=round_number,
            player1_id=player1.id,
            player2_id=player2.id,
        )
        db.add(new_match)
        db.commit()

        match_details.append({
            "id": new_match.id,
            "tournament_id": new_match.tournament_id,
            "round": new_match.round_number,
            "player1_id": new_match.player1_id,
            "player2_id": new_match.player2_id
        })
    return match_details


def update_scores(tournament_id: int, match_results: List[MatchResult], db: db_dependency):
    for result in match_results:
        match_id = result.match_id
        result_str = result.result

        match = db.query(Match).filter_by(id=match_id).first()
        if match:
            match.result = result_str
            db.commit()

            if result_str == "1-0":
                player1_points = 1
                player2_points = 0
            elif result_str == "0-1":
                player1_points = 0
                player2_points = 1
            elif result_str == "0.5-0.5":
                player1_points = 0.5
                player2_points = 0.5

            update_leaderboard(match.tournament_id, match.player1_id, player1_points, db)
            update_leaderboard(match.tournament_id, match.player2_id, player2_points, db)


def update_leaderboard(tournament_id: int, player_id: int, points: float, db: db_dependency):
    entry = db.query(Leaderboard).filter_by(tournament_id=tournament_id, player_id=player_id).first()
    if entry:
        entry.points += points
    else:
        new_entry = Leaderboard(tournament_id=tournament_id, player_id=player_id, points=points)
        db.add(new_entry)
    db.commit()



def calculate_points(match: Match, player_id: int):
    if match.result == "1-0" and match.player1_id == player_id:
        return 1
    if match.result == "0-1" and match.player2_id == player_id:
        return 1
    if match.result == "0.5-0.5":
        return 0.5
    return 0


def generate_leaderboard(tournament: Tournament, db: db_dependency):
    players = db.query(Player).join(TournamentParticipant).filter(TournamentParticipant.tournament_id == tournament.id).all()
    leaderboard = []

    for player in players:
        matches = db.query(Match).filter((Match.player1_id == player.id) | (Match.player2_id == player.id), Match.tournament_id == tournament.id).all()
        points = sum(calculate_points(match, player.id) for match in matches)
        
        leaderboard.append({
            "player_id": player.id,
            "name": player.name,
            "points": points
        })

    leaderboard.sort(key=lambda x: x["points"], reverse=True)
    return leaderboard
