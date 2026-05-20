import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Vote(Base):
    __tablename__ = "votes"

    voteId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    userId = Column(String, ForeignKey("users.userId"))
    roomId = Column(String, ForeignKey("rooms.roomId"))
    movieId = Column(String, ForeignKey("movies.movieId"))
    status = Column(String) # 'yes' or 'no'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="votes")
    room = relationship("Room", back_populates="votes")
    movie = relationship("Movie", back_populates="votes")
