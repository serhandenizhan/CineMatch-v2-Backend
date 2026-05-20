import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    userId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    passwordHash = Column(String, nullable=False)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    profileId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    userId = Column(String, ForeignKey("users.userId"), unique=True)
    favoriteGenres = Column(String, default="") # Stored as comma separated string
    favoriteDirectors = Column(String, default="") # Stored as comma separated string
    watchHistory = Column(String, default="") # Stored as comma separated string

    user = relationship("User", back_populates="profile")
