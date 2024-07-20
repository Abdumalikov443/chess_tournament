from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from player.models import Player
from db import Base


class Tournament(Base):
    __tablename__ = "tournament"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    creator = relationship("User", back_populates="tournaments")
    participants = relationship("TournamentParticipant", back_populates="tournament")
    matches = relationship("Match", back_populates="tournament")
    leaderboard_entries = relationship("Leaderboard", back_populates="tournament")


class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournament.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)

    tournament = relationship("Tournament", back_populates="participants")
    player = relationship("Player")
    


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournament.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    player1_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    result = Column(String, nullable=True)  # Store results like "1-0", "0-1", "0.5-0.5"

    tournament = relationship("Tournament", back_populates="matches")
    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])

