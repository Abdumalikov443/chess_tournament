from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from tournaments.models import Tournament
from db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Text)      
    is_staff = Column(Boolean, default=False)

    tournaments = relationship("Tournament", back_populates="creator")

    def __repr__(self):
        return f"<{self.full_name}>"




class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournament.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    points = Column(Float, default=0)

    player = relationship("Player", back_populates="leaderboard_entries")
    tournament = relationship("Tournament", back_populates="leaderboard_entries")