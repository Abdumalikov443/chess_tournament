from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Any


# TOURNAMENT
class TournamentCreate(BaseModel):
    name: str
    start_date: date
    end_date: date

    @validator('start_date', 'end_date', pre=True)
    def parse_date(cls, value: Any) -> date:
        if isinstance(value, date):
            return value
        return datetime.strptime(value, '%Y.%m.%d').date()

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Chess Tournament",
                "start_date": "2024.03.01",
                "end_date": "2024.03.10"
            }
        }


class TournamentParticipantCreate(BaseModel):
    tournament_id: int
    player_id: int


# MATCH
class MatchCreate(BaseModel):
    tournament_id: int
    round_number: int


class MatchResult(BaseModel):
    match_id: int
    result: str  # example, "1-0", "0-1", "0.5-0.5"