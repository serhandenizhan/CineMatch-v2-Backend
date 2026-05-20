import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class MatchHistory(Base):
    __tablename__ = "match_histories"

    matchId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    roomId = Column(String, ForeignKey("rooms.roomId"))
    matchedMovieId = Column(String, ForeignKey("movies.movieId"))
    matchedAt = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="match_histories")
    movie = relationship("Movie", back_populates="match_histories")
