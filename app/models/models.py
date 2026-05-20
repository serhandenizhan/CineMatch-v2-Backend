import uuid
from sqlalchemy import Column, String, Boolean, Table, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

# Many-to-Many relationship table for Users and Rooms
room_users = Table('room_users', Base.metadata,
    Column('room_id', String, ForeignKey('rooms.roomId')),
    Column('user_id', String, ForeignKey('users.userId'))
)

class User(Base):
    __tablename__ = "users"

    userId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    passwordHash = Column(String, nullable=False)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user")
    rooms = relationship("Room", secondary=room_users, back_populates="users")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    profileId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    userId = Column(String, ForeignKey("users.userId"), unique=True)
    favoriteGenres = Column(String, default="") # Stored as comma separated string
    favoriteDirectors = Column(String, default="") # Stored as comma separated string
    watchHistory = Column(String, default="") # Stored as comma separated string

    user = relationship("User", back_populates="profile")


class Room(Base):
    __tablename__ = "rooms"

    roomId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    joinCode = Column(String, unique=True, index=True)
    isActive = Column(Boolean, default=True)
    filterType = Column(String, default="popular")
    
    users = relationship("User", secondary=room_users, back_populates="rooms")
    votes = relationship("Vote", back_populates="room")
    match_histories = relationship("MatchHistory", back_populates="room")


class Movie(Base):
    __tablename__ = "movies"

    movieId = Column(String, primary_key=True, index=True) # TMDB id
    title = Column(String)
    director = Column(String)
    genre = Column(String) # Stored as comma separated string
    posterUrl = Column(String)
    
    votes = relationship("Vote", back_populates="movie")
    match_histories = relationship("MatchHistory", back_populates="movie")


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


class MatchHistory(Base):
    __tablename__ = "match_histories"

    matchId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    roomId = Column(String, ForeignKey("rooms.roomId"))
    matchedMovieId = Column(String, ForeignKey("movies.movieId"))
    matchedAt = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="match_histories")
    movie = relationship("Movie", back_populates="match_histories")
