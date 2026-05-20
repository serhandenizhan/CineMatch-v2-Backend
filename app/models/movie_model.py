import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Movie(Base):
    __tablename__ = "movies"

    movieId = Column(String, primary_key=True, index=True) # TMDB id
    title = Column(String)
    director = Column(String)
    genre = Column(String) # Stored as comma separated
    posterUrl = Column(String)
    
    votes = relationship("Vote", back_populates="movie")
    match_histories = relationship("MatchHistory", back_populates="movie")
