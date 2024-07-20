from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    country = Column(String, nullable=False)

    leaderboard_entries = relationship("Leaderboard", back_populates="player")

    def __repr__(self):
        return f"<{self.name} from {self.country}>"

